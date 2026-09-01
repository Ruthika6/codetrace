# 17 — Production RAG Deployment & Observability

## 1. Production Architecture Overview

CODETRACE is packaged using Docker and Docker Compose for zero-dependency local deployment:

- **Streamlit Frontend** (`app.py`): Python-only multi-page UI listening on port 8501.
- **FastAPI REST Service** (`api/main.py`): Asynchronous gateway API listening on port 8000.
- **Qdrant Vector Database**: Listening on port 6333.
- **PostgreSQL Relational DB**: Listening on port 5432.
- **Neo4j Graph Database**: Listening on ports 7474 (HTTP) and 7687 (Bolt).
- **Redis Cache & Task Broker**: Listening on port 6379.

---

## 2. Observability & Telemetry

`TelemetryLogger` tracks:
- Query latency per component (Hybrid search latency, reranker latency, graph traversal time).
- Token usage counts.
- Retrieval confidence scores.
- Evidence verification pass rates.
