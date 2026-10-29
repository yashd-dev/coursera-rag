import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main


class ParseOriginsTests(unittest.TestCase):
    def test_empty_adds_nothing(self):
        self.assertEqual(main.parse_allowed_origins(""), set())
        self.assertEqual(main.parse_allowed_origins(None), set())

    def test_exact_origins_accepted(self):
        self.assertEqual(
            main.parse_allowed_origins(
                "https://app.example.com, http://host.internal:3000"
            ),
            {"https://app.example.com", "http://host.internal:3000"},
        )

    def test_wildcards_paths_and_bad_schemes_rejected(self):
        for bad in (
            "*",
            "https://*.example.com",
            "https://app.example.com/",
            "https://app.example.com/x",
            "ftp://app.example.com",
            "app.example.com",
            "null",
        ):
            with self.assertRaises(ValueError, msg=bad):
                main.parse_allowed_origins(bad)

    def test_local_defaults_unchanged(self):
        self.assertTrue(main.LOCAL_ORIGINS <= main.ALLOWED_ORIGINS)
        self.assertIn("http://localhost:5173", main.ALLOWED_ORIGINS)


class GuardTests(unittest.TestCase):
    def post(self, origin):
        with mock.patch.object(main.db, "create_thread", return_value={"id": "x", "title": "t", "status": "regular", "template": "ieee", "custom": {}, "phase": "new", "updated": 0}):
            return TestClient(main.app).post(
                "/api/threads", json={}, headers={"origin": origin}
            )

    def test_unlisted_origin_blocked_on_mutation(self):
        self.assertEqual(self.post("https://evil.example.com").status_code, 403)

    def test_listed_hosted_origin_passes_guard_when_configured(self):
        extra = {"https://app.example.com"}
        with mock.patch.object(main, "ALLOWED_ORIGINS", main.LOCAL_ORIGINS | extra):
            self.assertNotEqual(self.post("https://app.example.com").status_code, 403)
            self.assertEqual(self.post("https://other.example.com").status_code, 403)

    def test_cors_preflight_only_for_allowed_origins(self):
        c = TestClient(main.app)
        h = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"}
        ok = c.options("/api/threads", headers={**h, "Origin": "http://localhost:5173"})
        self.assertEqual(ok.headers.get("access-control-allow-origin"), "http://localhost:5173")
        bad = c.options("/api/threads", headers={**h, "Origin": "https://evil.example.com"})
        self.assertNotEqual(bad.headers.get("access-control-allow-origin"), "https://evil.example.com")


if __name__ == "__main__":
    unittest.main()
