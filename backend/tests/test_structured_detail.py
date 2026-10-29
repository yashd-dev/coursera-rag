import unittest
from app import structured


class DetailTests(unittest.TestCase):
    def test_detail_is_short_and_redacts_keys(self):
        e = {"name": "APIError", "data": {"statusCode": 429, "message": "Rate limit reached. Authorization: Bearer gsk_abcdefghijk123456 retry in 20s"}}
        d = structured.provider_detail(e)
        self.assertIn("APIError", d)
        self.assertIn("status=429", d)
        self.assertIn("Rate limit", d)
        self.assertNotIn("abcdefghijk", d)
        self.assertLessEqual(len(d), 300)
        self.assertEqual(structured.provider_detail(None), "")

    def test_fail_event_carries_detail_only_when_present(self):
        err = structured._Typed("native_error", "x")
        err.detail = "APIError status=429"
        self.assertEqual(structured._fail("native_error", err, "s")[3][0]["detail"], "APIError status=429")
        self.assertNotIn("detail", structured._fail("timeout", ValueError("v"), "s")[3][0])

    def test_review_failure_text_includes_detail_and_stays_operational(self):
        from app import span_review
        ev = [{"kind": "error", "code": "native_error", "detail": "APIError status=429 Rate limit"}, {"kind": "done", "ok": False}]
        f = f'Span1: operational native_error{span_review._detail(ev)}: the review call returned no usable result'
        self.assertTrue(span_review.is_operational(f))
        self.assertIn("status=429", f)
        self.assertEqual(span_review._detail([]), "")


if __name__ == "__main__":
    unittest.main()
