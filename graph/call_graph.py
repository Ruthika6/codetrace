"""Call graph construction module for CODETRACE."""

from typing import List

from codetrace.database.neo4j import Neo4jGraphStore
from codetrace.ingestion.chunker import CodeChunk


class CallGraphBuilder:
    """Extracts function call relationships and builds call trees."""

    def __init__(self, graph_store: Neo4jGraphStore):
        self.graph_store = graph_store

    def build_call_graph(self, chunks: List[CodeChunk]):
        """Connect function caller and callee nodes in the graph store."""

        # Map symbol_name -> list of chunk_ids
        symbol_map = {}
        for chunk in chunks:
            if chunk.symbol_name:
                symbol_map.setdefault(chunk.symbol_name, []).append(chunk)

        for chunk in chunks:
            if not chunk.symbol_name or not chunk.calls:
                continue

            caller_id = f"{chunk.file_path}::{chunk.symbol_name}"

            for called_fn in chunk.calls:
                if called_fn in symbol_map:
                    # Found callee chunk
                    target_chunks = symbol_map[called_fn]
                    for target in target_chunks:
                        callee_id = f"{target.file_path}::{target.symbol_name}"
                        self.graph_store.add_relationship(
                            from_id=caller_id,
                            to_id=callee_id,
                            rel_type="CALLS",
                        )
                else:
                    # Unresolved external function call
                    callee_id = called_fn
                    self.graph_store.add_node(
                        label="Function",
                        node_id=callee_id,
                        properties={"name": called_fn, "file_path": "external"},
                    )
                    self.graph_store.add_relationship(
                        from_id=caller_id,
                        to_id=callee_id,
                        rel_type="CALLS",
                    )
