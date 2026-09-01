# 06 — Hybrid Retrieval & Reciprocal Rank Fusion (RRF)

## 1. Concept Overview

Neither Vector Search nor BM25 alone is sufficient for codebase search:
- **Vector Search** excels at natural language concepts ("Explain how user login works").
- **BM25 Search** excels at exact identifier matching ("Where is `REFRESH_TOKEN_EXPIRE` defined?").

Hybrid Retrieval combines both approaches.

---

## 2. Reciprocal Rank Fusion (RRF)

Instead of attempting to normalize raw cosine distance scores against raw BM25 scores (which live on entirely different numerical scales), CODETRACE uses **Reciprocal Rank Fusion (RRF)**:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M$ is the set of retrieval algorithms (Vector Search, BM25 Search).
- $r_m(d)$ is the rank position of document $d$ in algorithm $m$ (1-indexed).
- $k$ is a constant smoothing factor (default $k = 60$).

RRF rewards documents that appear near the top of *both* search strategies.
