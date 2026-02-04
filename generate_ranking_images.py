"""
Generate PNG images from the enhanced report for PowerPoint presentations.
Automatically splits long rankings into multiple slides.
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

def generate_ranking_images():
    """Generate PNG images of ranking sections from the HTML report"""
    
    # Create output directory
    output_dir = Path('ranking_images')
    output_dir.mkdir(exist_ok=True)
    
    print("Generating ranking images for PowerPoint...")
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Check if HTML report exists
    html_file = Path('EOY_Report_2025_Enhanced.html').absolute()
    if not html_file.exists():
        print(f"ERROR: {html_file} not found. Please generate the report first.")
        return
    
    print(f"Reading report: {html_file}")
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Load the HTML file
        page.goto(f'file:///{html_file}')
        page.wait_for_load_state('networkidle')
        
        print("Bypassing password protection...")
        # Enter the password automatically
        page.fill('#passwordInput', 'SBM2025')
        page.click('.password-btn')
        time.sleep(1)
        
        # Remove landing page
        page.evaluate("""
            document.querySelector('.landing-page')?.remove();
            console.log('Landing page removed');
        """)
        
        time.sleep(1)
        
        print("\nCapturing Overall Rankings...")
        
        # Get the first table (overall rankings) and count real data rows
        total_rows = page.evaluate("""
            const firstTable = document.querySelector('table');
            const tbody = firstTable?.querySelector('tbody');
            const rows = tbody?.querySelectorAll('tr') || [];
            rows.length;
        """)
        print(f"  Found {total_rows} ADs to capture")
        
        if total_rows > 0:
            # Split into two parts
            split_point = 18
            
            # Part 1: Top 18
            print(f"\n1. Capturing Top 18 ADs...")
            page.evaluate(f"""
                const firstSection = document.querySelector('.section');
                const table = firstSection.querySelector('table');
                const tbody = table.querySelector('tbody');
                const allRows = Array.from(tbody.querySelectorAll('tr'));
                
                // Hide rows after {split_point}
                allRows.forEach((row, idx) => {{
                    if (idx >= {split_point}) {{
                        row.style.display = 'none';
                    }}
                }});
                
                // Update header
                const h2 = firstSection.querySelector('h2');
                if (h2) h2.textContent = 'Overall Performance Rankings (Top 18)';
            """)
            
            time.sleep(1)
            page.screenshot(path=str(output_dir / '01_overall_rankings_top18.png'), full_page=False)
            print(f"  OK Saved: 01_overall_rankings_top18.png")
            
            # Part 2: Remaining ADs
            print(f"\n2. Capturing Remaining {total_rows - split_point} ADs...")
            page.evaluate(f"""
                const firstSection = document.querySelector('.section');
                const table = firstSection.querySelector('table');
                const tbody = table.querySelector('tbody');
                const allRows = Array.from(tbody.querySelectorAll('tr'));
                
                // Show all rows first
                allRows.forEach(row => row.style.display = '');
                
                // Hide rows before {split_point}
                allRows.forEach((row, idx) => {{
                    if (idx < {split_point}) {{
                        row.style.display = 'none';
                    }}
                }});
                
                // Update header
                const h2 = firstSection.querySelector('h2');
                if (h2) h2.textContent = 'Overall Performance Rankings (Continued)';
            """)
            
            time.sleep(1)
            page.screenshot(path=str(output_dir / '02_overall_rankings_remaining.png'), full_page=False)
            print(f"  OK Saved: 02_overall_rankings_remaining.png")
        
        print("\n3. All images captured successfully!")
        
        browser.close()
    
    print(f"\n[OK] Image generation complete!")
    print(f"\nImages saved to: {output_dir.absolute()}")
    print("\nGenerated images:")
    for img in sorted(output_dir.glob('*.png')):
        size_kb = img.stat().st_size / 1024
        print(f"  - {img.name} ({size_kb:.1f} KB)")
    
    print("\n[READY] Images ready for PowerPoint!")
    print("   Drag and drop the PNG files into your presentation.")

if __name__ == '__main__':
    try:
        generate_ranking_images()
    except ImportError:
        print("\n[ERROR] Playwright not installed")
        print("\nPlease install it with:")
        print("  pip install playwright")
        print("  playwright install chromium")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
