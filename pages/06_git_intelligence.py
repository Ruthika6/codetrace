"""Git Intelligence page for CODETRACE."""

import streamlit as st
from codetrace.git.repository_history import GitRepositoryHistory

st.set_page_config(page_title="Git Intelligence | CODETRACE", page_icon="📜", layout="wide")

st.title("📜 Git Intelligence & Regression History")

st.markdown("Inspect recent commits, author timelines, and code diff changes.")

history = GitRepositoryHistory(".")
commits = history.get_recent_commits(max_count=5)

for c in commits:
    with st.expander(f"Commit {c.short_hash} — {c.message}"):
        st.markdown(f"**Author**: {c.author_name} ({c.author_email})")
        st.markdown(f"**Timestamp**: {c.timestamp}")
        st.markdown(f"**Changed Files**: `{', '.join(c.changed_files)}`")
