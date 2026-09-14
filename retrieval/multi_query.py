"""Multi-Query expansion generator for CODETRACE."""

from typing import List


class MultiQueryGenerator:
    """Generates multiple search queries from a single complex request to improve recall."""

    @classmethod
    def generate_queries(cls, original_query: str) -> List[str]:
        """Expand original user query into multiple perspective queries."""
        queries = [original_query]

        q_lower = original_query.lower()

        # Add domain specific variations
        if "401" in q_lower or "unauthorized" in q_lower or "login" in q_lower:
            queries.extend([
                f"{original_query} JWT token authentication validation",
                f"{original_query} authorization header middleware",
                f"{original_query} user login authentication service",
            ])

        elif "order" in q_lower:
            queries.extend([
                f"{original_query} order service controller route",
                f"{original_query} order creation database repository",
            ])

        elif "database" in q_lower or "sql" in q_lower or "query" in q_lower:
            queries.extend([
                f"{original_query} database connection pool session",
                f"{original_query} SQL table schema repository model",
            ])

        else:
            queries.extend([
                f"{original_query} implementation function definition",
                f"{original_query} caller module usage",
            ])

        # Deduplicate preserving order
        seen = set()
        deduped = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                deduped.append(q)

        return deduped[:4]
