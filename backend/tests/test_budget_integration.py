import os as _os
_os.environ["PAPERFORGE_CLAIM_CHECKER"] = "legacy"  # these tests cover the legacy LLM review path
"""Controlled local orchestration acceptance; no hosted provider success implied."""

import json, tempfile, unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from app import (
    pipeline,
    db,
    source_links,
    span_review,
    evidence,
    section_purpose,
    sections,
    drafting,
    main,
)
from fastapi import HTTPException


class Job:
    def __init__(self):
        self.finishes = []
        self.texts = []

    def text(self, t):
        self.texts.append(t)

    def tool_start(self, *a):
        return "x"

    def tool_done(self, *a, **kw):
        pass

    def finish(self, *a):
        self.finishes.append(a)


BEFORE = (
    r"\maketitle"
    + "\n"
    + r"\section{Introduction}"
    + "\nKeep this original introduction exactly.\n"
    + r"\section{Conclusion}"
    + "\nKeep the existing conclusion.\n"
    + r"\begin{table}Source & Approach & Evaluation \\ \end{table}"
    + "\n"
    + r"\bibliographystyle{IEEEtran}\bibliography{refs}\end{document}"
)


class IntegrationTests(unittest.TestCase):
    def exercise(self, mode="edit", fail=None):
        with tempfile.TemporaryDirectory() as td, ExitStack() as stack:
            r = Path(td)
            (r / "paper").mkdir()
            (r / "sources").mkdir()
            (r / "paper/main.tex").write_text(BEFORE)
            (r / "paper/main.pdf").write_bytes(b"fixture")
            state = {
                "phase": "ready" if mode == "edit" else "new",
                "template": "ieee",
                "custom": {},
            }
            rows = []
            counts = {
                "add": 0,
                "index": 0,
                "resolve": 0,
                "edit": 0,
                "read": 0,
                "draft": 0,
                "export": 0,
                "discovery": 0,
                "review": 0,
            }

            def patcher(obj, name, *a, **kw):
                return stack.enter_context(patch.object(obj, name, *a, **kw))

            def update(tid, **kw):
                state.update(kw)

            def add(tid, row):
                counts["add"] += 1
                rows.append(dict(row, id="source", pages=1, chunk_count=3))
                return "source"

            def upd(sid, **kw):
                rows[0].update(kw)

            def resolve(url, root):
                counts["resolve"] += 1
                p = root / "sources/source.pdf"
                p.write_bytes(b"%PDF fixture")
                return (
                    {
                        "key": "unused",
                        "title": "Controlled source",
                        "authors": "Fixture Author",
                        "year": 2026,
                        "url": url,
                        "pdf_url": url,
                    },
                    p,
                    "fixturehash",
                    1,
                )

            def index(*a):
                counts["index"] += 1
                return 3

            def model(work, prompt, **kw):
                if "Read the entire source segment" in prompt:
                    counts["read"] += 1
                    if fail == "read" and counts["read"] == 2:
                        return (
                            "",
                            False,
                            None,
                            [{"kind": "error", "message": "provider unavailable"}],
                        )
                    return "Supported controlled source notes. " * 8, True, None, []
                counts["edit"] += 1
                return (
                    json.dumps(
                        {
                            "addition": "Author provides a bounded supported addition about graph community summaries.",
                            "summary": "Added controlled evidence.",
                        }
                    ),
                    True,
                    None,
                    [],
                )

            def review_one(root, i, block, *a):
                counts["review"] += 1
                if fail == "review":
                    return [], ["Span semantic evidence mismatch"]
                return [
                    {
                        "draft_quote": block,
                        "claim": block,
                        "source_key": rows[0]["key"],
                        "page": 1,
                        "quote": "Controlled source evidence.",
                        "status": "supported",
                    }
                ], []

            def exports(*a):
                counts["export"] += 1
                return [], {"rendered": True}

            def build(*a):
                if mode == "create":
                    self.assertIn(state["phase"], ("editing", "review_paused"))
                return {"ok": True, "pages": 1}, None

            patcher(db, "get_thread", side_effect=lambda tid: state)
            patcher(db, "update_thread", side_effect=update)
            patcher(db, "sources", side_effect=lambda tid: rows)
            patcher(db, "thread_dir", return_value=r)
            patcher(db, "add_source", side_effect=add)
            patcher(db, "update_source", side_effect=upd)
            patcher(source_links, "resolve", side_effect=resolve)
            patcher(
                source_links.research,
                "extract_pages",
                return_value=[(1, "Controlled source evidence. " * 400)],
            )
            patcher(source_links.research, "needs_ocr", return_value=False)
            patcher(source_links.rag, "index_source", side_effect=index)
            patcher(pipeline, "MAX_SEGMENTS_PER_RUN", 1)
            patcher(pipeline.opencode, "run_text", side_effect=model)
            patcher(pipeline.opencode, "available", return_value=(True, "fixture"))
            patcher(pipeline.rag, "retrieve", return_value=[])
            patcher(pipeline.rag, "stats", return_value={"chunks": 3})
            patcher(pipeline.latexbuild, "write_bib", side_effect=lambda tid: rows)
            patcher(pipeline.latexbuild, "prepare", return_value=r)
            patcher(pipeline, "build_loop", side_effect=build)
            patcher(pipeline, "export_all", side_effect=exports)
            patcher(span_review.structured, "run", return_value=("", False, None, []))
            patcher(
                span_review,
                "spans",
                side_effect=lambda tex: [x for x in tex.splitlines() if len(x) > 15][
                    :4
                ],
            )
            patcher(span_review, "review_one", side_effect=review_one)
            patcher(evidence, "validate", return_value=[])
            patcher(
                section_purpose, "check_limitations", return_value=fail != "purpose"
            )
            patcher(section_purpose, "repair_limitations", return_value=False)
            stack.enter_context(
                patch.dict(
                    "os.environ",
                    {
                        "PAPERFORGE_REVIEW_SPAN_BUDGET": "1",
                        "PAPERFORGE_REVIEW_REPAIR_ROUNDS": "1",
                    },
                )
            )

            def discover(*a):
                counts["discovery"] += 1
                source_links.ingest(a[0], a[1], "https://fixture.invalid/paper.pdf", r)
                return 1

            def draft(*a, **kw):
                counts["draft"] += 1
                return True, None

            patcher(pipeline, "discover_and_index", side_effect=discover)
            patcher(drafting, "generate", side_effect=draft)

            def plan(*a):
                p = {"title": "Controlled topic", "sections": []}
                (r / "plan.json").write_text(json.dumps(p))
                return p

            patcher(pipeline, "plan", side_effect=plan)
            job = Job()
            if mode == "edit":
                pipeline.run_edit(
                    job,
                    "fixture",
                    "/edit Add https://fixture.invalid/paper.pdf to Conclusion",
                )
            else:
                pipeline.run_create(job, "fixture", "Create controlled topic", "ieee")
            after = (r / "paper/main.tex").read_text()
            patcher(main.db, "list_messages", return_value=[])
            self.assertEqual(
                main.messages("fixture")["execution_state"],
                "ready" if state["phase"] == "ready" else "paused",
            )
            if fail:
                with self.assertRaises(HTTPException) as blocked:
                    main.files("fixture", "paper.pdf")
                self.assertEqual(blocked.exception.status_code, 409)
            if mode == "edit":
                sections.assert_preserved(
                    BEFORE, after, sections.locate(BEFORE, "Conclusion")
                )
            self.assertEqual(counts["add"], 1)
            self.assertEqual(counts["index"], 1)
            self.assertEqual(counts["resolve"], 1)
            self.assertEqual(len(rows), 1)
            if fail == "read":
                self.assertEqual(after, BEFORE)
                self.assertEqual(counts["edit"], 0)
                self.assertEqual(counts["export"], 0)
                self.assertNotEqual(state["phase"], "ready")
                self.assertEqual(counts["read"], 2)
            elif fail:
                self.assertEqual(counts["export"], 0)
                self.assertEqual(state["phase"], "review_paused")
                if mode == "edit":
                    self.assertEqual(after.count("Author provides"), 1)
                if fail == "purpose":
                    fail = None
                    patcher(section_purpose, "check_limitations", return_value=True)
                    pipeline.run_create(Job(), "fixture", "/resume", "ieee")
                    self.assertEqual(state["phase"], "ready")
                    self.assertEqual(counts["export"], 1)
                    self.assertEqual(counts["edit"], 1)
                    self.assertEqual(counts["add"], 1)
                    self.assertEqual(counts["index"], 1)
                    self.assertEqual((r / "paper/main.tex").read_text(), after)
            else:
                self.assertEqual(state["phase"], "ready")
                self.assertEqual(counts["export"], 1)
                self.assertGreater(counts["read"], 1)
                self.assertGreater(counts["review"], 1)
                self.assertEqual(job.finishes, [()])
                if mode == "edit":
                    self.assertEqual(counts["edit"], 1)
                    self.assertEqual(after.count("Author provides"), 1)
                else:
                    self.assertEqual(counts["draft"], 1)
                    self.assertEqual(counts["discovery"], 1)

    def test_new_link_read_and_review_slices_preserve_exact_outside_and_single_patch(
        self,
    ):
        self.exercise()

    def test_creation_budget_slices_do_not_repeat_discovery_ingestion_or_draft(self):
        self.exercise("create")

    def test_new_link_provider_error_stops_before_patch(self):
        self.exercise(fail="read")

    def test_new_link_semantic_failure_never_exports_or_reapplies_patch(self):
        self.exercise(fail="review")

    def test_new_link_purpose_failure_never_exports(self):
        self.exercise(fail="purpose")

    def test_creation_provider_error_stops_before_draft(self):
        self.exercise("create", fail="read")

    def test_creation_semantic_failure_never_exports(self):
        self.exercise("create", fail="review")
