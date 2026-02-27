#!/usr/bin/env python3
"""
Split Month End Ranking CSV by IFM.
Parses IFM-Account - Account Owner from the first column.
Keeps only account rows that have values in the data columns (RV not empty/dash).
"""

import csv
import re
from pathlib import Path
from collections import defaultdict

INPUT_CSV = Path("data/Month End Ranking - January 2026.csv")
OUTPUT_DIR = Path("data/month_end_by_ifm")
OUTPUT_DIR.mkdir(exist_ok=True)


def parse_row_label(label: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse 'IFM-Account - Account Owner' or 'IFM-Account - Location - Owner'.
    Returns (IFM, Account, Account Owner) or (None, None, None) if not parseable.
    """
    label = (label or "").strip()
    if not label or " - " not in label:
        return None, None, None
    # Split on " - " - last part is always the owner
    parts = label.split(" - ")
    owner = parts[-1].strip()
    before_owner = " - ".join(parts[:-1]).strip()
    if not before_owner or "-" not in before_owner:
        return None, None, None
    # First hyphen separates IFM from account (account may contain hyphens)
    ifm, _, account = before_owner.partition("-")
    ifm = ifm.strip()
    account = account.strip()
    if not ifm or not account:
        return None, None, None
    return ifm, account, owner


def has_rv_value(val: str) -> bool:
    """Check if RV column has a meaningful value (not dash/empty)."""
    v = (val or "").strip()
    if not v:
        return False
    # " - " or "-" or similar means no value
    if re.match(r'^[\s\-]+$', v):
        return False
    # Has numeric content (digits, parentheses for negatives, commas)
    return bool(re.search(r'[\d\(\)]', v))


def main():
    with open(INPUT_CSV, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Rows 0-4: title/headers, row 5: column headers ("Row Labels", "Sum of RV", ...)
    header_row = rows[5]
    data_start = 6

    # Build output: ifm -> list of (parsed_row_dict, original_data_cols)
    by_ifm = defaultdict(list)

    for i in range(data_start, len(rows)):
        row = rows[i]
        if not row:
            continue
        row_label = row[0].strip() if row else ""
        rv_val = row[1].strip() if len(row) > 1 else ""

        # Must be account row: contains " - "
        if " - " not in row_label:
            continue
        # Must have RV value
        if not has_rv_value(rv_val):
            continue

        ifm, account, owner = parse_row_label(row_label)
        if not ifm:
            continue

        by_ifm[ifm].append({
            "ifm": ifm,
            "account": account,
            "account_owner": owner,
            "row_label": row_label,
            "data_cols": row[1:],  # all columns after row label
        })

    # Write separate CSVs per IFM
    header_cols = ["IFM", "Account", "Account Owner"] + header_row[1:]
    written = []

    for ifm in sorted(by_ifm.keys()):
        records = by_ifm[ifm]
        out_path = OUTPUT_DIR / f"{ifm}_January_2026.csv"
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(header_cols)
            for r in records:
                w.writerow([r["ifm"], r["account"], r["account_owner"]] + r["data_cols"])
        written.append((ifm, len(records)))

    print(f"Split into {len(written)} IFM files in {OUTPUT_DIR}/")
    for ifm, count in written:
        print(f"  {ifm}: {count} accounts with values")


if __name__ == "__main__":
    main()
