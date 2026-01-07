# How to Clear Streamlit Cache

If you see old data in the dashboard after updates, follow these steps:

## Method 1: In the Browser (Easiest)
1. Open the Streamlit app in your browser (http://localhost:8501)
2. Press **`C`** on your keyboard (while the app is in focus)
3. Select "Clear cache" from the menu
4. The app will reload with fresh data

## Method 2: Keyboard Shortcut
1. Press **`R`** to rerun the app
2. Or press **`Ctrl+R`** (or `Cmd+R` on Mac) to refresh the browser

## Method 3: Hard Browser Refresh
1. Press **`Ctrl+Shift+R`** (Windows/Linux)
2. Or **`Cmd+Shift+R`** (Mac)
3. This clears the browser cache and reloads

## Method 4: Restart Streamlit
```bash
# Kill the process
taskkill /F /FI "WINDOWTITLE eq *streamlit*" /T

# Start fresh
python -m streamlit run app.py
```

## What Changed
- ✅ Fixed CSV parsing - all 8 sections now load correctly
- ✅ Corrected scores: **34.67 / 40** (was showing 29.67)
- ✅ Added Manufacturing vertical for Benjamin Ehrenberg
- ✅ Vertical filtering now active in sidebar

## Expected Values
- **Benjamin Ehrenberg**
  - Total Score: **34.67 / 40**
  - Account: Lockheed Martin
  - Vertical: Manufacturing
  - Individual Reviews: 36, 33, 35 (average: 34.67)

