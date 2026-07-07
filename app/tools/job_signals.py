from __future__ import annotations


ROLE_KEYWORDS = {
    "Business Analyst": ["business analyst", "requirements", "stakeholder", "process"],
    "Data Analyst": ["data analyst", "sql", "analysis", "analytics"],
    "Business Intelligence Analyst": ["business intelligence", "bi analyst", "dashboard", "reporting"],
    "Product Analyst": ["product analyst", "experiment", "feature", "user behavior"],
    "Operations Analyst": ["operations", "process improvement", "workflow", "supply"],
    "Strategy / Consulting": ["strategy", "consulting", "market entry", "profitability"],
    "Marketing / Growth Analytics": ["growth", "marketing", "campaign", "conversion"],
    "Finance / FinTech": ["finance", "fintech", "credit", "risk", "banking"],
    "AI / Data Product": ["ai", "machine learning", "model", "automation", "data product"],
}

TOOLS = [
    "sql",
    "python",
    "tableau",
    "power bi",
    "excel",
    "looker",
    "salesforce",
    "snowflake",
    "dbt",
    "bigquery",
]

RESPONSIBILITY_SIGNALS = [
    "dashboard",
    "reporting",
    "stakeholder",
    "kpi",
    "forecast",
    "automation",
    "process improvement",
    "data quality",
    "recommendation",
    "insights",
    "business case",
    "analytics case",
    "experimentation",
    "pricing",
    "segmentation",
    "customer journey",
]


def classify_role_family(job_description: str) -> str:
    jd = job_description.lower()
    best_role = "General Business / Analytics"
    best_score = 0

    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in jd)
        if score > best_score:
            best_role = role
            best_score = score

    return best_role


def extract_job_signals(job_description: str) -> dict:
    """Extract deterministic role signals from a job description."""
    jd = job_description.lower()
    tools = [tool for tool in TOOLS if tool in jd]
    responsibilities = [signal for signal in RESPONSIBILITY_SIGNALS if signal in jd]

    return {
        "role_family": classify_role_family(job_description),
        "tools": tools,
        "responsibilities": responsibilities,
    }
