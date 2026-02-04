"""
Convert HTML to PDF using wkhtmltopdf or weasyprint
"""
import subprocess
import os
import sys

html_file = 'EOY_Report_2025_Enhanced.html'
pdf_file = 'EOY_Report_2025_Enhanced.pdf'

print(f"Converting {html_file} to {pdf_file}...")

# Try wkhtmltopdf first (most common)
try:
    result = subprocess.run(
        ['wkhtmltopdf', '--enable-local-file-access', html_file, pdf_file],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"SUCCESS: PDF created using wkhtmltopdf: {pdf_file}")
        sys.exit(0)
except FileNotFoundError:
    print("wkhtmltopdf not found, trying alternative methods...")

# Try weasyprint
try:
    from weasyprint import HTML
    HTML(html_file).write_pdf(pdf_file)
    print(f"SUCCESS: PDF created using weasyprint: {pdf_file}")
    sys.exit(0)
except ImportError:
    print("weasyprint not installed...")

# Try Chrome/Chromium headless
chrome_paths = [
    'chrome',
    'google-chrome',
    'chromium',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
]

for chrome_path in chrome_paths:
    try:
        result = subprocess.run(
            [chrome_path, '--headless', '--disable-gpu', f'--print-to-pdf={pdf_file}', html_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"SUCCESS: PDF created using Chrome: {pdf_file}")
            sys.exit(0)
    except FileNotFoundError:
        continue

print("\nCould not find any PDF converter.")
print("\nAlternative options:")
print("1. Open the HTML file in your browser and use Print -> Save as PDF (Ctrl+P)")
print("2. Install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
print("3. Install weasyprint: pip install weasyprint")
print(f"\nHTML report is ready to view: {html_file}")
