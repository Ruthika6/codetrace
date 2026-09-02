"""Unit tests for Phase 4: Query Transformation & Parent-Child Context Expansion."""

import pytest
from codetrace.ingestion.chunker import CodeChunk
from codetrace.retrieval.query_rewriter import QueryClassifier, QueryCategory, QueryRewriter
from codetrace.retrieval.multi_query import MultiQueryGenerator
from codetrace.retrieval.parent_child import ParentChildRetriever


def test_query_classifier():
    cat = QueryClassifier.classify("Why am I getting a 401 Unauthorized error on login?")
    assert cat == QueryCategory.BUG_INVESTIGATION

    cat = QueryClassifier.classify("What happens when /api/orders endpoint is called?")
    assert cat == QueryCategory.API_TRACE

    cat = QueryClassifier.classify("Who changed auth.py in the last commit?")
    assert cat == QueryCategory.GIT_HISTORY


def test_query_rewriter():
    history = [
        {"role": "user", "content": "Why does the login API fail?"},
        {"role": "assistant", "content": "The login API uses JWT token validation."},
    ]
    rewritten = QueryRewriter.rewrite("Why does it fail?", chat_history=history)
    assert "login API" in rewritten


def test_multi_query_generator():
    queries = MultiQueryGenerator.generate_queries("Why does the order API return 401?")
    assert len(queries) >= 3
    assert any("JWT" in q or "token" in q for q in queries)


def test_parent_child_retriever():
    parent_chunk = CodeChunk(
        chunk_id="c_parent",
        file_path="auth.py",
        language="python",
        symbol_name="AuthService",
        symbol_type="class",
        start_line=1,
        end_line=20,
        parent_symbol=None,
        content="class AuthService:\n    secret = 'key'",
    )

    child_cand = {
        "payload": {
            "chunk_id": "c_child",
            "file_path": "auth.py",
            "symbol_name": "validate",
            "parent_symbol": "AuthService",
            "content": "def validate(self): pass",
        }
    }

    expanded = ParentChildRetriever.expand_parent_context([child_cand], [parent_chunk])
    assert expanded[0]["payload"]["parent_context"] == parent_chunk.content
