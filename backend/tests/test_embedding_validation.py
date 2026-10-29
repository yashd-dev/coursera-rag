import unittest
from unittest.mock import patch
from app import rag, config


class EmbeddingValidation(unittest.TestCase):
    def test_no_provider_fallback(self):
        with patch.object(config, "EMBED_PROVIDER", "typo"), patch.object(
            rag, "_local"
        ) as local:
            with self.assertRaises(rag.EmbeddingError):
                rag.embed(["fixture"])
            local.assert_not_called()

    def test_reject_response_count(self):
        with patch.object(config, "EMBED_PROVIDER", "voyage"), patch.object(
            rag, "_voyage", return_value=[]
        ):
            with self.assertRaises(rag.EmbeddingError):
                rag.embed(["fixture"])

    def test_reject_dimensions(self):
        with patch.object(config, "EMBED_PROVIDER", "voyage"), patch.object(
            rag, "_voyage", return_value=[[1, 0]]
        ):
            with self.assertRaises(rag.EmbeddingError):
                rag.embed(["fixture"])

    def test_reject_nan(self):
        with patch.object(config, "EMBED_PROVIDER", "voyage"), patch.object(
            config, "EMBED_DIM", 1
        ), patch.object(rag, "_voyage", return_value=[[float("nan")]]):
            with self.assertRaises(rag.EmbeddingError):
                rag.embed(["fixture"])

    def test_valid_shape(self):
        with patch.object(config, "EMBED_PROVIDER", "voyage"), patch.object(
            config, "EMBED_DIM", 2
        ), patch.object(rag, "_voyage", return_value=[[1.0, 0.0]]):
            self.assertEqual(rag.embed(["fixture"]), [[1.0, 0.0]])
