"""Metadata extraction and summary statistics helper for CODETRACE ingestion."""

from dataclasses import dataclass, field
from typing import Dict, List, Set

from codetrace.ingestion.chunker import CodeChunk
from codetrace.ingestion.repository_scanner import FileInfo


@dataclass
class RepositoryMetadataSummary:
    """Summary statistics for an ingested repository."""

    total_files: int = 0
    total_chunks: int = 0
    total_lines: int = 0
    total_bytes: int = 0
    category_counts: Dict[str, int] = field(default_factory=dict)
    language_counts: Dict[str, int] = field(default_factory=dict)
    symbol_counts: Dict[str, int] = field(default_factory=dict)
    file_import_map: Dict[str, List[str]] = field(default_factory=dict)


class MetadataExtractor:
    """Extracts summary metrics and structural cross-references from repository scans."""

    @classmethod
    def summarize(
        cls, files: List[FileInfo], chunks: List[CodeChunk]
    ) -> RepositoryMetadataSummary:
        """Calculate aggregate metadata statistics across scanned files and chunks."""
        summary = RepositoryMetadataSummary()
        summary.total_files = len(files)
        summary.total_chunks = len(chunks)

        for file_info in files:
            summary.total_lines += file_info.line_count
            summary.total_bytes += file_info.size_bytes

            cat_key = file_info.category.value
            summary.category_counts[cat_key] = summary.category_counts.get(cat_key, 0) + 1

            lang_key = file_info.language
            summary.language_counts[lang_key] = summary.language_counts.get(lang_key, 0) + 1

        for chunk in chunks:
            sym_type = chunk.symbol_type
            summary.symbol_counts[sym_type] = summary.symbol_counts.get(sym_type, 0) + 1

            if chunk.imports:
                existing = summary.file_import_map.get(chunk.file_path, [])
                for imp in chunk.imports:
                    if imp not in existing:
                        existing.append(imp)
                summary.file_import_map[chunk.file_path] = existing

        return summary
