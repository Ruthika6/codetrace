# 15 — Root Cause Analysis & Evidence-Backed Debugging

## 1. Concept Overview

A common failure mode of AI coding assistants is generating unverified, hallucinated explanations:

> AI: "Line 98 of auth.py has a syntax error." (When auth.py only has 40 lines).

CODETRACE enforces **Evidence-Backed Debugging**:

```text
Error Log / User Query
        ↓
Retrieved Source Code Chunks
        ↓
AST Symbol Verification
        ↓
Root Cause Hypothesis Synthesis
        ↓
Verified Evidence Citations (Exact file, line ranges, snippet)
```

---

## 2. Evidence Verification Guardrails

Every conclusion produced by `RootCauseInvestigator` includes:

- `likely_root_cause`: High-level explanation of the bug.
- `confidence_score`: Score between 0.0 and 1.0 based on evidence strength.
- `evidence`: List of `EvidenceItem` objects containing exact `file_path`, `start_line`, `end_line`, and verified source snippets.
- `patch`: Proposed Unified Git Diff for user review.
