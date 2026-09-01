# 14 — Git Intelligence & Temporal Code Analysis

## 1. Concept Overview

Software bugs rarely appear in isolation; they are often introduced by specific code modifications (regressions).

`GitRepositoryHistory` and `CommitAnalyzer` add a **temporal dimension** to RAG:

```text
Current Stack Trace (File: auth.py:42)
        ↓
Git Commit Log Query (paths="auth.py")
        ↓
Latest Commit (abc1234: "Modify JWT expiration logic")
        ↓
Unified Git Diff Analysis
        ↓
Temporal Evidence Verification
```

---

## 2. Temporal Code RAG Capabilities

1. **Regression Detection**: Correlates stack traces with recent commit hashes.
2. **Version Comparison**: Compares function definitions across two git tags or branch commits.
3. **Author & Commit Attribution**: Identifies which commit introduced breaking boundary logic.
