import json, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
from app import pipeline, rag, opencode, config


class Job:
    def text(self, *a):
        pass

    def tool_start(self, *a):
        return "x"

    def tool_done(self, *a, **kw):
        pass


class CoreTests(unittest.TestCase):
    def test_mathematical_latin_pdf_text_normalization(self):
        from app.latexbuild import normalize_generated_tex

        tex = "A bound 𝐾, italic 𝑥, bold italic 𝒙, double struck 𝔼, digit 𝟛, Greek 𝛼."
        out = normalize_generated_tex(tex)
        self.assertEqual(
            out,
            r"A bound \ensuremath{\mathit{K}}, italic \ensuremath{\mathit{x}}, bold italic \ensuremath{\boldsymbol{x}}, double struck \ensuremath{\mathbb{E}}, digit \ensuremath{\mathbb{3}}, Greek 𝛼.",
        )
        self.assertEqual(normalize_generated_tex(out), out)
        self.assertEqual(
            normalize_generated_tex("ASCII K, cafe é, $K$, 20\\%"),
            "ASCII K, cafe é, $K$, 20\\%",
        )

    def test_ask_and_ambiguous_are_read_only(self):
        t = {"phase": "done"}
        self.assertEqual(pipeline.route("What does the paper say?", t)[0], "ask")
        self.assertEqual(
            pipeline.route("/ask What is RAG?", {"phase": "new"})[0], "ask"
        )
        self.assertEqual(pipeline.route("something unclear", t)[0], "ask")
        self.assertEqual(pipeline.route("/edit Rewrite conclusion", t)[0], "edit")
        self.assertEqual(
            pipeline.route("/resume", {"phase": "reading_paused"})[0], "resume"
        )

    def test_chunks_keep_pages(self):
        chunks = rag.chunk_pages([(2, "a " * 2000), (9, "b " * 1000)])
        self.assertTrue(chunks)
        for page, text in chunks:
            self.assertIn(page, (2, 9))
            self.assertNotIn("b" if page == 2 else "a", text)

    def test_segments_are_bounded_and_lossless(self):
        text = "=== PAGE 1 ===\n" + "X" * 80000
        segs = pipeline._segments(text)
        self.assertEqual("".join(segs), text)
        self.assertTrue(all(len(s) <= 12000 for s in segs))

    def test_retrieval_sql_scopes_thread(self):
        with patch.object(rag, "assert_collection_model"), patch.object(
            rag, "embed", return_value=[[1, 0]]
        ), patch.object(rag.db, "q", return_value=[]) as query:
            self.assertEqual(rag.retrieve("chat-A", "question"), [])
            sql, args = query.call_args.args
            self.assertIn("WHERE c.thread_id=%s", sql)
            self.assertEqual(args[1], "chat-A")

    def test_hosted_calls_fail_closed(self):
        with patch.object(
            config, "VOYAGE_API_KEY", "test-only-not-a-key"
        ), patch.object(config, "HOSTED_CALLS", False):
            with self.assertRaises(rag.EmbeddingError):
                rag._voyage(["hello"], "document")

    def test_watchdog_kills_silent_process(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake"
            path.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n")
            path.chmod(0o755)
            with patch.object(config, "OPENCODE_BIN", str(path)):
                start = time.monotonic()
                events = list(
                    opencode.run(Path(td), "x", model="fixture/test", timeout=0.3)
                )
                self.assertLess(time.monotonic() - start, 3)
                self.assertFalse(events[-1]["ok"])

    def test_read_resume_never_accepts_partial(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sources").mkdir()
            (root / "notes").mkdir()
            source = root / "sources/k.txt"
            source.write_text("X" * 25000)
            row = {
                "status": "indexed",
                "key": "k",
                "id": "s",
                "title": "fixture",
                "text_path": str(source),
            }
            calls = []

            def fake(cwd, prompt, **kw):
                import re

                i = int(re.search(r"k\.(\d+)\.txt", prompt)[1])
                calls.append(i)
                (root / "notes/k" / f"{i}.md").write_text("fixture notes " * 15)
                return "fixture notes " * 15, True, None, []

            with patch.object(pipeline.db, "sources", return_value=[row]), patch.object(
                pipeline.db, "update_source"
            ), patch.object(
                pipeline.opencode, "run_text", side_effect=fake
            ), patch.object(
                pipeline, "MAX_SEGMENTS_PER_RUN", 1
            ):
                self.assertEqual(len(pipeline.read_papers(Job(), "t", root)), 1)
                self.assertEqual(len(pipeline.read_papers(Job(), "t", root)), 1)
                self.assertEqual(calls, list(range(1, 8)))


if __name__ == "__main__":
    unittest.main()


class BuildSafetyTests(unittest.TestCase):
    def test_literal_percent_does_not_comment_out_prose(self):
        from app.latexbuild import normalize_generated_tex

        self.assertEqual(normalize_generated_tex(r"13.6% lower"), r"13.6\% lower")
        self.assertEqual(normalize_generated_tex(r"13.6\% lower"), r"13.6\% lower")
        self.assertEqual(normalize_generated_tex("% real comment"), "% real comment")

    def test_resume_review_does_not_restart_discovery(self):
        self.assertEqual(
            pipeline.route("/resume", {"phase": "review_paused"})[0], "resume"
        )


class InlineTableTests(unittest.TestCase):
    def test_inline_table_normalization_is_idempotent(self):
        from app.latexbuild import normalize_generated_tex

        source = r"\documentclass{article}\usepackage{array,float}\begin{document}\begin{table}[H]X\end{table}\end{document}"
        result = normalize_generated_tex(source)
        self.assertIn(r"\renewenvironment{table}", result)
        self.assertNotIn(",float}", result)
        self.assertEqual(normalize_generated_tex(result), result)


class SpringerSafetyTests(unittest.TestCase):
    def test_anonymous_front_matter(self):
        from app.latexbuild import normalize_generated_tex

        source = r"\documentclass[runningheads]{llncs}\begin{document}\author{Anonymous}\maketitle"
        result = normalize_generated_tex(source)
        self.assertIn(r"\institute{}", result)
        self.assertIn(r"\titlerunning{", result)
        self.assertEqual(normalize_generated_tex(result), result)


class DocumentSafetyTests(unittest.TestCase):
    def test_unsafe_tex_blocked_before_compile(self):
        from app import latexbuild

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text(r"\input{/etc/passwd}")
            with patch.object(
                latexbuild.db, "thread_dir", return_value=root
            ), patch.object(latexbuild, "_run") as run:
                result = latexbuild.build("fixture")
                self.assertFalse(result["ok"])
                run.assert_not_called()


class ApiValidationTests(unittest.TestCase):
    def test_invalid_template_and_empty_request_rejected(self):
        from app.main import NewThread, Chat, Retrieve
        from pydantic import ValidationError

        for cls, value in [
            (NewThread, {"template": "../other"}),
            (Chat, {"text": ""}),
            (Retrieve, {"thread_id": "x", "query": "x", "k": -1}),
        ]:
            with self.assertRaises(ValidationError):
                cls(**value)

    def test_path_traversal_rejected(self):
        from app import db

        with self.assertRaises(ValueError):
            db.thread_dir("../other")

    def test_foreign_origin_mutation_rejected(self):
        from fastapi.testclient import TestClient
        from app.main import app

        c = TestClient(app)
        r = c.post(
            "/api/threads", headers={"Origin": "https://untrusted.invalid"}, json={}
        )
        self.assertEqual(r.status_code, 403)

    def test_running_thread_cannot_be_deleted(self):
        from app.main import delete, RUNNING
        from fastapi import HTTPException
        from types import SimpleNamespace

        RUNNING["test-running"] = SimpleNamespace(done=False)
        try:
            with patch(
                "app.main.db.get_thread", return_value={"id": "test-running"}
            ), patch("app.main.db.delete_thread") as remove:
                with self.assertRaises(HTTPException) as e:
                    delete("test-running")
                self.assertEqual(e.exception.status_code, 409)
                remove.assert_not_called()
        finally:
            RUNNING.pop("test-running", None)


class PlannerTests(unittest.TestCase):
    def test_inline_plan_disables_tools_and_saves_request(self):
        class J:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        response = json.dumps(
            {
                "title": "Graph retrieval review",
                "queries": [
                    "graph retrieval augmented generation recent advances",
                    "graph retrieval foundations",
                ],
                "sections": ["Review"],
                "keywords": ["graph RAG"],
            }
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(
                opencode, "run_text", return_value=(response, True, None, [])
            ), patch.object(pipeline.db, "update_thread"):
                result = pipeline.plan(
                    J(), "fixture", "latest graph RAG advancements", root
                )
            self.assertEqual(result["request"], "latest graph RAG advancements")
            self.assertEqual(
                json.loads((root / "plan-stage/opencode.json").read_text())[
                    "permission"
                ],
                {"*": "deny"},
            )
            self.assertTrue((root / "plan.json").exists())

    def test_invalid_model_plan_uses_labeled_fallback(self):
        class J:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td, patch.object(
            opencode, "run_text", return_value=("not json", False, None, [])
        ), patch.object(pipeline.db, "update_thread"):
            result = pipeline.plan(J(), "fixture", "review graph RAG", Path(td))
            self.assertTrue(result["fallback"])

    def test_planner_anchors_current_year_not_training_year(self):
        from datetime import datetime, timezone

        class J:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td, patch.object(
            opencode, "run_text", return_value=("invalid", False, None, [])
        ) as run, patch.object(pipeline.db, "update_thread"):
            pipeline.plan(J(), "fixture", "latest graph RAG", Path(td))
            self.assertIn(
                datetime.now(timezone.utc).date().isoformat(), run.call_args.args[1]
            )
            self.assertIn("never RLL", run.call_args.args[1])


class PlanDriftTests(unittest.TestCase):
    def test_rag_term_and_unrequested_old_year_drift_use_visible_fallback(self):
        import tempfile, json
        from pathlib import Path

        class J:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        for title, queries in [
            ("Graph RLL review", ["graph retrieval methods"]),
            ("Graph RAG review", ["graph retrieval 2023"]),
        ]:
            with tempfile.TemporaryDirectory() as td, patch.object(
                pipeline.opencode,
                "write_config",
                side_effect=lambda work, *a: (work / "opencode.json").write_text(
                    '{"agent":{"paperforge":{}}}'
                ),
            ), patch.object(
                pipeline.opencode,
                "run_text",
                return_value=(
                    json.dumps({"title": title, "queries": queries}),
                    True,
                    None,
                    [],
                ),
            ), patch.object(
                pipeline.db, "update_thread"
            ):
                result = pipeline.plan(
                    J(), "fixture", "latest graph RAG advancements", Path(td)
                )
                self.assertTrue(result["fallback"])
                self.assertNotIn("Rll", result["title"])
                self.assertNotIn("2023", " ".join(result["queries"]))


class InlineWorkerTests(unittest.TestCase):
    def test_tool_free_stage_overrides_file_worker_prompt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            opencode.write_config(root, [])
            cfg = json.loads((root / "opencode.json").read_text())
            cfg["agent"]["paperforge"]["tools"] = {"*": False}
            (root / "opencode.json").write_text(json.dumps(cfg))
            with patch.object(config, "OPENCODE_BIN", "/bin/echo"), patch.object(
                config, "MODEL", "fixture"
            ):
                list(opencode.run(root, "Return Markdown directly", timeout=1))
            prompt = json.loads((root / "opencode.json").read_text())["agent"][
                "paperforge"
            ]["prompt"]
            self.assertIn("Return the requested content directly", prompt)
            self.assertNotIn("Use read and write/edit", prompt)
