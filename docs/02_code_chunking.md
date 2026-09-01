# 02 — Code-Aware Structural Chunking

## 1. Concept Overview

Code-aware chunking is the process of partitioning source files along syntactic boundaries (functions, classes, methods, docstrings) rather than arbitrary character or token counts.

---

## 2. Structural Parsing vs. Naive Splitting

| Metric | Naive Character Splitting | CODETRACE Code-Aware Chunking |
| :--- | :--- | :--- |
| **Boundary Unit** | 500 characters | AST Node (Function, Class, Method) |
| **Context Completeness** | Frequently cuts functions mid-loop | 100% Function & Docstring Integrity |
| **Metadata Integrity** | None | Symbol Name, Line Bounds, Imports, Calls |
| **Parent References** | Lost | Preserved (`parent_symbol = "AuthService"`) |

---

## 3. Implementation in CODETRACE

In CODETRACE Phase 1, `CodeAwareChunker` operates as follows:

1. **AST Extraction**: `CodeParser` uses Python's standard `ast` module (and structural regex fallbacks for polyglot languages) to extract symbols with line ranges.
2. **Symbol-Bounded Chunks**: Creates `CodeChunk` objects for every function, async function, class, and method.
3. **Gap Handling**: Lines not covered by symbols (top-level scripts, import blocks, configuration files) are chunked using sliding windows.
4. **Deterministic Identification**: Generates deterministic SHA-256 chunk IDs based on `file_path::symbol_name::start_line-end_line`.
