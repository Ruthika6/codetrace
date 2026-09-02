"""FastAPI Gateway REST Service for CODETRACE."""

from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from codetrace.api.schemas import (
    DebugRequest,
    DebugResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
    SearchResponseItem,
)
from codetrace.agents.workflow import InvestigationWorkflow
from codetrace.ingestion.chunker import CodeAwareChunker
from codetrace.ingestion.repository_scanner import RepositoryScanner
from codetrace.retrieval.hybrid_search import HybridSearchEngine

# Global in-memory engine instances
hybrid_search = HybridSearchEngine()
workflow = InvestigationWorkflow(hybrid_search=hybrid_search)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown hooks."""
    # Index current directory on startup
    scanner = RepositoryScanner(".")
    files = scanner.scan(include_content=True)
    chunker = CodeAwareChunker()
    chunks = []
    for f in files:
        chunks.extend(chunker.chunk_file(f))
    hybrid_search.index_chunks(chunks)
    yield


app = FastAPI(
    title="CODETRACE Engine API",
    description="AI-Powered Codebase Investigation & Debugging REST Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "CODETRACE Engine"}


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_repository(req: IngestRequest):
    """Scan and index a repository path."""
    try:
        scanner = RepositoryScanner(req.repo_path)
        files = scanner.scan(include_content=True)
        chunker = CodeAwareChunker()
        chunks = []
        for f in files:
            chunks.extend(chunker.chunk_file(f))

        hybrid_search.index_chunks(chunks)

        total_lines = sum(f.line_count for f in files)
        return IngestResponse(
            status="success",
            total_files=len(files),
            total_chunks=len(chunks),
            total_lines=total_lines,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingestion failed: {str(e)}",
        )


@app.post("/api/search", response_model=SearchResponse)
async def search_codebase(req: SearchRequest):
    """Execute hybrid retrieval over codebase."""
    raw_results = hybrid_search.search(
        query=req.query,
        top_k=req.top_k,
        mode=req.mode,
        filter_file=req.filter_file,
    )

    items = []
    for r in raw_results:
        payload = r["payload"]
        items.append(
            SearchResponseItem(
                score=float(r.get("score", 0.0)),
                chunk_id=payload.get("chunk_id", ""),
                file_path=payload.get("file_path", ""),
                symbol_name=payload.get("symbol_name"),
                symbol_type=payload.get("symbol_type", "module"),
                start_line=payload.get("start_line", 1),
                end_line=payload.get("end_line", 1),
                content=payload.get("content", ""),
            )
        )

    return SearchResponse(
        query=req.query,
        mode=req.mode,
        total_results=len(items),
        results=items,
    )


@app.post("/api/investigate", response_model=DebugResponse)
async def investigate_bug(req: DebugRequest):
    """Run full 9-agent evidence-backed bug investigation."""
    try:
        state = workflow.run_investigation(query=req.query, raw_trace=req.stack_trace)
        rc = state.get("root_cause") or {}

        return DebugResponse(
            classified_category=state.get("classified_category", "GENERAL_REPOSITORY_QUESTION"),
            likely_root_cause=rc.get("likely_cause", "Unknown issue"),
            confidence_score=rc.get("confidence", 0.8),
            explanation=rc.get("explanation", ""),
            affected_files=rc.get("affected_files", []),
            evidence=state.get("evidence_items", []),
            suggested_patch=state.get("patch"),
            markdown_report=state.get("final_response", ""),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}",
        )
