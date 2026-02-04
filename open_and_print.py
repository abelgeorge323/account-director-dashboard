"""
Alternative PDF conversion using Playwright (if installed) or instructions
"""
import os
import webbrowser
from pathlib import Path

html_file = Path('EOY_Report_2025_Enhanced.html').absolute()

print("=" * 60)
print("PDF CONVERSION INSTRUCTIONS")
print("=" * 60)
print(f"\nHTML file location: {html_file}")
print("\nTo convert to PDF:")
print("1. Opening HTML file in your default browser...")

# Open in browser
webbrowser.open(str(html_file))

print("\n2. Once the page loads:")
print("   - Press Ctrl+P (or Cmd+P on Mac)")
print("   - Select 'Save as PDF' as the destination")
print("   - Click 'Save'")
print(f"   - Save as: EOY_Report_2025_Enhanced.pdf")
print("\n" + "=" * 60)
