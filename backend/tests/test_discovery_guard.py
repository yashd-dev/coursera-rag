import unittest
from unittest.mock import patch, Mock
from app import research, config


class DiscoveryGuard(unittest.TestCase):
    def test_no_search_when_free_budget_exhausted(self):
        r = Mock()
        r.json.return_value = {
            "rate_limit": {
                "daily_budget_usd": 1,
                "daily_used_usd": 1,
                "endpoint_costs_usd": {"search": 0.001},
                "onetime_credits_balance": 100,
            }
        }
        with patch.object(config, "OPENALEX_CALLS", True), patch.object(
            config, "OPENALEX_API_KEY", "fixture-not-a-key"
        ), patch("httpx.get", return_value=r) as get:
            with self.assertRaises(ValueError):
                research.search_openalex("fixture")
            self.assertEqual(get.call_count, 1)

    def test_disabled(self):
        with patch.object(config, "OPENALEX_CALLS", False), patch("httpx.get") as get:
            with self.assertRaises(ValueError):
                research.search_openalex("fixture")
            get.assert_not_called()

    def test_arxiv_terms_scoped(self):
        q = research.arxiv_query(
            "A literature comparison of surface BM25 and hybrid retrieval"
        )
        self.assertEqual(
            q, 'all:"surface" AND all:"BM25" AND all:"hybrid" AND all:"retrieval"'
        )

    def test_topical_filter_before_embeddings(self):
        c = [
            {"title": "Physics decay observations", "abstract": ""},
            {"title": "Hybrid BM25 retrieval for language models", "abstract": ""},
        ]
        self.assertEqual(
            research.relevant_candidates("BM25 hybrid retrieval language models", c),
            [c[1]],
        )

    def test_arxiv_backoff_shared_across_threads(self):
        import tempfile, json, time
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td, patch.object(
            config, "DATA_DIR", Path(td)
        ), patch.object(research, "search_arxiv") as arxiv, patch.object(
            research, "search_openalex", return_value=[]
        ), patch.object(
            research.time, "sleep"
        ):
            arxiv.__name__ = "search_arxiv"
            research.search_openalex.__name__ = "search_openalex"
            (Path(td) / "arxiv-backoff.json").write_text(
                json.dumps({"retry_after": time.time() + 3600})
            )
            research.discover(["first query"], checkpoint=Path(td) / "thread-a.json")
            research.discover(
                ["different query"], checkpoint=Path(td) / "thread-b.json"
            )
            arxiv.assert_not_called()

    def test_recent_intent_not_silently_ignored(self):
        self.assertTrue(
            research.wants_recent("graph RAG latest technology and advancements")
        )
        self.assertFalse(research.wants_recent("compare two retrieval approaches"))

    def test_recent_openalex_date_sort(self):
        r = Mock()
        r.json.return_value = {"results": []}
        with patch.object(config, "OPENALEX_CALLS", True), patch.object(
            config, "OPENALEX_API_KEY", ""
        ), patch.object(research.httpx, "get", return_value=r) as get:
            research.search_openalex(
                "graph retrieval augmented generation", recent=True
            )
            self.assertEqual(
                get.call_args.kwargs["params"]["sort"], "publication_date:desc"
            )

    def test_future_metadata_year_not_treated_as_latest(self):
        from datetime import datetime, timezone
        from app import rag

        year = datetime.now(timezone.utc).year
        rows = [
            {
                "title": "Graph retrieval augmented generation",
                "abstract": "graph retrieval advancements",
                "year": year + 2,
                "hits": 1,
                "cited_by": 0,
            }
        ]
        with patch.object(rag, "embed") as embed:
            self.assertEqual(
                research.rank_by_relevance("latest graph retrieval advancements", rows),
                [],
            )
            embed.assert_not_called()
