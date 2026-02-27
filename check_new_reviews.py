"""
Check if new reviews were added to performance_reviews.csv correctly.
Compares with source Year-End Review (9).csv and validates structure.
"""
import pandas as pd
from pathlib import Path

def main():
    pr_path = Path("data/performance_reviews.csv")
    source_path = Path("data/Year-End Review_ Account Director Leadership Evaluation(Sheet1) (9).csv")

    print("=" * 60)
    print("PERFORMANCE REVIEWS VALIDATION")
    print("=" * 60)

    # Load performance_reviews
    pr = pd.read_csv(pr_path, low_memory=False)
    print(f"\n1. performance_reviews.csv: {len(pr)} rows")

    # Basic structure checks
    req_cols = ["Id", "Account Name", "Account Director Name", "Key Projects & Initiatives", "Executive Presence & Presentation Skills"]
    missing = [c for c in req_cols if c not in pr.columns]
    if missing:
        print(f"   ISSUE: Missing columns: {missing}")
    else:
        print(f"   OK: All required columns present")

    # Duplicate IDs
    dup_ids = pr["Id"].duplicated().sum()
    if dup_ids:
        print(f"   ISSUE: {dup_ids} duplicate Id(s)")
    else:
        print(f"   OK: No duplicate Ids")

    # Score columns - check for valid 1-5 range
    score_cols = ["Key Projects & Initiatives", "Value Adds & Cost Avoidance", "Cost Savings Delivered",
                  "Innovation & Continuous Improvement", "Issues, Challenges & Accountability",
                  "2026 Forward Strategy & Vision", "Personal Goals & Role Maturity", "Executive Presence & Presentation Skills"]
    for col in score_cols:
        if col not in pr.columns:
            continue
        vals = pd.to_numeric(pr[col], errors="coerce")
        valid = vals.dropna()
        invalid = valid[(valid < 1) | (valid > 5)]
        if len(invalid) > 0:
            print(f"   WARN: {col} has {len(invalid)} score(s) outside 1-5 range")
        else:
            pass  # OK

    # Compare with source if exists
    if source_path.exists():
        src = pd.read_csv(source_path, low_memory=False)
        print(f"\n2. Source (Sheet1) (9).csv: {len(src)} rows")
        pr_ids = set(pr["Id"].astype(str))
        src_ids = set(src["Id"].astype(str))
        in_src_not_pr = src_ids - pr_ids
        in_pr_not_src = pr_ids - src_ids
        if in_src_not_pr:
            print(f"   WARN: {len(in_src_not_pr)} IDs in source but NOT in performance_reviews: {sorted(in_src_not_pr)[:10]}{'...' if len(in_src_not_pr)>10 else ''}")
        else:
            print(f"   OK: All source IDs are in performance_reviews")
        if in_pr_not_src:
            print(f"   INFO: {len(in_pr_not_src)} IDs in performance_reviews but not in source (may be from prior merge)")
    else:
        print(f"\n2. Source (9) not found: {source_path}")

    # Newest entries
    newest = pr.nlargest(5, "Id")[["Id", "Account Name", "Account Director Name", "Name"]]
    print(f"\n3. Newest 5 entries:")
    for _, row in newest.iterrows():
        print(f"   Id {row['Id']}: {row['Account Name'][:30]} | AD: {row['Account Director Name']} | Reviewer: {row['Name']}")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
