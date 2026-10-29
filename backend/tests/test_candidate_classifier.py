import tempfile, unittest, json
from pathlib import Path
from unittest.mock import patch
from app import limitations as l


class J:
    def tool_start(self, *a):
        return "t"

    def tool_done(self, *a, **kw):
        pass


class ClassifierTests(unittest.TestCase):
    def test_rejected_background_then_supported_method_keeps_quote(self):
        with tempfile.TemporaryDirectory() as td:
            rows = [
                {
                    "page": 1,
                    "quote": "One limitation of background method X is substantial model bias.",
                },
                {
                    "page": 2,
                    "quote": "A trade-off of this method is increased arithmetic cost for reduced latency.",
                },
            ]
            with patch.object(l, "excerpts_for", return_value=rows), patch.object(
                l.structured,
                "run",
                side_effect=[
                    (
                        '{"status":"unsupported","reason":"Background method"}',
                        True,
                        None,
                        [],
                    ),
                    (
                        '{"status":"supported","reason":"Reviewed method tradeoff"}',
                        True,
                        None,
                        [],
                    ),
                ],
            ) as run:
                result = l.classify_candidates(
                    J(), Path(td), {"key": "a", "title": "Reviewed Method"}
                )
                self.assertIn('"' + rows[1]["quote"] + '"', result)
                self.assertEqual(run.call_count, 2)

    def test_fixed_four_bound_and_error_never_implies_absence(self):
        with tempfile.TemporaryDirectory() as td:
            rows = [
                {
                    "page": i,
                    "quote": f"One limitation statement {i} concerns a method in the source.",
                }
                for i in range(9)
            ]
            with patch.object(l, "excerpts_for", return_value=rows), patch.object(
                l.structured,
                "run",
                return_value=(
                    '{"status":"unsupported","reason":"Not reviewed method"}',
                    True,
                    None,
                    [],
                ),
            ) as run:
                self.assertIsNone(l.classify_candidates(J(), Path(td), {"key": "a"}))
                self.assertEqual(run.call_count, 4)
            with patch.object(l, "excerpts_for", return_value=rows), patch.object(
                l.structured, "run", return_value=("", False, None, [])
            ) as run:
                self.assertIsNone(l.classify_candidates(J(), Path(td), {"key": "a"}))
                self.assertEqual(run.call_count, 1)

    def test_figure_description_is_not_concrete_tradeoff(self):
        with tempfile.TemporaryDirectory() as td:
            rows = [
                {
                    "page": 1,
                    "quote": "Table 1 and Figure 4 illustrate the trade-off between inference speed and operations.",
                },
                {
                    "page": 2,
                    "quote": "One limitation of speculative decoding is the increased arithmetic cost.",
                },
            ]
            with patch.object(l, "excerpts_for", return_value=rows), patch.object(
                l.structured,
                "run",
                return_value=(
                    '{"status":"supported","reason":"Concrete method limitation"}',
                    True,
                    None,
                    [],
                ),
            ) as run:
                result = l.classify_candidates(J(), Path(td), {"key": "a"})
                self.assertIn(rows[1]["quote"], result)
                self.assertNotIn("Table 1", run.call_args.args[1])
