import unittest
from app.continuation import BudgetProgress, continue_budgeted


class Job:
    def text(self, *a):
        pass


class ContinuationTests(unittest.TestCase):
    def test_budget_progress_continues_without_new_user_turn(self):
        calls = []

        def step():
            calls.append(1)
            if len(calls) < 4:
                raise BudgetProgress("read", len(calls), 4)
            return "complete"

        self.assertEqual(continue_budgeted(step, Job()), "complete")
        self.assertEqual(len(calls), 4)

    def test_no_progress_stops(self):
        calls = []

        def step():
            calls.append(1)
            raise BudgetProgress("read", 1, 4)

        self.assertIsNone(continue_budgeted(step, Job()))
        self.assertEqual(len(calls), 2)

    def test_real_errors_are_not_retried(self):
        calls = []

        def step():
            calls.append(1)
            raise ValueError("provider error")

        with self.assertRaises(ValueError):
            continue_budgeted(step, Job())
        self.assertEqual(len(calls), 1)

    def test_finite_safety_limit(self):
        calls = []

        def step():
            calls.append(1)
            raise BudgetProgress("read", len(calls), 100)

        self.assertIsNone(continue_budgeted(step, Job(), max_slices=3))
        self.assertEqual(len(calls), 3)


class StageContinuationTests(unittest.TestCase):
    def test_read_provider_error_stops_without_retry_even_after_saved_progress(self):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch
        from app import pipeline

        class J(Job):
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "sources").mkdir()
            p = r / "sources/k.txt"
            p.write_text("X" * 9000)
            row = {"id": "s", "key": "k", "status": "indexed", "text_path": str(p)}
            with patch.object(pipeline.db, "sources", return_value=[row]), patch.object(
                pipeline.db, "update_source"
            ), patch.object(pipeline, "MAX_SEGMENTS_PER_RUN", 1), patch.object(
                pipeline.opencode,
                "run_text",
                side_effect=[
                    ("good factual notes " * 10, True, None, []),
                    ("", False, None, [{"kind": "error", "message": "HTTP429"}]),
                ],
            ) as model:
                self.assertEqual(pipeline.read_papers(J(), "t", r), [])
                self.assertEqual(model.call_count, 2)
                self.assertEqual(
                    json.loads((r / "notes/k/progress.json").read_text())["done"], [1]
                )

    def test_review_budget_slices_complete_without_retrying_semantic_failure(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from app import span_review, evidence

        class J(Job):
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "paper").mkdir()
            blocks = [
                "A specific supported claim has enough words to require evidence.",
                "Another specific supported claim has enough words to require evidence.",
            ]
            (r / "paper/main.tex").write_text(
                r"\maketitle" + "\n" + "\n\n".join(blocks)
            )
            p = r / "source.txt"
            p.write_text("=== PAGE 1 ===\n" + "Source evidence sentence. " * 10)
            row = {"key": "k", "status": "indexed", "text_path": str(p)}

            def review(root, i, block, *a):
                return [
                    {
                        "draft_quote": block,
                        "claim": block,
                        "source_key": "k",
                        "page": 1,
                        "quote": "Source evidence sentence.",
                        "status": "supported",
                    }
                ], []

            with patch.object(
                span_review.db, "sources", return_value=[row]
            ), patch.object(span_review, "spans", return_value=blocks), patch.object(
                span_review, "review_one", side_effect=review
            ) as model, patch.object(
                evidence, "validate", return_value=[]
            ):
                self.assertTrue(
                    continue_budgeted(
                        lambda: span_review.review_all(J(), "t", r, [], max_spans=1),
                        J(),
                    )
                )
                self.assertEqual(model.call_count, 2)

    def test_review_budget_does_not_hide_integrity_error(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from app import span_review, evidence

        class J(Job):
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "paper").mkdir()
            (r / "paper/main.tex").write_text("draft")
            p = r / "source.txt"
            p.write_text("=== PAGE 1 ===\nSource evidence sentence. " * 5)
            row = {"key": "k", "status": "indexed", "text_path": str(p)}
            with patch.object(
                span_review.db, "sources", return_value=[row]
            ), patch.object(
                span_review, "spans", return_value=["first span", "second span"]
            ), patch.object(
                span_review,
                "review_one",
                return_value=([{"draft_quote": "first span"}], []),
            ) as model, patch.object(
                evidence,
                "validate",
                return_value=["Ledger draft_sha256 does not match the current TeX"],
            ):
                self.assertFalse(
                    continue_budgeted(
                        lambda: span_review.review_all(J(), "t", r, [], max_spans=1),
                        J(),
                    )
                )
                self.assertEqual(model.call_count, 1)


class OneRequestTests(unittest.TestCase):
    def test_one_creation_request_crosses_read_budgets_and_finishes_exports(self):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch
        from app import pipeline, drafting

        class J(Job):
            def __init__(self):
                self.finished = []

            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

            def finish(self, *a):
                self.finished.append(a)

        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "sources").mkdir()
            (r / "paper").mkdir()
            p = r / "sources/k.txt"
            p.write_text("X" * 9000)
            row = {"id": "s", "key": "k", "status": "indexed", "text_path": str(p)}
            (r / "plan.json").write_text(
                json.dumps({"title": "Fixture", "sections": []})
            )
            (r / "paper/main.tex").write_text("draft")
            (r / "paper/main.pdf").write_bytes(b"fixture")
            state = {"phase": "reading_paused", "template": "ieee"}

            def update(tid, **kw):
                state.update(kw)

            job = J()
            with patch.object(
                pipeline.db, "get_thread", side_effect=lambda tid: state
            ), patch.object(
                pipeline.db, "update_thread", side_effect=update
            ), patch.object(
                pipeline.db, "sources", return_value=[row]
            ), patch.object(
                pipeline.db, "update_source"
            ), patch.object(
                pipeline.latexbuild, "prepare", return_value=r
            ), patch.object(
                pipeline.latexbuild, "write_bib", return_value=[row]
            ), patch.object(
                pipeline.opencode, "available", return_value=(True, "fixture")
            ), patch.object(
                pipeline.opencode,
                "run_text",
                return_value=("factual source notes " * 10, True, None, []),
            ) as native, patch.object(
                pipeline, "MAX_SEGMENTS_PER_RUN", 1
            ), patch.object(
                drafting, "generate", return_value=(True, None)
            ), patch.object(
                pipeline, "build_loop", return_value=({"ok": True, "pages": 1}, None)
            ), patch.object(
                pipeline, "review_claims", return_value=(True, None)
            ), patch.object(
                pipeline,
                "export_all",
                return_value=(
                    [{"name": "paper.pdf", "label": "PDF"}],
                    {"rendered": True},
                ),
            ), patch.object(
                pipeline.rag, "stats", return_value={"chunks": 3}
            ):
                pipeline.run_create(job, "fixture", "/resume", "ieee")
            self.assertEqual(state["phase"], "ready")
            self.assertEqual(native.call_count, 3)
            self.assertEqual(job.finished, [()])


class ExecutionStateTests(unittest.TestCase):
    def test_running_job_and_dead_process_are_distinct(self):
        from unittest.mock import patch
        from app import main

        class Running:
            done = False

        with patch.object(
            main.db, "get_thread", return_value={"phase": "reading_paused"}
        ), patch.object(main.db, "list_messages", return_value=[]):
            main.RUNNING["status-fixture"] = Running()
            try:
                self.assertEqual(
                    main.messages("status-fixture")["execution_state"], "running"
                )
            finally:
                main.RUNNING.pop("status-fixture", None)
            self.assertEqual(
                main.messages("status-fixture")["execution_state"], "paused"
            )
