"""SentenceTransformer Embedder module for CODETRACE."""

from typing import List, Union
import numpy as np


class SentenceTransformerEmbedder:
    """Generates dense vector embeddings for code chunks and user queries."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                # Lightweight mock fallback if model download fails or offline
                self._model = "fallback"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings for a list of text strings."""
        self._load_model()
        if self._model == "fallback":
            # Return deterministic normalized 384-dim pseudo vectors for testing
            return [self._mock_vector(t) for t in texts]

        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Generate dense vector embedding for a single query."""
        self._load_model()
        if self._model == "fallback":
            return self._mock_vector(query)

        # For BGE models, query instruction prefix improves retrieval accuracy
        prompt_query = f"Represent this sentence for searching relevant code: {query}"
        embedding = self._model.encode([prompt_query], normalize_embeddings=True)[0]
        return embedding.tolist()

    @staticmethod
    def _mock_vector(text: str, dim: int = 384) -> List[float]:
        """Generate a deterministic normalized float vector based on string hash."""
        seed = sum(ord(c) for c in text)
        rng = np.random.RandomState(seed % (2**32 - 1))
        vec = rng.randn(dim)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()
