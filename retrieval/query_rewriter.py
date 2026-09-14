"""Query intent classification and contextual query rewriter for CODETRACE."""

from enum import Enum
import re
from typing import List, Optional


class QueryCategory(str, Enum):
    CODE_EXPLANATION = "CODE_EXPLANATION"
    BUG_INVESTIGATION = "BUG_INVESTIGATION"
    ARCHITECTURE = "ARCHITECTURE"
    DEPENDENCY_ANALYSIS = "DEPENDENCY_ANALYSIS"
    API_TRACE = "API_TRACE"
    FUNCTION_SEARCH = "FUNCTION_SEARCH"
    CHANGE_IMPACT = "CHANGE_IMPACT"
    SECURITY = "SECURITY"
    TESTING = "TESTING"
    GIT_HISTORY = "GIT_HISTORY"
    GENERAL_REPOSITORY_QUESTION = "GENERAL_REPOSITORY_QUESTION"


class QueryClassifier:
    """Classifies user queries into investigation intent categories."""

    @classmethod
    def classify(cls, query: str) -> QueryCategory:
        """Classify user query text into a QueryCategory."""
        q_lower = query.lower()

        if any(w in q_lower for w in ["error", "bug", "fail", "401", "500", "null", "exception", "stack trace", "crash", "issue"]):
            return QueryCategory.BUG_INVESTIGATION

        if any(w in q_lower for w in ["trace", "http", "endpoint", "/api/", "route", "handler", "request"]):
            return QueryCategory.API_TRACE

        if any(w in q_lower for w in ["commit", "history", "git", "diff", "author", "recent change", "version", "who changed"]):
            return QueryCategory.GIT_HISTORY

        if any(w in q_lower for w in ["impact", "break", "what happens if"]):
            return QueryCategory.CHANGE_IMPACT

        if any(w in q_lower for w in ["dependency", "call", "caller", "used by", "import", "hierarchy"]):
            return QueryCategory.DEPENDENCY_ANALYSIS

        if any(w in q_lower for w in ["security", "vulnerability", "secret", "sqli", "auth", "token", "password"]):
            return QueryCategory.SECURITY

        if any(w in q_lower for w in ["test", "unittest", "pytest", "spec", "coverage"]):
            return QueryCategory.TESTING

        if any(w in q_lower for w in ["explain", "overview", "how does", "what is"]):
            return QueryCategory.CODE_EXPLANATION

        return QueryCategory.GENERAL_REPOSITORY_QUESTION


class QueryRewriter:
    """Rewrites conversational queries into standalone code search queries."""

    @classmethod
    def rewrite(cls, current_query: str, chat_history: Optional[List[dict]] = None) -> str:
        """Rewrite ambiguous query (e.g. 'Why does it fail?') using chat history."""
        if not chat_history:
            return current_query

        # Look for pronouns or references
        pronouns = ["it", "this", "that", "the function", "the endpoint", "the error"]

        if any(p in current_query.lower() for p in pronouns):
            # Extract last user query topic
            for msg in reversed(chat_history):
                if msg.get("role") == "user":
                    last_text = msg.get("content", "")
                    if last_text and last_text != current_query:
                        return f"{last_text} - {current_query}"

        return current_query
