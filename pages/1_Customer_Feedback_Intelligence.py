import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
import streamlit as st
from utils.llm import sidebar_llm_config, call_llm_json

st.set_page_config(page_title="Customer Feedback Intelligence", page_icon="💬", layout="wide")
sidebar_llm_config()

st.title("💬 Customer Feedback Intelligence")
st.caption("Customer review telemetry and order cross-referencing pipeline for D2C product & operational intelligence.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ---------------- Load data ----------------
reviews = pd.read_csv(os.path.join(DATA_DIR, "reviews.csv"))
orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
merged = reviews.merge(orders[["order_id", "price_inr", "quantity"]], on="order_id", how="left")

with st.expander("📄 View Raw Telemetry Data"):
    t1, t2 = st.tabs(["Reviews", "Orders"])
    t1.dataframe(reviews, use_container_width=True)
    t2.dataframe(orders, use_container_width=True)

# ---------------- Filters ----------------
col1, col2 = st.columns(2)
product_filter = col1.multiselect("Filter by Product Catalog:", sorted(reviews["product"].unique()))
city_filter = col2.multiselect("Filter by Geographic Market:", sorted(reviews["city"].unique()))

filtered = merged.copy()
if product_filter:
    filtered = filtered[filtered["product"].isin(product_filter)]
if city_filter:
    filtered = filtered[filtered["city"].isin(city_filter)]

# ---------------- Color-Coded KPI Cards ----------------
st.subheader("📊 Performance Telemetry Overview")

if filtered.empty:
    st.warning("⚠️ No customer reviews match the selected product/city filters. Reset filters to view metrics.")
else:
    total_reviews = len(filtered)
    avg_rating = round(filtered["rating"].mean(), 2)
    neg_pct = round((filtered["rating"] <= 2).mean() * 100, 1)
    total_rev = int((filtered["price_inr"] * filtered["quantity"]).sum())

    # Determine KPI color coding thresholds
    if avg_rating >= 4.0:
        rating_color, rating_bg, rating_border = "#047857", "#ecfdf5", "#a7f3d0"
    elif avg_rating >= 3.0:
        rating_color, rating_bg, rating_border = "#b45309", "#fffbeb", "#fde68a"
    else:
        rating_color, rating_bg, rating_border = "#b91c1c", "#fef2f2", "#fecaca"

    if neg_pct <= 15.0:
        neg_color, neg_bg, neg_border = "#047857", "#ecfdf5", "#a7f3d0"
    elif neg_pct <= 30.0:
        neg_color, neg_bg, neg_border = "#b45309", "#fffbeb", "#fde68a"
    else:
        neg_color, neg_bg, neg_border = "#b91c1c", "#fef2f2", "#fecaca"

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; text-align: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">TOTAL REVIEWS</span>
                <div style="font-size: 28px; font-weight: 700; color: #0f172a; margin-top: 4px;">{total_reviews:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f"""
            <div style="background-color: {rating_bg}; border: 1px solid {rating_border}; border-radius: 8px; padding: 16px; text-align: center;">
                <span style="font-size: 13px; font-weight: 600; color: {rating_color};">AVG RATING</span>
                <div style="font-size: 28px; font-weight: 700; color: {rating_color}; margin-top: 4px;">{avg_rating} ★</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f"""
            <div style="background-color: {neg_bg}; border: 1px solid {neg_border}; border-radius: 8px; padding: 16px; text-align: center;">
                <span style="font-size: 13px; font-weight: 600; color: {neg_color};">NEGATIVE REVIEWS (≤2★)</span>
                <div style="font-size: 28px; font-weight: 700; color: {neg_color}; margin-top: 4px;">{neg_pct}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; text-align: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">REVENUE REPRESENTED</span>
                <div style="font-size: 28px; font-weight: 700; color: #0f172a; margin-top: 4px;">₹{total_rev:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- Visualizations ----------------
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Rating Distribution**")
        st.bar_chart(filtered["rating"].value_counts().sort_index())

    with c2:
        st.markdown("**Average Rating by Product**")
        st.bar_chart(filtered.groupby("product")["rating"].mean().sort_values())

    st.markdown("**Weekly Sentiment Trajectory & Review Volume**")
    trend = filtered.copy()
    trend["review_date"] = pd.to_datetime(trend["review_date"])
    weekly_trend = (
        trend.set_index("review_date")
        .resample("W")
        .agg(
            Weekly_Avg_Rating=("rating", "mean"),
            Weekly_Review_Volume=("rating", "count")
        )
    )
    st.line_chart(weekly_trend)

st.divider()

# ---------------- AI Analysis ----------------
st.subheader("🤖 AI Customer Insights Pipeline")
st.caption(
    "Executes structured sentiment extraction and issue theme aggregation across review telemetry."
)

if st.button("Run AI Analysis on Selected Telemetry", type="primary", disabled=filtered.empty):
    sample = filtered.sample(min(40, len(filtered)), random_state=1)
    review_lines = "\n".join(
        f"- [{r.rating}★] ({r.product}, {r.city}): {r.review_text}"
        for r in sample.itertuples()
    )

    system_prompt = (
        "You are a retail customer-insights analyst for a D2C footwear brand. "
        "You read customer reviews and turn them into crisp, actionable business insight. "
        "Always respond with ONLY valid JSON, no markdown fences, no commentary."
    )
    user_prompt = f"""Here are customer reviews (rating out of 5, product, city, text):

{review_lines}

Return JSON with this exact shape:
{{
  "overall_sentiment_summary": "2-3 sentence summary of the overall sentiment picture",
  "recurring_issues": [
    {{"theme": "short theme name", "severity": "high",
      "affected_products": ["product1"], "evidence_count": 5, "description": "1 sentence description"}}
  ],
  "positive_highlights": ["short bullet 1", "short bullet 2"],
  "recommendations": [
    {{"action": "short recommended action", "owner": "Product",
      "expected_impact": "1 sentence", "priority": "high"}}
  ]
}}
Identify at most 5 recurring_issues and 5 recommendations, ranked by importance."""

    with st.spinner("Executing sentiment extraction and issue aggregation..."):
        try:
            result = call_llm_json(system_prompt, user_prompt, max_tokens=4096)
            st.session_state["cfi_result"] = result
        except Exception as e:
            st.error(f"AI Analysis Failed: {e}")

if "cfi_result" in st.session_state:
    result = st.session_state["cfi_result"]

    st.markdown("#### Summary")
    st.write(result.get("overall_sentiment_summary", ""))

    st.markdown("#### 🚩 Recurring Issues Telemetry")
    issues = result.get("recurring_issues", [])
    if issues:
        issues_df = pd.DataFrame(issues)
        
        # Color code severity column
        def highlight_severity(val):
            val_str = str(val).lower()
            if val_str == "high":
                return "background-color: #fee2e2; color: #b91c1c; font-weight: bold;"
            elif val_str == "medium":
                return "background-color: #fef3c7; color: #b45309; font-weight: bold;"
            elif val_str == "low":
                return "background-color: #d1fae5; color: #047857; font-weight: bold;"
            return ""

        if "severity" in issues_df.columns:
            styled_df = issues_df.style.map(highlight_severity, subset=["severity"])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(issues_df, use_container_width=True)
    else:
        st.write("No recurring issues detected.")

    colp, colr = st.columns(2)
    with colp:
        st.markdown("#### ✅ Positive Product Highlights")
        for h in result.get("positive_highlights", []):
            st.markdown(f"- {h}")

    with colr:
        st.markdown("#### 🎯 Prioritized Action Recommendations")
        for rec in result.get("recommendations", []):
            prio = str(rec.get("priority", "low")).lower()
            if prio == "high":
                badge = '<span style="background-color:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:12px;">HIGH PRIORITY</span>'
            elif prio == "medium":
                badge = '<span style="background-color:#fef3c7; color:#b45309; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:12px;">MEDIUM PRIORITY</span>'
            else:
                badge = '<span style="background-color:#d1fae5; color:#047857; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:12px;">LOW PRIORITY</span>'

            st.markdown(
                f"""
                <div style="border-left: 4px solid #3b82f6; background-color: #f8fafc; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="margin-bottom: 4px;">{badge} &nbsp; <b>{rec.get('action')}</b> — <i>{rec.get('owner')}</i></div>
                    <div style="font-size: 13px; color: #475569;">{rec.get('expected_impact')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 📥 Export Deliverable")
    st.download_button(
        "⬇️ Export Insights JSON",
        data=json.dumps(result, indent=2),
        file_name="feedback_intelligence_insights.json",
        mime="application/json",
    )
