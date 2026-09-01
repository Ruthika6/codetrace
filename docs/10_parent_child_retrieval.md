# 10 — Parent-Child Context Retrieval

## 1. The Small Chunk vs Large Context Dilemma

- **Small Chunks** (Functions / Methods): Superior retrieval precision. Cosine distance accurately matches specific query intent.
- **Large Chunks** (Full Classes / Modules): Essential for generation. The LLM requires surrounding class attributes, imports, and helper methods to generate accurate code explanations and patches.

---

## 2. Implementation in CODETRACE

`ParentChildRetriever` resolves this dilemma:

1. Retrieve small, highly specific symbol chunks (e.g. `authenticate_user`).
2. Lookup its parent symbol (`AuthService`) or file module.
3. Attach the parent class content (`parent_context`) to the retrieved payload before passing context to the LLM.
