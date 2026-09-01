# 01 — Retrieval-Augmented Generation (RAG) Basics for Codebases

## 1. What is RAG?

Retrieval-Augmented Generation (RAG) is an AI architecture that enhances Large Language Model (LLM) responses by retrieving relevant background context from an external database before generating an answer.

Instead of relying solely on the parametric memory of an LLM, RAG introduces an information retrieval pipeline:

$$\text{User Query} \longrightarrow \text{Retriever} \longrightarrow \text{Relevant Context} \longrightarrow \text{LLM} \longrightarrow \text{Evidence-Backed Answer}$$

---

## 2. Why Generic RAG Fails on Code Repositories

Standard RAG implementations split text files into fixed character chunks (e.g. 500 characters with 50 character overlap). While this works for prose documents, **it breaks code**:

1. **Truncated Control Flow**: A function signature might be in Chunk A, while its parameter validation and `return` statement end up in Chunk B.
2. **Loss of Hierarchy**: Standard RAG treats a method in a class as isolated text, losing track of class properties, inheritance, and import modules.
3. **Variable Blindness**: Searching for exact symbol names (e.g., `JWT_SECRET` or `authenticate_user`) with dense vector search often fails due to semantic smoothing, missing exact string matches.

---

## 3. How CODETRACE Solves Code RAG

CODETRACE addresses code structure directly:

1. **AST-Based Structural Chunking**: Uses Abstract Syntax Trees (AST) to keep entire functions, classes, and methods intact.
2. **Rich Metadata Attachment**: Every chunk preserves exact file paths, symbol names, line numbers (`start_line`, `end_line`), import definitions, and parent class names.
3. **Dual Hybrid Retrieval**: Combines sparse BM25 keyword matching (for exact variable/symbol names) with dense vector embeddings (for conceptual intent), fused via Reciprocal Rank Fusion (RRF).
