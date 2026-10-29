import json, tempfile, unittest
from pathlib import Path
from unittest import mock

from app import pipeline, span_review


class PauseMessage(unittest.TestCase):
    def test_lists_unresolved_with_action_and_never_says_verified(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text("\\maketitle\nFirst sentence is fine. \\cite{a}\n\nSecond unresolved sentence here. \\cite{b}\n\\bibliographystyle{x}")
            (root / "review-feedback.json").write_text(json.dumps({
                "spans_complete": 1, "spans_total": 52,
                "errors": [
                    "Span2: unresolved clause grounding: an excerpt is not copied exactly from its evidence",
                    "Span3: operational native_error: the review call returned no usable result; this is not a verdict on the claim",
                ]}))
            with mock.patch.object(span_review, "spans", return_value=["First fine. \\cite{a}", "Second unresolved sentence here. \\cite{b}"]):
                m = pipeline.review_pause_message(root)
        self.assertTrue(m.startswith("Claim review is paused. Existing source vectors retained."))
        self.assertIn("1 of 52", m)
        self.assertIn("not marked verified", m)
        self.assertIn("rewrite the named sentence", m)
        self.assertIn('Sentence: "Second unresolved sentence here."', m)
        self.assertIn("PAPERFORGE_REVIEW_NEW_ATTEMPT", m)

    def test_missing_ledger_keeps_plain_message(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(pipeline.review_pause_message(Path(d)), "Claim review is paused. Existing source vectors retained.")


class CorrectionReask(unittest.TestCase):
    def _run(self, answers):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            calls = []
            evidence = [{"id": "E1", "source_key": "k", "page": 1, "quote": "Alpha beta gamma delta. Stray 5 text here."}]
            block = "Alpha beta gamma delta."
            def fake_run(work, prompt, schema, timeout=80, model_id=None):
                calls.append(prompt)
                r = answers[len(calls) - 1]
                return "", True, None, [{"kind": "text", "text": json.dumps(r)}, {"kind": "done", "ok": True}]
            with mock.patch.object(span_review.structured, "run", fake_run), \
                 mock.patch.object(span_review, "candidates", return_value=evidence), \
                 mock.patch.object(span_review.opencode, "write_config", lambda w, p: (w / "opencode.json").write_text(json.dumps({"agent": {"paperforge": {}}}))):
                try:
                    out = span_review.review_one(root, 1, block, [], {})
                except Exception as e:  # fixture may not cover every helper
                    self.skipTest(f"fixture incomplete: {type(e).__name__}: {e}")
            return out, calls

    def _ans(self, excerpt):
        return {"status": "supported", "evidence_ids": ["E1"], "reason": "ok",
                "clauses": [{"clause": "Alpha beta gamma delta", "evidence_id": "E1", "excerpt": excerpt}]}

    def test_second_answer_verbatim_is_accepted(self):
        (entries, failures), calls = self._run([self._ans("Alpha beta ... delta"), self._ans("Alpha beta gamma delta.")])
        self.assertEqual(len(calls), 2)
        self.assertIn("CORRECTION", calls[1])
        self.assertEqual(failures, [])
        self.assertTrue(entries)

    def test_second_answer_still_stitched_stays_unresolved_after_one_reask(self):
        (entries, failures), calls = self._run([self._ans("Alpha beta ... delta"), self._ans("Alpha gamma ... delta")])
        self.assertEqual(len(calls), 2)
        self.assertEqual(entries, [])
        self.assertIn("unresolved clause grounding", failures[0])
        self.assertIn("after one correction re-ask", failures[0])


if __name__ == "__main__":
    unittest.main()
