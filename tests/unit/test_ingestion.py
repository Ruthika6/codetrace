"""Unit tests for Phase 1: Repository Ingestion Engine."""

import os
from pathlib import Path
import tempfile
import pytest

from codetrace.ingestion.file_classifier import FileClassifier, FileCategory
from codetrace.ingestion.code_parser import CodeParser, ParsedSymbol
from codetrace.ingestion.chunker import CodeAwareChunker, CodeChunk
from codetrace.ingestion.repository_scanner import RepositoryScanner, FileInfo
from codetrace.ingestion.metadata import MetadataExtractor


def test_file_classifier():
    cat, lang = FileClassifier.classify("backend/auth.py")
    assert cat == FileCategory.SOURCE_CODE
    assert lang == "python"

    cat, lang = FileClassifier.classify("tests/test_auth.py")
    assert cat == FileCategory.TESTS
    assert lang == "python"

    cat, lang = FileClassifier.classify("docker-compose.yml")
    assert cat == FileCategory.BUILD
    assert lang == "docker"

    cat, lang = FileClassifier.classify(".venv/lib/site.py")
    assert cat == FileCategory.IGNORED


def test_code_parser_python():
    sample_code = '''"""Auth Module Docstring."""

import jwt
from datetime import datetime

class AuthService:
    """Service handling user authentication."""

    def __init__(self, secret: str):
        self.secret = secret

    async def authenticate_user(self, token: str) -> bool:
        """Validate JWT token."""
        decoded = jwt.decode(token, self.secret)
        return bool(decoded)

def health_check():
    return {"status": "ok"}
'''

    symbols = CodeParser.parse_file(sample_code, "python")
    symbol_names = [s.name for s in symbols]
    assert "AuthService" in symbol_names
    assert "authenticate_user" in symbol_names
    assert "health_check" in symbol_names

    auth_sym = next(s for s in symbols if s.name == "authenticate_user")
    assert auth_sym.symbol_type == "async_method"
    assert auth_sym.parent_name == "AuthService"
    assert auth_sym.docstring == "Validate JWT token."
    assert "jwt" in auth_sym.imports


def test_code_parser_generic():
    js_code = """
    function validateSession(sessionId) {
        return true;
    }

    class OrderController {
        constructor() {}
    }
    """
    symbols = CodeParser.parse_file(js_code, "javascript")
    names = [s.name for s in symbols]
    assert "validateSession" in names
    assert "OrderController" in names


def test_code_aware_chunker():
    sample_code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
    file_info = FileInfo(
        relative_path="math_utils.py",
        absolute_path="/tmp/math_utils.py",
        category=FileCategory.SOURCE_CODE,
        language="python",
        file_hash="hash123",
        line_count=8,
        size_bytes=100,
        content=sample_code,
    )

    chunker = CodeAwareChunker()
    chunks = chunker.chunk_file(file_info)

    assert len(chunks) >= 2
    symbols = [c.symbol_name for c in chunks if c.symbol_name]
    assert "add" in symbols
    assert "subtract" in symbols


def test_repository_scanner_and_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create dummy repo files
        (tmp_path / "main.py").write_text("def main(): pass", encoding="utf-8")
        (tmp_path / "README.md").write_text("# Project Readme", encoding="utf-8")
        (tmp_path / "config.json").write_text('{"env": "dev"}', encoding="utf-8")

        scanner = RepositoryScanner(str(tmp_path))
        files = scanner.scan(include_content=True)

        assert len(files) == 3
        paths = [f.relative_path for f in files]
        assert "main.py" in paths
        assert "README.md" in paths
        assert "config.json" in paths

        chunker = CodeAwareChunker()
        all_chunks = []
        for f in files:
            all_chunks.extend(chunker.chunk_file(f))

        summary = MetadataExtractor.summarize(files, all_chunks)
        assert summary.total_files == 3
        assert summary.total_chunks == len(all_chunks)
        assert summary.category_counts.get("source_code") == 1
