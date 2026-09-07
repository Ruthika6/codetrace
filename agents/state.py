"""LangGraph state schema for CODETRACE investigation workflows."""

from typing import Any, Dict, List, Optional, TypedDict


class InvestigationState(TypedDict):
    """Shared state dictionary passed across LangGraph investigation agents."""

    query: str
    classified_category: str
    plan: List[str]
    retrieved_chunks: List[Dict[str, Any]]
    dependency_context: List[Dict[str, Any]]
    git_commits: List[Dict[str, Any]]
    error_trace: Optional[Dict[str, Any]]
    evidence_items: List[Dict[str, Any]]
    root_cause: Optional[Dict[str, Any]]
    patch: Optional[Dict[str, Any]]
    is_verified: bool
    retry_count: int
    final_response: str
