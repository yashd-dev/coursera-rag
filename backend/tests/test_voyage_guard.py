import unittest
from unittest.mock import patch
from app import voyage_guard as g


class GuardTests(unittest.TestCase):
    def test_spacing_shared_query_document(self):
        self.assertEqual(g.delay([[100, 100]], 110, 20)[1], 12)

    def test_token_window(self):
        self.assertEqual(g.delay([[100, 5000], [122, 2000]], 145, 2000)[1], 16)

    def test_expired_window(self):
        self.assertEqual(g.delay([[100, 8000]], 162, 8000), ([], 0))

    def test_rpm(self):
        self.assertGreater(g.delay([[100, 1], [101, 1], [102, 1]], 130, 1)[1], 0)

    def test_token_batched(self):
        with patch.object(g, "estimate", return_value=3000):
            self.assertEqual(
                [len(b) for b, n in g.batches(["a", "b", "c"], "document")], [2, 1]
            )

    def test_large_input_blocks(self):
        with patch.object(g, "estimate", return_value=9000):
            with self.assertRaises(ValueError):
                list(g.batches(["a"], "query"))


class AdapterTests(unittest.TestCase):
    def test_retry_after_and_resume_cache(self):
        from app import rag, config
        from unittest.mock import Mock

        cache = {}
        reserve = []
        response429 = Mock(status_code=429, headers={"Retry-After": "80"})
        response200 = Mock(status_code=200)
        response200.json.return_value = {
            "usage": {"total_tokens": 1},
            "data": [{"index": 0, "embedding": [1.0, 0.0]}],
        }

        def cached(t, k):
            return cache.get((t, k))

        with patch.object(config, "VOYAGE_API_KEY", "fixture"), patch.object(
            config, "HOSTED_CALLS", True
        ), patch.object(config, "EMBED_DIM", 2), patch.object(
            config, "VOYAGE_TOKEN_CAP", 1000000
        ), patch.object(
            g, "cached_many", side_effect=lambda texts, k: [cached(t, k) for t in texts]
        ), patch.object(
            g, "store", side_effect=lambda t, k, v: cache.update({(t, k): v})
        ), patch.object(
            g, "batches", side_effect=lambda ts, k: [(ts, 100)] if ts else []
        ), patch.object(
            g, "reserve", side_effect=lambda n: reserve.append(n)
        ), patch.object(
            rag.db, "meta_get", return_value=0
        ), patch.object(
            rag.db, "meta_add"
        ), patch(
            "httpx.post", side_effect=[response429, response200]
        ) as post, patch.object(
            rag.time, "sleep"
        ) as sleep:
            self.assertEqual(rag._voyage(["hello"], "document"), [[1.0, 0.0]])
            sleep.assert_called_once_with(80)
            self.assertEqual(len(reserve), 2)
            self.assertEqual(rag._voyage(["hello"], "document"), [[1.0, 0.0]])
            self.assertEqual(post.call_count, 2)

    def test_bulk_cache_single_query(self):
        with patch.object(g, "cache_key", side_effect=lambda t, k: t), patch.object(
            g.db, "q", return_value=[{"key": "b", "value": "[1,2]"}]
        ) as query:
            self.assertEqual(
                g.cached_many(["a", "b", "b"], "document"), [None, [1, 2], [1, 2]]
            )
            query.assert_called_once()
