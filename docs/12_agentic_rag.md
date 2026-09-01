# 12 — Agentic RAG & LangGraph Multi-Agent Workflows

## 1. Why Agentic RAG Beats Single-Prompt RAG

Single-prompt RAG attempts to perform classification, retrieval, reasoning, and response generation in a single monolithic LLM call. This often leads to incomplete retrieval and hallucinated line citations.

Agentic RAG divides investigation responsibilities across specialized agents:

1. `Planner Agent`: Formulates step-by-step investigation goals.
2. `Code Retrieval Agent`: Executes hybrid vector + BM25 search.
3. `Dependency Agent`: Traverses Neo4j graph for callers and callees.
4. `Git Agent`: Queries commit diffs to check for recent regressions.
5. `Log Agent`: Parses error stack traces to map line numbers.
6. `Test Agent`: Finds unit tests covering affected symbols.
7. `Evidence Agent`: Verifies that line citations physically exist in source files.
8. `Debugging Agent`: Synthesizes root cause analysis.
9. `Fix Agent`: Proposes unified git patches for user review.

---

## 2. Self-Correcting Verification Loops

```text
Retrieve Chunks
       ↓
Verify Line Evidence against Source Files
       ├── Evidence Insufficient? → Expand Retrieval (Retry)
       └── Evidence Verified?     → Emit Final Evidence-Backed Response
```
