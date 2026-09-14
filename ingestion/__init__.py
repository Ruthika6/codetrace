"""Repository and Code Ingestion Pipeline Module."""

from codetrace.ingestion.repository_scanner import RepositoryScanner, FileInfo
from codetrace.ingestion.file_classifier import FileClassifier, FileCategory
from codetrace.ingestion.code_parser import CodeParser, ParsedSymbol
from codetrace.ingestion.chunker import CodeAwareChunker, CodeChunk
from codetrace.ingestion.metadata import MetadataExtractor

__all__ = [
    "RepositoryScanner",
    "FileInfo",
    "FileClassifier",
    "FileCategory",
    "CodeParser",
    "ParsedSymbol",
    "CodeAwareChunker",
    "CodeChunk",
    "MetadataExtractor",
]
