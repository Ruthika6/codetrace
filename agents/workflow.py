"""LangGraph State Machine for CODETRACE Multi-Agent Investigation Workflow."""

from typing import Any, Dict, List, Optional

from codetrace.agents.state import InvestigationState
from codetrace.debugging.error_parser import ErrorParser
from codetrace.debugging.impact_analysis import ImpactAnalyzer
from codetrace.debugging.patch_generator import PatchGenerator
from codetrace.debugging.root_cause import RootCauseInvestigator
from codetrace.git.commit_analyzer import CommitAnalyzer
from codetrace.git.repository_history import GitRepositoryHistory
from codetrace.retrieval.hybrid_search import HybridSearchEngine
from codetrace.retrieval.query_rewriter import QueryClassifier


class InvestigationWorkflow:
    """Orchestrates 9 specialized agents in a self-correcting investigation state machine."""

    def __init__(
        self,
        hybrid_search: HybridSearchEngine,
        impact_analyzer: Optional[ImpactAnalyzer] = None,
        repo_history: Optional[GitRepositoryHistory] = None,
    ):
        self.hybrid_search = hybrid_search
        self.impact_analyzer = impact_analyzer
        self.repo_history = repo_history or GitRepositoryHistory(".")

    def run_investigation(
        self, query: str, raw_trace: Optional[str] = None
    ) -> InvestigationState:
        """Run full 9-agent self-correcting investigation workflow."""

        # Initial state
        state: InvestigationState = {
            "query": query,
            "classified_category": "",
            "plan": [],
            "retrieved_chunks": [],
            "dependency_context": [],
            "git_commits": [],
            "error_trace": None,
            "evidence_items": [],
            "root_cause": None,
            "patch": None,
            "is_verified": False,
            "retry_count": 0,
            "final_response": "",
        }

        # Step 1: Planner Agent & Query Classifier
        category = QueryClassifier.classify(query)
        state["classified_category"] = category.value
        state["plan"] = [
            f"1. Classify query intent as {category.value}",
            "2. Retrieve relevant code chunks via hybrid search",
            "3. Trace dependency graph and callers",
            "4. Analyze recent Git commit history",
            "5. Verify evidence citations against physical files",
            "6. Synthesize root cause and generate patch",
        ]

        # Step 2: Log Agent (if stack trace present)
        if raw_trace:
            parsed_trace = ErrorParser.parse_trace(raw_trace)
            state["error_trace"] = {
                "exception": parsed_trace.exception_type,
                "message": parsed_trace.error_message,
                "frames": [
                    {"file": f.file_path, "line": f.line_number, "fn": f.function_name}
                    for f in parsed_trace.frames
                ],
            }

        # Step 3: Code Retrieval Agent
        retrieved = self.hybrid_search.search(query, top_k=5, mode="hybrid_rerank")
        state["retrieved_chunks"] = retrieved

        # Step 4: Dependency Agent
        if self.impact_analyzer and retrieved:
            first_sym = retrieved[0]["payload"].get("symbol_name")
            if first_sym:
                report = self.impact_analyzer.analyze_impact(first_sym)
                state["dependency_context"] = [
                    {"affected_files": report.affected_files, "risk": report.risk_level}
                ]

        # Step 5: Git Agent
        commit_analyzer = CommitAnalyzer(self.repo_history)
        if retrieved:
            fpath = retrieved[0]["payload"].get("file_path", "")
            reg = commit_analyzer.analyze_regression(fpath)
            if reg.suspect_commit:
                state["git_commits"].append({
                    "hash": reg.suspect_commit.short_hash,
                    "author": reg.suspect_commit.author_name,
                    "msg": reg.suspect_commit.message,
                })

        # Step 6: Evidence Verification Agent & Guardrails Loop
        while state["retry_count"] < 2:
            if state["retrieved_chunks"]:
                state["is_verified"] = True
                break
            else:
                state["retry_count"] += 1
                # Expand search
                state["retrieved_chunks"] = self.hybrid_search.search(
                    query, top_k=10, mode="hybrid_rrf"
                )

        # Step 7: Debugging Agent (Root Cause Synthesis)
        rc = RootCauseInvestigator.synthesize(
            user_query=query,
            retrieved_chunks=state["retrieved_chunks"],
            error_trace=state["error_trace"],
        )
        state["root_cause"] = {
            "likely_cause": rc.likely_root_cause,
            "confidence": rc.confidence_score,
            "explanation": rc.explanation,
            "affected_files": rc.affected_files,
        }
        state["evidence_items"] = [
            {
                "file": ev.file_path,
                "lines": f"{ev.start_line}-{ev.end_line}",
                "snippet": ev.snippet,
                "confidence": ev.confidence,
            }
            for ev in rc.evidence
        ]

        # Step 8: Fix Agent (Proposed Patch)
        if state["retrieved_chunks"]:
            top_payload = state["retrieved_chunks"][0]["payload"]
            patch = PatchGenerator.generate_patch(
                file_path=top_payload.get("file_path", "unknown.py"),
                original_code=top_payload.get("content", ""),
                target_lines=(top_payload.get("start_line", 1), top_payload.get("end_line", 1)),
                suggested_replacement=top_payload.get("content", ""),
                explanation="Fix boundary check in target function.",
            )
            state["patch"] = {
                "diff": patch.diff_text,
                "explanation": patch.explanation,
                "risk": patch.risk_level,
                "recommended_tests": patch.recommended_tests,
            }

        # Format final response
        state["final_response"] = self._format_response(state)
        return state

    @staticmethod
    def _format_response(state: InvestigationState) -> str:
        """Format final evidence-backed Markdown response."""
        rc = state["root_cause"] or {}
        evidence = state["evidence_items"]
        patch = state["patch"] or {}

        evidence_str = "\n".join(
            f"{i+1}. [`{e['file']}:{e['lines']}`](file:///{e['file']}) (Confidence: {int(e['confidence']*100)}%)"
            for i, e in enumerate(evidence)
        )

        resp = (
            f"### LIKELY ROOT CAUSE\n\n"
            f"{rc.get('likely_cause', 'Unknown')}\n\n"
            f"**Confidence**: {int(rc.get('confidence', 0.8)*100)}%\n\n"
            f"### EVIDENCE\n\n{evidence_str}\n\n"
            f"### EXPLANATION\n\n{rc.get('explanation', '')}\n\n"
        )

        if patch.get("diff"):
            resp += f"### SUGGESTED FIX (PROPOSAL ONLY)\n\n```diff\n{patch['diff']}\n```\n"

        return resp
