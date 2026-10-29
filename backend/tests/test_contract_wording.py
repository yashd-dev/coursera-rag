import unittest
from pathlib import Path

A = Path(__file__).resolve().parents[1] / "app"


class WordingContract(unittest.TestCase):
    def test_evaluation_cell_means_task_not_model_or_outcome(self):
        for f in ("drafting.py", "pipeline.py", "span_review.py"):
            t = (A / f).read_text()
            self.assertIn("task, dataset or benchmark", t, f)

    def test_conclusion_takes_no_added_qualifier(self):
        self.assertIn("no added qualifier", (A / "drafting.py").read_text())
