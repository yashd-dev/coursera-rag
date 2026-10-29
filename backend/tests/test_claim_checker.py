import os
import sys
import unittest

from app import claim_checker as cc


class Stub:
    def __init__(self, p):
        self.p, self.states = p, []

    def predict(self, state, q):
        self.states.append(state)
        return {"answers": {"support": {"noul": self.p(state) if callable(self.p) else self.p}}}


class ClaimCheckerTests(unittest.TestCase):
    def tearDown(self):
        cc.set_agent(None)
        os.environ.pop("PAPERFORGE_CLAIM_CHECKER", None)

    def test_default_is_laya_and_legacy_switch_disables_it_without_importing_laya(self):
        os.environ.pop("PAPERFORGE_CLAIM_CHECKER", None)
        self.assertTrue(cc.enabled())
        os.environ["PAPERFORGE_CLAIM_CHECKER"] = "legacy"
        self.assertFalse(cc.enabled())
        self.assertIsNone(cc.assess("c", ["p"]))
        self.assertNotIn("laya", sys.modules)

    def test_never_verified_and_single_part_label(self):
        cc.set_agent(Stub(0.99))
        r = cc.assess("The method uses attention.", ["short passage"])
        self.assertEqual(r["label"], "window_supported_single_part")
        self.assertIs(r["verified"], False)

    def test_multi_clause_claim_never_gets_unqualified_label(self):
        cc.set_agent(Stub(0.97))
        for claim in [
            "It uses attention and it reports SNLI results and it halves the parameters.",
            "It improves accuracy; it also halves latency.",
            "A reaches 90% while B reaches 80%.",
            "First sentence. Second sentence.",
        ]:
            with self.subTest(claim=claim):
                self.assertEqual(cc.assess(claim, ["p"])["label"], "window_level_only")

    def test_below_threshold(self):
        cc.set_agent(Stub(0.2))
        self.assertEqual(cc.assess("c", ["p"])["label"], "no_window_supported")

    def test_long_passage_is_windowed_and_labelled_window_level(self):
        s = Stub(lambda st: 0.9 if "NEEDLE" in st else 0.1)
        cc.set_agent(s)
        long = ("filler " * 400) + "NEEDLE " + ("filler " * 400)
        r = cc.assess("single claim", [long])
        self.assertGreater(len(s.states), 1)
        self.assertTrue(all(len(x) < 1400 for x in s.states))
        self.assertEqual(r["max_window_score"], 0.9)
        self.assertEqual(r["label"], "window_level_only")
        self.assertEqual(len(r["window_scores"]), r["windows"])

    def test_fact_at_a_window_boundary_is_whole_in_some_window(self):
        for offset in range(0, 1200, 37):
            fact = "KEYFACT-" + "x" * 150
            text = ("a" * (cc.MAX_PASSAGE_CHARS // 2 + offset)) + fact + ("b" * 2000)
            ws = cc._windows(text)
            self.assertTrue(any(fact in w for w in ws), offset)

    def test_prompt_contract_unchanged(self):
        self.assertEqual(
            cc.QUESTION,
            {"support": {"type": "noul", "instructions": "Does the evidence passage fully support every part of the claim?"}},
        )

    def test_load_failure_is_reported_not_raised_and_not_support(self):
        os.environ["PAPERFORGE_CLAIM_CHECKER"] = "laya"
        r = cc.assess("c", ["p"])  # laya is not installed here
        self.assertIn("error", r)
        self.assertNotIn("label", r)
        self.assertIs(r["verified"], False)

    def test_empty_passages_give_no_assessment(self):
        cc.set_agent(Stub(0.9))
        self.assertIsNone(cc.assess("c", []))


if __name__ == "__main__":
    unittest.main()


class SummaryTests(unittest.TestCase):
    def test_label_says_model_assessed_not_verified(self):
        import tempfile
        from pathlib import Path

        os.environ["PAPERFORGE_CLAIM_CHECKER"] = "laya"
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                cc.write_summary(root, {"checker": "laya", "total": 3, "verified": False,
                    "counts": {"window_supported_single_part": 1, "window_level_only": 1, "no_window_supported": 1},
                    "rows": [{"span": 3, "text": "Odd claim", "label": "no_window_supported", "score": 0.1, "pages": []}]})
                t = cc.summary_text(root)
                self.assertIn("model-assessed by Laya, not verified", t)
                self.assertIn("flagged: Odd claim", t)
                cc.write_summary(root, {"error": "OSError: out of memory", "total": 3})
                self.assertIn("did not run", cc.summary_text(root))
        finally:
            os.environ.pop("PAPERFORGE_CLAIM_CHECKER", None)
