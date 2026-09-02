"""Unit tests for Phase 5: Neo4j Code Graph & Impact Analysis."""

import pytest
from codetrace.database.neo4j import Neo4jGraphStore
from codetrace.graph.dependency_graph import DependencyGraphBuilder
from codetrace.graph.call_graph import CallGraphBuilder
from codetrace.debugging.impact_analysis import ImpactAnalyzer
from codetrace.ingestion.chunker import CodeChunk
from codetrace.ingestion.repository_scanner import FileInfo
from codetrace.ingestion.file_classifier import FileCategory


def test_neo4j_fallback_graph_store():
    store = Neo4jGraphStore(use_fallback=True)

    c1_id = "auth.py::authenticate_user"
    c2_id = "orders.py::place_order"

    store.add_node("Function", c1_id, {"name": "authenticate_user", "file_path": "auth.py"})
    store.add_node("Function", c2_id, {"name": "place_order", "file_path": "orders.py"})

    store.add_relationship(from_id=c2_id, to_id=c1_id, rel_type="CALLS")

    callers = store.get_callers("auth.py::authenticate_user", max_depth=2)
    assert len(callers) >= 1
    assert callers[0]["caller_name"] == "place_order"


def test_call_graph_builder_and_impact_analyzer():
    store = Neo4jGraphStore(use_fallback=True)

    chunk_auth = CodeChunk(
        chunk_id="auth_id",
        file_path="auth.py",
        language="python",
        symbol_name="authenticate_user",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def authenticate_user(): pass",
    )

    chunk_order = CodeChunk(
        chunk_id="order_id",
        file_path="orders.py",
        language="python",
        symbol_name="place_order",
        symbol_type="function",
        start_line=1,
        end_line=10,
        parent_symbol=None,
        content="def place_order(): authenticate_user()",
        calls=["authenticate_user"],
    )

    dep_builder = DependencyGraphBuilder(store)
    file_info = FileInfo("auth.py", "/tmp/auth.py", FileCategory.SOURCE_CODE, "python", "hash", 10, 100)
    dep_builder.build_graph([file_info], [chunk_auth, chunk_order])

    call_builder = CallGraphBuilder(store)
    call_builder.build_call_graph([chunk_auth, chunk_order])

    analyzer = ImpactAnalyzer(store)
    report = analyzer.analyze_impact("auth.py::authenticate_user")
    assert "place_order" in report.affected_functions
    assert "orders.py" in report.affected_files
