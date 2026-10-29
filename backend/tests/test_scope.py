import unittest
from unittest.mock import patch
from app import scope, pipeline


class ScopeTests(unittest.TestCase):
    def test_ambiguous_graph_rag_asks_before_creation(self):
        self.assertEqual(
            pipeline.route(
                "Write a review on graph-based RAG latest advancements",
                {"phase": "new"},
            )[0],
            "scope",
        )

    def test_explicit_llm_scope_creates(self):
        self.assertEqual(
            pipeline.route(
                "Write a review on graph-based RAG for LLM question answering",
                {"phase": "new"},
            )[0],
            "create",
        )

    def test_explicit_gfm_family_not_silently_changed(self):
        self.assertEqual(
            scope.graph_family("graph RAG for graph foundation models"), "gfm"
        )

    def test_conflicting_source_filtered_only_for_explicit_scope(self):
        c = {
            "title": "Generalizing Graph Foundation Models via Hyperbolic Retrieval-Augmented Generation",
            "abstract": "Zero shot node classification and graph benchmarks.",
        }
        self.assertFalse(
            scope.candidate_scope("graph RAG for LLM question answering", c)[0]
        )
        self.assertTrue(
            scope.candidate_scope("graph RAG for graph foundation models", c)[0]
        )

    def test_clarification_does_no_discovery_or_model_work(self):
        class J:
            def text(self, t):
                self.message = t

            def finish(self):
                pass

        job = J()
        with patch.object(
            pipeline.db, "get_thread", return_value={"phase": "new", "custom": {}}
        ), patch.object(pipeline.db, "update_thread") as save, patch.object(
            pipeline, "discover_and_index"
        ) as discover, patch.object(
            pipeline.opencode, "run_text"
        ) as model:
            pipeline.run_scope(job, "fixture", "graph RAG recent advances")
            self.assertEqual(save.call_args.kwargs["phase"], "scope_pending")
            discover.assert_not_called()
            model.assert_not_called()

    def test_reply_resumes_with_visible_original_and_explicit_scope(self):
        with patch.object(
            pipeline.db,
            "get_thread",
            return_value={
                "phase": "scope_pending",
                "template": "ieee",
                "custom": {"scope_request": "review graph RAG latest"},
            },
        ), patch.object(pipeline.db, "update_thread"), patch.object(
            pipeline, "run_create"
        ) as create:
            pipeline.run_scope(None, "fixture", "LLM question answering over documents")
            self.assertIn("review graph RAG latest", create.call_args.args[2])
            self.assertIn("Explicit scope clarification", create.call_args.args[2])
