"""
Convert Enhanced EOY Report HTML to PDF using Playwright
"""
from playwright.sync_api import sync_playwright
import os

html_file = "EOY_Report_2025_Enhanced.html"
pdf_file = "EOY_Report_2025_Enhanced.pdf"

print(f"🔧 Converting {html_file} to PDF...")

# Check if HTML file exists
if not os.path.exists(html_file):
    print(f"❌ ERROR: {html_file} not found!")
    print(f"   Please run 'python generate_enhanced_report.py' first.")
    exit(1)

# Convert to PDF
with sync_playwright() as p:
    print("   📂 Launching browser...")
    browser = p.chromium.launch()
    page = browser.new_page()
    
    print(f"   📄 Loading {html_file}...")
    page.goto(f'file:///{os.path.abspath(html_file)}')
    
    print(f"   💾 Saving as {pdf_file}...")
    page.pdf(
        path=pdf_file,
        format='Letter',
        print_background=True,
        margin={
            'top': '0.5in',
            'right': '0.5in',
            'bottom': '0.5in',
            'left': '0.5in'
        }
    )
    
    browser.close()

print(f"\n✅ SUCCESS! PDF created: {pdf_file}")
print(f"   File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
