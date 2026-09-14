"""Experiment runner for comparing RAG retrieval strategies."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from codetrace.evaluation.retrieval_metrics import RetrievalMetrics
from codetrace.retrieval.hybrid_search import HybridSearchEngine


@dataclass
class ExperimentResult:
    """Benchmark results for a single retrieval mode."""

    mode: str
    recall_at_5: float
    precision_at_5: float
    mrr: float
    ndcg_at_5: float
    hit_rate_at_5: float


class ExperimentRunner:
    """Runs evaluation benchmarks across RAG retrieval strategy variations."""

    @classmethod
    def run_benchmark(
        cls,
        search_engine: HybridSearchEngine,
        eval_dataset: List[Dict[str, Any]],
    ) -> List[ExperimentResult]:
        """Evaluate modes: vector_only, bm25_only, hybrid_rrf, hybrid_rerank."""

        modes = ["vector_only", "bm25_only", "hybrid_rrf", "hybrid_rerank"]
        results: List[ExperimentResult] = []

        for mode in modes:
            recalls, precisions, mrrs, ndcgs, hits = [], [], [], [], []

            for sample in eval_dataset:
                query = sample["query"]
                truth_files = set(sample["relevant_files"])

                retrieved = search_engine.search(query, top_k=5, mode=mode)
                retrieved_files = [r["payload"].get("file_path", "") for r in retrieved]

                recalls.append(RetrievalMetrics.recall_at_k(retrieved_files, truth_files, 5))
                precisions.append(RetrievalMetrics.precision_at_k(retrieved_files, truth_files, 5))
                mrrs.append(RetrievalMetrics.mrr(retrieved_files, truth_files))
                ndcgs.append(RetrievalMetrics.ndcg_at_k(retrieved_files, truth_files, 5))
                hits.append(RetrievalMetrics.hit_rate(retrieved_files, truth_files, 5))

            avg_recall = sum(recalls) / len(recalls) if recalls else 0.0
            avg_prec = sum(precisions) / len(precisions) if precisions else 0.0
            avg_mrr = sum(mrrs) / len(mrrs) if mrrs else 0.0
            avg_ndcg = sum(ndcgs) / len(ndcgs) if ndcgs else 0.0
            avg_hit = sum(hits) / len(hits) if hits else 0.0

            results.append(
                ExperimentResult(
                    mode=mode,
                    recall_at_5=round(avg_recall, 4),
                    precision_at_5=round(avg_prec, 4),
                    mrr=round(avg_mrr, 4),
                    ndcg_at_5=round(avg_ndcg, 4),
                    hit_rate_at_5=round(avg_hit, 4),
                )
            )

        return results
