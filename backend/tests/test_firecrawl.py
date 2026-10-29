import unittest
from unittest.mock import patch
from app import firecrawl as f, config


class FirecrawlTests(unittest.TestCase):
    def test_unverified_no_call(self):
        with patch.object(config, "FIRECRAWL_FREE_VERIFIED", False), patch.object(
            f.httpx, "get"
        ) as get:
            with self.assertRaises(ValueError):
                f.reserve(1)
            get.assert_not_called()

    def test_pdf_excluded(self):
        with patch.object(f, "reserve") as reserve:
            with self.assertRaises(ValueError):
                f.scrape("https://example.org/paper.pdf")
            reserve.assert_not_called()

    def test_social_excluded(self):
        with patch.object(f, "reserve") as reserve:
            with self.assertRaises(ValueError):
                f.scrape("https://www.linkedin.com/in/example")
            reserve.assert_not_called()
