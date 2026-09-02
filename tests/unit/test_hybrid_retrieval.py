"""Unit tests for Phase 3: BM25, Hybrid Search & Reranking."""

import pytest
from codetrace.ingestion.chunker import CodeChunk
from codetrace.retrieval.bm25_search import BM25SearchEngine, CodeTokenizer
from codetrace.retrieval.fusion import ReciprocalRankFusion
from codetrace.retrieval.reranker import CrossEncoderReranker
from codetrace.retrieval.hybrid_search import HybridSearchEngine


def test_code_tokenizer():
    tokens = CodeTokenizer.tokenize("authenticateUser(jwt_secret)")
    assert "authenticate" in tokens
    assert "user" in tokens
    assert "jwt" in tokens
    assert "secret" in tokens


def test_bm25_search():
    c1 = CodeChunk(
        chunk_id="chunk_jwt",
        file_path="config.py",
        language="python",
        symbol_name="JWT_SECRET",
        symbol_type="module",
        start_line=1,
        end_line=5,
        parent_symbol=None,
        content="JWT_SECRET = 'super_secret_key_123'",
    )
    c2 = CodeChunk(
        chunk_id="chunk_db",
        file_path="db.py",
        language="python",
        symbol_name="DATABASE_URL",
        symbol_type="module",
        start_line=1,
        end_line=5,
        parent_symbol=None,
        content="DATABASE_URL = 'postgresql://localhost/mydb'",
    )

    engine = BM25SearchEngine()
    engine.index_chunks([c1, c2])

    results = engine.search("JWT_SECRET", top_k=1)
    assert len(results) == 1
    assert results[0]["payload"]["chunk_id"] == "chunk_jwt"


def test_rrf_fusion():
    res1 = [{"payload": {"chunk_id": "A"}}, {"payload": {"chunk_id": "B"}}]
    res2 = [{"payload": {"chunk_id": "B"}}, {"payload": {"chunk_id": "C"}}]

    fused = ReciprocalRankFusion.fuse([res1, res2], k=60, top_k=3)
    chunk_ids = [f["payload"]["chunk_id"] for f in fused]
    assert "B" in chunk_ids  # B appears in both lists, should rank high


def test_hybrid_search_engine():
    c1 = CodeChunk(
        chunk_id="auth_chunk",
        file_path="auth.py",
        language="python",
        symbol_name="verify_token",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def verify_token(token):\n    # verifies JWT token validity\n    return True",
    )
    c2 = CodeChunk(
        chunk_id="order_chunk",
        file_path="orders.py",
        language="python",
        symbol_name="create_order",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def create_order(user_id, items):\n    # places new customer order\n    return {'status': 'created'}",
    )

    engine = HybridSearchEngine()
    engine.index_chunks([c1, c2])

    # Test hybrid_rerank mode
    results = engine.search("How to verify JWT tokens?", top_k=1, mode="hybrid_rerank")
    assert len(results) == 1
    assert results[0]["payload"]["symbol_name"] == "verify_token"
