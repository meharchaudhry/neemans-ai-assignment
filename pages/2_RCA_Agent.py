import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from utils.llm import sidebar_llm_config, get_provider_and_key
from utils.rca_agent import run_agent
from utils.agent_tools import list_products

st.set_page_config(page_title="RCA Agent", page_icon="🕵️", layout="wide")
sidebar_llm_config()

st.title("🕵️ Root Cause Analysis (RCA) Agent")
st.caption(
    "Autonomous Root Cause Analysis agent. Investigates business performance anomalies "
    "by querying sales, marketing, inventory, and operations telemetry to generate grounded reports."
)

with st.expander("ℹ️ Telemetry Scenario & Ground Truth Benchmark"):
    st.markdown(
        """
The telemetry dataset covers 12 weeks of sales, marketing spend, warehouse inventory, and ops events 
for Neeman's footwear catalog. A performance dip is present in **weeks 8–9** for **Cloud Sneaker - Grey** 
in **Delhi and Mumbai**, caused by a vendor raw-material shipment delay leading to a warehouse stockout 
alongside a concurrent marketing budget reallocation. The agent queries data tools dynamically to isolate these root causes.
"""
    )

products = list_products()
default_q = (
    "Sales dropped sharply in recent weeks. Investigate why and tell me the root cause(s) "
    "and what we should do about it."
)
question = st.text_area("Investigation Prompt:", value=default_q, height=80)

scope = st.selectbox("Scope Investigation to Specific Product (Optional):", ["(All Catalog Products)"] + products)
target_question = question
if scope != "(All Catalog Products)":
    target_question += f" Focus specifically on: {scope}."

run = st.button("🔍 Run Investigation", type="primary")

if run:
    provider, key = get_provider_and_key()
    if not key:
        st.error("Please configure your API key in the sidebar before running the agent.")
    else:
        trace = []
        log_container = st.container()
        log_container.markdown("#### 🔧 Agent Execution Trace (Live)")
        step_placeholder = log_container.empty()

        def log_callback(kind, payload):
            if kind == "thought":
                trace.append(f"**💭 Reasoning:** {payload}")
            elif kind == "tool_call":
                note = payload.get("note", "")
                trace.append(
                    f"**🔧 Called `{payload['name']}`** with `{payload['input']}` {note}\n\n"
                    f"→ Result: `{str(payload['result'])[:500]}{'...' if len(str(payload['result'])) > 500 else ''}`"
                )
            step_placeholder.markdown("\n\n---\n\n".join(trace))

        with st.spinner("Executing agent investigation (fetching telemetry, reasoning, correlating signals)..."):
            try:
                final_report = run_agent(provider, key, target_question, log_callback=log_callback)
                st.session_state["rca_report"] = final_report
                st.session_state["rca_trace"] = trace
            except Exception as e:
                st.error(f"Agent execution failed: {e}")

# Render trace and report persistently across all Streamlit user interactions
if "rca_trace" in st.session_state and st.session_state["rca_trace"]:
    with st.expander("🔧 View Agent Execution Trace & Telemetry Log", expanded=False):
        st.markdown("\n\n---\n\n".join(st.session_state["rca_trace"]))

if "rca_report" in st.session_state and st.session_state["rca_report"]:
    st.divider()
    st.subheader("📋 Final Root Cause Report")
    
    with st.container(border=True):
        st.markdown(st.session_state["rca_report"])

    st.markdown("### 📥 Export Deliverable")
    st.download_button(
        "⬇️ Download Root Cause Report (.md)",
        data=st.session_state["rca_report"],
        file_name="rca_report.md",
        mime="text/markdown",
    )
