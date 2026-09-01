# 03 — Vector Embeddings for Codebases

## 1. Concept Overview

Dense vector embeddings represent text (such as functions, classes, or search queries) as high-dimensional numerical vectors in a continuous semantic space.

In CODETRACE, we use `BAAI/bge-small-en-v1.5` (384 dimensions), which maps syntactically and semantically similar code snippets close to one another in vector space.

---

## 2. Why Code Embeddings Require Contextual Construction

Raw source code snippets often lack context if embedded without file boundaries or symbol tags. CODETRACE constructs a rich embedding input string:

```text
File: backend/auth.py
Symbol: authenticate_user (async_method)
Content:
def authenticate_user(token: str):
    ...
```

---

## 3. Query Instruction Prefix

Models like BGE perform better when queries are prefixed with search intent:

```python
prompt_query = f"Represent this sentence for searching relevant code: {query}"
```

This aligns query vectors with document vectors in dense space, maximizing cosine similarity precision.
