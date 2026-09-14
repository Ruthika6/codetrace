"""Dependency Explorer page for CODETRACE."""

import streamlit as st
from codetrace.database.neo4j import Neo4jGraphStore
from codetrace.debugging.impact_analysis import ImpactAnalyzer

st.set_page_config(page_title="Dependency Explorer | CODETRACE", page_icon="🕸️", layout="wide")

st.title("🕸️ Function Call & Import Dependency Explorer")

fn_input = st.text_input("Target Function / Symbol Name", value="authenticate_user")

if st.button("Calculate Blast Radius Impact", type="primary"):
    store = Neo4jGraphStore(use_fallback=True)

    c1_id = "backend/auth.py::authenticate_user"
    c2_id = "backend/routes/login.py::login_endpoint"
    c3_id = "backend/routes/orders.py::create_order"

    store.add_node("Function", c1_id, {"name": "authenticate_user", "file_path": "backend/auth.py"})
    store.add_node("Function", c2_id, {"name": "login_endpoint", "file_path": "backend/routes/login.py"})
    store.add_node("Function", c3_id, {"name": "create_order", "file_path": "backend/routes/orders.py"})

    store.add_relationship(c2_id, c1_id, "CALLS")
    store.add_relationship(c3_id, c1_id, "CALLS")

    analyzer = ImpactAnalyzer(store)
    report = analyzer.analyze_impact(c1_id)

    st.subheader(f"Impact Analysis for `{fn_input}`")
    st.markdown(f"**Risk Level**: `{report.risk_level}`")

    st.write("### Affected Callers")
    st.json(report.affected_functions)

    st.write("### Affected Files")
    st.json(report.affected_files)
