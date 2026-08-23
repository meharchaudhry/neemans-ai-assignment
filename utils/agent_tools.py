"""
Data retrieval interfaces for sales, marketing, inventory, and operations metrics.
Extracts structured metrics from local datasets for agentic root-cause analysis.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

_sales = pd.read_csv(os.path.join(DATA_DIR, "sales.csv"))
_marketing = pd.read_csv(os.path.join(DATA_DIR, "marketing.csv"))
_inventory = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))
_ops = pd.read_csv(os.path.join(DATA_DIR, "ops_events.csv"))

WEEK_ORDER = [f"W{n}" for n in range(1, 13)]


def _normalize_weeks(weeks):
    if isinstance(weeks, str):
        return [weeks]
    if isinstance(weeks, (list, tuple, set)):
        return list(weeks)
    return None


def get_sales_summary(product: str = None, city: str = None, weeks: list = None):
    """Returns weekly units sold and revenue, filtered by product, city, and weeks."""
    df = _sales.copy()
    if product:
        df = df[df["product"] == product]
    if city:
        df = df[df["city"] == city]
    w_list = _normalize_weeks(weeks)
    if w_list:
        df = df[df["week"].isin(w_list)]
    if df.empty:
        return []
    agg = df.groupby("week").agg(units_sold=("units_sold", "sum"), revenue_inr=("revenue_inr", "sum")).reset_index()
    agg["week_rank"] = agg["week"].apply(lambda w: WEEK_ORDER.index(w) if w in WEEK_ORDER else 999)
    return agg.sort_values("week_rank").drop(columns="week_rank").to_dict(orient="records")


def get_marketing_summary(product: str = None, weeks: list = None):
    """Returns weekly ad spend and impressions, filtered by product and weeks."""
    df = _marketing.copy()
    if product:
        df = df[df["product"] == product]
    w_list = _normalize_weeks(weeks)
    if w_list:
        df = df[df["week"].isin(w_list)]
    if df.empty:
        return []
    agg = df.groupby("week").agg(spend_inr=("spend_inr", "sum"), impressions=("impressions", "sum")).reset_index()
    agg["week_rank"] = agg["week"].apply(lambda w: WEEK_ORDER.index(w) if w in WEEK_ORDER else 999)
    return agg.sort_values("week_rank").drop(columns="week_rank").to_dict(orient="records")


def get_inventory_summary(product: str = None, weeks: list = None):
    """Returns weekly closing stock levels by warehouse, filtered by product and weeks."""
    df = _inventory.copy()
    if product:
        df = df[df["product"] == product]
    w_list = _normalize_weeks(weeks)
    if w_list:
        df = df[df["week"].isin(w_list)]
    if df.empty:
        return []
    return df[["week", "product", "warehouse", "closing_stock_units"]].to_dict(orient="records")


def get_ops_events(product: str = None, weeks: list = None):
    """Returns logged operational events including delays, stockouts, and budget changes."""
    df = _ops.copy()
    if product:
        df = df[df["product"] == product]
    w_list = _normalize_weeks(weeks)
    if w_list:
        df = df[df["week"].isin(w_list)]
    if df.empty:
        return []
    return df.to_dict(orient="records")


def list_products():
    """Returns the list of unique active products in the system catalog."""
    return sorted(_sales["product"].unique().tolist())


def find_biggest_wow_change(product: str = None):
    """Calculates the product and week with the largest week-over-week sales drop or variance."""
    df = _sales.copy()
    if product:
        df = df[df["product"] == product]
        agg = df.groupby("week")["units_sold"].sum().reindex(WEEK_ORDER).fillna(0)
        pct_change = agg.pct_change() * 100
        if pct_change.dropna().empty:
            return {"error": "Insufficient sales data to calculate week-over-week variance."}
        biggest_week = pct_change.abs().idxmax()
        prior_idx = WEEK_ORDER.index(biggest_week) - 1
        return {
            "product": product,
            "week": biggest_week,
            "pct_change": round(float(pct_change[biggest_week]), 1),
            "units_that_week": int(agg[biggest_week]),
            "units_prior_week": int(agg[WEEK_ORDER[prior_idx]]) if prior_idx >= 0 else None,
        }

    # Evaluate across all products to pinpoint product-level sales anomalies
    product_changes = []
    for p, group in df.groupby("product"):
        agg = group.groupby("week")["units_sold"].sum().reindex(WEEK_ORDER).fillna(0)
        pct = agg.pct_change() * 100
        if not pct.dropna().empty:
            # Prioritize negative sales drops first
            min_w = pct.idxmin()
            prior_idx = WEEK_ORDER.index(min_w) - 1
            product_changes.append({
                "product": p,
                "week": min_w,
                "pct_change": round(float(pct[min_w]), 1),
                "units_that_week": int(agg[min_w]),
                "units_prior_week": int(agg[WEEK_ORDER[prior_idx]]) if prior_idx >= 0 else None,
            })

    if not product_changes:
        return {"error": "No sales telemetry found."}

    # Return the product with the sharpest negative percentage sales drop
    product_changes.sort(key=lambda x: x["pct_change"])
    return product_changes[0]


TOOL_REGISTRY = {
    "get_sales_summary": get_sales_summary,
    "get_marketing_summary": get_marketing_summary,
    "get_inventory_summary": get_inventory_summary,
    "get_ops_events": get_ops_events,
    "list_products": list_products,
    "find_biggest_wow_change": find_biggest_wow_change,
}

# Anthropic tool-use schema
ANTHROPIC_TOOLS = [
    {
        "name": "list_products",
        "description": "List all products sold, to know valid product names to filter by.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "find_biggest_wow_change",
        "description": "Finds the specific product SKU and week with the largest week-over-week percentage sales drop across the catalog. Call this first to locate anomalies.",
        "input_schema": {
            "type": "object",
            "properties": {"product": {"type": "string", "description": "Optional product name to scope to."}},
        },
    },
    {
        "name": "get_sales_summary",
        "description": "Get weekly units sold and revenue, optionally filtered by product, city, and/or a list of weeks (e.g. ['W7','W8','W9']).",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "city": {"type": "string"},
                "weeks": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "get_marketing_summary",
        "description": "Get weekly ad spend and impressions, optionally filtered by product and/or weeks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "weeks": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "get_inventory_summary",
        "description": "Get weekly closing stock levels by warehouse, optionally filtered by product and/or weeks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "weeks": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "get_ops_events",
        "description": "Get logged operational events such as shipment delays, stockouts, marketing budget reallocations, and support ticket spikes. Optionally filtered by product and/or weeks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "weeks": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
]

# OpenAI function-calling schema
OPENAI_TOOLS = [
    {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}}
    for t in ANTHROPIC_TOOLS
]
