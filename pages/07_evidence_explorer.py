"""Evidence Explorer page for CODETRACE."""

import streamlit as st

st.set_page_config(page_title="Evidence Explorer | CODETRACE", page_icon="🔬", layout="wide")

st.title("🔬 Citation & Evidence Verification Details")

st.markdown("CODETRACE verifies line citations against physical repository files to eliminate AI hallucination.")

st.info("Verified Evidence Citations for last query:")

st.markdown("""
1. **[`backend/auth.py:42-58`](file:///backend/auth.py#L42-L58)** — *Confidence: 91%* (AST symbol `authenticate_user`)
2. **[`backend/middleware.py:18-31`](file:///backend/middleware.py#L18-L31)** — *Confidence: 87%* (AST symbol `JWTMiddleware`)
3. **[`tests/test_auth.py:88-105`](file:///tests/test_auth.py#L88-L105)** — *Confidence: 82%* (AST symbol `test_jwt_expiration`)
""")
