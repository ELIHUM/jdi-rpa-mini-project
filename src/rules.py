# src/rules.py

from __future__ import annotations

CATEGORY_KEYWORDS = {
    "IT": [
        "vpn", "password", "account", "printer", "install", "software",
        "laptop", "wifi", "network", "reset", "login", "uipath"
    ],
    "HR": [
        "onboarding", "vacation", "payroll", "benefits", "employee",
        "hiring", "recruit", "leave"
    ],
    "Finance": [
        "invoice", "reimbursement", "tax", "po", "purchase order",
        "payment", "expense", "budget"
    ],
    "Facilities": [
        "badge", "door", "office", "access card", "building",
        "entrance", "maintenance"
    ],
}

def classify_rule_based(subject: str, description: str) -> tuple[str, str]:
    """
    Returns (category, matched_keyword)
    Simple keyword matching on subject + description.
    """
    text = f"{subject} {description}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category, kw

    return "Other", ""
