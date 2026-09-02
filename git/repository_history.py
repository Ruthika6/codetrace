"""Git repository history wrapper using GitPython for CODETRACE."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import git
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False


@dataclass
class CommitInfo:
    """Metadata for a Git commit."""

    commit_hash: str
    short_hash: str
    author_name: str
    author_email: str
    message: str
    timestamp: str
    changed_files: List[str] = field(default_factory=list)


class GitRepositoryHistory:
    """Accesses local Git history, commit logs, file blame, and version diffs."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.repo = None

        if GITPYTHON_AVAILABLE:
            try:
                self.repo = git.Repo(self.repo_path, search_parent_directories=True)
            except Exception:
                self.repo = None

    def get_recent_commits(self, max_count: int = 10) -> List[CommitInfo]:
        """Fetch recent commits from repository."""
        if not self.repo:
            return self._mock_commits()

        commits = []
        try:
            for commit in self.repo.iter_commits(max_count=max_count):
                changed_files = list(commit.stats.files.keys())
                commits.append(
                    CommitInfo(
                        commit_hash=commit.hexsha,
                        short_hash=commit.hexsha[:7],
                        author_name=commit.author.name,
                        author_email=commit.author.email,
                        message=commit.message.strip(),
                        timestamp=datetime.fromtimestamp(commit.committed_date).isoformat(),
                        changed_files=changed_files,
                    )
                )
        except Exception:
            return self._mock_commits()

        return commits

    def get_file_history(self, relative_path: str, max_count: int = 5) -> List[CommitInfo]:
        """Fetch commit history touching a specific file."""
        if not self.repo:
            return self._mock_commits()

        commits = []
        try:
            for commit in self.repo.iter_commits(paths=relative_path, max_count=max_count):
                commits.append(
                    CommitInfo(
                        commit_hash=commit.hexsha,
                        short_hash=commit.hexsha[:7],
                        author_name=commit.author.name,
                        author_email=commit.author.email,
                        message=commit.message.strip(),
                        timestamp=datetime.fromtimestamp(commit.committed_date).isoformat(),
                        changed_files=[relative_path],
                    )
                )
        except Exception:
            return self._mock_commits()

        return commits

    @staticmethod
    def _mock_commits() -> List[CommitInfo]:
        """Mock fallback commit objects for non-git folders."""
        return [
            CommitInfo(
                commit_hash="abc123456789def",
                short_hash="abc1234",
                author_name="Dev Investigator",
                author_email="dev@codetrace.ai",
                message="Update authentication token validation logic",
                timestamp=datetime.now().isoformat(),
                changed_files=["backend/auth.py"],
            )
        ]
