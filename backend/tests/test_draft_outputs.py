import json, tempfile, unittest
from pathlib import Path
from unittest import mock

from app import pipeline


class Job:
    def __init__(self):
        self.done = []

    def tool_start(self, name, args):
        return 1

    def tool_done(self, tc, result, error=False):
        self.done.append((result, error))


class DraftOutputs(unittest.TestCase):
    def test_draft_names_never_collide_with_final_names(self):
        self.assertFalse(set(pipeline.DRAFT_FILES) & set(pipeline.FINAL_FILES))
        for n in pipeline.DRAFT_FILES:
            self.assertIn("draft", n)

    def test_export_draft_copies_without_final_names_or_model(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "paper").mkdir()
            (root / "paper/main.pdf").write_bytes(b"%PDF-1.5 x")
            docx = root / "paper/paper.docx"
            docx.write_bytes(b"docx")
            with mock.patch.object(pipeline.db, "thread_dir", return_value=root), \
                 mock.patch.object(pipeline.latexbuild, "export_docx", return_value={"ok": True, "path": docx, "log": ""}), \
                 mock.patch.object(pipeline.latexbuild, "source_zip", side_effect=lambda tid, name="paper-source.zip": (root / name).write_bytes(b"zip")):
                files = pipeline.export_draft(Job(), "t", "ieee")
            self.assertEqual([f["name"] for f in files], list(pipeline.DRAFT_FILES))
            for n in pipeline.FINAL_FILES:
                self.assertFalse((root / n).exists())
            self.assertTrue(all("not verified" in f["label"] for f in files))

    def test_docx_failure_still_returns_pdf_and_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "paper").mkdir()
            (root / "paper/main.pdf").write_bytes(b"%PDF")
            with mock.patch.object(pipeline.db, "thread_dir", return_value=root), \
                 mock.patch.object(pipeline.latexbuild, "export_docx", return_value={"ok": False, "log": "old pandoc"}), \
                 mock.patch.object(pipeline.latexbuild, "source_zip", side_effect=lambda tid, name="paper-source.zip": (root / name).write_bytes(b"zip")):
                files = pipeline.export_draft(Job(), "t", "ieee")
            self.assertEqual([f["name"] for f in files], ["paper-draft.pdf", "paper-draft-source.zip"])


if __name__ == "__main__":
    unittest.main()
