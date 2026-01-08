# Account Director Performance Dashboard

A modern, executive-facing performance review dashboard for year-end Account Director evaluations.

## 🎯 Current Version: Vanilla JavaScript

The active dashboard is now built with **Vanilla JavaScript** for maximum customization and mobile-friendliness. See `vanilla-js-app/` for details.

## 📂 Project Structure

```
Account-Directors/
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
│
├── vanilla-js-app/                    # ✨ ACTIVE APP
│   ├── index.html                     # Single-page application
│   ├── app.js                         # Frontend logic
│   ├── data.json                      # Generated dashboard data
│   ├── build_data.py                  # Data processor (CSV → JSON)
│   └── README.md                      # Vanilla JS app documentation
│
├── streamlit-app/                     # Legacy Streamlit version
│   ├── app.py                         # Main Streamlit app
│   ├── data_processor.py              # CSV parsing
│   ├── components/                    # UI components
│   ├── requirements.txt               # Python dependencies
│   ├── Procfile                       # Heroku config
│   └── runtime.txt                    # Python version
│
├── data/                              # Source data
│   ├── performance_reviews.csv        # Main CSV export
│   ├── verticals.csv                  # Vertical mappings
│   └── Year-End Review_...csv         # Original upload
│
├── templates/                         # Scorecard templates
│   └── year-end-review-scorecard.html # Blank template for reviews
│
├── reports/                           # Generated reports (not tracked)
│   └── benjamin-ehrenberg-scorecard.html
│
└── docs/                              # Documentation
    ├── DEPLOYMENT.md                  # Heroku deployment guide
    ├── VANILLA_JS_DEPLOYMENT.md       # Vanilla JS setup
    ├── MIGRATION_SUMMARY.md           # Streamlit → Vanilla JS migration
    └── ...other docs
```

## 🚀 Quick Start

### Running the Dashboard

**Option 1: Vanilla JS App (Recommended)**
```bash
cd vanilla-js-app
python -m http.server 8000
# Open http://localhost:8000
```

**Option 2: Streamlit App (Legacy)**
```bash
cd streamlit-app
pip install -r requirements.txt
streamlit run app.py
```

### Updating Data

1. Export new performance reviews to CSV
2. Place CSV in `data/` folder
3. Update `data/performance_reviews.csv` (or modify `build_data.py` path)
4. Regenerate JSON:
```bash
cd vanilla-js-app
python build_data.py
```
5. Refresh browser

## ✨ Features

### Vanilla JS Dashboard
- **Card-Style Leaderboard**: Beautiful, scannable ranking cards with hover effects
- **Mobile-Friendly**: Fully responsive with hamburger menu on mobile
- **Dynamic Filtering**: Filter by vertical and account
- **Expandable Rows**: Click to see 8 section scores with progress bars
- **Individual Reviews**: Detailed view showing all feedback by reviewer
- **Scoring Rubric**: Reference page with evaluation criteria
- **No Dependencies**: Pure HTML/CSS/JS with Google Fonts

### Streamlit Dashboard (Legacy)
- Rankings table with sorting
- Filter panel for vertical/account
- Individual review detail view
- Rubric reference page

## 📊 Data Format

The dashboard expects performance review data with:
- Account Director Name
- Account Name
- Reviewer Name & Email
- 8 scoring sections (1-5 scale):
  1. Key Projects & Initiatives
  2. Value Adds & Cost Avoidance
  3. Cost Savings Delivered
  4. Innovation & Continuous Improvement
  5. Issues, Challenges & Accountability
  6. 2026 Forward Strategy & Vision
  7. Personal Goals & Role Maturity
  8. Executive Presence & Presentation Skills
- Written feedback for each section

## 📝 Generating Personal Scorecards

Use `templates/year-end-review-scorecard.html` to create personalized feedback documents:
1. Run the dashboard to aggregate scores
2. Use the template to fill in individual scorecards
3. Export to PDF for distribution

Example: `reports/benjamin-ehrenberg-scorecard.html` (pre-filled example)

## 🔧 Technologies

### Vanilla JS App
- HTML5 + CSS3 + Vanilla JavaScript
- Google Fonts (Inter)
- Python 3.11+ (for data processing only)
- Pandas + NumPy (build script dependencies)

### Streamlit App
- Python 3.11.9
- Streamlit
- Pandas, NumPy

## 📚 Documentation

See `docs/` folder for detailed guides:
- **VANILLA_JS_DEPLOYMENT.md**: How to deploy the JS app
- **DEPLOYMENT.md**: Heroku deployment for Streamlit
- **MIGRATION_SUMMARY.md**: Why we switched to Vanilla JS

## 🌐 Deployment

**Vanilla JS**: Any static hosting (GitHub Pages, Netlify, Vercel, S3, etc.)
**Streamlit**: Heroku, Streamlit Cloud

See deployment docs for details.

## 📱 Mobile Support

The Vanilla JS dashboard is fully mobile-optimized with:
- Responsive layouts (1024px, 768px, 480px, 375px breakpoints)
- Hamburger menu for filters
- Touch-friendly buttons (44px minimum)
- Optimized card layouts for small screens

## 🎨 Design Philosophy

- **Scores First**: Numeric data emphasized for quick scanning
- **Rankings Second**: Dynamic ranking with visual hierarchy
- **Feedback Last**: Qualitative feedback accessible but secondary
- **Executive Polish**: Modern, credible aesthetic
- **No Judgment Colors**: Neutral colors avoid traffic-light semantics

## 📄 License

Internal use only.

---

**Current Version**: Vanilla JavaScript Dashboard  
**Last Updated**: January 2026  
**Status**: ✅ Production Ready
