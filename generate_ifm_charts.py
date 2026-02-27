#!/usr/bin/env python3
"""
Generate per-IFM charts (HTML + PDF) with Account and Account Owner.
Creates a separate chart and PDF for each IFM.
"""

import csv
from html import escape as html_escape
from pathlib import Path

INPUT_DIR = Path("data/month_end_by_ifm")
OUTPUT_DIR = Path("data/ifm_charts")
PDF_DIR = Path("data/ifm_charts/pdf")


def generate_html_chart(ifm: str, rows: list[dict]) -> Path:
    """Generate HTML chart for one IFM."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = OUTPUT_DIR / f"{ifm}_January_2026.html"

    html_rows = "".join(
        f'<tr><td>{html_escape(r["Account"])}</td><td>{html_escape(r["Account Owner"])}</td></tr>'
        for r in rows
    )

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{html_escape(ifm)} - Accounts & Owners</title>
<style>
  body {{ font-family: system-ui; margin: 2rem; background: #f8f8f8; }}
  h1 {{ color: #2A4B8F; }}
  .subtitle {{ color: #646464; margin-bottom: 1.5rem; }}
  table {{ border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  th, td {{ padding: 10px 16px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
  th {{ background: #2A4B8F; color: white; font-weight: 600; }}
  tr:hover {{ background: #f5f5f5; }}
  @media print {{ body {{ background: white; margin: 0.5in; }} table {{ box-shadow: none; }} }}
</style>
</head>
<body>
<h1>{html_escape(ifm)} — Accounts & Account Owners</h1>
<p class="subtitle">January 2026 • {len(rows)} accounts</p>
<table>
<thead><tr><th>Account</th><th>Account Owner</th></tr></thead>
<tbody>{html_rows}</tbody>
</table>
</body>
</html>"""
    html_path.write_text(html, encoding="utf-8")
    return html_path


def convert_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Convert HTML to PDF. Returns True if successful."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            html_file = html_path.resolve()
            page.goto(f"file:///{html_file.as_posix()}")
            page.wait_for_load_state("networkidle")
            PDF_DIR.mkdir(parents=True, exist_ok=True)
            page.pdf(
                path=str(pdf_path),
                format="Letter",
                print_background=True,
                margin={"top": "0.5in", "right": "0.5in", "bottom": "0.5in", "left": "0.5in"},
            )
            browser.close()
        return True
    except Exception:
        return False


def main():
    print("=" * 60)
    print("IFM Charts & PDFs - Account + Account Owner")
    print("=" * 60)

    generated = []
    for csv_path in sorted(INPUT_DIR.glob("*_January_2026.csv")):
        ifm = csv_path.stem.replace("_January_2026", "")
        rows = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                account = row.get("Account", "").strip()
                owner = row.get("Account Owner", "").strip()
                if account:
                    rows.append({"Account": account, "Account Owner": owner or "—"})

        if not rows:
            continue

        rows.sort(key=lambda r: r["Account"].upper())
        html_path = generate_html_chart(ifm, rows)
        generated.append((ifm, html_path, len(rows)))
        print(f"  {ifm}: {len(rows)} accounts -> {html_path.name}")

    print(f"\nCreated {len(generated)} HTML charts in {OUTPUT_DIR}/")

    # PDF generation
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
        has_playwright = True
    except ImportError:
        has_playwright = False

    if has_playwright:
        print("\nGenerating PDFs...")
        for ifm, html_path, _ in generated:
            pdf_path = PDF_DIR / f"{ifm}_January_2026.pdf"
            if convert_to_pdf(html_path, pdf_path):
                print(f"  {ifm} -> {pdf_path.name}")
            else:
                print(f"  {ifm} -> [skipped]")
        print(f"\nPDFs saved to {PDF_DIR}/")
    else:
        print("\n[PDF] Playwright not installed. HTML charts ready.")
        print("  To generate PDFs: pip install playwright && playwright install chromium")
        print("  Or: Open each HTML in browser -> Print -> Save as PDF")

    print("=" * 60)


if __name__ == "__main__":
    main()
