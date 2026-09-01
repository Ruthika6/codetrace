# 16 — RAG Evaluation & Benchmark Metrics

## 1. Why Evaluation is Essential for Production RAG

Without quantitative metrics, architectural changes to chunking, embeddings, or reranking are based on guesswork.

CODETRACE evaluates retrieval quality across 5 standard Information Retrieval (IR) metrics:

1. **Recall@K**: Proportion of relevant ground truth files retrieved in Top K.
2. **Precision@K**: Proportion of top K retrieved files that are relevant.
3. **MRR (Mean Reciprocal Rank)**: Reciprocal rank $1/\text{rank}$ of the first relevant result.
4. **NDCG@K**: Evaluates both relevance and position ordering.
5. **Hit Rate@K**: Proportion of queries with at least 1 relevant hit in Top K.

---

## 2. Evaluation Strategy Variations

`ExperimentRunner` benchmark runs compare 4 strategy variations:

- `vector_only`: Baseline dense vector retrieval.
- `bm25_only`: Keyword-only retrieval.
- `hybrid_rrf`: Dense + Sparse Reciprocal Rank Fusion.
- `hybrid_rerank`: Hybrid retrieval + Cross-Encoder deep reranking (Production standard).
