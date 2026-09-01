# 04 — Vector Search & Qdrant Payload Filtering

## 1. Vector Search Architecture

Vector search calculates the Cosine Similarity between a query vector $\vec{q}$ and chunk vectors $\vec{v}_i$:

$$\text{Similarity}(\vec{q}, \vec{v}_i) = \frac{\vec{q} \cdot \vec{v}_i}{\|\vec{q}\| \|\vec{v}_i\|}$$

---

## 2. Qdrant Vector Store Integration

CODETRACE uses Qdrant for dense vector storage and retrieval.

Key Configuration:
- **Distance Metric**: `Distance.COSINE`
- **Vector Dimension**: 384
- **Payload Indexing**: Indexed payload fields for `file_path`, `symbol_name`, `symbol_type`, `language`.

---

## 3. Payload Filtering

Filtering allows restrict search to specific subsets of the codebase without re-embedding:

```python
# Filter search results to only function symbols in auth.py
results = qdrant_client.search(
    collection_name="codetrace_code_chunks",
    query_vector=query_vector,
    query_filter=Filter(must=[
        FieldCondition(key="file_path", match=MatchValue(value="backend/auth.py")),
        FieldCondition(key="symbol_type", match=MatchValue(value="function"))
    ])
)
```
