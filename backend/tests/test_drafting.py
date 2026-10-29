import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from app import drafting


class Job:
    def tool_start(self, *args):
        return "x"

    def tool_done(self, *args, **kwargs):
        pass


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.limitation = patch(
            "app.limitations.classify_candidates",
            return_value="Author notes a supported method scope boundary.",
        )
        self.limitation.start()
        self.addCleanup(self.limitation.stop)

    def test_escaped_text(self):
        self.assertEqual(drafting.escape("50% & x_y"), r"50\% \& x\_y")

    def test_source_and_synthesis_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("Source facts")
            (root / "plan.json").write_text(json.dumps({"keywords": ["keyword"]}))
            row = {
                "key": "a",
                "title": "Source title",
                "status": "indexed",
                "authors": "Author",
                "year": 2025,
            }
            section = {
                **{
                    k: "A supported narrow source description"
                    for k in [
                        "summary",
                        "limitations",
                        "approach",
                        "evaluation",
                        "abstract",
                        "introduction",
                        "conclusion",
                    ]
                },
                "evaluation": "Foo corpus",
            }
            section["abstract"] = (
                "The review describes evidence with a different abstract sentence."
            )
            synth = {
                "abstract": "This review describes the processed evidence and its limits.",
                "introduction": "The question concerns a comparison of the processed methods and evidence.",
                "conclusion": "The sources provide distinct findings and do not establish a unified ranking.",
            }
            with patch.object(drafting.db, "sources", return_value=[row]), patch.object(
                drafting.opencode,
                "run_text",
                side_effect=[(json.dumps(section), True, None, [])],
            ) as run:
                self.assertTrue(drafting.generate(Job(), "t", root, "Title", "ieee")[0])
                self.assertEqual(run.call_count, 1)
                self.assertIn(
                    "named source authors or method and their research aim",
                    run.call_args.args[1],
                )
                self.assertNotIn("about this paper purpose", run.call_args.args[1])
                self.assertTrue(drafting.generate(Job(), "t", root, "Title", "ieee")[0])
                self.assertEqual(run.call_count, 1)
            tex = (root / "paper/main.tex").read_text()
            self.assertIn(r"\section{Introduction}", tex)
            self.assertIn(r"\section{Conclusion}", tex)
            self.assertIn("keyword", tex)
            abstract = tex.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
            self.assertNotIn(section["summary"], abstract)

    def test_ambiguous_self_attribution_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("Source facts")
            (root / "plan.json").write_text("{}")
            row = {
                "key": "a",
                "title": "Source title",
                "status": "indexed",
                "authors": "Author",
                "year": 2025,
            }
            data = {
                **{
                    k: "A supported narrow source description"
                    for k in [
                        "summary",
                        "limitations",
                        "approach",
                        "evaluation",
                        "abstract",
                        "introduction",
                        "conclusion",
                    ]
                },
                "evaluation": "Foo corpus",
            }
            data["introduction"] = (
                "This paper proposes the method as a new contribution."
            )
            with patch.object(drafting.db, "sources", return_value=[row]), patch.object(
                drafting.opencode,
                "run_text",
                return_value=(json.dumps(data), True, None, []),
            ):
                self.assertFalse(
                    drafting.generate(Job(), "t", root, "Title", "ieee")[0]
                )
            self.assertFalse((root / "paper/main.tex").exists())

    def test_explicit_attribution_repair_retries_once(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("Source facts")
            (root / "plan.json").write_text("{}")
            row = {
                "key": "a",
                "title": "Source title",
                "status": "indexed",
                "authors": "Author",
                "year": 2025,
            }
            data = {
                **{
                    k: "Author describes a supported narrow source finding"
                    for k in [
                        "summary",
                        "limitations",
                        "approach",
                        "evaluation",
                        "abstract",
                        "introduction",
                        "conclusion",
                    ]
                },
                "evaluation": "Foo corpus",
            }
            bad = dict(data, abstract="This paper proposes a new method in the field.")
            with patch.object(drafting.db, "sources", return_value=[row]), patch.object(
                drafting.opencode,
                "run_text",
                side_effect=[
                    (json.dumps(bad), True, None, []),
                    (json.dumps(data), True, None, []),
                ],
            ) as run:
                self.assertTrue(drafting.generate(Job(), "t", root, "Title", "ieee")[0])
                self.assertEqual(run.call_count, 2)
            self.assertNotIn(
                "This paper proposes", (root / "paper/main.tex").read_text()
            )

    def test_near_spelled_author_name_blocks_without_silent_rewrite(self):
        self.assertTrue(
            drafting.author_spelling_mismatch(
                {"introduction": "Jakik Hossain proposes a method."},
                "Jakir Hossain, Ahmet Erdem Sarıyüce",
            )
        )
        self.assertTrue(
            drafting.author_spelling_mismatch(
                {"summary": "Ahmet Erdem Sarüüe proposes a method."},
                "Jakir Hossain, Ahmet Erdem Sarıyüce",
            )
        )
        self.assertFalse(
            drafting.author_spelling_mismatch(
                {"introduction": "Hossain proposes a method."},
                "Jakir Hossain, Ahmet Erdem Sarıyüce",
            )
        )
        self.assertFalse(
            drafting.author_spelling_mismatch(
                {"introduction": "GraphRAG describes global summaries."},
                "Jakir Hossain, Ahmet Erdem Sarıyüce",
            )
        )


class RegressionTests(unittest.TestCase):
    keys = {"chen2023accelerating", "leviathan2022fast"}

    def test_raw_citation_keys_are_removed_only_for_indexed_keys(self):
        t = "Chen proposed it [chen2023accelerating, p.1]. Also see [chen2023accelerating; leviathan2022fast] and [Table 1] and [unknown2020, p.2]."
        out = drafting.strip_raw_citations(t, self.keys)
        r = drafting.render_cites(drafting.escape(out))
        self.assertIn(r"\cite[p.~1]{chen2023accelerating}", r)
        self.assertIn(r"\cite{leviathan2022fast}", r)
        self.assertNotIn("[chen2023accelerating", r)
        self.assertIn("[Table 1]", out)
        self.assertIn("[unknown2020, p.2]", out)
        self.assertIn("Chen proposed it", out)

    def test_untouched_text_without_keys_is_identical(self):
        t = "Plain text [1] with brackets."
        self.assertEqual(drafting.strip_raw_citations(t, self.keys), t)

    def test_outcome_labels_rejected_task_labels_accepted(self):
        for bad in (
            "target model Mp",
            "draft model Mq",
            "decoding speedup",
            "wall-time comparison",
            "accuracy improvement",
            "latency",
        ):
            self.assertTrue(drafting.outcome_label(bad), bad)
        for good in (
            "XSum and HumanEval",
            "translation and summarization",
            "T5-XXL translation",
        ):
            self.assertFalse(drafting.outcome_label(good), good)

    def test_task_label_must_occur_in_source_text(self):
        src = "We evaluate on XSum summarization and HumanEval code generation."
        self.assertFalse(drafting.ungrounded_label("XSum and HumanEval", src))
        self.assertTrue(drafting.ungrounded_label("Medical question answering", src))
        self.assertTrue(drafting.outcome_label("tokens accepted"))
        self.assertFalse(
            drafting.ungrounded_label(
                "ENDE translation and summarization",
                "We tested English to German translation fine tuned on WMT ENDE, and summarization tasks.",
            )
        )
        self.assertTrue(drafting.ungrounded_label("XSum and ImageNet", src))
        refs = "We evaluate on translation.\nReferences\nBengio. Language modeling with pathways. 2021."
        self.assertTrue(drafting.ungrounded_label("language modeling benchmarks", refs))
        self.assertFalse(drafting.ungrounded_label("translation", refs))
        self.assertFalse(drafting.ungrounded_label("anything", ""))

    def test_new_source_must_be_named(self):
        src = {
            "authors": "Tianle Cai, Yuhong Li",
            "title": "Medusa: Simple LLM Inference Acceleration Framework",
        }
        self.assertFalse(
            drafting.names_source("The new source demonstrates heads.", src)
        )
        self.assertFalse(drafting.names_source("Heads are attached to the model.", src))
        self.assertTrue(drafting.names_source("Cai et al. attach decoding heads.", src))
        self.assertTrue(drafting.names_source("Medusa attaches decoding heads.", src))

    def test_ieee_caption_precedes_table_rows(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("x")
            (root / "plan.json").write_text("{}")
            row = {
                "key": "a",
                "title": "T",
                "status": "indexed",
                "authors": "Au Thor",
                "year": 2025,
            }
            d = {
                **{
                    k: "Thor describes a supported narrow finding"
                    for k in [
                        "summary",
                        "limitations",
                        "approach",
                        "evaluation",
                        "abstract",
                        "introduction",
                        "conclusion",
                    ]
                },
                "evaluation": "Foo corpus",
            }
            d["introduction"] = "Thor proposes it [a, p.1]."
            with patch.object(drafting.db, "sources", return_value=[row]), patch.object(
                drafting.opencode,
                "run_text",
                return_value=(json.dumps(d), True, None, []),
            ), patch(
                "app.limitations.classify_candidates",
                return_value="Thor notes a scope.",
            ):
                self.assertTrue(drafting.generate(Job(), "t", root, "Title", "ieee")[0])
            tex = (root / "paper/main.tex").read_text()
            self.assertLess(tex.index(r"\caption{"), tex.index(r"\begin{tabular}"))
            self.assertNotIn("[a, p.1]", tex)
            self.assertIn(r"\cite[p.~1]{a}", tex)

    def test_outcome_evaluation_cell_triggers_task_repair_then_blocks_if_still_outcome(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("x")
            (root / "plan.json").write_text("{}")
            row = {
                "key": "a",
                "title": "T",
                "status": "indexed",
                "authors": "Au Thor",
                "year": 2025,
            }
            d = {
                **{
                    k: "Thor describes a supported narrow finding"
                    for k in [
                        "summary",
                        "limitations",
                        "approach",
                        "evaluation",
                        "abstract",
                        "introduction",
                        "conclusion",
                    ]
                },
                "evaluation": "Foo corpus",
            }
            d["evaluation"] = "decoding speedup"
            fixed = {"approach": "draft model", "evaluation": "XSum summarization"}
            with patch.object(drafting.db, "sources", return_value=[row]), patch.object(
                drafting.opencode,
                "run_text",
                side_effect=[
                    (json.dumps(d), True, None, []),
                    (json.dumps(fixed), True, None, []),
                ],
            ) as run, patch(
                "app.limitations.classify_candidates",
                return_value="Thor notes a scope.",
            ):
                self.assertTrue(drafting.generate(Job(), "t", root, "Title", "ieee")[0])
                self.assertEqual(run.call_count, 2)
            self.assertIn("XSum summarization", (root / "paper/main.tex").read_text())
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("x")
            (root / "plan.json").write_text("{}")
            still = {"approach": "draft model", "evaluation": "wall-time speedup"}
            with patch.object(drafting.db, "sources", return_value=[row]), patch.object(
                drafting.opencode,
                "run_text",
                side_effect=[
                    (json.dumps(d), True, None, []),
                    (json.dumps(still), True, None, []),
                    (json.dumps(still), True, None, []),
                ],
            ), patch(
                "app.limitations.classify_candidates",
                return_value="Thor notes a scope.",
            ):
                self.assertFalse(
                    drafting.generate(Job(), "t", root, "Title", "ieee")[0]
                )
            self.assertFalse((root / "paper/main.tex").exists())

    def test_evaluation_cell_that_restates_method_is_rejected(self):
        self.assertTrue(
            drafting.restates_method(
                "modified rejection sampling",
                "modified rejection sampling",
                "Accelerating Decoding with Speculative Sampling",
            )
        )
        self.assertTrue(
            drafting.restates_method(
                "Speculative sampling",
                "draft model",
                "Decoding with Speculative Sampling",
            )
        )
        self.assertFalse(
            drafting.restates_method(
                "XSum and HumanEval",
                "modified rejection sampling",
                "Decoding with Speculative Sampling",
            )
        )
