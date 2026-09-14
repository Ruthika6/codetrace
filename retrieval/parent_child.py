"""Parent-Child chunk retriever and context expansion resolver."""

from typing import Any, Dict, List, Optional

from codetrace.ingestion.chunker import CodeChunk


class ParentChildRetriever:
    """Resolves small child chunks to parent function/class/module context."""

    @classmethod
    def expand_parent_context(
        cls, candidates: List[Dict[str, Any]], all_chunks: List[CodeChunk]
    ) -> List[Dict[str, Any]]:
        """Expand retrieved child symbol chunks with parent symbol or file module context."""

        chunk_lookup = {c.chunk_id: c for c in all_chunks}
        symbol_parent_map = {}
        for c in all_chunks:
            if c.symbol_name:
                key = (c.file_path, c.symbol_name)
                symbol_parent_map[key] = c

        expanded_candidates = []
        for cand in candidates:
            item = cand.copy()
            payload = item["payload"]
            parent_name = payload.get("parent_symbol")
            file_path = payload.get("file_path")

            parent_content = None
            if parent_name and file_path:
                parent_chunk = symbol_parent_map.get((file_path, parent_name))
                if parent_chunk:
                    parent_content = parent_chunk.content

            payload["parent_context"] = parent_content
            expanded_candidates.append(item)

        return expanded_candidates
