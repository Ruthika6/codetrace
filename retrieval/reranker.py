"""Cross-Encoder Reranker module for CODETRACE."""

from typing import Any, Dict, List, Optional
import numpy as np


class CrossEncoderReranker:
    """Reranks candidate search results using fine-grained cross-attention model."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load CrossEncoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
            except Exception:
                self._model = "fallback"

    def rerank(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank candidates based on deep query-document cross attention."""
        if not candidates:
            return []

        self._load_model()

        # Prepare (query, passage) pairs
        pairs = []
        for cand in candidates:
            payload = cand["payload"]
            passage = (
                f"File: {payload.get('file_path')}\n"
                f"Symbol: {payload.get('symbol_name') or 'block'}\n"
                f"Content: {payload.get('content')}"
            )
            pairs.append((query, passage))

        if self._model == "fallback":
            # Heuristic token overlap fallback scoring
            scores = []
            q_tokens = set(query.lower().split())
            for q, p in pairs:
                p_tokens = set(p.lower().split())
                overlap = len(q_tokens.intersection(p_tokens))
                scores.append(float(overlap))
        else:
            raw_scores = self._model.predict(pairs)
            scores = [float(s) for s in raw_scores]

        # Attach rerank score
        reranked = []
        for cand, score in zip(candidates, scores):
            item = cand.copy()
            item["rerank_score"] = float(score)
            item["score"] = float(score)
            reranked.append(item)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
