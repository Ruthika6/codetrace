# 07 — Cross-Encoder Reranking

## 1. Bi-Encoder vs Cross-Encoder

- **Bi-Encoders** (Vector Search Embeddings): Compute query and document vectors independently. Fast ($O(1)$ lookup via vector index), but sacrifices fine-grained cross-attention between query words and code tokens.
- **Cross-Encoders**: Pass query and document jointly through full transformer attention layers (`[CLS] Query [SEP] Passage [SEP]`). Computationally expensive, but significantly more accurate.

---

## 2. Two-Stage Retrieval Architecture in CODETRACE

```text
Full Repository (40,000+ Code Chunks)
        ↓  (Hybrid Retrieval: Vector + BM25)
Top 20 Fused Candidates
        ↓  (Cross-Encoder Reranker: BAAI/bge-reranker-base)
Top 5 High-Precision Chunks
        ↓
LLM Context Window
```

This 2-stage design achieves sub-100ms retrieval latencies while maintaining top-1 precision for complex code debugging queries.
