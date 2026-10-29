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

    def test_disabled_by_default_and_does_not_import_laya(self):
        self.assertIsNone(cc.assess("c", ["p"]))
        self.assertNotIn("laya", sys.modules)

    def test_never_verified(self):
        cc.set_agent(Stub(0.99))
        r = cc.assess("claim", ["passage"])
        self.assertEqual(r["label"], "model_assessment_supported")
        self.assertIs(r["verified"], False)

    def test_not_supported_below_threshold(self):
        cc.set_agent(Stub(0.2))
        self.assertEqual(cc.assess("c", ["p"])["label"], "model_assessment_not_supported")

    def test_long_passage_is_windowed_and_max_taken(self):
        s = Stub(lambda st: 0.9 if "NEEDLE" in st else 0.1)
        cc.set_agent(s)
        long = ("filler " * 400) + "NEEDLE " + ("filler " * 400)
        r = cc.assess("c", [long])
        self.assertGreater(len(s.states), 1)
        self.assertTrue(all(len(x) < 1400 for x in s.states))
        self.assertEqual(r["p_support"], 0.9)

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
