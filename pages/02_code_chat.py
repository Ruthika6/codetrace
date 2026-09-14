"""Code Chat page for CODETRACE."""

import streamlit as st
from codetrace.retrieval.hybrid_search import HybridSearchEngine
from codetrace.agents.workflow import InvestigationWorkflow
from codetrace.ingestion.repository_scanner import RepositoryScanner
from codetrace.ingestion.chunker import CodeAwareChunker

st.set_page_config(page_title="Code Chat | CODETRACE", page_icon="💬", layout="wide")

st.title("💬 Evidence-Backed Code Chat")

# Initialize engine in session state
if "workflow" not in st.session_state:
    scanner = RepositoryScanner(".")
    files = scanner.scan(include_content=True)
    chunker = CodeAwareChunker()
    chunks = []
    for f in files:
        chunks.extend(chunker.chunk_file(f))

    engine = HybridSearchEngine()
    engine.index_chunks(chunks)
    st.session_state.workflow = InvestigationWorkflow(hybrid_search=engine)
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask a question about this repository (e.g. 'How does authentication work?')...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Investigating repository, tracing dependencies, and verifying citations..."):
            res_state = st.session_state.workflow.run_investigation(user_query)
            response = res_state["final_response"]
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
