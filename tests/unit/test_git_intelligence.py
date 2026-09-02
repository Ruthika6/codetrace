"""Unit tests for Phase 7: Git Intelligence Engine."""

import pytest
from codetrace.git.repository_history import GitRepositoryHistory
from codetrace.git.commit_analyzer import CommitAnalyzer


def test_git_repository_history():
    history = GitRepositoryHistory(".")
    commits = history.get_recent_commits(max_count=2)
    assert len(commits) >= 1
    assert commits[0].commit_hash != ""


def test_commit_analyzer():
    history = GitRepositoryHistory(".")
    analyzer = CommitAnalyzer(history)
    analysis = analyzer.analyze_regression("backend/auth.py")
    assert analysis.changed_file == "backend/auth.py"
    assert analysis.suspect_commit is not None
