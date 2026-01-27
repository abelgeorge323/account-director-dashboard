# View Report Locally

## Quick Commands

### Option 1: Open in Default Browser (Simplest)
```bash
start EOY_Report_2025_Enhanced.html
```

### Option 2: Open with Specific Browser

**Chrome:**
```bash
start chrome EOY_Report_2025_Enhanced.html
```

**Edge:**
```bash
start msedge EOY_Report_2025_Enhanced.html
```

**Firefox:**
```bash
start firefox EOY_Report_2025_Enhanced.html
```

### Option 3: Start a Local Web Server (Best for development)

**Using Python:**
```bash
python -m http.server 8000
```
Then open: http://localhost:8000/EOY_Report_2025_Enhanced.html

**Using Node.js (if installed):**
```bash
npx http-server -p 8000
```
Then open: http://localhost:8000/EOY_Report_2025_Enhanced.html

---

## Default Password
**Password:** `SBM2025`

---

## Generate Fresh Report
```bash
python generate_enhanced_report.py
```

## Convert to PDF
```bash
python convert_to_pdf.py
```
