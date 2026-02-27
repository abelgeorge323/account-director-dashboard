#!/usr/bin/env python3
"""
Generate IFM -> Accounts list for emailing IFM leaders.
Outputs an email-ready document with each IFM and its accounts.
"""

import csv
from pathlib import Path

INPUT_DIR = Path("data/month_end_by_ifm")
OUTPUT_FILE = Path("data/IFM_Accounts_for_Email.txt")


def main():
    ifm_accounts = {}

    for csv_path in sorted(INPUT_DIR.glob("*_January_2026.csv")):
        ifm = csv_path.stem.replace("_January_2026", "")
        accounts = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                account = row.get("Account", "").strip()
                owner = row.get("Account Owner", "").strip()
                if account:
                    accounts.append((account, owner))
        ifm_accounts[ifm] = accounts

    lines = [
        "=" * 60,
        "IFM ACCOUNTS - January 2026",
        "For awareness / distribution to IFM leaders",
        "=" * 60,
        "",
    ]

    for ifm in sorted(ifm_accounts.keys()):
        accounts = ifm_accounts[ifm]
        lines.append(f"\n{'─' * 50}")
        lines.append(f"IFM: {ifm} ({len(accounts)} accounts)")
        lines.append("─" * 50)
        for account, owner in accounts:
            lines.append(f"  • {account}" + (f" ({owner})" if owner else ""))
        lines.append("")

    # Also create per-IFM copy-paste blocks for easy email use
    lines.append("\n" + "=" * 60)
    lines.append("COPY-PASTE BLOCKS FOR INDIVIDUAL EMAILS")
    lines.append("=" * 60)

    for ifm in sorted(ifm_accounts.keys()):
        accounts = ifm_accounts[ifm]
        lines.append(f"\n--- Email to {ifm} leader ---\n")
        lines.append(f"Accounts under {ifm} ({len(accounts)} total):\n")
        for account, owner in accounts:
            lines.append(f"• {account}" + (f" – {owner}" if owner else ""))
        lines.append("")

    text = "\n".join(lines)
    OUTPUT_FILE.write_text(text, encoding="utf-8")
    print(f"Created {OUTPUT_FILE}")
    print(f"  {len(ifm_accounts)} IFMs, ready to copy into emails")


if __name__ == "__main__":
    main()
