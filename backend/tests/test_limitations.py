import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from app import limitations as l


class J:
    def tool_start(self, *a):
        return "x"

    def tool_done(self, *a, **kw):
        pass


class LimitationsTests(unittest.TestCase):
    def test_processing_and_absence_boilerplate_rejected(self):
        for s in [
            "Segment ends mid-sentence in Related Work",
            "Architecture is not specified",
            "Generalizability beyond the reported evaluation remains unestablished",
        ]:
            self.assertTrue(l.forbidden(s))

    def test_exact_page_quotation_required_and_no_invented_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            e = [
                {
                    "id": "E1",
                    "page": 3,
                    "source_key": "a",
                    "quote": "The acceleration depends on agreement between draft and target distributions.",
                }
            ]
            good = {
                "status": "supported",
                "sentence": "Author notes that acceleration depends on draft and target agreement.",
                "evidence_id": "E1",
                "quote": e[0]["quote"],
            }
            with patch.object(l, "excerpts_for", return_value=e), patch.object(
                l.structured,
                "run",
                side_effect=[
                    (json.dumps(good), True, None, []),
                    (
                        '{"status":"supported","reason":"Exact scope boundary supported"}',
                        True,
                        None,
                        [],
                    ),
                ],
            ):
                self.assertEqual(
                    l.generate(J(), Path(td), {"key": "a"}),
                    'The source authors state: "' + e[0]["quote"] + '"',
                )
            bad = dict(good, evidence_id="E99")
            (Path(td) / "limitations-stages/a/result.json").unlink()
            with patch.object(l, "excerpts_for", return_value=e), patch.object(
                l.structured, "run", return_value=(json.dumps(bad), True, None, [])
            ) as run:
                self.assertIsNone(l.generate(J(), Path(td), {"key": "a"}))
                self.assertEqual(run.call_count, 2)

    def test_independent_support_failure_blocks_and_never_caches_success(self):
        with tempfile.TemporaryDirectory() as td:
            e = [
                {
                    "id": "E1",
                    "page": 3,
                    "source_key": "a",
                    "quote": "A source describes the target distribution and its algorithm.",
                }
            ]
            proposal = {
                "status": "supported",
                "sentence": "Author claims the algorithm never works in another domain.",
                "evidence_id": "E1",
            }
            outputs = [
                (json.dumps(proposal), True, None, []),
                (
                    "{"
                    + '"status":"unsupported","reason":"Claim inferred from silence"'
                    + "}",
                    True,
                    None,
                    [],
                ),
            ] * 2
            with patch.object(l, "excerpts_for", return_value=e), patch.object(
                l.structured, "run", side_effect=outputs
            ) as run:
                self.assertIsNone(l.generate(J(), Path(td), {"key": "a"}))
                self.assertEqual(run.call_count, 4)
            self.assertFalse((Path(td) / "limitations-stages/a/result.json").exists())

    def test_absence_requires_successful_full_source_assessment(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "source.txt"
            p.write_text("=== PAGE 1 ===\nComplete source text.")
            source = {"key": "a", "text_path": str(p)}
            e = [{"id": "E1", "page": 1, "source_key": "a", "quote": "Source text"}]
            with patch.object(l, "excerpts_for", return_value=e), patch.object(
                l.structured,
                "run",
                side_effect=[
                    (
                        '{"status":"unavailable","sentence":"","evidence_id":""}',
                        True,
                        None,
                        [],
                    ),
                    (
                        '{"status":"absent","reason":"No explicit scope statement"}',
                        True,
                        None,
                        [],
                    ),
                ],
            ):
                self.assertEqual(l.generate(J(), Path(td), source), "")
            with patch.object(l, "excerpts_for", return_value=e), patch.object(
                l.structured,
                "run",
                return_value=('{"status":"unavailable"}', False, None, []),
            ):
                self.assertIsNone(l.generate(J(), Path(td), source))

    def test_explicit_method_limitation_survives_candidate_ranking(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "source.txt"
            p.write_text(
                "=== PAGE 1 ===\nRelated work and general context.\n=== PAGE 2 ===\nOne limitation of speculative decoding is increased arithmetic operations without extra compute resources."
            )
            candidates = l.excerpts_for({"key": "a", "text_path": str(p)})
            self.assertEqual(candidates[0]["page"], 2)
            self.assertIn("One limitation", candidates[0]["quote"])

    def test_autoregressive_word_is_not_regression_signal(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "source.txt"
            p.write_text(
                "=== PAGE 1 ===\n"
                + "Auto-regressive decoding is a general method. " * 30
                + "\n=== PAGE 2 ===\nThe speedup plateaus as draft length increases. This is a trade-off in speculative sampling."
            )
            self.assertEqual(
                l.excerpts_for({"key": "a", "text_path": str(p)})[0]["page"], 2
            )

    def test_rendered_selection_input_has_explicit_identity_and_attempt_provenance(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            e = [
                {
                    "id": "E1",
                    "page": 3,
                    "source_key": "a",
                    "quote": "The method has a trade-off in increased arithmetic operations.",
                }
            ]
            good = {"status": "supported", "sentence": "", "evidence_id": "E1"}
            with patch.object(l, "excerpts_for", return_value=e), patch.object(
                l.structured,
                "run",
                side_effect=[
                    (json.dumps(good), True, None, []),
                    (
                        "{"
                        + '"status":"supported","reason":"Actual reviewed method tradeoff"'
                        + "}",
                        True,
                        None,
                        [],
                    ),
                ],
            ) as run:
                self.assertTrue(
                    l.generate(
                        J(), Path(td), {"key": "a", "title": "Exact Reviewed Method"}
                    )
                )
                self.assertIn(
                    "SOURCE TITLE: Exact Reviewed Method", run.call_args_list[0].args[1]
                )
            work = Path(td) / "limitations-stages/a"
            latest = json.loads((work / "latest-attempt.json").read_text())
            attempt = Path(td) / latest["path"]
            self.assertTrue((attempt / "selection-prompt.txt").exists())
            self.assertTrue((attempt / "support-events-0.json").exists())
