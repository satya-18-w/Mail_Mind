"""Embedding service using BAAI/bge-small-en-v1.5 (runs locally, free).

Generates 384-dimensional embeddings for semantic search.
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer("BAAI/bge-small-en-v1.5")


class EmbeddingService:
    """Generates text embeddings for semantic search."""

    def __init__(self):
        self.model = _get_model()

    def embed(self, text: str) -> list[float]:
        """Generate embedding vector for a single text.

        Args:
            text: The text to embed.

        Returns:
            384-dimensional embedding vector.
        """
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of 384-dimensional embedding vectors.
        """
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
