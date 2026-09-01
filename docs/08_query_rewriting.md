# 08 — Query Classification & Contextual Rewriting

## 1. Intent Classification

Before executing retrieval, CODETRACE classifies user intent:

- `BUG_INVESTIGATION`: Prefers log line matches, stack trace mappings, and recent git diffs.
- `API_TRACE`: Prefers router endpoints, middleware chains, and controller functions.
- `DEPENDENCY_ANALYSIS`: Triggers Neo4j graph multi-hop queries.
- `SECURITY`: Filters for secret scans and authentication handlers.

---

## 2. Contextual Query Rewriting

Conversational follow-up questions often contain ambiguous references:

> User: "Why does the login endpoint fail?"
> Assistant: "..."
> User: "Why does it fail?"

`QueryRewriter` uses conversation memory to transform `"Why does it fail?"` into `"Why does the login endpoint fail?"`, ensuring single-shot vector and BM25 retrievers receive fully specified search intent.
