# Account Director Performance Dashboard

A modern, executive-facing performance review dashboard for year-end Account Director evaluations. Built with Streamlit and Python 3.11.9.

## Features

- **Rankings View**: Sortable table showing Account Directors ranked by performance scores
- **Dynamic Filtering**: Filter by Account and Vertical (when data provided)
- **Detail Drawer**: Click any Account Director to view individual reviews with section-by-section feedback
- **Scoring Rubric**: Reference page documenting evaluation methodology and criteria
- **Executive Design**: Clean, professional aesthetic optimized for leadership reviews
- **Multi-Reviewer Support**: Aggregates scores when multiple reviewers evaluate the same AD

## Project Structure

```
account-directors/
├── app.py                          # Main Streamlit application
├── data_processor.py               # CSV parsing and score aggregation
├── components/
│   ├── __init__.py
│   ├── rankings_table.py           # Rankings table with filtering
│   └── rubric_page.py              # Scoring rubric reference
├── data/
│   └── performance_reviews.csv     # Performance review data
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── requirements.txt                # Python dependencies
├── Procfile                        # Heroku deployment config
├── runtime.txt                     # Python version
└── README.md                       # This file
```

## Local Development

### Prerequisites

- Python 3.11.9
- pip

### Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Data Format

The dashboard expects a CSV file at `data/performance_reviews.csv` with the following structure:

- **Account Director Name**: Name of the Account Director being reviewed
- **Account Name**: Associated account
- **Reviewer Name**: Name of the person conducting the review
- **Reviewer Email**: Reviewer's email
- **Score Columns**: 8 sections, each scored 1-5:
  - Key Projects & Initiatives
  - Value Adds & Cost Avoidance
  - Cost Savings Delivered
  - Innovation & Continuous Improvement
  - Issues, Challenges & Accountability
  - 2026 Forward Strategy & Vision
  - Personal Goals & Role Maturity
  - Executive Presence & Presentation Skills
- **Feedback Columns**: Written feedback for each section

## Deploying to Heroku

### Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account

### Deployment Steps

1. **Login to Heroku**
```bash
heroku login
```

2. **Create a new Heroku app**
```bash
heroku create your-app-name
```

3. **Add Python buildpack**
```bash
heroku buildpacks:set heroku/python
```

4. **Initialize git repository (if not already done)**
```bash
git init
git add .
git commit -m "Initial commit"
```

5. **Deploy to Heroku**
```bash
git push heroku main
```

Or if your default branch is `master`:
```bash
git push heroku master
```

6. **Open your deployed app**
```bash
heroku open
```

### Environment Configuration

The app is configured to work with Heroku out of the box:
- `Procfile` specifies the web process command
- `runtime.txt` specifies Python 3.11.9
- `requirements.txt` lists all dependencies
- Streamlit will automatically use the `$PORT` environment variable set by Heroku

### Updating Your Deployment

After making changes:
```bash
git add .
git commit -m "Your commit message"
git push heroku main
```

## Adding Vertical Data

To enable vertical filtering:

1. Create a CSV file `data/verticals.csv` with the format:
```csv
Account Director Name,Vertical
John Doe,Technology
Jane Smith,Healthcare
```

2. Update `data_processor.py` to load and merge vertical data:
```python
# In load_performance_data function
verticals_df = pd.read_csv("data/verticals.csv")
df = df.merge(verticals_df, on="Account Director Name", how="left")
```

3. Update `get_filter_options` to include verticals:
```python
"verticals": sorted(aggregated_df["Vertical"].dropna().unique().tolist())
```

## Scoring Methodology

- **Individual Sections**: 1-5 points each (5 = Exceptional, 1 = Needs Improvement)
- **Total Score**: 8 sections × 5 points = 40 points maximum
- **Aggregation**: When multiple reviewers evaluate the same AD, scores are averaged for rankings
- **Detail View**: All individual reviews are preserved and displayed in the detail drawer

## Design Philosophy

- **Scores First**: Numeric data is emphasized for quick scanning
- **Rankings Second**: Dynamic ranking based on current filters and sort
- **Feedback Last**: Qualitative feedback is secondary but accessible
- **Executive Polish**: Modern, credible aesthetic suitable for leadership reviews
- **No Judgment Colors**: Neutral color scheme avoids red/green traffic light semantics

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Python 3.11.9**: Programming language

## Support

For issues or questions about the dashboard, contact your development team.

## License

Internal use only.

