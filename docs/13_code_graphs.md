# 13 — Code Graphs & Change Impact Analysis

## 1. Concept Overview

Before modifying a function in a large codebase, engineers must know its **blast radius**:

> "What could break if I change `authenticate_user()`?"

---

## 2. Impact Analyzer Architecture

`ImpactAnalyzer` uses `Neo4jGraphStore` to calculate the blast radius:

1. **Direct Callers**: Identifies functions calling `authenticate_user()`.
2. **Affected Files**: Isolates repository files containing those calling functions.
3. **Affected Tests**: Isolates test suites (e.g. `tests/test_auth.py`) that invoke the call chain.
4. **Risk Scoring**: Evaluates risk (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) based on total caller fan-out.
