# 09 — Multi-Query Retrieval Expansion

## 1. Concept Overview

Complex software questions frequently touch multiple system layers (routes, services, middleware, database tables).

A single search query like `"Why does the order API return 401?"` might miss the specific middleware class where token validation occurs.

---

## 2. Multi-Query Expansion Pipeline

`MultiQueryGenerator` breaks down the original request into multiple perspective sub-queries:

1. `Original`: "Why does the order API return 401?"
2. `Query 1`: "order API authentication handler"
3. `Query 2`: "/api/orders JWT validation middleware"
4. `Query 3`: "401 authorization failure error handling"

Retrieval is executed for each sub-query, and candidate sets are combined via Reciprocal Rank Fusion (RRF).
