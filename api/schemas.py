"""Pydantic v2 schemas for CODETRACE REST API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    repo_path: str = Field(default=".", description="Local directory path or ZIP file path")


class IngestResponse(BaseModel):
    status: str
    total_files: int
    total_chunks: int
    total_lines: int


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    mode: str = Field(default="hybrid_rerank", description="vector_only, bm25_only, hybrid_rrf, hybrid_rerank")
    filter_file: Optional[str] = None


class SearchResponseItem(BaseModel):
    score: float
    chunk_id: str
    file_path: str
    symbol_name: Optional[str] = None
    symbol_type: str
    start_line: int
    end_line: int
    content: str


class SearchResponse(BaseModel):
    query: str
    mode: str
    total_results: int
    results: List[SearchResponseItem]


class DebugRequest(BaseModel):
    query: str
    stack_trace: Optional[str] = None


class DebugResponse(BaseModel):
    classified_category: str
    likely_root_cause: str
    confidence_score: float
    explanation: str
    affected_files: List[str]
    evidence: List[Dict[str, Any]]
    suggested_patch: Optional[Dict[str, Any]] = None
    markdown_report: str
