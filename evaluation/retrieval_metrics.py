"""Retrieval evaluation metrics calculation engine for CODETRACE."""

import math
from typing import List, Set


class RetrievalMetrics:
    """Calculates IR evaluation metrics: Recall@K, Precision@K, MRR, NDCG@K, Hit Rate."""

    @classmethod
    def recall_at_k(cls, retrieved: List[str], ground_truth: Set[str], k: int) -> float:
        """Recall@K = |Retrieved[:K] ∩ GroundTruth| / |GroundTruth|."""
        if not ground_truth:
            return 0.0
        cutoff = retrieved[:k]
        hits = len(set(cutoff).intersection(ground_truth))
        return hits / len(ground_truth)

    @classmethod
    def precision_at_k(cls, retrieved: List[str], ground_truth: Set[str], k: int) -> float:
        """Precision@K = |Retrieved[:K] ∩ GroundTruth| / K."""
        if k == 0:
            return 0.0
        cutoff = retrieved[:k]
        hits = len(set(cutoff).intersection(ground_truth))
        return hits / k

    @classmethod
    def mrr(cls, retrieved: List[str], ground_truth: Set[str]) -> float:
        """Mean Reciprocal Rank (MRR) = 1 / rank of first relevant item."""
        for rank, item in enumerate(retrieved, 1):
            if item in ground_truth:
                return 1.0 / rank
        return 0.0

    @classmethod
    def ndcg_at_k(cls, retrieved: List[str], ground_truth: Set[str], k: int) -> float:
        """Normalized Discounted Cumulative Gain (NDCG@K)."""
        dcg = 0.0
        for i, item in enumerate(retrieved[:k]):
            if item in ground_truth:
                dcg += 1.0 / math.log2(i + 2)

        idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(ground_truth), k)))
        return dcg / idcg if idcg > 0 else 0.0

    @classmethod
    def hit_rate(cls, retrieved: List[str], ground_truth: Set[str], k: int) -> float:
        """Hit Rate@K = 1.0 if at least one relevant item in top K, else 0.0."""
        cutoff = retrieved[:k]
        return 1.0 if any(item in ground_truth for item in cutoff) else 0.0
