#!/usr/bin/env python3
"""Generate Account -> IFM chart for manufacturing accounts only."""

import csv
from html import escape as html_escape
from pathlib import Path

INPUT_DIR = Path("data/month_end_by_ifm")
OUTPUT_CSV = Path("data/Manufacturing_Account_IFM_Chart.csv")
OUTPUT_HTML = Path("data/Manufacturing_Account_IFM_Chart.html")

# Manufacturing accounts (user-specified) - match patterns to our data
MANUFACTURING_ACCOUNTS = [
    "3M Corp",
    "Ball Corporation",
    "Boeing Company",
    "Clorox Company",
    "Coca-Cola",
    "Covestro",
    "Danfoss Power Solutions",
    "DuPont",
    "Gallo Wine",
    "GE Healthcare",
    "GE Power",
    "General Dynamics",
    "General Electric",
    "Lockheed Martin",
    "Mars",
    "Molson Coors",
    "Nestle",
    "Northrop Grumman",
    "Procter & Gamble Company",
    "Procter & Gamble Company - Costa Rica",
    "Spirit Aerosystems",
    "Textron Aviation",
    "Textron Aviation - Singapore",
    "United Technologies",
    "Westinghouse",
]


def main():
    manufacturing_set = set(MANUFACTURING_ACCOUNTS)
    rows = []

    for csv_path in sorted(INPUT_DIR.glob("*_January_2026.csv")):
        ifm = csv_path.stem.replace("_January_2026", "")
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                account = row.get("Account", "").strip()
                if account in manufacturing_set:
                    rows.append({"Account": account, "IFM": ifm})

    rows.sort(key=lambda r: (r["Account"].upper(), r["IFM"]))

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Account", "IFM"])
        w.writeheader()
        w.writerows(rows)
    print(f"Created {OUTPUT_CSV} ({len(rows)} manufacturing accounts)")

    html_rows = "".join(
        f'<tr><td>{html_escape(r["Account"])}</td><td>{html_escape(r["IFM"])}</td></tr>'
        for r in rows
    )
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Manufacturing Accounts → IFM Chart</title>
<style>
  body {{ font-family: system-ui; margin: 2rem; background: #f8f8f8; }}
  h1 {{ color: #2A4B8F; }}
  .subtitle {{ color: #646464; margin-bottom: 1.5rem; }}
  table {{ border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  th, td {{ padding: 10px 16px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
  th {{ background: #2A4B8F; color: white; font-weight: 600; }}
  tr:hover {{ background: #f5f5f5; }}
</style>
</head>
<body>
<h1>Manufacturing Accounts → IFM Chart</h1>
<p class="subtitle">January 2026 • {len(rows)} manufacturing accounts</p>
<table>
<thead><tr><th>Account</th><th>IFM</th></tr></thead>
<tbody>{html_rows}</tbody>
</table>
</body>
</html>"""
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Created {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
