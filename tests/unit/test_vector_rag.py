"""Unit tests for Phase 2: Vector RAG & Dual Indexing."""

import pytest
from codetrace.embeddings.embedder import SentenceTransformerEmbedder
from codetrace.database.qdrant import QdrantVectorStore
from codetrace.retrieval.vector_search import VectorSearchEngine
from codetrace.ingestion.chunker import CodeChunk


def test_sentence_transformer_embedder():
    embedder = SentenceTransformerEmbedder()
    vecs = embedder.embed_texts(["def login(user, password): pass", "class User: pass"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 384

    q_vec = embedder.embed_query("How does login work?")
    assert len(q_vec) == 384


def test_vector_search_engine():
    chunk1 = CodeChunk(
        chunk_id="c1",
        file_path="auth.py",
        language="python",
        symbol_name="authenticate_user",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def authenticate_user(username, password):\n    # validates JWT token\n    return True",
    )

    chunk2 = CodeChunk(
        chunk_id="c2",
        file_path="db.py",
        language="python",
        symbol_name="connect_database",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def connect_database(uri):\n    # connects to PostgreSQL database\n    pass",
    )

    engine = VectorSearchEngine()
    engine.index_chunks([chunk1, chunk2])

    results = engine.search("user token authentication", top_k=2)
    assert len(results) >= 1
    top_payload = results[0]["payload"]
    assert top_payload["symbol_name"] == "authenticate_user"
    assert top_payload["file_path"] == "auth.py"
