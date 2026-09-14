"""Evaluation Lab page for CODETRACE."""

import streamlit as st
import pandas as pd
from codetrace.evaluation.experiments import ExperimentRunner, ExperimentResult
from codetrace.retrieval.hybrid_search import HybridSearchEngine
from codetrace.ingestion.chunker import CodeChunk

st.set_page_config(page_title="Evaluation Lab | CODETRACE", page_icon="🧪", layout="wide")

st.title("🧪 RAG Strategy Benchmark & Experiment Lab")

st.markdown("Compare retrieval strategies: **Vector Only** vs **BM25 Only** vs **Hybrid RRF** vs **Hybrid + CrossEncoder Rerank**.")

if st.button("Run Benchmark Experiments", type="primary"):
    with st.spinner("Evaluating retrieval strategies over benchmark dataset..."):
        chunk = CodeChunk("c1", "backend/auth.py", "python", "authenticate_user", "function", 1, 10, None, "def authenticate_user(): pass")
        engine = HybridSearchEngine()
        engine.index_chunks([chunk])

        dataset = [{"query": "Where is authenticate_user defined?", "relevant_files": ["backend/auth.py"]}]
        results = ExperimentRunner.run_benchmark(engine, dataset)

        data = [
            {
                "Strategy": r.mode,
                "Recall@5": r.recall_at_5,
                "Precision@5": r.precision_at_5,
                "MRR": r.mrr,
                "NDCG@5": r.ndcg_at_5,
                "Hit Rate@5": r.hit_rate_at_5,
            }
            for r in results
        ]

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
