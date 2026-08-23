# Neeman's AI Operations & Customer Intelligence Copilot

**Author:** Mehar Chaudhry  
**Repository:** [meharchaudhry/neemans-ai-assignment](https://github.com/meharchaudhry/neemans-ai-assignment)

A completed AI analytics and autonomous diagnostic platform for D2C footwear operations, implementing **Customer Feedback Intelligence** (Part 1) and **Root Cause Analysis (RCA) Agent** (Part 2).

---

## 1. Problem Statement

D2C footwear brands like Neeman's generate telemetry across fragmented surfaces (reviews, marketplace feedback, sales velocity, ad spend, warehouse inventory, and ops logs). Two core operational challenges addressed by this platform:

1. **Unstructured Customer Feedback**: Customer reviews are fragmented across channels, causing recurring product sizing, quality, and delivery issues to surface late after impacting customer retention.
2. **Slow Root-Cause Identification**: Diagnosing performance anomalies (e.g., SKU sales drops in specific cities) requires manually correlating sales, ad spend, warehouse inventory, and ops events across separate tools.

---

## 2. Solution Overview

| Module | Core Functionality | Deliverable Output |
|---|---|---|
| **Customer Feedback Intelligence** | Aggregates review telemetry with order records, computes rating and sentiment trajectories, and extracts recurring issue themes. | Color-coded KPI dashboard, severity-ranked issue table, and prioritized action recommendations. |
| **Root Cause Analysis (RCA) Agent** | Autonomous diagnostic agent with data tools for querying sales, marketing spend, warehouse stock, and operational events. | Multi-step telemetry trace, fact-grounded root cause report, and downloadable Markdown deliverable. |

The platform operates on a realistic 12-week D2C footwear catalog dataset (8 SKUs, 8 cities) pre-configured with operational telemetry scenarios, including a multi-factor anomaly in weeks 8–9 (vendor raw-material delay, warehouse stockout, and marketing budget reallocation).

---

## 3. System Architecture

```
neemans-ai-assignment/
├── Home.py                                # Platform landing page & sidebar configuration
├── pages/
│   ├── 1_Customer_Feedback_Intelligence.py # Review telemetry & sentiment analytics
│   └── 2_RCA_Agent.py                     # Autonomous diagnostic agent interface
├── utils/
│   ├── llm.py                             # Multi-provider client wrapper (Gemini, OpenAI, Anthropic)
│   ├── agent_tools.py                     # Structured telemetry querying interfaces
│   └── rca_agent.py                       # Fact-grounded agent loop & guardrail engine
├── data/                                  # Pre-seeded CSV telemetry datasets
├── generate_data.py                       # Telemetry dataset generation script
├── build_roadmap_pdf.py                   # AI Opportunity Roadmap PDF generator
└── requirements.txt                       # Python dependencies
```

---

## 4. AI Models & System Stack

- **Google Gemini 2.5 Flash** (default provider) / **OpenAI GPT-4o-mini** / **Claude 3.5 Sonnet** — Multi-provider support configured via runtime sidebar.
- **`json-repair`** — Fault-tolerant JSON recovery for structured outputs.
- **Streamlit** — Web application framework.
- **pandas** — High-performance metric computation and data wrangling.

---

## 5. Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/meharchaudhry/neemans-ai-assignment.git
cd neemans-ai-assignment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the application:
```bash
python3 -m streamlit run Home.py
```

4. Regenerate synthetic telemetry data (optional):
```bash
python3 generate_data.py
```

5. Build the AI Opportunity Roadmap PDF (optional):
```bash
python3 build_roadmap_pdf.py
```

---

## 6. System Design Assumptions

- Telemetry schemas follow standard e-commerce and D2C warehouse structures (order IDs, SKU variants, weekly closing inventory, ad impressions).
- Multi-provider compatibility allows runtime execution using Google Gemini, OpenAI, or Anthropic API credentials without hardcoded keys.
- Agent guardrails enforce numeric fact grounding against tool execution outputs and short-circuit duplicate tool calls.
