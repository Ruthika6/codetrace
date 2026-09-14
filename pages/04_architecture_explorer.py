"""Architecture Explorer page for CODETRACE."""

import streamlit as st

st.set_page_config(page_title="Architecture Explorer | CODETRACE", page_icon="🏗️", layout="wide")

st.title("🏗️ System Architecture Explorer")

st.markdown("Visual diagram of repository architecture, API routers, controllers, and services.")

st.code(
    """
[HTTP Client / Frontend]
         │
         ▼
┌─────────────────────────┐
│ FastAPI API Gateway     │
└──────────┬──────────────┘
           │
 ┌─────────┴─────────┐
 ▼                   ▼
┌─────────────────┐ ┌──────────────────┐
│ Auth Controller │ │ Order Controller │
└────────┬────────┘ └────────┬─────────┘
         │                   │
         ▼                   ▼
┌─────────────────┐ ┌──────────────────┐
│ AuthService     │ │ OrderService     │
└────────┬────────┘ └────────┬─────────┘
         │                   │
         └─────────┬─────────┘
                   ▼
       ┌──────────────────────┐
       │ PostgreSQL Database  │
       └──────────────────────┘
""",
    language="text",
)

st.info("Click any component to inspect corresponding source code files and structural line bounds.")
