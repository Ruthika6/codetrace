# CODETRACE — AI-Powered Codebase Investigation & Debugging Engine

> **100% Python-Based Flagship RAG Project**

CODETRACE is an AI software investigator that parses entire code repositories, builds structural code-aware chunks, constructs call/dependency graphs in Neo4j, indexes code in Qdrant and BM25, traces Git execution history, parses stack traces, and utilizes a self-correcting 9-agent LangGraph workflow to identify root causes with verified evidence.

---

## 🌟 Key Features

1. **AST-Aware Structural Chunking**: Preserves functions, classes, methods, docstrings, line numbers (`start_line`, `end_line`), imports, and calls.
2. **Hybrid Search + Reciprocal Rank Fusion (RRF)**: Combines dense vector retrieval (`sentence-transformers / BAAI/bge-small-en-v1.5`) with sparse keyword matching (`rank-bm25`).
3. **Cross-Encoder Deep Reranking**: Reranks fused Top 20 candidate chunks down to Top 5 high-precision snippets using `CrossEncoder`.
4. **Neo4j Code Graph & Blast Radius Impact Analysis**: Traces callers, callees, API endpoints, and database queries across multi-hop dependencies.
5. **Polyglot Error Log & Stack Trace Debugger**: Parses Python, JavaScript/TypeScript, and Java tracebacks to map line numbers directly to source files.
6. **Git Intelligence & Regression Detection**: Analyzes commit history, author timelines, and code diffs using GitPython.
7. **9-Agent LangGraph Workflow with Self-Correction Loop**: Orchestrates `Planner`, `Code Retrieval`, `Dependency`, `Git`, `Log`, `Test`, `Evidence`, `Debugging`, and `Fix` agents.
8. **Evidence-Backed Verification & Citations**: Verifies line citations against physical files before generating answers, preventing AI hallucination.
9. **Evaluation Lab & Observability**: Measures Recall@K, Precision@K, MRR, NDCG@K, and Hit Rate across search variations.

---

## 🚀 Quick Start Guide

### 1. Setup Virtual Environment

```bash
cd codetrace
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Unit Tests

```bash
python -m pytest tests/unit/
```

### 3. Launch Streamlit UI Dashboard

```bash
streamlit run app.py
```

### 4. Launch FastAPI REST Service

```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Launch with Docker Compose (Infrastructure Included)

```bash
docker-compose up -d
```

---

## 📂 Project Structure

```text
codetrace/
├── app.py                         # Streamlit Entrypoint
├── pages/                         # Streamlit 9-Page UI
├── api/                           # FastAPI REST Gateway
├── ingestion/                     # Code Parsing, Classification & Structural Chunker
├── embeddings/                    # Vector Embeddings Engine
├── retrieval/                     # Hybrid Search, BM25, RRF Fusion & Reranker
├── graph/                         # Code Graph, Call Trees & Neo4j Client
├── git/                           # GitPython History & Regression Analyzer
├── agents/                        # LangGraph 9-Agent Workflow
├── debugging/                     # Polyglot Stack Trace Parser & Patch Generator
├── evaluation/                    # RAG Benchmark Suite & Retrieval Metrics
├── database/                      # Qdrant, PostgreSQL, and Neo4j Drivers
├── tests/                         # Pytest Unit Test Suite
├── docs/                          # Comprehensive Learning Manual (17 Markdown files)
├── Dockerfile                     # Production Container Image
├── docker-compose.yml             # Full Infrastructure Compose File
└── README.md                      # Comprehensive Architecture & Usage Guide
```
