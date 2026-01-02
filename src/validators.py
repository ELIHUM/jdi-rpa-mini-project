# src/validators.py

from __future__ import annotations
import re

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

ALLOWED_PRIORITIES = {"Low", "Medium", "High"}

def validate_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_required_fields(row: dict, required: list[str]) -> list[str]:
    """
    Returns list of missing field names.
    """
    missing = []
    for field in required:
        val = row.get(field, "")
        if val is None or (isinstance(val, str) and val.strip() == ""):
            missing.append(field)
    return missing

def validate_priority(priority: str) -> bool:
    if not isinstance(priority, str):
        return False
    return priority.strip() in ALLOWED_PRIORITIES
