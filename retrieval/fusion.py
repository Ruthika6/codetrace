"""Reciprocal Rank Fusion (RRF) module for CODETRACE."""

from typing import Any, Dict, List


class ReciprocalRankFusion:
    """Fuses multiple ranked result lists using Reciprocal Rank Fusion algorithm."""

    @classmethod
    def fuse(
        cls,
        results_list: List[List[Dict[str, Any]]],
        k: int = 60,
        top_k: int = 20,
    ) -> List[Dict[str, Any]]:
        """Perform Reciprocal Rank Fusion over multiple retrieval result sets."""
        rrf_scores: Dict[str, float] = {}
        payload_map: Dict[str, Dict[str, Any]] = {}

        for result_set in results_list:
            for rank, item in enumerate(result_set, 1):
                chunk_id = item["payload"]["chunk_id"]
                payload_map[chunk_id] = item["payload"]

                score_contribution = 1.0 / (k + rank)
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + score_contribution

        # Format fused candidates
        fused_results = []
        for chunk_id, score in rrf_scores.items():
            fused_results.append({
                "score": float(score),
                "payload": payload_map[chunk_id],
                "fusion_method": "RRF",
            })

        fused_results.sort(key=lambda x: x["score"], reverse=True)
        return fused_results[:top_k]
