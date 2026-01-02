# src/main.py

from __future__ import annotations

import pandas as pd
from pathlib import Path

from rules import classify_rule_based
from validators import validate_email, validate_required_fields, validate_priority
from utils import ensure_dir, now_iso

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "requests.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_XLSX = OUTPUT_DIR / "output_report.xlsx"
LOG_FILE = OUTPUT_DIR / "logs.txt"

REQUIRED_FIELDS = [
    "request_id",
    "created_at",
    "requester_name",
    "requester_email",
    "subject",
    "description",
    "priority",
]

def log_line(line: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main() -> None:
    ensure_dir(OUTPUT_DIR)

    # reset logs
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    processed_rows = []
    issues_rows = []

    log_line(f"[{now_iso()}] START processing {len(df)} requests")

    for _, r in df.iterrows():
        row = r.to_dict()

        # Validation
        missing = validate_required_fields(row, REQUIRED_FIELDS)
        email_ok = validate_email(str(row.get("requester_email", "")))
        priority_ok = validate_priority(str(row.get("priority", "")))

        issues = []
        if missing:
            issues.append(f"Missing fields: {', '.join(missing)}")
        if not email_ok:
            issues.append("Invalid email format")
        if not priority_ok:
            issues.append("Invalid priority (must be Low/Medium/High)")

        # Classification
        subject = str(row.get("subject", ""))
        desc = str(row.get("description", ""))
        category, matched_kw = classify_rule_based(subject, desc)

        # Build processed output row
        out = dict(row)
        out["predicted_category"] = category
        out["matched_keyword"] = matched_kw
        out["has_issues"] = "Yes" if issues else "No"
        out["issues_detail"] = " | ".join(issues)

        processed_rows.append(out)

        if issues:
            issues_rows.append(out)
            log_line(f"[{now_iso()}] ISSUE {row.get('request_id','(no id)')}: {out['issues_detail']}")

    processed_df = pd.DataFrame(processed_rows)
    issues_df = pd.DataFrame(issues_rows)

    # Simple KPIs
    total = len(processed_df)
    with_issues = len(issues_df)
    by_cat = processed_df["predicted_category"].value_counts(dropna=False).reset_index()
    by_cat.columns = ["category", "count"]

    kpi_df = pd.DataFrame([
        {"metric": "total_requests", "value": total},
        {"metric": "requests_with_issues", "value": with_issues},
        {"metric": "requests_ok", "value": total - with_issues},
        {"metric": "issue_rate_percent", "value": round((with_issues / total) * 100, 2) if total else 0},
    ])

    # Export to Excel
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        processed_df.to_excel(writer, index=False, sheet_name="Processed")
        issues_df.to_excel(writer, index=False, sheet_name="Issues")
        by_cat.to_excel(writer, index=False, sheet_name="CategorySummary")
        kpi_df.to_excel(writer, index=False, sheet_name="KPIs")

    log_line(f"[{now_iso()}] DONE. Output: {OUTPUT_XLSX}")
    log_line(f"[{now_iso()}] KPIs: total={total}, issues={with_issues}, ok={total-with_issues}")

    print("✅ Done!")
    print(f"Excel report: {OUTPUT_XLSX}")
    print(f"Logs: {LOG_FILE}")

if __name__ == "__main__":
    main()
