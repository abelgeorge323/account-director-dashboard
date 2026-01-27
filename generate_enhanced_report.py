"""
Generate Enhanced EOY Account Director Review Report with Financial KPIs
"""
import pandas as pd
import json
from collections import defaultdict
from pathlib import Path

def clean_numeric_value(val):
    """Clean malformed numeric values from CSVs
    Handles cases like: '\"\"\"1\",\"104\"\"\"' -> 1104
    """
    if pd.isna(val) or val == '':
        return None
    
    try:
        # Convert to string and remove all quotes and commas
        cleaned = str(val).replace('"', '').replace(',', '').strip()
        if cleaned:
            return float(cleaned)
    except:
        pass
    return None

def load_performance_data():
    """Load performance review data"""
    df = pd.read_csv("data/performance_reviews.csv", low_memory=False)
    
    # Split joint reviews into individual entries
    expanded_rows = []
    for _, row in df.iterrows():
        ad_name = str(row.get("Account Director Name", "")).strip()
        if "/" in ad_name:
            names = [n.strip() for n in ad_name.split("/")]
            for name in names:
                new_row = row.copy()
                new_row["Account Director Name"] = name
                expanded_rows.append(new_row)
        else:
            expanded_rows.append(row)
    
    return pd.DataFrame(expanded_rows)

def load_financial_data():
    """Load all AD CSV files and aggregate financial metrics"""
    ad_csvs_dir = Path("data/ad_csvs")
    ad_financial_data = {}
    
    for csv_file in ad_csvs_dir.glob("*.csv"):
        ad_name = csv_file.stem.replace('-', ' ').title()
        
        try:
            df = pd.read_csv(csv_file)
            
            # Get unique accounts
            accounts = df['Account'].unique().tolist()
            
            # Calculate metrics for Dec-25 (most recent)
            revenue_total = 0
            csat_values = []
            headcount_total = 0
            red_sites_count = 0
            growth_values = []
            
            for account in accounts:
                account_df = df[df['Account'] == account]
                
                # Revenue
                rev_row = account_df[account_df['KPI'] == 'Revenue ($)']
                if not rev_row.empty and 'Dec-25' in rev_row.columns:
                    val = rev_row['Dec-25'].values[0]
                    cleaned_val = clean_numeric_value(val)
                    if cleaned_val is not None:
                        revenue_total += cleaned_val
                
                # CSAT
                csat_row = account_df[account_df['KPI'] == 'CSAT']
                if not csat_row.empty and 'Dec-25' in csat_row.columns:
                    val = csat_row['Dec-25'].values[0]
                    cleaned_val = clean_numeric_value(val)
                    if cleaned_val is not None:
                        csat_values.append(cleaned_val)
                
                # Headcount
                hc_row = account_df[account_df['KPI'] == 'Headcount']
                if not hc_row.empty and 'Dec-25' in hc_row.columns:
                    val = hc_row['Dec-25'].values[0]
                    cleaned_val = clean_numeric_value(val)
                    if cleaned_val is not None:
                        headcount_total += int(cleaned_val)
                
                # Red Sites #
                rs_row = account_df[account_df['KPI'] == 'Red Sites (#)']
                if not rs_row.empty and 'Dec-25' in rs_row.columns:
                    val = rs_row['Dec-25'].values[0]
                    cleaned_val = clean_numeric_value(val)
                    if cleaned_val is not None:
                        red_sites_count += int(cleaned_val)
                
                # Growth %
                growth_row = account_df[account_df['KPI'] == 'Growth (%)']
                if not growth_row.empty and 'Dec-25' in growth_row.columns:
                    val = growth_row['Dec-25'].values[0]
                    cleaned_val = clean_numeric_value(val)
                    if cleaned_val is not None:
                        growth_values.append(cleaned_val)
            
            ad_financial_data[ad_name] = {
                'accounts': accounts,
                'num_accounts': len(accounts),
                'revenue_total': revenue_total,
                'csat_avg': sum(csat_values) / len(csat_values) if csat_values else None,
                'headcount_total': headcount_total,
                'red_sites_count': red_sites_count,
                'growth_avg': sum(growth_values) / len(growth_values) if growth_values else None
            }
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            continue
    
    return ad_financial_data

def get_score_columns(df):
    """Identify score columns from CSV"""
    score_cols = []
    section_keywords = [
        ["Key Projects", "Initiatives"],
        ["Value Adds", "Cost Avoidance"],
        ["Cost Savings", "Savings Delivered"],
        ["Innovation", "Continuous Improvement"],
        ["Issues", "Challenges", "Accountability"],
        ["2026", "Strategy", "Path Forward"],
        ["Personal Goals", "Goals"],
        ["Executive Presence", "Communication"]
    ]
    
    for col in df.columns:
        if "Comment" in col or "comment" in col:
            continue
        for keywords in section_keywords:
            if any(keyword in col for keyword in keywords):
                score_cols.append(col)
                break
    
    return score_cols

def calculate_rankings(df):
    """Calculate average scores for each AD in each section"""
    rankings = {}
    score_cols = get_score_columns(df)
    
    for score_col in score_cols:
        ad_scores = defaultdict(list)
        
        for _, row in df.iterrows():
            ad_name = str(row.get("Account Director Name", "")).strip()
            if not ad_name or ad_name == "nan":
                continue
            score = row.get(score_col)
            if pd.notna(score) and score != "":
                try:
                    ad_scores[ad_name].append(float(score))
                except:
                    pass
        
        section_rankings = []
        for ad_name, scores in ad_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                section_rankings.append({
                    "name": ad_name,
                    "avg_score": round(avg_score, 2),
                    "num_reviews": len(scores)
                })
        
        section_rankings.sort(key=lambda x: x["avg_score"], reverse=True)
        rankings[score_col] = section_rankings
    
    return rankings

def format_currency(value):
    """Format currency with proper scale (millions for >= 1000K)"""
    if value >= 1000:
        return f"${value/1000:.2f}M"
    elif value > 0:
        return f"${value:.0f}K"
    else:
        return "N/A"

def generate_enhanced_html(rankings, df, financial_data):
    """Generate enhanced HTML with financial data"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 Account Director Performance Review</title>
    <style>
        @page {
            margin: 0.5in;
            size: letter;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
            color: #1a1a1a;
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
            background: white;
            font-size: 9pt;
        }
        
        h1 {
            color: #1a1a1a;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
            font-size: 26pt;
            margin: 0 0 10px 0;
            font-weight: 600;
        }
        
        h2 {
            color: #1a1a1a;
            font-size: 14pt;
            margin: 15px 0 6px 0;
            page-break-after: avoid;
            font-weight: 600;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 5px;
        }
        
        h2.first-section {
            margin-top: 5px;
        }
        
        h3 {
            color: #4b5563;
            font-size: 11pt;
            margin: 15px 0 8px 0;
            font-weight: 600;
        }
        
        .subtitle {
            font-size: 10pt;
            color: #6b7280;
            margin-bottom: 15px;
        }
        
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0 15px 0;
            font-size: 7.5pt;
            border: 1px solid #e5e7eb;
        }
        
        th {
            background: #1f2937;
            color: white;
            padding: 6px 4px;
            text-align: left;
            font-weight: 600;
            font-size: 7.5pt;
            border-bottom: 2px solid #111827;
        }
        
        td {
            padding: 4px;
            border-bottom: 1px solid #f3f4f6;
        }
        
        tr:hover {
            background: #fafafa;
        }
        
        .rank-1 { 
            border-left: 4px solid #10b981;
            background: #f0fdf4;
        }
        .rank-2 { 
            border-left: 4px solid #3b82f6;
            background: #eff6ff;
        }
        .rank-3 { 
            border-left: 4px solid #8b5cf6;
            background: #faf5ff;
        }
        
        .tier-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 7pt;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        
        .tier-exceptional {
            background: #10b981;
            color: white;
        }
        
        .tier-strong {
            background: #3b82f6;
            color: white;
        }
        
        .tier-solid {
            background: #f59e0b;
            color: white;
        }
        
        .tier-development {
            background: #ef4444;
            color: white;
        }
        
        .section {
            page-break-after: always;
        }
        
        .accounts-list {
            font-size: 6.5pt;
            color: #6b7280;
            line-height: 1.3;
        }
        
        .section-summary {
            font-size: 8.5pt;
            color: #6b7280;
            margin: -3px 0 8px 0;
            font-style: italic;
        }
        
        @media print {
            .section { page-break-after: always; }
            tr { page-break-inside: avoid; }
            .password-overlay { display: none !important; }
        }
        
        .password-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #1a1a1a;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        
        .password-box {
            background: white;
            padding: 30px 40px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 90%;
        }
        
        .password-box h2 {
            margin: 0 0 20px 0;
            font-size: 20pt;
            border: none;
            padding: 0;
        }
        
        .password-input {
            width: 100%;
            padding: 12px;
            font-size: 14pt;
            border: 2px solid #e5e7eb;
            border-radius: 4px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        
        .password-input:focus {
            outline: none;
            border-color: #2563eb;
        }
        
        .password-btn {
            width: 100%;
            padding: 12px;
            font-size: 12pt;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .password-btn:hover {
            background: #1d4ed8;
        }
        
        .password-error {
            color: #ef4444;
            font-size: 10pt;
            margin-top: 10px;
            display: none;
        }
        
        .report-content {
            display: none;
        }
        
        .report-content.unlocked {
            display: block;
        }
    </style>
</head>
<body>
    <div class="password-overlay" id="passwordOverlay">
        <div class="password-box">
            <h2>Protected Report</h2>
            <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 10pt;">
                Enter password to view the 2025 Account Director Performance Review
            </p>
            <input 
                type="password" 
                id="passwordInput" 
                class="password-input" 
                placeholder="Enter password"
                autocomplete="off"
            >
            <button class="password-btn" onclick="checkPassword()">Unlock Report</button>
            <p class="password-error" id="passwordError">Incorrect password. Please try again.</p>
        </div>
    </div>
    
    <div class="report-content" id="reportContent">
    <h1>2025 Account Director Performance Review</h1>
    <p class="subtitle">
        Comprehensive performance analysis across 16 Account Directors | December 2025
    </p>
"""
    
    # Calculate overall rankings
    overall_scores = defaultdict(lambda: {"total": 0, "count": 0})
    for section_name, section_data in rankings.items():
        for ad_data in section_data:
            overall_scores[ad_data['name']]["total"] += ad_data['avg_score']
            overall_scores[ad_data['name']]["count"] += 1
    
    overall_rankings = []
    for ad_name, data in overall_scores.items():
        avg = data["total"] / data["count"] if data["count"] > 0 else 0
        total_out_of_40 = data["total"]
        
        # Get financial data
        fin_data = financial_data.get(ad_name, {})
        
        overall_rankings.append({
            "name": ad_name,
            "avg": round(avg, 2),
            "total": round(total_out_of_40, 1),
            "accounts": fin_data.get('accounts', []),
            "num_accounts": fin_data.get('num_accounts', 0),
            "revenue": fin_data.get('revenue_total', 0),
            "csat": fin_data.get('csat_avg'),
            "headcount": fin_data.get('headcount_total', 0),
            "red_sites": fin_data.get('red_sites_count', 0),
            "growth": fin_data.get('growth_avg')
        })
    
    overall_rankings.sort(key=lambda x: x["total"], reverse=True)
    
    # Calculate portfolio-wide metrics for other sections
    total_revenue = sum(ad['revenue'] for ad in overall_rankings if ad['revenue'] > 0)
    total_headcount = sum(ad['headcount'] for ad in overall_rankings if ad['headcount'] > 0)
    avg_score = sum(ad['total'] for ad in overall_rankings) / len(overall_rankings) if overall_rankings else 0
    avg_csat = sum(ad['csat'] for ad in overall_rankings if ad['csat']) / len([ad for ad in overall_rankings if ad['csat']]) if any(ad['csat'] for ad in overall_rankings) else 0
    avg_growth = sum(ad['growth'] for ad in overall_rankings if ad['growth']) / len([ad for ad in overall_rankings if ad['growth']]) if any(ad['growth'] for ad in overall_rankings) else 0
    
    # MAIN PERFORMANCE + FINANCIAL RANKINGS TABLE
    html += """
    <div class="section">
        <h2 class="first-section">Overall Performance Rankings</h2>
        <p class="section-summary">Comprehensive performance scores with financial metrics (December 2025)</p>
        <table>
        <thead>
            <tr>
                <th style="width: 30px;">Rank</th>
                <th style="width: 120px;">Account Director</th>
                <th style="width: 60px;">Score</th>
                <th style="width: 80px;">Tier</th>
                <th style="width: 200px;">Accounts Managed</th>
                <th style="width: 80px;">Revenue</th>
                <th style="width: 60px;">CSAT</th>
                <th style="width: 60px;">Headcount</th>
                <th style="width: 60px;">Red Sites</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for rank, ad_data in enumerate(overall_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        
        if ad_data['avg'] >= 4.5:
            tier = '<span class="tier-badge tier-exceptional">EXCEPTIONAL</span>'
        elif ad_data['avg'] >= 4.0:
            tier = '<span class="tier-badge tier-strong">STRONG</span>'
        elif ad_data['avg'] >= 3.5:
            tier = '<span class="tier-badge tier-solid">SOLID</span>'
        else:
            tier = '<span class="tier-badge tier-development">DEVELOPMENT</span>'
        
        accounts_str = ", ".join(ad_data['accounts'][:3])
        if len(ad_data['accounts']) > 3:
            accounts_str += f" +{len(ad_data['accounts'])-3} more"
        
        revenue_str = format_currency(ad_data['revenue'])
        csat_str = f"{ad_data['csat']:.2f}" if ad_data['csat'] else "N/A"
        headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
        red_sites_str = str(ad_data['red_sites']) if ad_data['red_sites'] >= 0 else "0"
        
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td><strong>{ad_data['name']}</strong></td>
                <td><strong>{ad_data['total']}</strong> / 40</td>
                <td>{tier}</td>
                <td class="accounts-list">{accounts_str}</td>
                <td>{revenue_str}</td>
                <td>{csat_str}</td>
                <td>{headcount_str}</td>
                <td>{red_sites_str}</td>
            </tr>
"""
    
    html += """
        </tbody>
        </table>
    </div>
"""
    
    # FINANCIAL RANKINGS SECTIONS
    html += """
    <div class="section">
        <h2>Revenue Performance Rankings</h2>
        <p class="section-summary">Ranked by total portfolio revenue (December 2025). Top performers manage multi-million dollar accounts.</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 120px;">Total Revenue</th>
                    <th style="width: 80px;">Accounts</th>
                    <th style="width: 100px;">Perf Score</th>
                    <th style="width: 100px;">Rev/Employee</th>
                </tr>
            </thead>
            <tbody>
"""
    
    revenue_rankings = [ad for ad in overall_rankings if ad['revenue'] > 0]
    revenue_rankings.sort(key=lambda x: x['revenue'], reverse=True)
    
    for rank, ad_data in enumerate(revenue_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        rev_per_ee = ad_data['revenue'] / ad_data['headcount'] if ad_data['headcount'] > 0 else 0
        rev_per_ee_str = f"${rev_per_ee:.1f}K" if rev_per_ee > 0 else "N/A"
        
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td>{ad_data['name']}</td>
                <td><strong>{format_currency(ad_data['revenue'])}</strong></td>
                <td>{ad_data['num_accounts']}</td>
                <td>{ad_data['total']}/40</td>
                <td>{rev_per_ee_str}</td>
            </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Customer Satisfaction Rankings</h2>
        <p class="section-summary">CSAT scores (1.00-5.00 scale). Portfolio median: """ + f"{avg_csat:.2f}" + """. Top quartile: 4.75+</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 100px;">Avg CSAT</th>
                    <th style="width: 80px;">Accounts</th>
                    <th style="width: 100px;">Revenue</th>
                    <th style="width: 100px;">Perf Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    csat_rankings = [ad for ad in overall_rankings if ad['csat'] is not None]
    csat_rankings.sort(key=lambda x: x['csat'], reverse=True)
    
    for rank, ad_data in enumerate(csat_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td>{ad_data['name']}</td>
                <td><strong>{ad_data['csat']:.2f}</strong> / 5.00</td>
                <td>{ad_data['num_accounts']}</td>
                <td>{format_currency(ad_data['revenue'])}</td>
                <td>{ad_data['total']}/40</td>
            </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Year-over-Year Growth Rankings</h2>
        <p class="section-summary">YoY revenue growth rates (December 2025). Portfolio average: """ + f"{avg_growth:.1f}%" + """</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 100px;">Growth Rate</th>
                    <th style="width: 100px;">Revenue</th>
                    <th style="width: 80px;">Accounts</th>
                    <th style="width: 100px;">Perf Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    growth_rankings = [ad for ad in overall_rankings if ad['growth'] is not None]
    growth_rankings.sort(key=lambda x: x['growth'], reverse=True)
    
    for rank, ad_data in enumerate(growth_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        growth_color = "#10b981" if ad_data['growth'] > 0 else "#ef4444"
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td>{ad_data['name']}</td>
                <td style="color: {growth_color}; font-weight: 600;"><strong>+{ad_data['growth']:.1f}%</strong></td>
                <td>{format_currency(ad_data['revenue'])}</td>
                <td>{ad_data['num_accounts']}</td>
                <td>{ad_data['total']}/40</td>
            </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Operational Excellence - Red Sites</h2>
        <p class="section-summary">Sites with performance issues (lower is better). Green: 0-2, Yellow: 3-10, Red: 10+</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 100px;">Red Sites</th>
                    <th style="width: 100px;">Headcount</th>
                    <th style="width: 80px;">Accounts</th>
                    <th style="width: 100px;">Perf Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    red_sites_rankings = [ad for ad in overall_rankings if ad['red_sites'] is not None]
    red_sites_rankings.sort(key=lambda x: x['red_sites'])  # Lower is better
    
    for rank, ad_data in enumerate(red_sites_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        rs_color = "#10b981" if ad_data['red_sites'] <= 2 else "#ef4444" if ad_data['red_sites'] > 10 else "#f59e0b"
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td>{ad_data['name']}</td>
                <td style="color: {rs_color}; font-weight: 600;"><strong>{ad_data['red_sites']}</strong></td>
                <td>{ad_data['headcount']:,}</td>
                <td>{ad_data['num_accounts']}</td>
                <td>{ad_data['total']}/40</td>
            </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Workforce Management Rankings</h2>
        <p class="section-summary">Total employees managed across all accounts. Largest portfolios exceed 400 employees.</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 100px;">Headcount</th>
                    <th style="width: 100px;">Revenue</th>
                    <th style="width: 100px;">Rev/Employee</th>
                    <th style="width: 100px;">Perf Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    headcount_rankings = [ad for ad in overall_rankings if ad['headcount'] > 0]
    headcount_rankings.sort(key=lambda x: x['headcount'], reverse=True)
    
    for rank, ad_data in enumerate(headcount_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        rev_per_ee = ad_data['revenue'] / ad_data['headcount'] if ad_data['headcount'] > 0 else 0
        rev_per_ee_str = f"${rev_per_ee:.1f}K" if rev_per_ee > 0 else "N/A"
        
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td>{ad_data['name']}</td>
                <td><strong>{ad_data['headcount']:,}</strong></td>
                <td>{format_currency(ad_data['revenue'])}</td>
                <td>{rev_per_ee_str}</td>
                <td>{ad_data['total']}/40</td>
            </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    </div> <!-- Close report-content -->
    
    <script>
        // Set your password here (case-sensitive)
        const REPORT_PASSWORD = "SBM2025";
        
        // Check password function
        function checkPassword() {
            const input = document.getElementById('passwordInput');
            const overlay = document.getElementById('passwordOverlay');
            const content = document.getElementById('reportContent');
            const error = document.getElementById('passwordError');
            
            if (input.value === REPORT_PASSWORD) {
                overlay.style.display = 'none';
                content.classList.add('unlocked');
                error.style.display = 'none';
            } else {
                error.style.display = 'block';
                input.value = '';
                input.focus();
            }
        }
        
        // Allow Enter key to submit
        document.getElementById('passwordInput').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                checkPassword();
            }
        });
        
        // Focus input on load
        window.addEventListener('load', function() {
            document.getElementById('passwordInput').focus();
        });
    </script>
</body>
</html>
"""
    
    return html

# Main execution
if __name__ == "__main__":
    print("Generating Enhanced EOY Report with Financial KPIs...")
    
    print("Loading performance review data...")
    df = load_performance_data()
    
    print("Loading financial data from AD CSVs...")
    financial_data = load_financial_data()
    print(f"  - Loaded financial data for {len(financial_data)} ADs")
    
    print("Calculating performance rankings...")
    rankings = calculate_rankings(df)
    
    print("Generating enhanced HTML report...")
    html_content = generate_enhanced_html(rankings, df, financial_data)
    
    print("Writing report file...")
    with open("EOY_Report_2025_Enhanced.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("\nSUCCESS! Enhanced report generated: EOY_Report_2025_Enhanced.html")
    print("  - Performance scores + Financial KPIs integrated")
    print("  - 5 new financial ranking sections added")
    print("  - Accounts managed listed for each AD")
    print("\nTo convert to PDF, run:")
    print("  python convert_to_pdf.py")
