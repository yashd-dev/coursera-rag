import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from app import drafting, pipeline


class Job:
    def __init__(self):
        self.done = []

    def tool_start(self, *a):
        return "x"

    def tool_done(self, tc, result, error=False):
        self.done.append((result, error))

    def text(self, s):
        pass


def row():
    return {"key": "a", "title": "Are Large Language Models Really Good Logical Reasoners", "status": "indexed", "authors": "Author", "year": 2025}


def first_section(evaluation):
    d = {k: "A supported narrow source description" for k in ["summary", "limitations", "approach", "evaluation", "abstract", "introduction", "conclusion"]}
    d["abstract"] = "The review describes evidence with a different abstract sentence."
    d["evaluation"] = evaluation
    d["approach"] = "framework evaluation"
    return d


class TableCellTests(unittest.TestCase):
    def test_pushed_escaped_retry_reply_is_parsed(self):
        raw = '{\\n  \\"approach\\": \\"content-neutral NeuLR dataset 3k samples\\",\\n  \\"evaluation\\": \\"Logical reasoning benchmark zero-shot few-shot\\"\\n}'
        out = drafting.parse_cells(raw)
        self.assertEqual(out["approach"], "content-neutral NeuLR dataset 3k samples")
        self.assertEqual(drafting.parse_cells('```json\n{"a": "b"}\n```'), {"a": "b"})
        # Bounded: valid JSON keeps its backslashes; mixed quoting is not rewritten.
        self.assertEqual(drafting.parse_cells('{"a": "x\\\\n y"}'), {"a": "x\\n y"})
        for bad in ('{"a": \\"b\\", "c": "d"}', "not json", "[1, 2]"):
            with self.assertRaises(ValueError):
                drafting.parse_cells(bad)

    def test_two_letter_model_label_scope_unchanged(self):
        self.assertTrue(drafting.outcome_label("Mp and Mq"))
        self.assertTrue(drafting.outcome_label("15 datasets 7 models"))

    def test_grounded_phrases_are_verbatim_and_pass_all_guards(self):
        text = (
            "We evaluate on the SNLI dataset and the NeuLR dataset. "
            "Experiments on logical reasoning tasks show that logical reasoning tasks differ. "
            "The logical reasoning tasks are described. Results are samples and surveyed. References\n"
        )
        got = drafting.grounded_phrases(text, "framework evaluation", "A title")
        self.assertIn("SNLI", got)
        self.assertIn("NeuLR", got)
        self.assertIn("logical reasoning", got)
        self.assertNotIn("samples", got)
        for p in got:
            self.assertIn(p, text)
            self.assertFalse(drafting.outcome_label(p))
            self.assertFalse(drafting.ungrounded_label(p, text))
        self.assertEqual(drafting.grounded_phrases("", "", ""), [])

    def test_compact_prompt_lists_grounded_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("Source facts")
            (root / "plan.json").write_text("{}")
            src = root / "a.txt"
            src.write_text("We evaluate on the NeuLR dataset in experiments. Experiments use the NeuLR dataset again.")
            r = {**row(), "text_path": str(src)}
            good = json.dumps({"approach": "framework evaluation", "evaluation": "NeuLR"})
            replies = [(json.dumps(first_section("15 datasets 7 models")), True, None, []), (good, True, None, [])]
            with patch.object(drafting.db, "sources", return_value=[r]), patch.object(
                drafting.opencode, "run_text", side_effect=replies
            ) as run, patch("app.limitations.classify_candidates", return_value="Q."):
                self.assertTrue(drafting.generate(Job(), "t", root, "T", "ieee")[0])
                self.assertIn('"NeuLR"', run.call_args_list[1].args[1])
                self.assertIn("appear verbatim in the source", run.call_args_list[1].args[1])

    def test_retry_prompt_names_the_rule_and_accepts_escaped_json_reply(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("Source facts")
            (root / "plan.json").write_text("{}")
            long_cells = {"approach": "x " * 30, "evaluation": "Logical reasoning benchmarks across 15 datasets with 7 LLMs"}
            good = '{\\n \\"approach\\": \\"NeuLR dataset\\",\\n \\"evaluation\\": \\"Logical reasoning\\"\\n}'
            replies = [
                (json.dumps(first_section("15 datasets 7 models")), True, None, []),
                (json.dumps(long_cells), True, None, []),
                (good, True, None, []),
            ]
            with patch.object(drafting.db, "sources", return_value=[row()]), patch.object(
                drafting.opencode, "run_text", side_effect=replies
            ) as run, patch("app.limitations.classify_candidates", return_value="Q."):
                job = Job()
                self.assertTrue(drafting.generate(job, "t", root, "T", "ieee")[0])
                retry_prompt = run.call_args_list[2].args[1]
                self.assertIn("at most 8 words", retry_prompt)
                self.assertIn("plain JSON", retry_prompt)
                self.assertNotIn('\\"approach\\"', retry_prompt)
            self.assertIn("Logical reasoning", (root / "paper/main.tex").read_text())

    def test_still_invalid_cells_still_abort(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes").mkdir()
            (root / "paper").mkdir()
            (root / "notes/a.md").write_text("Source facts")
            (root / "plan.json").write_text("{}")
            bad = json.dumps({"approach": "framework evaluation", "evaluation": "accuracy improvement"})
            with patch.object(drafting.db, "sources", return_value=[row()]), patch.object(
                drafting.opencode,
                "run_text",
                side_effect=[(json.dumps(first_section("15 datasets 7 models")), True, None, []), (bad, True, None, []), (bad, True, None, [])],
            ):
                job = Job()
                self.assertFalse(drafting.generate(job, "t", root, "T", "ieee")[0])
                self.assertTrue(job.done[-1][1])

    def test_banner_is_honest_per_phase(self):
        d = pipeline.start_banner("draft_paused", "Springer LNCS")
        self.assertIn("Resuming", d)
        self.assertNotIn("embed every PDF", d)
        r = pipeline.start_banner("reading_paused", "Springer LNCS")
        self.assertIn("only unfinished segments", r)
        self.assertNotIn("reading is complete", r.lower())
        self.assertIn("embed every PDF", pipeline.start_banner("", "Springer LNCS"))


if __name__ == "__main__":
    unittest.main()
