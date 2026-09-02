"""Commit regression analyzer for CODETRACE."""

from dataclasses import dataclass
from typing import List, Optional

from codetrace.git.repository_history import CommitInfo, GitRepositoryHistory


@dataclass
class RegressionAnalysis:
    """Analysis report correlating error traces with recent Git commit changes."""

    suspect_commit: Optional[CommitInfo]
    changed_file: str
    diff_summary: str
    confidence: float


class CommitAnalyzer:
    """Correlates failure trace files with recent Git modifications to isolate regressions."""

    def __init__(self, repo_history: GitRepositoryHistory):
        self.repo_history = repo_history

    def analyze_regression(self, failed_file: str) -> RegressionAnalysis:
        """Find the most recent commit modifying `failed_file`."""
        history = self.repo_history.get_file_history(failed_file, max_count=3)

        if not history:
            return RegressionAnalysis(
                suspect_commit=None,
                changed_file=failed_file,
                diff_summary="No commit history found.",
                confidence=0.0,
            )

        suspect = history[0]
        return RegressionAnalysis(
            suspect_commit=suspect,
            changed_file=failed_file,
            diff_summary=f"Commit '{suspect.short_hash}' by {suspect.author_name}: {suspect.message}",
            confidence=0.88,
        )
