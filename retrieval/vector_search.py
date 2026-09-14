"""Vector search retrieval engine for CODETRACE."""

from typing import Any, Dict, List, Optional

from codetrace.database.qdrant import QdrantVectorStore
from codetrace.embeddings.embedder import SentenceTransformerEmbedder
from codetrace.ingestion.chunker import CodeChunk


class VectorSearchEngine:
    """Provides semantic vector search capabilities over structural code chunks."""

    def __init__(
        self,
        embedder: Optional[SentenceTransformerEmbedder] = None,
        vector_store: Optional[QdrantVectorStore] = None,
    ):
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.vector_store = vector_store or QdrantVectorStore(in_memory=True)

    def index_chunks(self, chunks: List[CodeChunk]):
        """Embed structural code chunks and index into Qdrant vector store."""
        if not chunks:
            return

        texts_to_embed = []
        for chunk in chunks:
            # Construct rich context string for embedding
            context_str = (
                f"File: {chunk.file_path}\n"
                f"Symbol: {chunk.symbol_name or 'block'} ({chunk.symbol_type})\n"
                f"Content:\n{chunk.content}"
            )
            texts_to_embed.append(context_str)

        embeddings = self.embedder.embed_texts(texts_to_embed)
        self.vector_store.upsert_chunks(chunks, embeddings)

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_file: Optional[str] = None,
        filter_symbol_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search top K relevant code chunks using dense semantic vector similarity."""
        query_vector = self.embedder.embed_query(query)
        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            filter_file=filter_file,
            filter_symbol_type=filter_symbol_type,
        )
        return results
