import unittest, tempfile, json
from pathlib import Path
from unittest.mock import patch
from app import evidence as e


class EvidenceTests(unittest.TestCase):
    def test_exact_page_quote(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "paper").mkdir()
            (r / "paper/main.tex").write_text(
                r"Reported perplexity is 8.95 in Table 2. \cite{k} \begin{table}\end{table}"
            )
            p = r / "source.txt"
            p.write_text(
                "=== PAGE 1 ===\nReported perplexity is 8.95 in Table 2.\n=== PAGE 2 ===\nDifferent text."
            )
            c = {
                "claim": "Perplexity is 8.95",
                "source_key": "k",
                "page": 1,
                "quote": "Reported perplexity is 8.95 in Table 2.",
                "status": "supported",
                "draft_quote": "Reported perplexity is 8.95 in Table 2.",
            }
            (r / "claim-review.json").write_text(
                json.dumps(
                    {
                        "claims": [c],
                        "draft_sha256": __import__("hashlib")
                        .sha256((r / "paper/main.tex").read_bytes())
                        .hexdigest(),
                    }
                )
            )
            with patch.object(
                e.db,
                "sources",
                return_value=[{"key": "k", "status": "indexed", "text_path": str(p)}],
            ):
                self.assertEqual(e.validate("t", r), [])
                c["page"] = 2
                (r / "claim-review.json").write_text(
                    json.dumps(
                        {
                            "claims": [c],
                            "draft_sha256": __import__("hashlib")
                            .sha256((r / "paper/main.tex").read_bytes())
                            .hexdigest(),
                        }
                    )
                )
                self.assertTrue(e.validate("t", r))

    def test_missing_ledger_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(e.validate("t", Path(td)))

    def test_malformed_model_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "claim-review.json").write_text('[{"claim":"test"}]')
            self.assertTrue(e.validate("t", r))
