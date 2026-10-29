import unittest, tempfile, json
from pathlib import Path
from unittest.mock import patch
from app import transform as t, config


class TransformTests(unittest.TestCase):
    def test_wrong_endpoint_no_call(self):
        with patch.object(
            config, "UNSTRUCTURED_API_URL", "https://wrong.invalid"
        ), patch.object(t.httpx, "post") as post:
            with self.assertRaises(ValueError):
                t.pages(Path("x"), 1)
            post.assert_not_called()

    def test_unverified_free_no_call(self):
        with patch.object(
            config, "UNSTRUCTURED_API_URL", "https://transform.unstructured.io/api/v2"
        ), patch.object(
            config, "UNSTRUCTURED_FREE_PAGES_VERIFIED", False
        ), patch.object(
            t.httpx, "post"
        ) as post:
            with self.assertRaises(ValueError):
                t.pages(Path("x"), 1)
            post.assert_not_called()

    def test_reuse_cached_result_no_upload(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.pdf"
            p.write_bytes(b"%PDF-fixture")
            state = {
                "result": {
                    "status": "completed",
                    "elements": [{"text": "fixture", "metadata": {"page_number": 2}}],
                }
            }
            with patch.object(
                config,
                "UNSTRUCTURED_API_URL",
                "https://transform.unstructured.io/api/v2",
            ), patch.object(
                config, "UNSTRUCTURED_FREE_PAGES_VERIFIED", True
            ), patch.object(
                t.db, "q", return_value=[{"value": json.dumps(state)}]
            ), patch.object(
                t.httpx, "post"
            ) as post:
                self.assertEqual(t.pages(p, 3), [(2, "fixture")])
                post.assert_not_called()
