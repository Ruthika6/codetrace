"""Hybrid Retrieval Engine combining Dense Vector Search, BM25 Keyword Search, RRF Fusion & Reranking."""

from typing import Any, Dict, List, Optional

from codetrace.ingestion.chunker import CodeChunk
from codetrace.retrieval.bm25_search import BM25SearchEngine
from codetrace.retrieval.fusion import ReciprocalRankFusion
from codetrace.retrieval.reranker import CrossEncoderReranker
from codetrace.retrieval.vector_search import VectorSearchEngine


class HybridSearchEngine:
    """Production-grade hybrid search pipeline for software codebases."""

    def __init__(
        self,
        vector_engine: Optional[VectorSearchEngine] = None,
        bm25_engine: Optional[BM25SearchEngine] = None,
        reranker: Optional[CrossEncoderReranker] = None,
    ):
        self.vector_engine = vector_engine or VectorSearchEngine()
        self.bm25_engine = bm25_engine or BM25SearchEngine()
        self.reranker = reranker or CrossEncoderReranker()

    def index_chunks(self, chunks: List[CodeChunk]):
        """Index code chunks into both Vector Store and BM25 Index."""
        self.vector_engine.index_chunks(chunks)
        self.bm25_engine.index_chunks(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 20,
        mode: str = "hybrid_rerank",
        filter_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform search over code base supporting multiple strategies.

        Modes:
            - vector_only: Semantic dense search only
            - bm25_only: Exact keyword search only
            - hybrid_rrf: Vector + BM25 combined via Reciprocal Rank Fusion
            - hybrid_rerank: Vector + BM25 RRF candidates reranked by CrossEncoder
        """
        if mode == "vector_only":
            return self.vector_engine.search(query, top_k=top_k, filter_file=filter_file)

        if mode == "bm25_only":
            return self.bm25_engine.search(query, top_k=top_k)

        # Retrieve candidates from both sources for hybrid modes
        vec_candidates = self.vector_engine.search(query, top_k=candidate_k, filter_file=filter_file)
        bm25_candidates = self.bm25_engine.search(query, top_k=candidate_k)

        # Fuse candidates using Reciprocal Rank Fusion
        fused_candidates = ReciprocalRankFusion.fuse(
            results_list=[vec_candidates, bm25_candidates],
            k=60,
            top_k=candidate_k,
        )

        if mode == "hybrid_rrf":
            return fused_candidates[:top_k]

        # Mode: hybrid_rerank (Default production mode)
        final_reranked = self.reranker.rerank(
            query=query,
            candidates=fused_candidates,
            top_k=top_k,
        )
        return final_reranked
