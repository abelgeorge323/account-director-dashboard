"""
PDF Generator for Account Director Reports
Uses Playwright to convert HTML reports to PDF with perfect formatting
"""

import os
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("\nInstall with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


def ensure_pdf_directory():
    """Create PDF output directory if it doesn't exist"""
    pdf_dir = Path("reports/pdf")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir


def convert_html_to_pdf(html_path, pdf_path):
    """Convert a single HTML file to PDF using Playwright"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Load HTML file
        html_file = Path(html_path).resolve()
        page.goto(f"file:///{html_file}")
        
        # Wait for content to load
        page.wait_for_load_state("networkidle")
        
        # Generate PDF with print-optimized settings
        page.pdf(
            path=str(pdf_path),
            format="Letter",
            print_background=True,
            margin={
                "top": "0.5in",
                "right": "0.5in",
                "bottom": "0.5in",
                "left": "0.5in"
            }
        )
        
        browser.close()


def main():
    """Generate PDFs for all HTML reports"""
    
    print("=" * 70)
    print("PDF GENERATION - Account Director Reports")
    print("=" * 70)
    
    # Ensure output directory exists
    pdf_dir = ensure_pdf_directory()
    
    # Define reports to convert
    reports = []
    
    # 1. Individual AD scorecards
    scorecard_dir = Path("reports")
    for html_file in scorecard_dir.glob("*-scorecard.html"):
        pdf_name = html_file.stem + ".pdf"
        reports.append((html_file, pdf_dir / pdf_name))
    
    # 2. Comprehensive EOY Report
    eoy_report = Path("EOY_Report_2025.html")
    if eoy_report.exists():
        reports.append((eoy_report, pdf_dir / "EOY_Report_2025.pdf"))
    
    # 3. Highlights Report
    highlights_report = Path("AD_Highlights_Report_2025.html")
    if highlights_report.exists():
        reports.append((highlights_report, pdf_dir / "AD_Highlights_Report_2025.pdf"))
    
    if not reports:
        print("❌ No HTML reports found!")
        print("\nGenerate reports first:")
        print("  python generate_scorecards.py")
        print("  python generate_report.py")
        return
    
    print(f"\n📄 Found {len(reports)} report(s) to convert\n")
    
    # Convert each report
    success_count = 0
    for html_path, pdf_path in reports:
        try:
            print(f"Converting: {html_path.name} → {pdf_path.name}...", end=" ")
            convert_html_to_pdf(html_path, pdf_path)
            print("✅")
            success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully generated {success_count}/{len(reports)} PDFs")
    print(f"📁 PDFs saved to: {pdf_dir.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    main()

