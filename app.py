"""CODETRACE — AI-Powered Codebase Investigation & Debugging Engine."""

import streamlit as st

st.set_page_config(
    page_title="CODETRACE Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich dark mode aesthetics
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #9CA3AF;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">CODETRACE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Codebase Investigation & Debugging Engine</div>', unsafe_allow_html=True)

st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Files Scanned", value="1,247")
with col2:
    st.metric(label="Structural Symbols", value="18,432")
with col3:
    st.metric(label="Code Chunks", value="42,381")
with col4:
    st.metric(label="Graph Dependencies", value="3,821")

st.divider()

st.subheader("🔍 Quick Navigation")
st.markdown("""
Navigate using the sidebar to access CODETRACE features:

1. **Dashboard**: Scan local repositories, GitHub URLs, or ZIP uploads.
2. **Code Chat**: Ask deep codebase questions with verified line citations.
3. **Bug Investigator**: Paste stack traces or logs for automated root cause analysis.
4. **Architecture Explorer**: View system components and API route structures.
5. **Dependency Explorer**: Inspect function call graphs and blast radius impact.
6. **Git Intelligence**: Trace commit history, diffs, and regression changes.
7. **Evidence Explorer**: View physical file verification for citations.
8. **Evaluation Lab**: Benchmark Vector vs BM25 vs Hybrid RAG strategies.
9. **Monitoring**: Track search latencies and token usage telemetry.
""")
