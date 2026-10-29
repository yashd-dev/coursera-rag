import json, os, tempfile, unittest
from pathlib import Path
from unittest import mock
from app import structured, config, span_review


class Rec(Exception):
    pass


def fake_run_capture(store):
    def popen(cmd, cwd=None, **k):
        store["cfg"] = json.loads((Path(cwd) / "opencode.json").read_text())
        raise Rec()

    return popen


class ReviewModelTests(unittest.TestCase):
    def _cfg(self):
        w = Path(tempfile.mkdtemp())
        from app import opencode

        opencode.write_config(w, [])
        return w

    def run_capture(self, **kw):
        w = self._cfg()
        store = {}
        with mock.patch(
            "app.structured.subprocess.Popen", side_effect=fake_run_capture(store)
        ):
            try:
                structured.run(w, "p", {"type": "object"}, timeout=3, **kw)
            except Rec:
                pass
        return store.get("cfg")

    def test_default_run_is_unchanged_and_has_no_reviewer_model(self):
        cfg = self.run_capture()
        self.assertEqual(
            list(cfg["provider"]["nvidia"]["models"]),
            ["nvidia/nemotron-3.5-lightning-30b-a3b"],
        )

    def test_reviewer_model_is_added_only_to_that_run_with_options_and_limit(self):
        with mock.patch.object(
            config,
            "REVIEW_MODEL_OPTIONS",
            '{"chat_template_kwargs":{"reasoning_effort":"medium"}}',
        ):
            cfg = self.run_capture(model_id="nvidia/minimaxai/minimax-m3.1-flash")
        m = cfg["provider"]["nvidia"]["models"]
        self.assertIn("minimaxai/minimax-m3.1-flash", m)
        self.assertIn("nvidia/nemotron-3.5-lightning-30b-a3b", m)
        e = m["minimaxai/minimax-m3.1-flash"]
        self.assertEqual(
            e["options"]["chat_template_kwargs"]["reasoning_effort"], "medium"
        )
        self.assertEqual(e["limit"]["output"], 4096)

    def test_bad_options_or_model_fail_typed_without_starting_anything(self):
        w = self._cfg()
        with mock.patch(
            "app.structured.subprocess.Popen",
            side_effect=AssertionError("must not start"),
        ):
            with mock.patch.object(config, "REVIEW_MODEL_OPTIONS", "{bad"):
                r = structured.run(w, "p", {"type": "object"}, model_id="nvidia/x/y")
                self.assertEqual(structured.outcome_code(r[3]), "invalid_model")
            with mock.patch.object(config, "REVIEW_MODEL_OPTIONS", ""):
                r = structured.run(w, "p", {"type": "object"}, model_id="nomodelslash")
                self.assertEqual(structured.outcome_code(r[3]), "invalid_model")

    def test_review_calls_pass_reviewer_model_but_repair_does_not(self):
        src = Path(span_review.__file__).read_text()
        self.assertEqual(src.count("model_id=(config.REVIEW_MODEL or None)"), 2)
        self.assertIn("structured.run(repair_work,prompt,schema,timeout=timeout)", src)

    def test_default_config_has_empty_reviewer_model(self):
        self.assertEqual(
            os.environ.get("PAPERFORGE_REVIEW_MODEL", ""), config.REVIEW_MODEL
        )

    def test_cache_key_includes_reviewer_model_only_when_set(self):
        src = Path(span_review.__file__).read_text()
        self.assertIn(
            "(('|review-model:'+config.REVIEW_MODEL) if config.REVIEW_MODEL else '')",
            src,
        )
        import hashlib

        self.assertEqual(
            hashlib.sha256(("a" + "b" + "").encode()).hexdigest(),
            hashlib.sha256(b"ab").hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
