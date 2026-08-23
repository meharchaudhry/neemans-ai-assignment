"""
Generates dummy data for:
Part 1: Customer Feedback Intelligence (reviews.csv, orders.csv)
Part 2: RCA Agent (sales.csv, marketing.csv, inventory.csv, ops_events.csv)

Neeman's is a D2C footwear brand, so data is themed around that.
"""
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

PRODUCTS = [
    "Cloud Sneaker - Grey", "Cloud Sneaker - Black", "Trail Runner - Olive",
    "Classic Slip-On - White", "Everyday Loafer - Tan", "Recycled Runner - Navy",
    "Wool Blend Sneaker - Charcoal", "Kids Comfort Shoe - Blue"
]
CITIES = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Chennai", "Jaipur", "Ahmedabad"]

# ---------------- Part 1: Customer Feedback Intelligence ----------------

positive_templates = [
    "Super comfortable, wore them all day at work with zero pain.",
    "Great quality for the price, will definitely buy another pair.",
    "Fits true to size and looks even better in person.",
    "Love the sustainable materials, feels good to buy consciously.",
    "Perfect for my daily walks, very lightweight.",
]
negative_size_templates = [
    "Runs really small, had to return and reorder a size up.",
    "Sizing is inconsistent with your last collection, too tight on the sides.",
    "Ordered my usual size but it's way too narrow for my feet.",
]
negative_quality_templates = [
    "Sole started peeling off within three weeks of light use.",
    "Stitching came undone after the first wash.",
    "Color faded badly after just a couple of wears in the sun.",
]
negative_delivery_templates = [
    "Took 12 days to arrive even though the site promised 4-5 days.",
    "Delivery partner delayed twice, no updates on tracking page.",
    "Box arrived damaged and the shoe had a scuff mark already.",
]
negative_cs_templates = [
    "Raised a return request 5 days ago, no response from support yet.",
    "Customer care kept transferring my call, issue still unresolved.",
    "Refund promised in 7 days, it has been 3 weeks now.",
]

review_pool = (
    [(t, "positive") for t in positive_templates] +
    [(t, "negative_size") for t in negative_size_templates] +
    [(t, "negative_quality") for t in negative_quality_templates] +
    [(t, "negative_delivery") for t in negative_delivery_templates] +
    [(t, "negative_cs") for t in negative_cs_templates]
)

reviews = []
orders = []
start_date = datetime(2026, 5, 1)

for i in range(1, 221):
    product = random.choice(PRODUCTS)
    city = random.choice(CITIES)
    order_date = start_date + timedelta(days=random.randint(0, 110))
    review_date = order_date + timedelta(days=random.randint(2, 14))
    text, tag = random.choice(review_pool)

    # weight ratings roughly consistent with sentiment tag
    if tag == "positive":
        rating = random.choice([4, 5, 5])
    elif tag == "negative_quality":
        rating = random.choice([1, 2])
    elif tag == "negative_size":
        rating = random.choice([2, 3])
    elif tag == "negative_delivery":
        rating = random.choice([1, 2, 3])
    else:
        rating = random.choice([1, 2])

    orders.append({
        "order_id": f"ORD{1000+i}",
        "customer_id": f"CUST{500+i}",
        "product": product,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "quantity": random.choice([1, 1, 1, 2]),
        "price_inr": random.choice([1799, 1999, 2299, 2499, 2799]),
        "city": city,
    })

    reviews.append({
        "review_id": f"REV{2000+i}",
        "order_id": f"ORD{1000+i}",
        "customer_id": f"CUST{500+i}",
        "product": product,
        "rating": rating,
        "review_text": text,
        "review_date": review_date.strftime("%Y-%m-%d"),
        "city": city,
    })

pd.DataFrame(orders).to_csv("data/orders.csv", index=False)
pd.DataFrame(reviews).to_csv("data/reviews.csv", index=False)

# ---------------- Part 2: RCA Agent ----------------
# Simulate a 12-week window where sales dip in weeks 8-9 for a specific product/city
# due to a combination of a marketing spend cut AND a stockout/delivery issue.

weeks = [f"W{n}" for n in range(1, 13)]
sales_rows, marketing_rows, inventory_rows, ops_rows = [], [], [], []

base_sales = 1200  # units/week baseline across all products/stores combined

for idx, wk in enumerate(weeks):
    week_start = start_date + timedelta(days=idx * 7)
    dip = idx in (7, 8)  # weeks 8 & 9 (0-indexed 7,8)

    for product in PRODUCTS:
        for city in CITIES:
            noise = random.randint(-6, 6)
            units = max(0, int(base_sales / (len(PRODUCTS) * len(CITIES))) + noise)

            if dip and product == "Cloud Sneaker - Grey":
                # sharpest in Delhi/Mumbai (where the stockout hit), still visible elsewhere
                factor = 0.25 if city in ("Delhi", "Mumbai") else 0.6
                units = int(units * factor)

            sales_rows.append({
                "week": wk,
                "week_start": week_start.strftime("%Y-%m-%d"),
                "product": product,
                "city": city,
                "units_sold": units,
                "revenue_inr": units * random.choice([1799, 1999, 2299]),
            })

    # Marketing spend - cut specifically for Cloud Sneaker - Grey in weeks 8-9
    for product in PRODUCTS:
        spend = random.randint(15000, 30000)
        if dip and product == "Cloud Sneaker - Grey":
            spend = int(spend * 0.2)  # budget reallocated elsewhere
        marketing_rows.append({
            "week": wk,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "product": product,
            "channel": random.choice(["Meta Ads", "Google Ads", "Influencer", "Email"]),
            "spend_inr": spend,
            "impressions": spend * random.randint(8, 12),
        })

    # Inventory levels - stockout for Cloud Sneaker Grey in Delhi warehouse during dip
    for product in PRODUCTS:
        stock = random.randint(200, 800)
        if dip and product == "Cloud Sneaker - Grey":
            stock = random.randint(0, 40)
        inventory_rows.append({
            "week": wk,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "product": product,
            "warehouse": "Delhi-DC1" if product == "Cloud Sneaker - Grey" else random.choice(["Delhi-DC1", "Mumbai-DC2", "Bengaluru-DC3"]),
            "closing_stock_units": stock,
        })

# Ops events log
ops_rows = [
    {"week": "W7", "week_start": (start_date + timedelta(days=6*7)).strftime("%Y-%m-%d"),
     "event": "Cloud Sneaker - Grey: raw material (sole foam) shipment delayed from vendor by 9 days",
     "severity": "high", "product": "Cloud Sneaker - Grey"},
    {"week": "W8", "week_start": (start_date + timedelta(days=7*7)).strftime("%Y-%m-%d"),
     "event": "Delhi-DC1 warehouse stockout on Cloud Sneaker - Grey (all sizes)",
     "severity": "high", "product": "Cloud Sneaker - Grey"},
    {"week": "W8", "week_start": (start_date + timedelta(days=7*7)).strftime("%Y-%m-%d"),
     "event": "Marketing budget for Cloud Sneaker - Grey reallocated to Trail Runner - Olive launch campaign",
     "severity": "medium", "product": "Cloud Sneaker - Grey"},
    {"week": "W9", "week_start": (start_date + timedelta(days=8*7)).strftime("%Y-%m-%d"),
     "event": "Customer support tickets for Cloud Sneaker - Grey delivery delays up 40% week-on-week",
     "severity": "medium", "product": "Cloud Sneaker - Grey"},
    {"week": "W10", "week_start": (start_date + timedelta(days=9*7)).strftime("%Y-%m-%d"),
     "event": "Restock of Cloud Sneaker - Grey completed at Delhi-DC1",
     "severity": "low", "product": "Cloud Sneaker - Grey"},
]

pd.DataFrame(sales_rows).to_csv("data/sales.csv", index=False)
pd.DataFrame(marketing_rows).to_csv("data/marketing.csv", index=False)
pd.DataFrame(inventory_rows).to_csv("data/inventory.csv", index=False)
pd.DataFrame(ops_rows).to_csv("data/ops_events.csv", index=False)

print("Data generated:")
for f in ["orders.csv", "reviews.csv", "sales.csv", "marketing.csv", "inventory.csv", "ops_events.csv"]:
    df = pd.read_csv(f"data/{f}")
    print(f"  data/{f}: {len(df)} rows")
