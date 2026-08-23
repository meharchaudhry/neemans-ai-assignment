import streamlit as st
from utils.llm import sidebar_llm_config

st.set_page_config(
    page_title="Neeman's AI Operations Copilot",
    page_icon="🧵",
    layout="wide",
)

sidebar_llm_config()

st.title("🧵 Neeman's AI Operations Copilot")
st.caption("D2C Operations & Customer Intelligence Engine")

st.markdown(
    """
This application integrates AI-driven telemetry analytics and autonomous root-cause investigation modules tailored for Neeman's D2C footwear operational catalog:

### 1. 💬 Customer Feedback Intelligence *(Part 1 — Operational Tool)*
Processes customer review telemetry alongside order records to surface sentiment trajectories, categorize recurring product/delivery/support friction, and generate prioritized action plans.

➡️ Access **"1 Customer Feedback Intelligence"** from the left navigation sidebar.

### 2. 🕵️ Root Cause Analysis (RCA) Agent *(Part 2 — Autonomous Agent)*
An autonomous diagnostic agent that investigates performance variances (such as SKU or city sales drops) by dynamically querying sales, marketing spend, warehouse inventory, and operational event telemetry to deliver grounded root-cause reports.

➡️ Access **"2 RCA Agent"** from the left navigation sidebar.

---

### 🔑 System Quickstart
Provide a Google Gemini, OpenAI, or Anthropic API key in the sidebar configuration. All telemetry datasets are pre-seeded in `/data` for immediate execution.
"""
)

st.info(
    "Architecture overview, data warehouse integration design, and technical specifications "
    "are documented in the project README."
)
