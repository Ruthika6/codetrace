"""Unit tests for Phase 8 & 9: LangGraph Multi-Agent Orchestration & Self-Correction."""

import pytest
from codetrace.ingestion.chunker import CodeChunk
from codetrace.retrieval.hybrid_search import HybridSearchEngine
from codetrace.agents.workflow import InvestigationWorkflow


def test_investigation_workflow_end_to_end():
    chunk = CodeChunk(
        chunk_id="auth_chunk",
        file_path="backend/auth.py",
        language="python",
        symbol_name="authenticate_user",
        symbol_type="function",
        start_line=42,
        end_line=58,
        parent_symbol=None,
        content="def authenticate_user(token):\n    if token.exp < current_time:\n        raise Exception('Expired')\n    return True",
    )

    engine = HybridSearchEngine()
    engine.index_chunks([chunk])

    workflow = InvestigationWorkflow(hybrid_search=engine)
    state = workflow.run_investigation("Why does login fail with expired token?")

    assert state["is_verified"] is True
    assert len(state["plan"]) >= 5
    assert state["root_cause"] is not None
    assert "backend/auth.py" in state["root_cause"]["affected_files"]
    assert "LIKELY ROOT CAUSE" in state["final_response"]
    assert "EVIDENCE" in state["final_response"]
