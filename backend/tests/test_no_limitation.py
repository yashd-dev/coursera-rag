import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from app import drafting, limitations as l, section_purpose


class Job:
    def __init__(self):
        self.done, self.texts = [], []

    def tool_start(self, *a):
        return "x"

    def tool_done(self, tc, result, error=False):
        self.done.append((result, error))

    def text(self, s):
        self.texts.append(s)


def row(key):
    return {"key": key, "title": f"Title {key}", "status": "indexed", "authors": "Author", "year": 2025}


def section():
    d = {k: "A supported narrow source description" for k in ["summary", "limitations", "approach", "evaluation", "abstract", "introduction", "conclusion"]}
    d["evaluation"] = "Foo corpus"
    d["abstract"] = "The review describes evidence with a different abstract sentence."
    return d


def root_with(td, keys):
    root = Path(td)
    (root / "notes").mkdir()
    (root / "paper").mkdir()
    for k in keys:
        (root / f"notes/{k}.md").write_text("Source facts")
    (root / "plan.json").write_text(json.dumps({"keywords": ["k"]}))
    return root


class NoLimitationTests(unittest.TestCase):
    def test_zero_candidates_is_not_extracted_not_failure(self):
        with tempfile.TemporaryDirectory() as td:
            rows = [{"page": 1, "quote": "Plain results sentence without any boundary terms at all."}]
            with patch.object(l, "excerpts_for", return_value=rows), patch.object(l.structured, "run") as run:
                job = Job()
                self.assertEqual(l.classify_candidates(job, Path(td), {"key": "a"}), l.NOT_EXTRACTED)
                run.assert_not_called()
                self.assertFalse(job.done[-1][1])
                self.assertEqual(job.done[-1][0]["status"], "not_extracted")
                self.assertIn("does not mean", job.done[-1][0]["note"])

    def test_provider_failure_stays_failure(self):
        with tempfile.TemporaryDirectory() as td:
            rows = [{"page": 1, "quote": "One limitation statement concerns a method in the source."}]
            with patch.object(l, "excerpts_for", return_value=rows), patch.object(
                l.structured, "run", return_value=("", False, None, [])
            ):
                self.assertIsNone(l.classify_candidates(Job(), Path(td), {"key": "a"}))

    def test_no_limitation_anywhere_omits_section_and_review_accepts_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = root_with(td, ["a"])
            with patch.object(drafting.db, "sources", return_value=[row("a")]), patch.object(
                drafting.opencode, "run_text", return_value=(json.dumps(section()), True, None, [])
            ), patch("app.limitations.classify_candidates", return_value=l.NOT_EXTRACTED):
                job = Job()
                self.assertTrue(drafting.generate(job, "t", root, "T", "ieee")[0])
                tex = (root / "paper/main.tex").read_text()
                self.assertNotIn("Evidence limitations", tex)
                self.assertIn(drafting.NO_LIMITATIONS_MARKER, tex)
                self.assertTrue(any("omitted" in t for t in job.texts))
                self.assertTrue(section_purpose.check_limitations(job, root))

    def test_deleted_section_without_marker_still_fails_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text(r"\section{Conclusion} End")
            self.assertFalse(section_purpose.check_limitations(Job(), root))

    def test_mixed_sources_keep_only_supported_limitation(self):
        with tempfile.TemporaryDirectory() as td:
            root = root_with(td, ["a", "b"])
            outs = {"a": "The source authors state: \"Limit A.\"", "b": l.NOT_EXTRACTED}
            with patch.object(drafting.db, "sources", return_value=[row("a"), row("b")]), patch.object(
                drafting.opencode, "run_text", return_value=(json.dumps(section()), True, None, [])
            ), patch("app.limitations.classify_candidates", side_effect=lambda j, r, s, timeout=80: outs[s["key"]]):
                self.assertTrue(drafting.generate(Job(), "t", root, "T", "ieee")[0])
                tex = (root / "paper/main.tex").read_text()
                part = tex.split(r"\section{Evidence limitations}")[1].split(r"\section{Conclusion}")[0]
                self.assertIn("Limit A", part)
                self.assertEqual(part.count(r"\cite"), 1)

    def test_resume_reuses_cached_source_draft_without_new_model_call(self):
        with tempfile.TemporaryDirectory() as td:
            root = root_with(td, ["a"])
            with patch.object(drafting.db, "sources", return_value=[row("a")]), patch.object(
                drafting.opencode, "run_text", return_value=(json.dumps(section()), True, None, [])
            ) as run, patch("app.limitations.classify_candidates", return_value=l.NOT_EXTRACTED):
                self.assertTrue(drafting.generate(Job(), "t", root, "T", "ieee")[0])
                first = (root / "paper/main.tex").read_text()
                self.assertEqual(run.call_count, 1)
                self.assertTrue(drafting.generate(Job(), "t", root, "T", "ieee")[0])
                self.assertEqual(run.call_count, 1)
                self.assertEqual((root / "paper/main.tex").read_text(), first)

    def test_classifier_failure_closes_open_tool_entry(self):
        with tempfile.TemporaryDirectory() as td:
            root = root_with(td, ["a"])
            with patch.object(drafting.db, "sources", return_value=[row("a")]), patch.object(
                drafting.opencode, "run_text", return_value=(json.dumps(section()), True, None, [])
            ), patch("app.limitations.classify_candidates", return_value=None):
                job = Job()
                self.assertFalse(drafting.generate(job, "t", root, "T", "ieee")[0])
                self.assertTrue(job.done and job.done[-1][1])
                self.assertIn("not a finding about the source", job.done[-1][0]["error"])


if __name__ == "__main__":
    unittest.main()
