"""BM25 Sparse Keyword Search Engine for CODETRACE."""

import re
from typing import Any, Dict, List, Optional

try:
    from rank_bm25 import BM25Okapi
    RANK_BM25_AVAILABLE = True
except ImportError:
    RANK_BM25_AVAILABLE = False

from codetrace.ingestion.chunker import CodeChunk


class CodeTokenizer:
    """Tokenizer tailored for source code, splitting camelCase, snake_case, and symbols."""

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """Tokenize source code or query string."""
        if not text:
            return []

        # Split camelCase
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
        # Replace non-alphanumeric and underscores with space
        text = re.sub(r"[^\w\s]|_", " ", text)
        # Convert to lowercase and split by whitespace
        tokens = [t.lower() for t in text.split() if len(t) > 1]
        return tokens


class BM25SearchEngine:
    """BM25 Sparse Keyword Retrieval Engine for exact code symbol and variable search."""

    def __init__(self):
        self.chunks: List[CodeChunk] = []
        self.corpus_tokens: List[List[str]] = []
        self.bm25: Optional[Any] = None

    def index_chunks(self, chunks: List[CodeChunk]):
        """Build BM25 index over code chunks."""
        self.chunks = chunks
        self.corpus_tokens = []

        for chunk in chunks:
            raw_text = (
                f"{chunk.file_path} {chunk.symbol_name or ''} "
                f"{chunk.symbol_type} {chunk.content}"
            )
            tokens = CodeTokenizer.tokenize(raw_text)
            self.corpus_tokens.append(tokens)

        if RANK_BM25_AVAILABLE and self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search top K chunks matching exact keywords using BM25 scoring."""
        if not self.chunks:
            return []

        query_tokens = CodeTokenizer.tokenize(query)
        if not query_tokens:
            return []

        if RANK_BM25_AVAILABLE and self.bm25:
            scores = self.bm25.get_scores(query_tokens)
        else:
            # Fallback simple TF keyword match
            scores = []
            for doc_tokens in self.corpus_tokens:
                score = sum(doc_tokens.count(qt) for qt in query_tokens)
                scores.append(float(score))

        # Pair scores with chunks
        results = []
        for idx, score in enumerate(scores):
            if score > 0:
                chunk = self.chunks[idx]
                results.append({
                    "score": float(score),
                    "payload": {
                        "chunk_id": chunk.chunk_id,
                        "file_path": chunk.file_path,
                        "language": chunk.language,
                        "symbol_name": chunk.symbol_name,
                        "symbol_type": chunk.symbol_type,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "parent_symbol": chunk.parent_symbol,
                        "content": chunk.content,
                    }
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
