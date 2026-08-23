from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleBig", fontSize=22, leading=26, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="SubTitle", fontSize=11, leading=15, textColor=colors.HexColor("#555555"), spaceAfter=18))
styles.add(ParagraphStyle(name="SectionHeading", fontSize=14, leading=18, spaceBefore=4, spaceAfter=8, textColor=colors.white, backColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold", leftIndent=6, borderPadding=(6, 6, 6, 6)))
styles.add(ParagraphStyle(name="OppNum", fontSize=10, leading=12, textColor=colors.HexColor("#c0392b"), fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="Label", fontSize=9, leading=12, fontName="Helvetica-Bold", textColor=colors.HexColor("#1a1a2e")))
styles.add(ParagraphStyle(name="Body", fontSize=9.5, leading=13, fontName="Helvetica", textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="Intro", fontSize=10, leading=15, textColor=colors.HexColor("#222222"), spaceAfter=10))

doc = SimpleDocTemplate(
    "AI_Opportunity_Roadmap.pdf",
    pagesize=A4,
    topMargin=18 * mm,
    bottomMargin=16 * mm,
    leftMargin=16 * mm,
    rightMargin=16 * mm,
    title="Neeman's AI Opportunity Roadmap",
)

story = []
story.append(Paragraph("AI Opportunity Roadmap", styles["TitleBig"]))
story.append(Paragraph("Neeman's — Prioritized 90-day-to-12-month view · Prepared by Mehar, AI Intern Assignment (Part 3)", styles["SubTitle"]))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd"), spaceAfter=10))

story.append(Paragraph(
    "If I joined Neeman's tomorrow, these are the 10 AI opportunities I'd prioritize, ordered "
    "roughly by a combination of impact, ease of implementation, and how directly they touch "
    "revenue or cost. The first two are the tools prototyped in Parts 1 &amp; 2 of this assignment "
    "and are listed here in their fuller, production-scale form.",
    styles["Intro"]
))

opportunities = [
    {
        "title": "1. Customer Feedback &amp; Review Intelligence",
        "problem": "Reviews across the website, marketplaces, and support tickets are read manually or not at all, so recurring product/sizing/delivery complaints surface late, after they've already hurt ratings and repeat purchase.",
        "solution": "LLM pipeline that ingests reviews + order data daily, classifies sentiment and issue themes (sizing, quality, delivery, support), and pushes a weekly digest with prioritized, owner-tagged recommendations to Product/Ops/Support Slack channels.",
        "impact": "Faster detection of quality/sizing issues before they scale; directly supports return-rate reduction and rating improvement across Shopify + marketplaces.",
        "hours": "6-8 hrs/week (manual review reading + report compilation)",
        "stack": "Claude/GPT API, Shopify + marketplace review APIs, Airflow/cron for scheduling, Slack webhook",
    },
    {
        "title": "2. Root Cause Analysis (RCA) Agent",
        "problem": "When a KPI moves (sales dip in a SKU/city, conversion drop), diagnosing why means manually cross-referencing sales, marketing, inventory, and ops spreadsheets — slow and reactive.",
        "solution": "An agent with tool access to the sales/marketing/inventory/ops data warehouse that autonomously investigates anomalies on-demand or on a schedule, and outputs a root-cause report with recommended corrective actions.",
        "impact": "Cuts time-to-diagnosis from days to minutes; enables corrective action (restock, budget reallocation) while the issue is still small.",
        "hours": "5-7 hrs/week (analyst time spent manually cross-referencing dashboards)",
        "stack": "Claude/GPT tool use (function calling), warehouse (BigQuery/Postgres), LangGraph optional for more complex flows",
    },
    {
        "title": "3. AI Customer Support Copilot",
        "problem": "Support team manually triages and drafts replies to a high volume of repetitive queries (order status, return eligibility, sizing questions), slowing first-response time.",
        "solution": "Copilot that reads incoming tickets/WhatsApp messages, classifies intent, drafts a suggested reply grounded in order data and policy docs (RAG), and auto-resolves simple cases (order status, tracking) with human approval for edge cases.",
        "impact": "Faster first-response time, higher CSAT, frees support agents to focus on complex/escalated cases.",
        "hours": "10-15 hrs/week across the support team",
        "stack": "RAG (Claude/GPT + vector DB e.g. Pinecone/pgvector), Freshdesk/Gorgias or WhatsApp Business API integration",
    },
    {
        "title": "4. Inventory &amp; Demand Forecasting Agent",
        "problem": "Stockouts on fast-moving SKUs and overstock on slow movers both hurt margin — current replenishment decisions are largely manual/reactive.",
        "solution": "Agent that combines sales velocity, seasonality, and marketing calendar to forecast demand per SKU/warehouse and proactively recommend replenishment quantities and stock transfers between warehouses.",
        "impact": "Reduced stockout-driven lost sales and reduced dead stock/markdowns; improves working-capital efficiency.",
        "hours": "8-10 hrs/week (manual replenishment planning)",
        "stack": "Time-series forecasting (Prophet/statsmodels) + LLM for narrative recommendations, WMS/ERP integration",
    },
    {
        "title": "5. Marketplace Performance Copilot",
        "problem": "Pricing, listing quality, and ad spend across Amazon/Flipkart/Myntra are optimized manually per platform, making it hard to spot underperforming listings or pricing gaps quickly.",
        "solution": "Copilot that pulls marketplace sales, pricing, and ad performance data, flags underperforming listings (poor CTR, buy-box loss, pricing gaps vs. competitors), and recommends specific fixes (title/image/price changes).",
        "impact": "Improved marketplace revenue share and ad ROAS; faster reaction to buy-box/pricing issues.",
        "hours": "6-8 hrs/week (manual marketplace dashboard reviews)",
        "stack": "Marketplace seller APIs, LLM for recommendation generation, scheduled reporting dashboard",
    },
    {
        "title": "6. D2C Marketing Campaign Intelligence",
        "problem": "Campaign performance across Meta/Google/influencers is reviewed manually; creative fatigue and underperforming audiences aren't caught quickly enough to reallocate budget.",
        "solution": "Copilot that ingests ad platform data daily, flags creative fatigue and CAC drift per campaign, and recommends budget reallocation with expected impact estimates.",
        "impact": "Improved marketing ROI through faster budget reallocation away from underperforming campaigns.",
        "hours": "5-6 hrs/week (manual ad account reviews)",
        "stack": "Meta/Google Ads APIs, LLM for insight generation, existing BI tool (Looker Studio) for visualization",
    },
    {
        "title": "7. AI Product Content &amp; SEO Generator",
        "problem": "Writing unique, SEO-optimized product descriptions and marketplace listing copy for every SKU/variant is slow and inconsistent across the catalog.",
        "solution": "LLM pipeline that generates on-brand product descriptions, SEO metadata, and marketplace-specific listing copy from structured product attributes, with a human review step before publish.",
        "impact": "Faster time-to-list for new SKUs, more consistent brand voice, improved organic search visibility.",
        "hours": "4-6 hrs/week (content team time on listing copy)",
        "stack": "Claude/GPT API, Shopify/marketplace CMS integration, simple review UI",
    },
    {
        "title": "8. Returns &amp; Exchange Root-Cause Analyzer",
        "problem": "Returns are logged but rarely analyzed systematically for root cause, so recurring sizing/quality issues driving returns aren't fed back to product design quickly.",
        "solution": "Pipeline that classifies return reasons (free-text + dropdown) by SKU/size/batch, correlates with manufacturing batch or size-chart data, and surfaces patterns to product/QA teams.",
        "impact": "Lower return rate over time as sizing/quality issues get caught and fixed at the source; reduced reverse-logistics cost.",
        "hours": "4-5 hrs/week (manual returns log review)",
        "stack": "LLM classification, pandas for batch correlation analysis, dashboard for Product/QA team",
    },
    {
        "title": "9. Competitor Intelligence Agent",
        "problem": "Competitor pricing, assortment, and new launches are tracked ad hoc, if at all, making it hard to react quickly to market moves.",
        "solution": "Agent that periodically scans public competitor sites/marketplaces for pricing, new launches, and promotions, and generates a structured weekly competitive brief.",
        "impact": "Faster, more informed pricing and assortment decisions relative to competitors.",
        "hours": "3-4 hrs/week (manual competitor site checks)",
        "stack": "Web scraping (Playwright/BeautifulSoup) or SERP APIs, LLM for brief generation, scheduled job",
    },
    {
        "title": "10. Daily Business Briefing Agent",
        "problem": "Leadership pieces together business health from multiple dashboards each morning, which is slow and inconsistent across reviewers.",
        "solution": "Agent that consolidates sales, marketing, inventory, and support metrics overnight and generates a concise daily exec briefing highlighting trends, risks, opportunities, and recommended actions.",
        "impact": "Faster, more consistent leadership decision-making; surfaces risks before the weekly review cadence.",
        "hours": "2-3 hrs/week (leadership + analyst time compiling updates)",
        "stack": "Data warehouse, LLM for narrative summary, email/Slack delivery, scheduled job (cron/Airflow)",
    },
]

field_order = [("problem", "Business problem"), ("solution", "Proposed AI solution"), ("impact", "Expected business impact"), ("hours", "Est. hours saved/week"), ("stack", "Suggested tools/stack")]

for i, opp in enumerate(opportunities):
    story.append(Paragraph(opp["title"], styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    for key, label in field_order:
        story.append(Paragraph(f'<font color="#1a1a2e"><b>{label}:</b></font> {opp[key]}', styles["Body"]))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 10))
    if i < len(opportunities) - 1 and (i + 1) % 3 == 0:
        story.append(PageBreak())

story.append(PageBreak())
story.append(Paragraph("Prioritization Summary", styles["TitleBig"]))
story.append(Spacer(1, 8))

table_data = [["#", "Opportunity", "Est. hrs saved/wk", "Impact area"]]
impact_areas = ["CX/Retention", "Ops/Revenue", "Support", "Supply Chain", "Marketplace", "Marketing", "Content", "Product/QA", "Strategy", "Leadership"]
for i, (opp, area) in enumerate(zip(opportunities, impact_areas), start=1):
    clean_title = opp["title"].split(". ", 1)[1].replace("&amp;", "&")
    table_data.append([str(i), clean_title, opp["hours"].split(" hrs")[0] + " hrs", area])

t = Table(table_data, colWidths=[18, 230, 90, 90])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f8")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)

story.append(Spacer(1, 16))
story.append(Paragraph(
    "<b>Suggested sequencing:</b> Opportunities 1-2 are prototyped in this submission and can go from "
    "pilot to production fastest since the data plumbing is simplest (reviews, orders) or already "
    "conceptually scoped (RCA tool access). Opportunities 3-4 (Support Copilot, Demand Forecasting) "
    "have the highest hours-saved potential and should follow once data pipelines from the first two "
    "are proven. Opportunities 5-9 are high-value but depend on marketplace/ad platform API access "
    "being set up. Opportunity 10 is a natural aggregation layer once 1-9 are feeding a shared warehouse.",
    styles["Body"]
))

doc.build(story)
print("PDF generated.")
