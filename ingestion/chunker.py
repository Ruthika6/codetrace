"""Code-aware structural chunking engine for CODETRACE."""

from dataclasses import dataclass, field
import hashlib
from typing import List, Optional

from codetrace.ingestion.code_parser import CodeParser, ParsedSymbol
from codetrace.ingestion.repository_scanner import FileInfo


@dataclass
class CodeChunk:
    """Represents a structural code chunk ready for embedding and vector database indexing."""

    chunk_id: str
    file_path: str
    language: str
    symbol_name: Optional[str]
    symbol_type: str  # function, async_function, class, method, module, text
    start_line: int
    end_line: int
    parent_symbol: Optional[str]
    content: str
    imports: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    chunk_type: str = "symbol"  # symbol, file_module, sliding_window


class CodeAwareChunker:
    """Splits repository files into meaningful code chunks preserving symbol structure."""

    def __init__(self, max_chunk_lines: int = 60, overlap_lines: int = 10):
        self.max_chunk_lines = max_chunk_lines
        self.overlap_lines = overlap_lines

    def chunk_file(self, file_info: FileInfo) -> List[CodeChunk]:
        """Convert a FileInfo object into structural code chunks."""

        if not file_info.content:
            return []

        chunks: List[CodeChunk] = []

        # Parse AST symbols
        symbols = CodeParser.parse_file(file_info.content, file_info.language)

        # Tracks lines covered by AST symbols
        covered_lines = set()

        # 1. Create chunks from AST symbols
        for sym in symbols:
            for l in range(sym.start_line, sym.end_line + 1):
                covered_lines.add(l)

            chunk_id = self._generate_chunk_id(file_info.relative_path, sym.name, sym.start_line, sym.end_line)
            chunk = CodeChunk(
                chunk_id=chunk_id,
                file_path=file_info.relative_path,
                language=file_info.language,
                symbol_name=sym.name,
                symbol_type=sym.symbol_type,
                start_line=sym.start_line,
                end_line=sym.end_line,
                parent_symbol=sym.parent_name,
                content=sym.code_text,
                imports=sym.imports,
                calls=sym.calls,
                docstring=sym.docstring,
                chunk_type="symbol",
            )
            chunks.append(chunk)

        # 2. Process uncovered lines / generic files via sliding window
        lines = file_info.content.splitlines()
        total_lines = len(lines)

        if not symbols:
            # File had no structural AST symbols (e.g. config, docs, top-level scripts)
            chunks.extend(self._sliding_window_chunks(file_info, lines))
        else:
            # Check for large uncovered gaps in code file
            uncovered_range = []
            for line_no in range(1, total_lines + 1):
                if line_no not in covered_lines:
                    uncovered_range.append(line_no)

            if uncovered_range and len(uncovered_range) > 5:
                start_l = uncovered_range[0]
                end_l = uncovered_range[-1]
                gap_text = "\n".join(lines[start_l - 1 : end_l])
                if gap_text.strip():
                    chunk_id = self._generate_chunk_id(file_info.relative_path, "module_top_level", start_l, end_l)
                    chunks.append(
                        CodeChunk(
                            chunk_id=chunk_id,
                            file_path=file_info.relative_path,
                            language=file_info.language,
                            symbol_name="<top_level>",
                            symbol_type="module",
                            start_line=start_l,
                            end_line=end_l,
                            parent_symbol=None,
                            content=gap_text,
                            chunk_type="file_module",
                        )
                    )

        return chunks

    def _sliding_window_chunks(self, file_info: FileInfo, lines: List[str]) -> List[CodeChunk]:
        """Create sliding window chunks for files without structural symbols."""
        chunks: List[CodeChunk] = []
        total_lines = len(lines)
        step = max(1, self.max_chunk_lines - self.overlap_lines)

        for i in range(0, total_lines, step):
            end_idx = min(i + self.max_chunk_lines, total_lines)
            chunk_lines = lines[i:end_idx]
            content_str = "\n".join(chunk_lines)

            if not content_str.strip():
                continue

            start_line = i + 1
            end_line = end_idx
            chunk_id = self._generate_chunk_id(file_info.relative_path, f"chunk_{i}", start_line, end_line)

            chunks.append(
                CodeChunk(
                    chunk_id=chunk_id,
                    file_path=file_info.relative_path,
                    language=file_info.language,
                    symbol_name=None,
                    symbol_type="text" if file_info.category.value in ("documentation", "configuration") else "module",
                    start_line=start_line,
                    end_line=end_line,
                    parent_symbol=None,
                    content=content_str,
                    chunk_type="sliding_window",
                )
            )

        return chunks

    @staticmethod
    def _generate_chunk_id(file_path: str, symbol_name: Optional[str], start_line: int, end_line: int) -> str:
        """Deterministic chunk ID generator."""
        raw = f"{file_path}::{symbol_name or 'block'}::{start_line}-{end_line}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
