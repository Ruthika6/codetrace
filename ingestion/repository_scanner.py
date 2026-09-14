"""Repository scanner and file loader for CODETRACE."""

from dataclasses import dataclass, field
import hashlib
import fnmatch
from pathlib import Path
import zipfile
import tempfile
import os
from typing import List, Optional

from codetrace.ingestion.file_classifier import FileClassifier, FileCategory


@dataclass
class FileInfo:
    """Metadata container for a scanned repository file."""

    relative_path: str
    absolute_path: str
    category: FileCategory
    language: str
    file_hash: str
    line_count: int
    size_bytes: int
    content: Optional[str] = None
    is_ignored: bool = False


class RepositoryScanner:
    """Scans local directories, ZIP archives, or git repositories."""

    def __init__(self, target_path: str):
        self.target_path = Path(target_path).resolve()
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None
        self.actual_repo_dir: Path = self.target_path
        self._gitignore_patterns: List[str] = []

    def scan(self, include_content: bool = True) -> List[FileInfo]:
        """Scan repository and return list of FileInfo objects."""

        # Handle ZIP files
        if self.target_path.is_file() and self.target_path.suffix.lower() == ".zip":
            self.temp_dir = tempfile.TemporaryDirectory()
            with zipfile.ZipFile(self.target_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir.name)
            self.actual_repo_dir = Path(self.temp_dir.name)

        if not self.actual_repo_dir.exists() or not self.actual_repo_dir.is_dir():
            raise ValueError(f"Target repository path does not exist or is not a directory: {self.target_path}")

        # Load .gitignore patterns
        self._load_gitignore()

        scanned_files: List[FileInfo] = []

        for root, dirs, files in os.walk(self.actual_repo_dir):
            root_path = Path(root)
            rel_root = root_path.relative_to(self.actual_repo_dir)

            # Filter out ignored directories in place
            dirs[:] = [
                d for d in dirs
                if not self._is_path_ignored(str(rel_root / d), is_dir=True)
            ]

            for file_name in files:
                abs_file_path = root_path / file_name
                rel_file_path = str(abs_file_path.relative_to(self.actual_repo_dir)).replace("\\", "/")

                if self._is_path_ignored(rel_file_path, is_dir=False):
                    continue

                category, language = FileClassifier.classify(rel_file_path)
                if category in (FileCategory.IGNORED, FileCategory.BINARY):
                    continue

                try:
                    size_bytes = abs_file_path.stat().st_size
                    # Skip files larger than 2MB
                    if size_bytes > 2 * 1024 * 1024:
                        continue

                    content: Optional[str] = None
                    line_count = 0
                    file_hash = ""

                    with open(abs_file_path, "rb") as f:
                        raw_bytes = f.read()
                        file_hash = hashlib.sha256(raw_bytes).hexdigest()

                    if include_content:
                        try:
                            content = raw_bytes.decode("utf-8")
                            line_count = len(content.splitlines())
                        except UnicodeDecodeError:
                            # Skip unreadable non-utf8 files
                            continue

                    file_info = FileInfo(
                        relative_path=rel_file_path,
                        absolute_path=str(abs_file_path),
                        category=category,
                        language=language,
                        file_hash=file_hash,
                        line_count=line_count,
                        size_bytes=size_bytes,
                        content=content,
                        is_ignored=False,
                    )
                    scanned_files.append(file_info)

                except Exception:
                    continue

        return scanned_files

    def _load_gitignore(self):
        """Parse .gitignore patterns if available."""
        gitignore_file = self.actual_repo_dir / ".gitignore"
        if gitignore_file.exists() and gitignore_file.is_file():
            try:
                with open(gitignore_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            self._gitignore_patterns.append(line)
            except Exception:
                pass

    def _is_path_ignored(self, relative_path: str, is_dir: bool = False) -> bool:
        """Check if path matches default ignore lists or .gitignore rules."""
        category, _ = FileClassifier.classify(relative_path)
        if category == FileCategory.IGNORED:
            return True

        norm_path = relative_path.replace("\\", "/")
        path_parts = norm_path.split("/")

        # Check default dir exclusions
        for part in path_parts:
            if part in FileClassifier.DEFAULT_IGNORED_DIRS:
                return True

        # Check .gitignore patterns
        for pattern in self._gitignore_patterns:
            clean_pattern = pattern.rstrip("/")
            if fnmatch.fnmatch(norm_path, clean_pattern) or fnmatch.fnmatch(path_parts[-1], clean_pattern):
                return True

        return False

    def cleanup(self):
        """Clean up temporary directories if created."""
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None
