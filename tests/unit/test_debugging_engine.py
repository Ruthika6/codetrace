"""Unit tests for Phase 6: Stack Trace & Root Cause Debugging Engine."""

import pytest
from codetrace.debugging.error_parser import ErrorParser
from codetrace.debugging.root_cause import RootCauseInvestigator
from codetrace.debugging.patch_generator import PatchGenerator


def test_python_traceback_parser():
    raw_tb = '''Traceback (most recent call last):
  File "backend/auth.py", line 42, in authenticate_user
    decoded = jwt.decode(token, secret)
jwt.exceptions.ExpiredSignatureError: Signature has expired
'''

    parsed = ErrorParser.parse_trace(raw_tb)
    assert parsed.exception_type == "jwt.exceptions.ExpiredSignatureError"
    assert "expired" in parsed.error_message.lower()
    assert len(parsed.frames) == 1
    assert parsed.frames[0].file_path == "backend/auth.py"
    assert parsed.frames[0].line_number == 42


def test_root_cause_synthesis():
    cand = {
        "score": 0.85,
        "payload": {
            "file_path": "backend/auth.py",
            "start_line": 40,
            "end_line": 50,
            "symbol_name": "authenticate_user",
            "content": "def authenticate_user(): pass",
        }
    }

    report = RootCauseInvestigator.synthesize(
        user_query="Why is login returning 401?",
        retrieved_chunks=[cand],
    )
    assert report.confidence_score >= 0.8
    assert "backend/auth.py" in report.affected_files
    assert len(report.evidence) >= 1
    assert report.evidence[0].file_path == "backend/auth.py"


def test_patch_generator():
    original = "if token.exp < current_time:"
    patch = PatchGenerator.generate_patch(
        file_path="backend/auth.py",
        original_code=original,
        target_lines=(1, 1),
        suggested_replacement="if token.exp <= current_time:",
        explanation="Fix token expiration boundary check",
    )

    assert "diff --git" in patch.diff_text
    assert "- if token.exp < current_time:" in patch.diff_text
    assert "+ if token.exp <= current_time:" in patch.diff_text
