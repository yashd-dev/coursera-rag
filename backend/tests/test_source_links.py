import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from app import source_links as sl, sections


class SectionTests(unittest.TestCase):
    def sample(self):
        return (
            "".join(
                r"\section{Section "
                + str(i)
                + "}\nText\n"
                + (r"\subsection{Specific topic} old content\n" if i == 7 else "")
                for i in range(1, 9)
            )
            + r"\bibliographystyle{IEEEtran}\bibliography{refs}\end{document}"
        )

    def test_seven_a_and_number_and_title(self):
        tex = self.sample()
        for q in ("Add to section 7 A", "Change section 7.1", "Rewrite Specific topic"):
            t = sections.locate(tex, q)
            self.assertEqual(t["title"], "Specific topic")

    def test_missing_section_fails_closed(self):
        with self.assertRaises(sections.SectionError):
            sections.locate(self.sample(), "change section 10A")

    def test_outside_patch_rejected(self):
        tex = self.sample()
        target = sections.locate(tex, "change section 7A")
        with self.assertRaises(sections.SectionError):
            sections.apply(tex, [{"old": "Section 8", "new": "Unwanted edit"}], target)

    def test_target_patch_preserves_all_other_bytes(self):
        tex = self.sample()
        target = sections.locate(tex, "change section 7A")
        after = sections.apply(
            tex, [{"old": "old content", "new": "new cited content"}], target
        )
        self.assertEqual(after.replace("new cited content", "old content"), tex)

    def test_multiple_targets_not_silently_chosen(self):
        with self.assertRaises(sections.SectionError):
            sections.locate(self.sample(), "change section 6 and section 7")


class LinkTests(unittest.TestCase):
    def test_extracts_only_explicit_urls(self):
        self.assertEqual(
            sl.links("add https://example.org/a.pdf. and https://example.org/a.pdf"),
            ["https://example.org/a.pdf"],
        )

    def test_no_local_network_link(self):
        with patch.object(
            sl.socket,
            "getaddrinfo",
            return_value=[(None, None, None, None, ("127.0.0.1", 443))],
        ):
            with self.assertRaises(sl.LinkError):
                sl.public_url("https://example.org/paper.pdf")

    def test_plain_http_disallowed(self):
        with self.assertRaises(sl.LinkError):
            sl.public_url("http://example.org/paper.pdf")

    def test_landing_metadata(self):
        m = sl.Metadata()
        m.feed(
            '<meta name="citation_title" content="A scholarly paper"><meta name="citation_author" content="Author A"><meta name="citation_pdf_url" content="/paper.pdf">'
        )
        self.assertEqual(m.first("citation_title"), "A scholarly paper")
        self.assertEqual(m.first("citation_pdf_url"), "/paper.pdf")

    def test_indexed_checkpoint_does_not_repeat_embedding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "link-ingestion"
            ledger.mkdir()
            url = "https://example.org/paper.pdf"
            (
                ledger / (sl.hashlib.sha256(url.encode()).hexdigest() + ".json")
            ).write_text(json.dumps({"source_id": "source-a"}))
            row = {"id": "source-a", "status": "indexed"}
            with patch.object(sl.db, "sources", return_value=[row]), patch.object(
                sl, "resolve"
            ) as resolve, patch.object(sl.rag, "index_source") as embed:
                self.assertEqual(sl.ingest(None, "thread-a", url, root), row)
                resolve.assert_not_called()
                embed.assert_not_called()

    def test_real_pdf_ingestion_stage_with_mock_embedding(self):
        # Actual fixture PDF parse/extraction, mocked DB/vector write. Not a hosted E2E claim.
        from pypdf import PdfWriter

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sources").mkdir()
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            writer.add_metadata(
                {"/Title": "Synthetic test paper metadata", "/Author": "Fixture Author"}
            )
            fixture = root / "fixture.pdf"
            with fixture.open("wb") as f:
                writer.write(f)
            rows = []

            def add(tid, row):
                rows.append({"id": "fixture-source", **row})
                return "fixture-source"

            def update(sid, **kw):
                rows[0].update(kw)

            class J:
                def tool_start(self, *a):
                    return "x"

                def tool_done(self, *a, **kw):
                    pass

            with patch.object(
                sl,
                "fetch",
                return_value=("https://example.org/paper.pdf", fixture.read_bytes()),
            ), patch.object(
                sl.db, "sources", side_effect=lambda tid: rows
            ), patch.object(
                sl.db, "add_source", side_effect=add
            ), patch.object(
                sl.db, "update_source", side_effect=update
            ), patch.object(
                sl.research,
                "extract_pages",
                return_value=[(1, "Synthetic academic passage " * 200)],
            ), patch.object(
                sl.research, "needs_ocr", return_value=False
            ), patch.object(
                sl.rag, "index_source", return_value=7
            ) as embed:
                source = sl.ingest(
                    J(), "thread-a", "https://example.org/paper.pdf", root
                )
                self.assertEqual(source["status"], "indexed")
                self.assertEqual(source["title"], "Synthetic test paper metadata")
                sl.ingest(J(), "thread-a", "https://example.org/paper.pdf", root)
                embed.assert_called_once()
                self.assertEqual(
                    embed.call_args.args[:2], ("thread-a", "fixture-source")
                )

    def test_surname_first_metadata_normalized(self):
        from pypdf import PdfWriter

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            fixture = root / "x.pdf"
            with fixture.open("wb") as f:
                writer.write(f)
            html = b'<meta name="citation_title" content="A test scholarly title"><meta name="citation_author" content="Edge, Darren"><meta name="citation_author" content="Trinh, Ha"><meta name="citation_pdf_url" content="https://example.org/x.pdf">'
            with patch.object(
                sl,
                "fetch",
                side_effect=[
                    ("https://example.org/abs", html),
                    ("https://example.org/x.pdf", fixture.read_bytes()),
                ],
            ):
                row, *_ = sl.resolve("https://example.org/abs", root)
                self.assertEqual(row["authors"], "Darren Edge, Ha Trinh")


class SectionReferenceRegression(unittest.TestCase):
    def test_section_number_before_and_is_not_letter_a(self):
        tex = r"\section{One} text\section{Two} text"
        self.assertEqual(
            sections.locate(tex, "edit section 1 and preserve section text")["title"],
            "One",
        )
