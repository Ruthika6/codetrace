"""Bug Investigator page for CODETRACE."""

import streamlit as st
from codetrace.retrieval.hybrid_search import HybridSearchEngine
from codetrace.agents.workflow import InvestigationWorkflow
from codetrace.ingestion.repository_scanner import RepositoryScanner
from codetrace.ingestion.chunker import CodeAwareChunker

st.set_page_config(page_title="Bug Investigator | CODETRACE", page_icon="🐛", layout="wide")

st.title("🐛 Bug & Stack Trace Investigator")

st.markdown("Paste an error log, stack trace, or HTTP failure details below to run an automated root cause investigation.")

query_input = st.text_input("Bug / Issue Description", value="Why am I getting a 401 Unauthorized error?")
trace_input = st.text_area(
    "Error Log / Stack Trace (Optional)",
    height=200,
    value='''Traceback (most recent call last):
  File "backend/auth.py", line 42, in authenticate_user
    decoded = jwt.decode(token, secret)
jwt.exceptions.ExpiredSignatureError: Signature has expired''',
)

if st.button("Investigate Root Cause", type="primary"):
    with st.spinner("Analyzing stack trace, searching AST chunks, checking Git history, and generating patch..."):
        scanner = RepositoryScanner(".")
        files = scanner.scan(include_content=True)
        chunker = CodeAwareChunker()
        chunks = []
        for f in files:
            chunks.extend(chunker.chunk_file(f))

        engine = HybridSearchEngine()
        engine.index_chunks(chunks)
        workflow = InvestigationWorkflow(hybrid_search=engine)

        state = workflow.run_investigation(query=query_input, raw_trace=trace_input)

        st.markdown(state["final_response"])
