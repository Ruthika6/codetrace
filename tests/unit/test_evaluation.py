"""Unit tests for Phase 10: RAG Evaluation & Benchmark Lab."""

import pytest
from codetrace.evaluation.retrieval_metrics import RetrievalMetrics
from codetrace.evaluation.experiments import ExperimentRunner
from codetrace.retrieval.hybrid_search import HybridSearchEngine
from codetrace.ingestion.chunker import CodeChunk


def test_retrieval_metrics():
    retrieved = ["auth.py", "db.py", "orders.py"]
    ground_truth = {"auth.py"}

    rec = RetrievalMetrics.recall_at_k(retrieved, ground_truth, k=3)
    prec = RetrievalMetrics.precision_at_k(retrieved, ground_truth, k=3)
    mrr_val = RetrievalMetrics.mrr(retrieved, ground_truth)
    hit = RetrievalMetrics.hit_rate(retrieved, ground_truth, k=3)

    assert rec == 1.0
    assert abs(prec - 0.3333) < 0.01
    assert mrr_val == 1.0
    assert hit == 1.0


def test_experiment_runner():
    chunk = CodeChunk(
        chunk_id="auth_c",
        file_path="backend/auth.py",
        language="python",
        symbol_name="authenticate_user",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def authenticate_user(): pass",
    )

    engine = HybridSearchEngine()
    engine.index_chunks([chunk])

    dataset = [
        {
            "query": "Where is authenticate_user defined?",
            "relevant_files": ["backend/auth.py"],
        }
    ]

    results = ExperimentRunner.run_benchmark(engine, dataset)
    assert len(results) == 4
    rerank_res = next(r for r in results if r.mode == "hybrid_rerank")
    assert rerank_res.hit_rate_at_5 == 1.0
