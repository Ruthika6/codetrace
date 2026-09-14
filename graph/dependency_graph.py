"""Dependency graph construction module for CODETRACE."""

from typing import List

from codetrace.database.neo4j import Neo4jGraphStore
from codetrace.ingestion.chunker import CodeChunk
from codetrace.ingestion.repository_scanner import FileInfo


class DependencyGraphBuilder:
    """Builds file, module, and import dependency relationships in the graph store."""

    def __init__(self, graph_store: Neo4jGraphStore):
        self.graph_store = graph_store

    def build_graph(self, files: List[FileInfo], chunks: List[CodeChunk]):
        """Populate graph nodes and import edges from files and structural chunks."""

        # 1. Create File nodes
        for file_info in files:
            self.graph_store.add_node(
                label="File",
                node_id=file_info.relative_path,
                properties={
                    "name": file_info.relative_path,
                    "file_path": file_info.relative_path,
                    "language": file_info.language,
                    "category": file_info.category.value,
                },
            )

        # 2. Create Symbol nodes and relationships
        for chunk in chunks:
            if not chunk.symbol_name:
                continue

            sym_id = f"{chunk.file_path}::{chunk.symbol_name}"
            label = "Class" if chunk.symbol_type == "class" else "Function"

            self.graph_store.add_node(
                label=label,
                node_id=sym_id,
                properties={
                    "name": chunk.symbol_name,
                    "file_path": chunk.file_path,
                    "symbol_type": chunk.symbol_type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                },
            )

            # File CONTAINS Symbol
            self.graph_store.add_relationship(
                from_id=chunk.file_path,
                to_id=sym_id,
                rel_type="CONTAINS",
            )

            # Class HAS_METHOD Function
            if chunk.parent_symbol:
                parent_id = f"{chunk.file_path}::{chunk.parent_symbol}"
                self.graph_store.add_relationship(
                    from_id=parent_id,
                    to_id=sym_id,
                    rel_type="HAS_METHOD",
                )
