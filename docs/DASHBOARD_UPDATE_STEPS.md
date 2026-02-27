# Dashboard Update Steps

How to refresh the Account Director Performance Dashboard with new reviews, financial data, and ATB.

---

## Quick Commands (in order)

```bash
# 1. Merge new reviews (if you have a new Year-End Review export)
python merge_new_reviews.py

# 2. Rebuild dashboard data (reviews + financial + ATB)
cd vanilla-js-app
python build_data.py

# 3. Serve locally to view
python -m http.server 8000
# Open http://localhost:8000
```

---

## Step-by-Step

### 1. Add New Reviews

**Option A: Merge from new export**
- Place new CSV in `data/` (e.g. `Year-End Review_ Account Director Leadership Evaluation(Sheet1) (X).csv`)
- Update `merge_new_reviews.py` to point to that file (line 19)
- Run: `python merge_new_reviews.py`

**Option B: Manual**
- Append new rows to `data/performance_reviews.csv`
- Match column structure (Id, Start time, Account Name, Account Director Name, scores, feedback)

### 2. Update Verticals (AD → Vertical mapping)

Edit `data/verticals.csv`:

| Account Director | Vertical | Notes |
|------------------|----------|-------|
| Corey Wallace | Life Science, Finance | AbbVie (Life Science) + GEICO (Finance) |
| Colleen Doles | Finance | Wells Fargo |
| Joshua Grady | Life Science | Gilead |
| Jennifer Segovia | Manufacturing | Northrop Grumman, General Dynamics |

### 3. Connect ATB to Reviews

ATB is **already connected** when you run `build_data.py`:
- `data/ATB Q4.2025-Jan. 2026.csv` → loaded automatically
- Matched by account name (from `ad_csvs/*.csv`)
- Add aliases in `vanilla-js-app/build_data.py` → `ATB_ACCOUNT_ALIASES` if account names differ

### 4. Connect Financial Data

**Source:** `data/ad_csvs/*.csv` (one file per AD, e.g. `corey-wallace.csv`)

- Each CSV has: Account, KPI (Revenue, CSAT, Headcount, etc.), Dec-25 values
- `build_data.py` aggregates by AD
- Manual overrides in `apply_manual_mappings()` for special cases

**To add a new AD:**
1. Create `data/ad_csvs/{first-last}.csv` with Account, KPI, Dec-25 columns
2. Add row to `data/verticals.csv`
3. Add account→AD mapping in `data/ad_account_mapping.csv` if reviews use different account names

### 5. Rebuild Dashboard

```bash
cd vanilla-js-app
python build_data.py
```

Output: `vanilla-js-app/data.json` (used by the dashboard)

### 6. Deploy (if hosted)

- Commit changes
- Push to Heroku / hosting
- Clear cache if needed (see `docs/CACHE_CLEAR_INSTRUCTIONS.md`)

---

## Data Flow

```
performance_reviews.csv  ──┐
verticals.csv            ──┼──► build_data.py ──► data.json ──► Dashboard
ad_csvs/*.csv            ──┤
ATB Q4.2025-Jan. 2026   ──┤
ad_account_mapping.csv   ──┘
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| AD missing from dashboard | Add to `verticals.csv` + `ad_csvs` or `apply_manual_mappings` |
| ATB not showing | Check account name matches ATB CSV (e.g. "Geico" not "GEICO") |
| Wrong vertical filter | Update `verticals.csv` |
| Duplicate AD rows | Remove duplicate from `verticals.csv` (last row wins) |
