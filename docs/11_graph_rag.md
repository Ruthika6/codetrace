# 11 — GraphRAG & Multi-Hop Context Traversal

## 1. Why Vector RAG Needs GraphRAG

Dense vector search finds individual code chunks based on semantic textual similarity. However, software architecture relies on multi-hop dependencies:

```text
LoginController (/login endpoint)
       ↓ calls
AuthService (authenticate_user)
       ↓ calls
JWTService (validate_token)
       ↓ queries
UserRepository (find_by_id)
```

Vector search might retrieve `JWTService` in isolation. GraphRAG traverses Neo4j graph relationships (`CALLS`, `IMPORTS`, `ROUTES_TO`), fetching the entire execution chain into context.

---

## 2. Implementation in CODETRACE

When a query is categorized as `DEPENDENCY_ANALYSIS` or `API_TRACE`:

1. CODETRACE identifies the root symbol via hybrid retrieval.
2. Neo4j graph queries extract 1-hop and 2-hop callers/callees.
3. The graph chain is formatted into structural context for the LLM.
