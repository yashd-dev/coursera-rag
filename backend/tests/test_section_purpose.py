import tempfile, json, unittest
from pathlib import Path
from unittest.mock import patch
from app import section_purpose


class Job:
    def tool_start(self, *a):
        return "x"

    def tool_done(self, *a, **kw):
        pass


class PurposeTests(unittest.TestCase):
    def test_evidence_supported_method_still_blocks_and_cache_binds_exact_section(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "paper").mkdir()
            p = r / "paper/main.tex"
            p.write_text(
                r"\section{Evidence limitations} The method caches representations. \section{Conclusion} End"
            )
            events = []
            with patch.object(
                section_purpose.opencode,
                "run_text",
                return_value=(
                    json.dumps(
                        {
                            "status": "fail",
                            "reason": "Method description, not a limitation.",
                        }
                    ),
                    True,
                    None,
                    events,
                ),
            ) as model:
                self.assertFalse(section_purpose.check_limitations(Job(), r))
                self.assertFalse(section_purpose.check_limitations(Job(), r))
                self.assertEqual(model.call_count, 1)
                p.write_text(
                    r"\section{Evidence limitations} Future work covers dynamic graphs. \section{Conclusion} End"
                )
                model.return_value = (
                    json.dumps(
                        {"status": "pass", "reason": "Attributed future-work scope."}
                    ),
                    True,
                    None,
                    events,
                )
                self.assertTrue(section_purpose.check_limitations(Job(), r))
                self.assertEqual(model.call_count, 2)

    def test_invalid_verdict_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "paper").mkdir()
            (r / "paper/main.tex").write_text(
                r"\section{Evidence limitations} Text \section{Conclusion} End"
            )
            with patch.object(
                section_purpose.opencode,
                "run_text",
                return_value=("bad", True, None, []),
            ):
                self.assertFalse(section_purpose.check_limitations(Job(), r))

    def test_invalid_verdict_does_not_become_permanent_semantic_failure(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            (r / "paper").mkdir()
            (r / "paper/main.tex").write_text(
                r"\section{Evidence limitations} Text \section{Conclusion} End"
            )
            with patch.object(
                section_purpose.opencode,
                "run_text",
                side_effect=[
                    ("bad", True, None, []),
                    (
                        json.dumps({"status": "pass", "reason": "Scope boundary."}),
                        True,
                        None,
                        [],
                    ),
                ],
            ) as model:
                self.assertFalse(section_purpose.check_limitations(Job(), r))
                self.assertTrue(section_purpose.check_limitations(Job(), r))
                self.assertEqual(model.call_count, 2)


class PurposeRepairTests(unittest.TestCase):
    def fixture(self, root):
        import hashlib

        (root / "paper").mkdir()
        before = r"\section{Introduction} Keep.\section{Evidence limitations} Benefit only.\section{Conclusion} Keep."
        (root / "paper/main.tex").write_text(before)
        source = root / "source.txt"
        quote = "The method is not useful where additional compute resources are unavailable."
        source.write_text("=== PAGE 8 ===\n" + quote)
        d = root / "limitations-classification" / "k"
        d.mkdir(parents=True)
        (d / "verified.json").write_text(
            json.dumps(
                {
                    "quote": quote,
                    "page": 8,
                    "source_sha": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
            )
        )
        d = root / "section-purpose"
        d.mkdir()
        (d / "result.json").write_text('{"status":"fail","reason":"Benefit alone"}')
        return before, [
            {
                "key": "k",
                "status": "indexed",
                "title": "Reviewed method",
                "text_path": str(source),
            }
        ]

    def test_source_bound_change_exact_outside_and_one_attempt(self):
        from app import structured, db, opencode

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            before, rows = self.fixture(root)
            result = json.dumps(
                {
                    "paragraphs": [
                        {
                            "source_key": "k",
                            "sentence": "The method requires additional available compute resources to deliver latency gains.",
                        }
                    ]
                }
            )
            with patch.object(db, "sources", return_value=rows), patch.object(
                opencode, "write_config"
            ), patch.object(
                structured, "run", return_value=(result, True, None, [])
            ) as model:
                self.assertTrue(section_purpose.repair_limitations(Job(), "t", root))
                after = (root / "paper/main.tex").read_text()
                self.assertEqual(
                    before.split(r"\section{Evidence limitations}")[0],
                    after.split(r"\section{Evidence limitations}")[0],
                )
                self.assertEqual(
                    before.split(r"\section{Conclusion}")[1],
                    after.split(r"\section{Conclusion}")[1],
                )
                self.assertIn(r"\cite{k}", after)
                (root / "paper/main.tex").write_text(before)
                self.assertFalse(section_purpose.repair_limitations(Job(), "t", root))
                self.assertEqual(model.call_count, 1)

    def test_wrong_source_unknown_citation_stale_source_and_structure_blocked(self):
        from app import structured, db, opencode

        for bad in ("unknown", "structure", "stale"):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                before, rows = self.fixture(root)
                if bad == "stale":
                    Path(rows[0]["text_path"]).write_text("changed")
                result = json.dumps(
                    {
                        "paragraphs": [
                            {
                                "source_key": "other" if bad == "unknown" else "k",
                                "sentence": (
                                    r"\section{Injected}"
                                    if bad == "structure"
                                    else "A valid looking resource limitation sentence."
                                ),
                            }
                        ]
                    }
                )
                with patch.object(db, "sources", return_value=rows), patch.object(
                    opencode, "write_config"
                ), patch.object(
                    structured, "run", return_value=(result, True, None, [])
                ):
                    self.assertFalse(
                        section_purpose.repair_limitations(Job(), "t", root)
                    )
                    self.assertEqual((root / "paper/main.tex").read_text(), before)
