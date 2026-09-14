"""Dashboard page for CODETRACE."""

import streamlit as st
from pathlib import Path
from codetrace.ingestion.repository_scanner import RepositoryScanner
from codetrace.ingestion.chunker import CodeAwareChunker
from codetrace.ingestion.metadata import MetadataExtractor

st.set_page_config(page_title="Dashboard | CODETRACE", page_icon="📁", layout="wide")

st.title("📁 Repository Ingestion & Overview")

st.markdown("Provide a local path or repository directory to analyze.")

repo_input = st.text_input("Local Repository Path", value=".")

if st.button("Ingest Repository", type="primary"):
    with st.spinner("Scanning repository, parsing AST, and creating structural chunks..."):
        try:
            scanner = RepositoryScanner(repo_input)
            files = scanner.scan(include_content=True)

            chunker = CodeAwareChunker()
            chunks = []
            for f in files:
                chunks.extend(chunker.chunk_file(f))

            summary = MetadataExtractor.summarize(files, chunks)

            st.success(f"Successfully ingested repository! Found {summary.total_files} files and {summary.total_chunks} structural chunks.")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Files", summary.total_files)
            c2.metric("Total Chunks", summary.total_chunks)
            c3.metric("Total Lines", summary.total_lines)
            c4.metric("Total Size (KB)", summary.total_bytes // 1024)

            st.divider()

            col_a, col_b = st.columns(2)
            with col_a:
                st.write("### File Taxonomy Breakdown")
                st.json(summary.category_counts)
            with col_b:
                st.write("### Language Breakdown")
                st.json(summary.language_counts)

        except Exception as e:
            st.error(f"Error during ingestion: {e}")
