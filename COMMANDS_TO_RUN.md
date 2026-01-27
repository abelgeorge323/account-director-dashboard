# Commands to Run - Enhanced EOY Report

## Step 1: Generate Enhanced HTML Report
```bash
python generate_enhanced_report.py
```

**Output:** `EOY_Report_2025_Enhanced.html`

This will create an enhanced report with:
- ✅ Overall rankings with financial KPIs (Revenue, CSAT, Headcount, Red Sites)
- ✅ Revenue Rankings section
- ✅ CSAT Rankings section
- ✅ Growth Rankings section
- ✅ Red Sites Rankings section (lower is better)
- ✅ Team Size Rankings section

---

## Step 2: Convert HTML to PDF (Using Playwright - INSTALLED ✅)
```bash
python convert_to_pdf.py
```

**Output:** `EOY_Report_2025_Enhanced.pdf`

This will create a professional, print-ready PDF with proper formatting and margins!

---

## Next: Dashboard (Step 2)
After you have the enhanced report, we'll build an interactive dashboard!
