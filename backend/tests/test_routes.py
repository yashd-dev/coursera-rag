import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import main, pipeline, answering, config


class RouteTests(unittest.TestCase):
    def test_ask_route_direct_answering_no_document_writes(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "paper.tex"
            file.write_text("unchanged")
            t = {"phase": "done", "template": "ieee", "custom": {}}
            hit = {
                "key": "paper2026",
                "page": 2,
                "score": 0.9,
                "text": "Only fixture evidence.",
            }
            source = {
                "key": "paper2026",
                "authors": "Fixture Author",
                "year": 2026,
                "title": "Fixture",
                "status": "indexed",
            }
            with patch.object(main.db, "get_thread", return_value=t), patch.object(
                main.db, "add_message"
            ), patch.object(
                pipeline.db, "sources", return_value=[source]
            ), patch.object(
                pipeline.rag, "retrieve", return_value=[hit]
            ), patch.object(
                pipeline.rag, "stats", return_value={}
            ), patch.object(
                pipeline.answering,
                "answer_native",
                side_effect=[
                    '{"sentences":[{"text":"Fixture answer supported by the passage.","evidence_ids":[1]}]}',
                    '{"verdict":"supported","reason":"ok"}',
                ],
            ) as ans, patch.object(
                pipeline.opencode, "run_text"
            ) as agent, patch.object(
                pipeline.db, "thread_dir"
            ) as directory:
                r = TestClient(main.app).post(
                    "/api/threads/route-ask/chat", json={"text": "What is reported?"}
                )
                self.assertEqual(r.status_code, 200)
                self.assertIn("Fixture answer", r.text)
                self.assertEqual(ans.call_count, 2)
                agent.assert_not_called()
                directory.assert_not_called()
                self.assertEqual(file.read_text(), "unchanged")
                self.assertEqual(list(Path(td).iterdir()), [file])

    def test_edit_route_invokes_document_agent_not_answerer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text("before")
            t = {"phase": "done", "template": "ieee", "custom": {}}
            with patch.object(main.db, "get_thread", return_value=t), patch.object(
                main.db, "add_message"
            ), patch.object(main.db, "update_thread"), patch.object(
                main.db, "thread_dir", return_value=root
            ), patch.object(
                pipeline.latexbuild, "prepare"
            ), patch.object(
                pipeline.opencode, "run_text", return_value=("no edit", True, None, [])
            ) as agent, patch.object(
                pipeline.answering, "answer"
            ) as answer:
                r = TestClient(main.app).post(
                    "/api/threads/route-edit/chat",
                    json={"text": "/edit Rewrite conclusion"},
                )
                self.assertEqual(r.status_code, 200)
                agent.assert_called_once()
                answer.assert_not_called()
                self.assertTrue(list((root / "history").glob("*.tex")))

    def test_answering_disabled_by_default(self):
        with patch.object(config, "ANSWER_CALLS", False):
            with self.assertRaises(answering.AnswerError):
                answering.answer("fixture")

    def test_failed_template_edit_restores_saved_template(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text("before")
            t = {"phase": "ready", "template": "ieee", "custom": {}}

            class J:
                def tool_start(self, *a):
                    return "x"

                def tool_done(self, *a, **kw):
                    pass

                def finish(self, *a):
                    pass

            with patch.object(pipeline.db, "get_thread", return_value=t), patch.object(
                pipeline.db, "thread_dir", return_value=root
            ), patch.object(pipeline.db, "update_thread") as update, patch.object(
                pipeline.latexbuild, "prepare"
            ), patch.object(
                pipeline.opencode, "run_text", return_value=("invalid", False, None, [])
            ):
                pipeline.run_edit(J(), "fixture", "/edit Convert to Springer")
                self.assertEqual(
                    update.call_args.kwargs, {"phase": "ready", "template": "ieee"}
                )
                self.assertEqual((root / "paper/main.tex").read_text(), "before")

    def test_interrupted_edit_resumes_original_request(self):
        import json

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = "/edit Convert to Springer"
            (root / "pending-edit.json").write_text(
                json.dumps(
                    {
                        "request": request,
                        "original": {"phase": "ready", "template": "ieee"},
                    }
                )
            )

            class J:
                pass

            job = J()
            with patch.object(
                pipeline.db, "get_thread", return_value={"phase": "edit_paused"}
            ), patch.object(
                pipeline.latexbuild, "prepare", return_value=root
            ), patch.object(
                pipeline.opencode, "available", return_value=(True, "fixture")
            ), patch.object(
                pipeline, "run_edit"
            ) as edit:
                pipeline.run_create(job, "fixture", "/resume", "springer")
                edit.assert_called_once_with(
                    job,
                    "fixture",
                    request,
                    original={"phase": "ready", "template": "ieee"},
                )
            self.assertEqual(
                pipeline.route("/resume", {"phase": "edit_paused"})[0], "resume"
            )

    def test_saved_edit_patch_resumes_build_not_repeated_edit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            class J:
                def finish(self, *a):
                    pass

            with patch.object(
                pipeline.db, "get_thread", return_value={"phase": "review_paused"}
            ), patch.object(
                pipeline.latexbuild, "prepare", return_value=root
            ), patch.object(
                pipeline.opencode, "available", return_value=(True, "fixture")
            ), patch.object(
                pipeline, "build_loop", return_value=({"ok": False}, None)
            ) as build, patch.object(
                pipeline.db, "update_thread"
            ), patch.object(
                pipeline, "run_edit"
            ) as edit:
                pipeline.run_create(J(), "fixture", "/resume", "ieee")
                build.assert_called_once()
                edit.assert_not_called()

    def test_crash_after_patch_write_does_not_repeat_edit(self):
        import hashlib, json

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text("edited")
            (root / "pending-edit.json").write_text(
                json.dumps(
                    {
                        "request": "/edit change",
                        "original": {"phase": "ready", "template": "ieee"},
                        "before_sha256": hashlib.sha256(b"before").hexdigest(),
                    }
                )
            )
            state = {"phase": "edit_paused"}

            def update(tid, **kw):
                state.update(kw)

            class J:
                def finish(self, *a):
                    pass

            with patch.object(
                pipeline.db, "get_thread", side_effect=lambda tid: state
            ), patch.object(
                pipeline.db, "update_thread", side_effect=update
            ), patch.object(
                pipeline.latexbuild, "prepare", return_value=root
            ), patch.object(
                pipeline.opencode, "available", return_value=(True, "fixture")
            ), patch.object(
                pipeline, "build_loop", return_value=({"ok": False}, None)
            ) as build, patch.object(
                pipeline, "run_edit"
            ) as edit:
                pipeline.run_create(J(), "fixture", "/resume", "ieee")
                edit.assert_not_called()
                build.assert_called_once()

    def test_link_section_edit_passes_new_evidence_and_protects_other_sections(self):
        import json
        from app import source_links

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "notes").mkdir()
            before = r"\section{Introduction} Keep this exact.\section{Target} Old section content.\section{Conclusion} Keep ending.\bibliographystyle{IEEEtran}\bibliography{refs}\end{document}"
            (root / "paper/main.tex").write_text(before)
            (root / "notes/new2026.md").write_text(
                "New source supported finding, physical page2."
            )
            source = {
                "id": "new",
                "key": "new2026",
                "title": "New source",
                "status": "indexed",
            }
            state = {"phase": "ready", "template": "ieee", "custom": {}}

            class J:
                def tool_start(self, *a):
                    return "x"

                def tool_done(self, *a, **kw):
                    pass

                def finish(self, *a):
                    pass

                def text(self, *a):
                    pass

            response = json.dumps(
                {
                    "addition": "New source reports a supported finding for this distinct direction.",
                    "summary": "Added source",
                }
            )
            with patch.object(
                pipeline.db, "get_thread", return_value=state
            ), patch.object(pipeline.db, "thread_dir", return_value=root), patch.object(
                pipeline.db, "update_thread"
            ), patch.object(
                source_links, "ingest", return_value=source
            ) as ingest, patch.object(
                pipeline, "read_papers", return_value=[source]
            ), patch.object(
                pipeline.latexbuild, "write_bib"
            ), patch.object(
                pipeline.latexbuild, "prepare"
            ), patch.object(
                pipeline.rag,
                "retrieve",
                return_value=[
                    {
                        "key": "new2026",
                        "page": 2,
                        "text": "Exact supported source finding.",
                    }
                ],
            ), patch.object(
                pipeline.opencode, "run_text", return_value=(response, True, None, [])
            ) as model, patch.object(
                pipeline, "build_loop", return_value=({"ok": True, "pages": 1}, None)
            ), patch.object(
                pipeline, "review_claims", return_value=(True, None)
            ), patch.object(
                pipeline, "export_all", return_value=([], {"rendered": True})
            ):
                pipeline.run_edit(
                    J(), "fixture", "/edit Add https://example.org/paper.pdf to Target"
                )
                ingest.assert_called_once()
                prompt = model.call_args.args[1]
                self.assertIn("physical page2", prompt)
                self.assertIn("PAGE EVIDENCE", prompt)
                self.assertNotIn("Keep ending.", prompt)
                after = (root / "paper/main.tex").read_text()
                self.assertIn(
                    r"New source reports a supported finding for this distinct direction. \cite{new2026}",
                    after,
                )
                self.assertTrue(after.startswith(before.split(r"\section{Target}")[0]))
                self.assertTrue(
                    after.endswith(before[before.index(r"\section{Conclusion}") :])
                )

    def test_unnamed_new_source_attribution_is_repaired_once_and_raw_key_removed(self):
        import json
        from app import source_links

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "notes").mkdir()
            before = r"\section{Introduction} Keep this exact.\section{Target} Old section content.\section{Conclusion} Keep ending.\bibliographystyle{IEEEtran}\bibliography{refs}\end{document}"
            (root / "paper/main.tex").write_text(before)
            (root / "notes/new2026.md").write_text(
                "New source supported finding, physical page2."
            )
            source = {
                "id": "new",
                "key": "new2026",
                "title": "New source",
                "status": "indexed",
            }
            state = {"phase": "ready", "template": "ieee", "custom": {}}

            class J:
                def tool_start(self, *a):
                    return "x"

                def tool_done(self, *a, **kw):
                    pass

                def finish(self, *a):
                    pass

                def text(self, *a):
                    pass

            response = json.dumps(
                {
                    "addition": "New source reports a supported finding for this distinct direction.",
                    "summary": "Added source",
                }
            )
            with patch.object(
                pipeline.db, "get_thread", return_value=state
            ), patch.object(pipeline.db, "thread_dir", return_value=root), patch.object(
                pipeline.db, "update_thread"
            ), patch.object(
                source_links, "ingest", return_value=source
            ) as ingest, patch.object(
                pipeline, "read_papers", return_value=[source]
            ), patch.object(
                pipeline.latexbuild, "write_bib"
            ), patch.object(
                pipeline.latexbuild, "prepare"
            ), patch.object(
                pipeline.rag,
                "retrieve",
                return_value=[
                    {
                        "key": "new2026",
                        "page": 2,
                        "text": "Exact supported source finding.",
                    }
                ],
            ), patch.object(
                pipeline.opencode,
                "run_text",
                side_effect=[
                    (
                        json.dumps(
                            {
                                "addition": "The new source shows a supported finding [new2026, p.2] for this distinct direction.",
                                "summary": "x",
                            }
                        ),
                        True,
                        None,
                        [],
                    ),
                    (
                        json.dumps(
                            {
                                "addition": "New source reports a supported finding for this distinct direction.",
                                "summary": "x",
                            }
                        ),
                        True,
                        None,
                        [],
                    ),
                ],
            ) as model, patch.object(
                pipeline, "build_loop", return_value=({"ok": True, "pages": 1}, None)
            ), patch.object(
                pipeline, "review_claims", return_value=(True, None)
            ), patch.object(
                pipeline, "export_all", return_value=([], {"rendered": True})
            ):
                pipeline.run_edit(
                    J(), "fixture", "/edit Add https://example.org/paper.pdf to Target"
                )
                ingest.assert_called_once()
                self.assertEqual(model.call_count, 2)
                prompt = model.call_args_list[0].args[1]
                self.assertIn("physical page2", prompt)
                self.assertIn("PAGE EVIDENCE", prompt)
                self.assertNotIn("Keep ending.", prompt)
                after = (root / "paper/main.tex").read_text()
                self.assertIn(
                    r"New source reports a supported finding for this distinct direction. \cite{new2026}",
                    after,
                )
                self.assertTrue(after.startswith(before.split(r"\section{Target}")[0]))
                self.assertTrue(
                    after.endswith(before[before.index(r"\section{Conclusion}") :])
                )

    def test_unnamed_new_source_attribution_still_unnamed_keeps_original(self):
        import json
        from app import source_links

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "notes").mkdir()
            before = r"\section{Introduction} Keep this exact.\section{Target} Old section content.\section{Conclusion} Keep ending.\bibliographystyle{IEEEtran}\bibliography{refs}\end{document}"
            (root / "paper/main.tex").write_text(before)
            (root / "notes/new2026.md").write_text(
                "New source supported finding, physical page2."
            )
            source = {
                "id": "new",
                "key": "new2026",
                "title": "New source",
                "status": "indexed",
            }
            state = {"phase": "ready", "template": "ieee", "custom": {}}

            class J:
                def tool_start(self, *a):
                    return "x"

                def tool_done(self, *a, **kw):
                    pass

                def finish(self, *a):
                    pass

                def text(self, *a):
                    pass

            response = json.dumps(
                {
                    "addition": "New source reports a supported finding for this distinct direction.",
                    "summary": "Added source",
                }
            )
            with patch.object(
                pipeline.db, "get_thread", return_value=state
            ), patch.object(pipeline.db, "thread_dir", return_value=root), patch.object(
                pipeline.db, "update_thread"
            ), patch.object(
                source_links, "ingest", return_value=source
            ) as ingest, patch.object(
                pipeline, "read_papers", return_value=[source]
            ), patch.object(
                pipeline.latexbuild, "write_bib"
            ), patch.object(
                pipeline.latexbuild, "prepare"
            ), patch.object(
                pipeline.rag,
                "retrieve",
                return_value=[
                    {
                        "key": "new2026",
                        "page": 2,
                        "text": "Exact supported source finding.",
                    }
                ],
            ), patch.object(
                pipeline.opencode,
                "run_text",
                side_effect=[
                    (
                        json.dumps(
                            {
                                "addition": "The new source shows a supported finding [new2026, p.2] for this distinct direction.",
                                "summary": "x",
                            }
                        ),
                        True,
                        None,
                        [],
                    ),
                    (
                        json.dumps(
                            {
                                "addition": "The new source shows a supported finding [new2026, p.2] for this distinct direction.",
                                "summary": "x",
                            }
                        ),
                        True,
                        None,
                        [],
                    ),
                ],
            ) as model, patch.object(
                pipeline, "build_loop", return_value=({"ok": True, "pages": 1}, None)
            ), patch.object(
                pipeline, "review_claims", return_value=(True, None)
            ), patch.object(
                pipeline, "export_all", return_value=([], {"rendered": True})
            ):
                pipeline.run_edit(
                    J(), "fixture", "/edit Add https://example.org/paper.pdf to Target"
                )
                ingest.assert_called_once()
                self.assertEqual(model.call_count, 2)
                prompt = ""
                self.assertEqual((root / "paper/main.tex").read_text(), before)

    def test_answer_cannot_cite_unretrieved_page(self):
        hits = [{"key": "fixture", "page": 1}]
        self.assertEqual(
            answering.validate_citations("A supported passage. [fixture p.1]", hits),
            "A supported passage. [fixture p.1]",
        )
        with self.assertRaises(answering.AnswerError):
            answering.validate_citations("A claim. [fixture p.9]", hits)
        with self.assertRaises(answering.AnswerError):
            answering.validate_citations(
                "An uncited paragraph.\n\nAnother claim. [fixture p.1]", hits
            )

    def test_structured_answer_assigns_pages_from_evidence_ids(self):
        hits = [{"key": "a", "page": 6}, {"key": "b", "page": 2}]
        self.assertEqual(
            answering.render_evidence_answer(
                '{"sentences":[{"text":"A supported factual sentence.","evidence_ids":[1]}]}',
                hits,
            ),
            "A supported factual sentence. [a p.6] (not independently checked)",
        )
        with self.assertRaises(answering.AnswerError):
            answering.render_evidence_answer(
                '{"sentences":[{"text":"A factual sentence.","evidence_ids":[7]}]}',
                hits,
            )


class AnswerStatusTests(unittest.TestCase):
    def test_rate_limit_and_auth_errors_are_classified_without_response_body(self):
        import httpx
        from unittest.mock import patch

        for status, expected in [
            (429, "rate limit"),
            (401, "access refused"),
            (503, "temporarily unavailable"),
        ]:
            response = httpx.Response(
                status,
                request=httpx.Request(
                    "POST", "https://provider.invalid/chat/completions"
                ),
                text="private diagnostic body",
                headers={"retry-after": "60"},
            )
            with patch.object(config, "ANSWER_CALLS", True), patch.object(
                config, "ANSWER_BASE_URL", "https://provider.invalid"
            ), patch.object(config, "ANSWER_MODEL", "fixture"), patch.object(
                config, "ANSWER_API_KEY", "fixture"
            ), patch(
                "httpx.post", return_value=response
            ):
                with self.assertRaises(answering.AnswerError) as error:
                    answering.answer("fixture")
                self.assertIn(expected, str(error.exception))
                self.assertNotIn("private diagnostic", str(error.exception))


class SourceScopeTests(unittest.TestCase):
    def test_unique_named_paper_scopes_retrieval(self):
        rows = [
            {
                "key": "edge2024",
                "title": "From Local to Global Graph RAG",
                "authors": "Darren Edge, Ha Trinh",
                "status": "indexed",
            },
            {
                "key": "other2026",
                "title": "Other graph approach",
                "authors": "Other Author",
                "status": "indexed",
            },
        ]
        self.assertEqual(
            answering.named_source("How does the Edge GraphRAG source work?", rows),
            "edge2024",
        )
        self.assertEqual(
            answering.named_source("What does edge2024 report?", rows), "edge2024"
        )
        self.assertIsNone(
            answering.named_source(
                "Compare Edge source and Author source approaches", rows
            )
        )
        self.assertIsNone(
            answering.named_source("How do community summaries work?", rows)
        )
        self.assertIsNone(answering.named_source("How does edge filtering work?", rows))

    def test_shared_surname_is_not_guessed(self):
        rows = [
            {"key": "a", "authors": "Darren Edge", "status": "indexed"},
            {"key": "b", "authors": "Another Edge", "status": "indexed"},
        ]
        self.assertIsNone(answering.named_source("Edge source", rows))


class AnswerGroundingTests(unittest.TestCase):
    H = [
        {
            "key": "cai",
            "page": 3,
            "text": "Medusa heads are additional decoding heads. Medusa-1 keeps the backbone frozen while Medusa-2 trains jointly.",
        },
        {
            "key": "chen",
            "page": 5,
            "text": "Choice of draft models: any drafter that exposes logits.",
        },
    ]

    def r(self, t, ids, **kw):
        import json

        return answering.render_evidence_answer(
            json.dumps({"sentences": [{"text": t, "evidence_ids": ids}]}), self.H, **kw
        )

    def test_scope_rejects_other_source_citation(self):
        out = self.r(
            "Medusa uses extra decoding heads on the model.", [1, 2], scope_key="cai"
        )
        self.assertIn("do not contain enough evidence", out)
        self.assertIn(
            "[cai p.3]",
            self.r(
                "Medusa uses extra decoding heads on the model.", [1], scope_key="cai"
            ),
        )

    def test_unsupported_absolute_dropped_supported_kept(self):
        self.assertIn(
            "not contain enough",
            self.r(
                "It works without computational overhead from auxiliary models.", [1]
            ),
        )
        self.assertIn(
            "[cai p.3]", self.r("Medusa heads are additional decoding heads.", [1])
        )
        h = [
            {
                "key": "k",
                "page": 1,
                "text": "This is done without extra overhead in practice.",
            }
        ]
        import json

        self.assertIn(
            "[k p.1]",
            answering.render_evidence_answer(
                json.dumps(
                    {
                        "sentences": [
                            {
                                "text": "It is done without extra overhead.",
                                "evidence_ids": [1],
                            }
                        ]
                    }
                ),
                h,
            ),
        )

    def test_veto_only_verifier(self):
        self.assertIn(
            "withheld",
            self.r(
                "Medusa heads are additional decoding heads.",
                [1],
                verify=lambda t, h: False,
            ),
        )
        self.assertIn(
            "[cai p.3]",
            self.r(
                "Medusa-2 trains the heads jointly with the backbone.",
                [1],
                verify=lambda t, h: True,
            ),
        )
        # an unchecked sentence is never presented as an answer, labelled or not
        out = self.r(
            "Medusa heads are additional decoding heads.", [1], verify=lambda t, h: None
        )
        self.assertIn("withheld", out)
        self.assertNotIn("[cai", out)
        self.assertNotIn(
            "not independently",
            self.r(
                "Medusa heads are additional decoding heads.",
                [1],
                verify=lambda t, h: True,
            ),
        )

    def test_partial_withholding_is_disclosed(self):
        import json

        h = [{"key": "k", "page": 1, "text": "Heads are added on top of the model."}]
        raw = json.dumps(
            {
                "sentences": [
                    {
                        "text": "Heads are added on top of the model.",
                        "evidence_ids": [1],
                    },
                    {
                        "text": "Heads are added with no cost at all.",
                        "evidence_ids": [1],
                    },
                ]
            }
        )
        out = answering.render_evidence_answer(
            raw, h, None, lambda t, x: "no cost" not in t
        )
        self.assertIn("[k p.1]", out)
        self.assertIn("1 further drafted sentence could not be verified", out)

    def test_training_claim_must_keep_variants_or_is_omitted(self):
        self.assertIn(
            "not contain enough",
            self.r("Medusa trains the heads jointly with the backbone.", [1]),
        )
        self.assertIn(
            "[cai p.3]",
            self.r(
                "Medusa-1 keeps the backbone frozen while Medusa-2 trains jointly.", [1]
            ),
        )
        self.assertIn(
            "[chen p.5]",
            self.r("Any drafter that exposes logits can train separately.", [2]),
        )

    def test_method_name_scopes_source(self):
        srcs = [
            {
                "key": "cai2024medusa",
                "status": "indexed",
                "title": "Medusa: Simple LLM Inference Acceleration",
                "authors": "Tianle Cai",
            },
            {
                "key": "chen2023accelerating",
                "status": "indexed",
                "title": "Accelerating Large Language Model Decoding with Speculative Sampling",
                "authors": "Charlie Chen",
            },
        ]
        self.assertEqual(
            answering.named_source(
                "According to the Medusa paper, how are tokens drafted?", srcs
            ),
            "cai2024medusa",
        )
        self.assertIsNone(
            answering.named_source("How does speculative sampling work?", srcs)
        )
