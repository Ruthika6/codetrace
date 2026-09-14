"""File classification engine for CODETRACE."""

from enum import Enum
from pathlib import Path
import re


class FileCategory(str, Enum):
    SOURCE_CODE = "source_code"
    TESTS = "tests"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    DATABASE = "database"
    BUILD = "build"
    DEPENDENCY = "dependency"
    ENVIRONMENT = "environment"
    GENERATED = "generated"
    BINARY = "binary"
    IGNORED = "ignored"


class FileClassifier:
    """Classifies files in a software repository into functional categories."""

    # Default directories to ignore
    DEFAULT_IGNORED_DIRS = {
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "build",
        "dist",
        ".idea",
        ".vscode",
        ".next",
        "coverage",
        ".eggs",
    }

    # Binary file extensions
    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".pdf",
        ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib",
        ".pyc", ".pyo", ".pyd", ".db", ".sqlite", ".sqlite3", ".bin", ".dat",
        ".woof", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4", ".avi",
    }

    # Source code extensions
    SOURCE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c_header",
        ".hpp": "cpp_header",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sql": "sql",
        ".sh": "bash",
        ".bash": "bash",
        ".ps1": "powershell",
    }

    # Configuration extensions
    CONFIG_EXTENSIONS = {
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml", ".properties"
    }

    # Special file mappings
    SPECIAL_FILES = {
        "dockerfile": (FileCategory.BUILD, "docker"),
        "docker-compose.yml": (FileCategory.BUILD, "docker"),
        "docker-compose.yaml": (FileCategory.BUILD, "docker"),
        "makefile": (FileCategory.BUILD, "make"),
        "cmake-lists.txt": (FileCategory.BUILD, "cmake"),
        "package.json": (FileCategory.DEPENDENCY, "npm"),
        "package-lock.json": (FileCategory.DEPENDENCY, "npm"),
        "requirements.txt": (FileCategory.DEPENDENCY, "pip"),
        "pipfile": (FileCategory.DEPENDENCY, "pipenv"),
        "poetry.lock": (FileCategory.DEPENDENCY, "poetry"),
        "pyproject.toml": (FileCategory.CONFIGURATION, "python_config"),
        ".env": (FileCategory.ENVIRONMENT, "env"),
        ".env.example": (FileCategory.ENVIRONMENT, "env"),
        ".gitignore": (FileCategory.CONFIGURATION, "git"),
    }

    @classmethod
    def classify(cls, relative_path: str) -> tuple[FileCategory, str]:
        """Classify a relative file path into a category and language tag.

        Returns:
            tuple[FileCategory, str]: (Category, language_or_type_string)
        """
        path = Path(relative_path)
        parts = [p.lower() for p in path.parts]
        file_name = path.name.lower()
        ext = path.suffix.lower()

        # Check ignored directories
        for part in parts[:-1]:
            if part in cls.DEFAULT_IGNORED_DIRS or part.startswith("."):
                return FileCategory.IGNORED, "none"

        # Check special filenames
        if file_name in cls.SPECIAL_FILES:
            return cls.SPECIAL_FILES[file_name]

        # Check binary extensions
        if ext in cls.BINARY_EXTENSIONS:
            return FileCategory.BINARY, "binary"

        # Check test directories or test naming patterns
        is_test_path = any(
            p in ("test", "tests", "spec", "__tests__") for p in parts
        )
        is_test_file = (
            file_name.startswith("test_")
            or file_name.endswith("_test.py")
            or file_name.endswith(".test.js")
            or file_name.endswith(".spec.js")
            or file_name.endswith(".test.ts")
            or file_name.endswith(".spec.ts")
        )
        if is_test_path or is_test_file:
            lang = cls.SOURCE_EXTENSIONS.get(ext, "text")
            return FileCategory.TESTS, lang

        # Check documentation
        if ext in (".md", ".rst", ".txt", ".adoc") or "docs" in parts:
            return FileCategory.DOCUMENTATION, "markdown" if ext == ".md" else "text"

        # Check database / SQL
        if ext == ".sql" or "migrations" in parts:
            return FileCategory.DATABASE, "sql"

        # Check source code
        if ext in cls.SOURCE_EXTENSIONS:
            return FileCategory.SOURCE_CODE, cls.SOURCE_EXTENSIONS[ext]

        # Check configuration
        if ext in cls.CONFIG_EXTENSIONS:
            return FileCategory.CONFIGURATION, ext.lstrip(".")

        return FileCategory.SOURCE_CODE if ext else FileCategory.DOCUMENTATION, "text"
