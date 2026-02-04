"""
Generate Enhanced EOY Account Director Review Report with Financial KPIs
"""
import pandas as pd
import json
from collections import defaultdict
from pathlib import Path

def normalize_ad_name(name):
    """Normalize AD names to ensure consistent matching"""
    if not name or pd.isna(name):
        return ""
    
    # Name normalization mapping
    name_map = {
        # Remove possessive
        "Logan Newman's": "Logan Newman",
        
        # Standardize David/Dave
        "Dave Pergola": "David Pergola",
        "Pergola, David": "David Pergola",
        
        # Standardize Gregory/Greg DeMedio
        "Greg DeMedio": "Gregory DeMedio",
        "Greg Demedio": "Gregory DeMedio",
        "Gregory Demedio": "Gregory DeMedio",
        
        # Other variations
        "Nick Trenkamp": "Nicholas Trenkamp",
        "Nike Trenkamp": "Nicholas Trenkamp",
        "Ayesha Nasi": "Ayesha Nasir",
        "Gisell Langelier": "Giselle Langelier",
        "Collen Doles": "Colleen Doles",
        "RJ Ober": "Russell Ober",
        "Sid Shah": "Siddarth Shah",
        "Mike Barry": "Michael Barry",
        "Peggy McElwee": "Peggy Shum",
    }
    
    name_str = str(name).strip()
    return name_map.get(name_str, name_str)

def calculate_letter_grade(score):
    """Calculate letter grade based on total score out of 40"""
    if score >= 39.0:
        return "A+"
    elif score >= 37.0:
        return "A"
    elif score >= 35.0:
        return "A-"
    elif score >= 34.0:
        return "B+"
    elif score >= 32.0:
        return "B"
    elif score >= 30.0:
        return "B-"
    elif score >= 28.0:
        return "C+"
    elif score >= 26.0:
        return "C"
    elif score >= 24.0:
        return "C-"
    elif score >= 20.0:
        return "D"
    else:
        return "F"

def get_grade_class(letter_grade):
    """Get CSS class for letter grade color"""
    if not letter_grade or letter_grade == "N/A":
        return "tier-badge"
    
    first_letter = letter_grade[0].upper()
    if first_letter == 'A':
        return "tier-badge grade-a"
    elif first_letter == 'B':
        return "tier-badge grade-b"
    elif first_letter == 'C':
        return "tier-badge grade-c"
    elif first_letter == 'D':
        return "tier-badge grade-d"
    elif first_letter == 'F':
        return "tier-badge grade-f"
    else:
        return "tier-badge"

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
                new_row["Account Director Name"] = normalize_ad_name(name)
                expanded_rows.append(new_row)
        else:
            row["Account Director Name"] = normalize_ad_name(ad_name)
            expanded_rows.append(row)
    
    return pd.DataFrame(expanded_rows)

def load_financial_data():
    """Load all AD CSV files and aggregate financial metrics"""
    ad_csvs_dir = Path("data/ad_csvs")
    ad_financial_data = {}
    
    for csv_file in ad_csvs_dir.glob("*.csv"):
        # Convert filename to AD name (e.g., "aaron-simpson.csv" -> "Aaron Simpson")
        ad_name = csv_file.stem.replace('-', ' ').title()
        # Normalize the name
        ad_name = normalize_ad_name(ad_name)
        
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
            account_revenues = {}  # Track revenue per account for sorting
            
            for account in accounts:
                account_df = df[df['Account'] == account]
                
                # Revenue
                account_revenue = 0
                rev_row = account_df[account_df['KPI'] == 'Revenue ($)']
                if not rev_row.empty and 'Dec-25' in rev_row.columns:
                    val = rev_row['Dec-25'].values[0]
                    cleaned_val = clean_numeric_value(val)
                    if cleaned_val is not None:
                        account_revenue = cleaned_val
                        revenue_total += cleaned_val
                account_revenues[account] = account_revenue
                
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
            
            # Sort accounts by revenue (biggest to smallest)
            sorted_accounts = sorted(accounts, key=lambda x: account_revenues.get(x, 0), reverse=True)
            
            ad_financial_data[ad_name] = {
                'accounts': sorted_accounts,
                'num_accounts': len(sorted_accounts),
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

def load_tier_data():
    """Load tier assignments, vertical, and scorecard data from verticals.csv"""
    try:
        df = pd.read_csv("data/verticals.csv")
        tier_data = {}
        vertical_data = {}
        scorecard_data = {}
        for _, row in df.iterrows():
            ad_name = str(row.get("Account Director", "")).strip()
            tier = str(row.get("Tier", "")).strip()
            vertical = str(row.get("Vertical", "")).strip()
            scorecard = row.get("Scorecard", "")
            if ad_name:
                # Normalize the name
                normalized_name = normalize_ad_name(ad_name)
                if tier:
                    tier_data[normalized_name] = tier
                if vertical:
                    vertical_data[normalized_name] = vertical
                # Add scorecard if available
                if pd.notna(scorecard) and scorecard != "":
                    try:
                        scorecard_data[normalized_name] = float(scorecard)
                    except:
                        pass
        return tier_data, vertical_data, scorecard_data
    except Exception as e:
        print(f"Warning: Could not load tier data: {e}")
        return {}, {}, {}

def apply_manual_mappings(financial_data):
    """Apply manual mappings for ADs with special cases"""
    
    # Rade Kukobat → Use Eli Lilly data
    if "Eli Lilly" in financial_data:
        financial_data["Rade Kukobat"] = financial_data["Eli Lilly"].copy()
        print("  - Mapped Rade Kukobat to Eli Lilly")
    
    # David Pergola & Justin Homa → Calculate from Merck headcount ratio
    # Brian Davis Merck Dec-25: Revenue=$4,077K, Headcount=345
    # Revenue per employee = $11.82K
    merck_rev_per_employee = 4077 / 345  # $11.82K per employee
    
    # David Pergola: 135 headcount (Merck Sodexo)
    david_headcount = 135
    david_revenue = david_headcount * merck_rev_per_employee
    financial_data["David Pergola"] = {
        'accounts': ['Merck Sodexo'],
        'num_accounts': 1,
        'revenue_total': david_revenue,
        'csat_avg': 4.75,  # Use Brian's Merck CSAT
        'headcount_total': david_headcount,
        'red_sites_count': 0,  # Estimated
        'growth_avg': 8.9,  # Use Brian's Merck growth
        'calculated_revenue': True  # Flag for asterisk
    }
    print(f"  - Mapped David Pergola: {david_headcount} HC = ${david_revenue:.0f}K revenue (Merck Sodexo)")
    
    # Justin Homa: Keep Organon data + ADD Merck CBRE calculation
    justin_headcount_merck = 155
    justin_revenue_merck = justin_headcount_merck * merck_rev_per_employee
    
    if "Justin Homa" in financial_data:
        # Add Merck CBRE to existing Organon data
        organon_data = financial_data["Justin Homa"]
        financial_data["Justin Homa"] = {
            'accounts': ['Merck CBRE', 'Organon'],
            'num_accounts': 2,
            'revenue_total': justin_revenue_merck + organon_data.get('revenue_total', 0),
            'csat_avg': 4.75,  # Use Merck CSAT
            'headcount_total': justin_headcount_merck + organon_data.get('headcount_total', 0),
            'red_sites_count': organon_data.get('red_sites_count', 0),
            'growth_avg': 8.9,
            'calculated_revenue': True  # Flag for asterisk
        }
        print(f"  - Mapped Justin Homa: Merck CBRE ({justin_headcount_merck} HC) + Organon = ${financial_data['Justin Homa']['revenue_total']:.0f}K total")
    
    # Headcount overrides (AD-confirmed adjustments)
    headcount_overrides = {
        'Jack Thornton': 79,
    }
    
    for ad_name, confirmed_headcount in headcount_overrides.items():
        if ad_name in financial_data:
            old_headcount = financial_data[ad_name]['headcount_total']
            financial_data[ad_name]['headcount_total'] = confirmed_headcount
            financial_data[ad_name]['headcount_adjusted'] = True  # Flag for asterisk
            print(f"  - Adjusted {ad_name} headcount: {old_headcount} -> {confirmed_headcount} (AD-confirmed)")
    
    # Account reassignments (transfer accounts between ADs)
    
    # Stuart Kelloff: Add Adobe (transfer from Rosalvina Quinonez)
    # Adobe: $855K revenue, 106 HC
    if "Stuart Kelloff" in financial_data:
        adobe_revenue = 855
        adobe_headcount = 106
        stuart_data = financial_data["Stuart Kelloff"]
        financial_data["Stuart Kelloff"] = {
            'accounts': stuart_data.get('accounts', []) + ['Adobe Systems'],
            'num_accounts': stuart_data.get('num_accounts', 0) + 1,
            'revenue_total': stuart_data.get('revenue_total', 0) + adobe_revenue,
            'csat_avg': stuart_data.get('csat_avg', 4.5),
            'headcount_total': stuart_data.get('headcount_total', 0) + adobe_headcount,
            'red_sites_count': stuart_data.get('red_sites_count', 0),
            'growth_avg': stuart_data.get('growth_avg', 0)
        }
        print(f"  - Added Adobe Systems to Stuart Kelloff: +${adobe_revenue}K, +{adobe_headcount} HC")
    
    # Grant Frazier: Assign Meta (from Luna Duarte)
    # Meta: $4,176K revenue, 437 HC
    financial_data["Grant Frazier"] = {
        'accounts': ['Meta'],
        'num_accounts': 1,
        'revenue_total': 4176,
        'csat_avg': 4.74,
        'headcount_total': 437,
        'red_sites_count': 1,
        'growth_avg': 30.9
    }
    print(f"  - Assigned Meta to Grant Frazier: $4,176K, 437 HC")
    
    # Taylor Wattenberg: Assign Microsoft (from TBH)
    # Microsoft: $5,376K revenue, 600 HC
    financial_data["Taylor Wattenberg"] = {
        'accounts': ['Microsoft'],
        'num_accounts': 1,
        'revenue_total': 5376,
        'csat_avg': 4.66,
        'headcount_total': 600,
        'red_sites_count': 4,
        'growth_avg': 28.1
    }
    print(f"  - Assigned Microsoft to Taylor Wattenberg: $5,376K, 600 HC")
    
    # Rade Kukobat: Assign Eli Lilly LCC/LRL
    # Calculate revenue based on Chad Boulton's Eli Lilly account ratio
    # Chad: $2,075K revenue / 399 HC = $5.20K per HC
    # Rade: 83 HC × $5.20K = $431.5K
    eli_lilly_rev_per_hc = 2075 / 399  # Chad's Eli Lilly ratio
    rade_headcount = 83
    rade_revenue = eli_lilly_rev_per_hc * rade_headcount
    
    financial_data["Rade Kukobat"] = {
        'accounts': ['Eli Lilly LCC/LRL'],
        'num_accounts': 1,
        'revenue_total': rade_revenue,
        'csat_avg': 2.25,
        'headcount_total': rade_headcount,
        'red_sites_count': 1,
        'growth_avg': 55.4,
        'headcount_adjusted': True,  # Flag for asterisk - AD confirmed
        'calculated_revenue': True   # Flag for asterisk - calculated from ratio
    }
    print(f"  - Assigned Eli Lilly LCC/LRL to Rade Kukobat: ${rade_revenue:.0f}K, {rade_headcount} HC (calculated from Chad's ratio)")
    
    # Isaac Calderon: Use actual audited headcount (285 instead of 340)
    if "Isaac Calderon" in financial_data:
        isaac_data = financial_data["Isaac Calderon"]
        # Keep all existing data but update headcount to audited value
        financial_data["Isaac Calderon"]['headcount_total'] = 285
        print(f"  - Corrected Isaac Calderon headcount to 285 (from audit)")
    
    # Giselle Langelier: Add accounts (Medtronic, Capsida, Fuji Film)
    financial_data["Giselle Langelier"] = {
        'accounts': ['Medtronic', 'Capsida Biotherapeutics', 'Fuji Film'],
        'num_accounts': 3,
        'revenue_total': 672,
        'csat_avg': 4.59,  # Average from the three accounts
        'headcount_total': 98,
        'red_sites_count': 2,
        'growth_avg': 5.0
    }
    print(f"  - Assigned accounts to Giselle Langelier: $672K, 98 HC")
    
    # Peggy Shum: Add accounts (Chubb Insurance, Deutsche Bank)
    financial_data["Peggy Shum"] = {
        'accounts': ['Chubb Insurance', 'Deutsche Bank'],
        'num_accounts': 2,
        'revenue_total': 547,
        'csat_avg': 4.50,  # Estimated
        'headcount_total': 67,
        'red_sites_count': 0,
        'growth_avg': 0
    }
    print(f"  - Assigned accounts to Peggy Shum: $547K, 67 HC")
    
    # Gregory DeMedio: Add Abbott Labs (from LIFE SCIENCE.csv)
    financial_data["Gregory DeMedio"] = {
        'accounts': ['Abbott Labs'],
        'num_accounts': 1,
        'revenue_total': 1713,
        'csat_avg': 4.49,
        'headcount_total': 278,
        'red_sites_count': 10,
        'growth_avg': 0.8
    }
    print(f"  - Assigned Abbott Labs to Gregory DeMedio: $1,713K, 278 HC")
    
    # Keith Deuber: Assign Amazon (same as Dustin Smith)
    # Amazon: $3,140K revenue, 733 HC (from dustin-smith.csv Dec-25 data)
    financial_data["Keith Deuber"] = {
        'accounts': ['Amazon'],
        'num_accounts': 1,
        'revenue_total': 3140,
        'csat_avg': 4.76,
        'headcount_total': 733,
        'red_sites_count': 16,
        'growth_avg': -38.7
    }
    print(f"  - Assigned Amazon to Keith Deuber: $3,140K, 733 HC")
    
    return financial_data

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

def generate_enhanced_html(rankings, df, financial_data, tier_data, scorecard_data):
    """Generate enhanced HTML with tier-based rankings"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 Account Director Performance Review</title>
    <style>
        @page {
            margin: 0.6in 0.5in;
            size: letter;
        }
        
        * {
            box-sizing: border-box;
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.4;
            color: #1a1a1a;
            max-width: 100%;
            margin: 0;
            padding: 0;
            background: white;
            font-size: 9pt;
        }
        
        h1 {
            color: #1a1a1a;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 8px;
            font-size: 22pt;
            margin: 0 0 8px 0;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        h2 {
            color: #1a1a1a;
            font-size: 13pt;
            margin: 0 0 6px 0;
            page-break-after: avoid;
            font-weight: 700;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 4px;
            letter-spacing: -0.3px;
        }
        
        h2.first-section {
            margin-top: 0;
        }
        
        h3 {
            color: #4b5563;
            font-size: 10pt;
            margin: 12px 0 6px 0;
            font-weight: 600;
        }
        
        .subtitle {
            font-size: 9pt;
            color: #6b7280;
            margin-bottom: 12px;
            line-height: 1.3;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 6px 0 0 0;
            font-size: 7.5pt;
            border: 1px solid #d1d5db;
            page-break-inside: auto;
        }
        
        thead {
            display: table-header-group;
        }
        
        tbody {
            display: table-row-group;
        }
        
        th {
            background: #1f2937;
            color: white;
            padding: 7px 5px;
            text-align: left;
            font-weight: 700;
            font-size: 7.5pt;
            border-bottom: 2px solid #111827;
            border-right: 1px solid #374151;
            letter-spacing: 0.2px;
        }
        
        th:last-child {
            border-right: none;
        }
        
        td {
            padding: 5px;
            border-bottom: 1px solid #e5e7eb;
            border-right: 1px solid #f3f4f6;
            vertical-align: top;
        }
        
        td:last-child {
            border-right: none;
        }
        
        tr {
            page-break-inside: avoid;
        }
        
        tr:hover {
            background: #fafafa;
        }
        
        tbody tr:last-child td {
            border-bottom: 1px solid #d1d5db;
        }
        
        .rank-1 { 
            border-left: 4px solid #10b981;
            background: #ecfdf5 !important;
        }
        .rank-2 { 
            border-left: 4px solid #3b82f6;
            background: #eff6ff !important;
        }
        .rank-3 { 
            border-left: 4px solid #8b5cf6;
            background: #f5f3ff !important;
        }
        
        .tier-badge {
            display: inline-block;
            padding: 3px 7px;
            border-radius: 3px;
            font-size: 7pt;
            font-weight: 700;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }
        
        /* Letter Grade Colors */
        .grade-a {
            background: #10b981;
            color: white;
        }
        
        .grade-b {
            background: #3b82f6;
            color: white;
        }
        
        .grade-c {
            background: #f59e0b;
            color: white;
        }
        
        .grade-d {
            background: #ef4444;
            color: white;
        }
        
        .grade-f {
            background: #dc2626;
            color: white;
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
            page-break-inside: avoid;
            margin-bottom: 0;
        }
        
        .accounts-list {
            font-size: 6.5pt;
            color: #6b7280;
            line-height: 1.4;
        }
        
        .section-summary {
            font-size: 8pt;
            color: #6b7280;
            margin: -2px 0 8px 0;
            font-style: italic;
            line-height: 1.3;
        }
        
        /* ===== LANDING PAGE STYLES ===== */
        .landing-page {
            page-break-after: always;
            padding: 20px;
        }
        
        .landing-header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px 0;
            border-bottom: 3px solid #2563eb;
        }
        
        .landing-title {
            font-size: 32pt;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0 0 10px 0;
            letter-spacing: -1px;
            line-height: 1.2;
        }
        
        .landing-subtitle {
            font-size: 12pt;
            color: #6b7280;
            margin: 0;
            font-weight: 500;
        }
        
        .landing-content {
            max-width: 100%;
        }
        
        .intro-box {
            background: #f8fafc;
            border-left: 4px solid #2563eb;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .intro-box h3 {
            margin-top: 0;
            color: #1a1a1a;
            font-size: 11pt;
        }
        
        .intro-box p {
            margin: 5px 0 0 0;
            font-size: 9pt;
            line-height: 1.5;
        }
        
        .views-section {
            margin: 25px 0;
        }
        
        .views-section > p {
            font-size: 9pt;
            margin-bottom: 15px;
        }
        
        .view-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 15px 0;
        }
        
        .view-card {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }
        
        .view-icon {
            font-size: 24pt;
            margin-bottom: 8px;
        }
        
        .view-title {
            font-weight: 700;
            font-size: 9.5pt;
            color: #1a1a1a;
            margin-bottom: 4px;
        }
        
        .view-desc {
            font-size: 8pt;
            color: #6b7280;
            line-height: 1.3;
        }
        
        .tier-definitions {
            margin: 25px 0;
        }
        
        .tier-def-section {
            margin: 20px 0;
            background: #fafafa;
            padding: 15px;
            border-radius: 6px;
        }
        
        .tier-def-section h3 {
            margin-top: 0;
            font-size: 11pt;
            color: #1a1a1a;
        }
        
        .tier-note {
            font-size: 8pt;
            color: #6b7280;
            font-style: italic;
            margin: 5px 0 10px 0;
        }
        
        .tier-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .tier-def-item {
            background: white;
            padding: 8px 10px;
            border-radius: 4px;
            border: 1px solid #e5e7eb;
            font-size: 8pt;
            text-align: center;
        }
        
        .tier-label {
            font-weight: 700;
            color: #2563eb;
            display: inline-block;
            margin-right: 4px;
        }
        
        .metrics-overview {
            margin: 25px 0;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        
        .metric-box {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24pt;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 9pt;
            font-weight: 600;
            margin-bottom: 3px;
        }
        
        .metric-sublabel {
            font-size: 7.5pt;
            opacity: 0.9;
        }
        
        .footnote {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
            font-size: 7.5pt;
            color: #6b7280;
        }
        
        .footnote p {
            margin: 3px 0;
        }
        
        /* ===== CONSOLIDATED TIER SECTIONS ===== */
        .tier-container {
            page-break-after: always;
        }
        
        .tier-subsection {
            margin-bottom: 25px;
        }
        
        .tier-subsection:last-child {
            margin-bottom: 0;
        }
        
        .tier-subsection h2 {
            font-size: 12pt;
            margin-bottom: 5px;
        }
        
        .tier-subsection .section-summary {
            font-size: 7.5pt;
            margin-bottom: 6px;
        }
        
        .tier-subsection table {
            font-size: 7pt;
        }
        
        .tier-subsection th {
            padding: 5px 4px;
            font-size: 7pt;
        }
        
        .tier-subsection td {
            padding: 4px;
        }
        
        @media print {
            body {
                margin: 0;
                padding: 0;
            }
            
            .section { 
                page-break-after: always;
                page-break-inside: avoid;
            }
            
            .section:last-child {
                page-break-after: auto;
            }
            
            table { 
                page-break-inside: auto;
            }
            
            tr { 
                page-break-inside: avoid;
                page-break-after: auto;
            }
            
            thead { 
                display: table-header-group;
            }
            
            h1, h2, h3 {
                page-break-after: avoid;
                page-break-inside: avoid;
            }
            
            .section-summary {
                page-break-after: avoid;
            }
            
            .password-overlay { 
                display: none !important;
            }
            
            .report-content {
                display: block !important;
            }
            
            /* Ensure colors print properly */
            * {
                print-color-adjust: exact !important;
                -webkit-print-color-adjust: exact !important;
            }
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
    
    <!-- LANDING PAGE / EXECUTIVE SUMMARY -->
    <div class="landing-page">
        <div class="landing-header">
            <h1 class="landing-title">2025 Account Director<br>Performance Review</h1>
            <p class="landing-subtitle">Comprehensive Year-End Analysis | December 2025</p>
        </div>
        
        <div class="landing-content">
            <div class="views-section">
                <h3>🔍 Report Views & Structure</h3>
                <p>This report presents performance data through multiple lenses for comprehensive analysis:</p>
                
                <div class="view-grid">
                    <div class="view-card">
                        <div class="view-icon">🎯</div>
                        <div class="view-title">Overall Rankings</div>
                        <div class="view-desc">All ADs ranked by performance score (out of 40 points)</div>
                    </div>
                    
                    <div class="view-card">
                        <div class="view-icon">💰</div>
                        <div class="view-title">Revenue Tiers</div>
                        <div class="view-desc">6 tiers grouped by account revenue size</div>
                    </div>
                    
                    <div class="view-card">
                        <div class="view-icon">🏢</div>
                        <div class="view-title">Vertical Views</div>
                        <div class="view-desc">5 industry verticals (Manufacturing, Life Science, Technology, Distribution, Finance)</div>
                    </div>
                    
                    <div class="view-card">
                        <div class="view-icon">👥</div>
                        <div class="view-title">Headcount Tiers</div>
                        <div class="view-desc">Tier 4-6 grouped by account size (employees managed)</div>
                    </div>
                </div>
            </div>
            
            <div class="tier-definitions">
                <div class="tier-def-section">
                    <h3>💰 Revenue Tier Definitions</h3>
                    <div class="tier-grid">
                        <div class="tier-def-item"><span class="tier-label">Tier 1</span> &lt; $100K</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 2</span> $100K - $500K</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 3</span> $500K - $750K</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 4</span> $750K - $1M</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 5</span> $1M - $1.5M</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 6</span> &gt; $1.5M</div>
                    </div>
                </div>
                
                <div class="tier-def-section">
                    <h3>👥 Headcount Tier Definitions</h3>
                    <p class="tier-note">Account Directors are assigned tiers based on total employees under management</p>
                    <div class="tier-grid">
                        <div class="tier-def-item"><span class="tier-label">Tier 1</span> 1-28 employees</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 2</span> 29-39 employees</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 3</span> 40-50 employees</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 4</span> 51-100 employees</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 5</span> 101-250 employees</div>
                        <div class="tier-def-item"><span class="tier-label">Tier 6</span> 250+ employees</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- OVERALL PERFORMANCE RANKINGS -->
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
        
        # Get tier data
        tier = tier_data.get(ad_name, "Unassigned")
        
        # Get vertical data
        vertical = vertical_data.get(ad_name, "Unassigned")
        
        # Calculate letter grade
        letter_grade = calculate_letter_grade(total_out_of_40)
        
        # Get scorecard data (use from verticals.csv if available, otherwise use csat_avg)
        scorecard = scorecard_data.get(ad_name, fin_data.get('csat_avg'))
        
        overall_rankings.append({
            "name": ad_name,
            "avg": round(avg, 2),
            "total": round(total_out_of_40, 1),
            "tier": tier,
            "vertical": vertical,
            "letter_grade": letter_grade,
            "accounts": fin_data.get('accounts', []),
            "num_accounts": fin_data.get('num_accounts', 0),
            "revenue": fin_data.get('revenue_total', 0),
            "scorecard": scorecard,
            "headcount": fin_data.get('headcount_total', 0),
            "growth": fin_data.get('growth_avg'),
            "calculated_revenue": fin_data.get('calculated_revenue', False),
            "headcount_adjusted": fin_data.get('headcount_adjusted', False)
        })
    
    overall_rankings.sort(key=lambda x: x["total"], reverse=True)
    
    # ==================== CREATE ALL GROUPINGS ====================
    # Revenue tier groups
    revenue_tier_groups = {
        "Tier 1 (< $100K)": [],
        "Tier 2 ($100K - $500K)": [],
        "Tier 3 ($500K - $750K)": [],
        "Tier 4 ($750K - $1M)": [],
        "Tier 5 ($1M - $1.5M)": [],
        "Tier 6 (> $1.5M)": []
    }
    
    for ad in overall_rankings:
        revenue = ad.get('revenue', 0)
        if revenue < 100:
            revenue_tier_groups["Tier 1 (< $100K)"].append(ad)
        elif revenue < 500:
            revenue_tier_groups["Tier 2 ($100K - $500K)"].append(ad)
        elif revenue < 750:
            revenue_tier_groups["Tier 3 ($500K - $750K)"].append(ad)
        elif revenue < 1000:
            revenue_tier_groups["Tier 4 ($750K - $1M)"].append(ad)
        elif revenue < 1500:
            revenue_tier_groups["Tier 5 ($1M - $1.5M)"].append(ad)
        else:
            revenue_tier_groups["Tier 6 (> $1.5M)"].append(ad)
    
    # Sort each revenue tier by performance score
    for tier in revenue_tier_groups:
        revenue_tier_groups[tier].sort(key=lambda x: x['total'], reverse=True)
    
    # Vertical groups
    vertical_groups = {
        "Manufacturing": [],
        "Life Science": [],
        "Technology": [],
        "Distribution": [],
        "Finance": []
    }
    
    # #region agent log
    vertical_sample = []
    # #endregion
    
    for ad in overall_rankings:
        vertical = ad.get('vertical', 'Unassigned')
        
        # #region agent log
        if len(vertical_sample) < 10:
            vertical_sample.append({"name": ad.get('name'), "vertical": vertical, "in_groups": vertical in vertical_groups})
        # #endregion
        
        if vertical in vertical_groups:
            vertical_groups[vertical].append(ad)
    
    # #region agent log
    with open(r'c:\Users\abelg\OneDrive\Desktop\Account-Directors\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"location":"generate_enhanced_report.py:1206","message":"After populating vertical_groups","data":{"vertical_sample":vertical_sample,"vertical_groups_sizes_after":{k:len(v) for k,v in vertical_groups.items()}},"timestamp":__import__('time').time()*1000,"sessionId":"debug-session","hypothesisId":"F"})+'\n')
    # #endregion
    
    # Sort each vertical by performance score
    for vertical in vertical_groups:
        vertical_groups[vertical].sort(key=lambda x: x['total'], reverse=True)
    
    # Performance tier groups
    tier_groups = {
        "Tier 4": [],
        "Tier 5": [],
        "Tier 6": []
    }
    
    for ad in overall_rankings:
        tier = ad.get('tier', 'Unassigned')
        if tier in tier_groups:
            tier_groups[tier].append(ad)
    
    # Sort each tier by performance score
    for tier in tier_groups:
        tier_groups[tier].sort(key=lambda x: x['total'], reverse=True)
    
    # Calculate portfolio-wide metrics for other sections
    total_revenue = sum(ad['revenue'] for ad in overall_rankings if ad['revenue'] > 0)
    total_headcount = sum(ad['headcount'] for ad in overall_rankings if ad['headcount'] > 0)
    avg_score = sum(ad['total'] for ad in overall_rankings) / len(overall_rankings) if overall_rankings else 0
    avg_scorecard = sum(ad['scorecard'] for ad in overall_rankings if ad['scorecard']) / len([ad for ad in overall_rankings if ad['scorecard']]) if any(ad['scorecard'] for ad in overall_rankings) else 0
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
                <th style="width: 80px;">Performance Grade</th>
                <th style="width: 200px;">Accounts Managed</th>
                <th style="width: 80px;">Revenue</th>
                <th style="width: 60px;">Scorecard</th>
                <th style="width: 60px;">Headcount</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for rank, ad_data in enumerate(overall_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        
        # Get letter grade and apply badge styling
        letter_grade = ad_data['letter_grade']
        if letter_grade.startswith('A'):
            grade_badge = f'<span class="{get_grade_class(letter_grade)}">{letter_grade}</span>'
        elif letter_grade.startswith('B'):
            grade_badge = f'<span class="tier-badge tier-strong">{letter_grade}</span>'
        elif letter_grade.startswith('C'):
            grade_badge = f'<span class="tier-badge tier-solid">{letter_grade}</span>'
        else:
            grade_badge = f'<span class="tier-badge tier-development">{letter_grade}</span>'
        
        accounts_str = ", ".join(ad_data['accounts'][:3])
        if len(ad_data['accounts']) > 3:
            accounts_str += f" +{len(ad_data['accounts'])-3} more"
        
        revenue_str = format_currency(ad_data['revenue'])
        if ad_data.get('calculated_revenue'):
            revenue_str += "*"
        
        # Format scorecard value
        if ad_data.get('scorecard') is not None:
            scorecard_str = f"{ad_data['scorecard']:.2f}"
        else:
            scorecard_str = "N/A"
        
        headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
        if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
            headcount_str += "*"
        
        html += f"""
            <tr class="{row_class}">
                <td><strong>#{rank}</strong></td>
                <td><strong>{ad_data['name']}</strong></td>
                <td><strong>{ad_data['total']}</strong> / 40</td>
                <td>{grade_badge}</td>
                <td class="accounts-list">{accounts_str}</td>
                <td>{revenue_str}</td>
                <td>{scorecard_str}</td>
                <td>{headcount_str}</td>
            </tr>
"""
    
    html += """
        </tbody>
        </table>
    </div>
"""
    
    # ==================== REVENUE TIER SECTIONS ====================
    # Skip Tier 1 (< $100K), Consolidate Revenue Tiers 2, 3, 4 on one page
    tier_groups_page1 = ["Tier 2 ($100K - $500K)", "Tier 3 ($500K - $750K)", "Tier 4 ($750K - $1M)"]
    has_page1_content = any(revenue_tier_groups[t] for t in tier_groups_page1)
    
    if has_page1_content:
        html += '<div class="tier-container">\n'
        
        for tier_name in tier_groups_page1:
            tier_ads = revenue_tier_groups[tier_name]
            if not tier_ads:
                continue
            
            tier_avg_score = sum(ad['total'] for ad in tier_ads) / len(tier_ads) if tier_ads else 0
            tier_total_revenue = sum(ad['revenue'] for ad in tier_ads if ad['revenue'] > 0)
            tier_total_headcount = sum(ad['headcount'] for ad in tier_ads if ad['headcount'] > 0)
            
            html += f"""
    <div class="tier-subsection">
        <h2>Revenue {tier_name}</h2>
        <p class="section-summary">
            {len(tier_ads)} Account Directors | Avg Performance Score: {tier_avg_score:.1f}/40 | 
            Combined Revenue: {format_currency(tier_total_revenue)} | Total Headcount: {tier_total_headcount:,}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 70px;">Grade</th>
                    <th style="width: 50px;">Score</th>
                    <th style="width: 160px;">Accounts Managed</th>
                    <th style="width: 70px;">Revenue</th>
                    <th style="width: 50px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for rank, ad_data in enumerate(tier_ads, 1):
                row_class = f"rank-{rank}" if rank <= 3 else ""
                letter_grade = ad_data.get('letter_grade', 'N/A')
                grade_badge = f'<span class="{get_grade_class(letter_grade)}">{letter_grade}</span>'
                
                accounts_str = ", ".join(ad_data['accounts'][:3])
                if len(ad_data['accounts']) > 3:
                    accounts_str += f" +{len(ad_data['accounts'])-3} more"
                
                revenue_str = format_currency(ad_data['revenue'])
                if ad_data.get('calculated_revenue'):
                    revenue_str += "*"
                
                headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
                if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                    headcount_str += "*"
                
                html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td>{grade_badge}</td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>{scorecard_str}</td>
                    <td>{headcount_str}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += '</div>\n'
    
    # Consolidate Revenue Tiers 5, 6 on one page
    tier_groups_page2 = ["Tier 5 ($1M - $1.5M)", "Tier 6 (> $1.5M)"]
    has_page2_content = any(revenue_tier_groups[t] for t in tier_groups_page2)
    
    if has_page2_content:
        html += '<div class="tier-container">\n'
        
        for tier_name in tier_groups_page2:
            tier_ads = revenue_tier_groups[tier_name]
            if not tier_ads:
                continue
            
            tier_avg_score = sum(ad['total'] for ad in tier_ads) / len(tier_ads) if tier_ads else 0
            tier_total_revenue = sum(ad['revenue'] for ad in tier_ads if ad['revenue'] > 0)
            tier_total_headcount = sum(ad['headcount'] for ad in tier_ads if ad['headcount'] > 0)
            
            html += f"""
    <div class="tier-subsection">
        <h2>Revenue {tier_name}</h2>
        <p class="section-summary">
            {len(tier_ads)} Account Directors | Avg Performance Score: {tier_avg_score:.1f}/40 | 
            Combined Revenue: {format_currency(tier_total_revenue)} | Total Headcount: {tier_total_headcount:,}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 70px;">Grade</th>
                    <th style="width: 50px;">Score</th>
                    <th style="width: 160px;">Accounts Managed</th>
                    <th style="width: 70px;">Revenue</th>
                    <th style="width: 50px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for rank, ad_data in enumerate(tier_ads, 1):
                row_class = f"rank-{rank}" if rank <= 3 else ""
                letter_grade = ad_data.get('letter_grade', 'N/A')
                grade_badge = f'<span class="{get_grade_class(letter_grade)}">{letter_grade}</span>'
                
                accounts_str = ", ".join(ad_data['accounts'][:3])
                if len(ad_data['accounts']) > 3:
                    accounts_str += f" +{len(ad_data['accounts'])-3} more"
                
                revenue_str = format_currency(ad_data['revenue'])
                if ad_data.get('calculated_revenue'):
                    revenue_str += "*"
                
                headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
                if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                    headcount_str += "*"
                
                html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td>{grade_badge}</td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>{scorecard_str}</td>
                    <td>{headcount_str}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += '</div>\n'

    
    # VERTICAL SECTIONS MOVED TO END OF REPORT (after headcount tiers)
    
    # ==================== HEADCOUNT TIER-BASED RANKINGS ====================
    # TIER-BASED RANKINGS SECTIONS (Performance Tiers from verticals.csv)
    # Consolidate Tier 4 and 5 on one page
    perf_tier_groups_page1 = ["Tier 4", "Tier 5"]
    has_perf_page1 = any(tier_groups[t] for t in perf_tier_groups_page1)
    
    if has_perf_page1:
        html += '<div class="tier-container">\n'
        
        for tier_name in perf_tier_groups_page1:
            tier_ads = tier_groups[tier_name]
            if not tier_ads:
                continue
            
            tier_avg_score = sum(ad['total'] for ad in tier_ads) / len(tier_ads) if tier_ads else 0
            tier_total_revenue = sum(ad['revenue'] for ad in tier_ads if ad['revenue'] > 0)
            tier_total_headcount = sum(ad['headcount'] for ad in tier_ads if ad['headcount'] > 0)
            
            # Get HC range
            if tier_name == "Tier 4":
                hc_range = "51-100 employees"
            elif tier_name == "Tier 5":
                hc_range = "101-250 employees"
            else:
                hc_range = "250+ employees"
            
            html += f"""
    <div class="tier-subsection">
        <h2>{tier_name} - Headcount-Based Performance Rankings</h2>
        <p class="section-summary">
            {len(tier_ads)} Account Directors ({hc_range}) | Avg Score: {tier_avg_score:.1f}/40 | 
            Combined Revenue: {format_currency(tier_total_revenue)} | Total Headcount: {tier_total_headcount:,}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 50px;">Score</th>
                    <th style="width: 180px;">Accounts Managed</th>
                    <th style="width: 70px;">Revenue</th>
                    <th style="width: 50px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for rank, ad_data in enumerate(tier_ads, 1):
                row_class = f"rank-{rank}" if rank <= 3 else ""
                
                accounts_str = ", ".join(ad_data['accounts'][:3])
                if len(ad_data['accounts']) > 3:
                    accounts_str += f" +{len(ad_data['accounts'])-3} more"
                
                revenue_str = format_currency(ad_data['revenue'])
                if ad_data.get('calculated_revenue'):
                    revenue_str += "*"
                
                headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
                if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                    headcount_str += "*"
                
                html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>TBD</td>
                    <td>{headcount_str}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += '</div>\n'
    
    # Tier 6 on its own page
    if tier_groups["Tier 6"]:
        tier_ads = tier_groups["Tier 6"]
        tier_avg_score = sum(ad['total'] for ad in tier_ads) / len(tier_ads) if tier_ads else 0
        tier_total_revenue = sum(ad['revenue'] for ad in tier_ads if ad['revenue'] > 0)
        tier_total_headcount = sum(ad['headcount'] for ad in tier_ads if ad['headcount'] > 0)
        
        html += f"""
    <div class="section">
        <h2>Tier 6 - Headcount-Based Performance Rankings</h2>
        <p class="section-summary">
            {len(tier_ads)} Account Directors (250+ employees) | Avg Score: {tier_avg_score:.1f}/40 | 
            Combined Revenue: {format_currency(tier_total_revenue)} | Total Headcount: {tier_total_headcount:,}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 60px;">Score</th>
                    <th style="width: 200px;">Accounts Managed</th>
                    <th style="width: 80px;">Revenue</th>
                    <th style="width: 60px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for rank, ad_data in enumerate(tier_ads, 1):
            row_class = f"rank-{rank}" if rank <= 3 else ""
            
            accounts_str = ", ".join(ad_data['accounts'][:3])
            if len(ad_data['accounts']) > 3:
                accounts_str += f" +{len(ad_data['accounts'])-3} more"
            
            revenue_str = format_currency(ad_data['revenue'])
            if ad_data.get('calculated_revenue'):
                revenue_str += "*"
            
            headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
            if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                headcount_str += "*"
            
            html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>TBD</td>
                    <td>{headcount_str}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
    
    html += """
            </tbody>
        </table>
    </div>
"""
    
    # ==================== VERTICAL SECTIONS (AT END OF REPORT) ====================
    # Add all 5 vertical views at the end
    # ==================== VERTICAL SECTIONS (CONSOLIDATED PAGES) ====================
    
    # PAGE 1: Manufacturing (standalone)
    html += '<div class="tier-container" style="page-break-after: always;">'
    for vertical_name in ["Manufacturing"]:
        vertical_ads = vertical_groups.get(vertical_name, [])
        if not vertical_ads:
            continue
        
        vertical_avg_score = sum(ad['total'] for ad in vertical_ads) / len(vertical_ads) if vertical_ads else 0
        vertical_total_revenue = sum(ad['revenue'] for ad in vertical_ads if ad['revenue'] > 0)
        vertical_total_headcount = sum(ad['headcount'] for ad in vertical_ads if ad['headcount'] > 0)
        score_str = f"{vertical_avg_score:.1f}"
        rev_str = format_currency(vertical_total_revenue)
        hc_str = f"{vertical_total_headcount:,}"
        
        html += f"""
    <div class="section">
        <h2>{vertical_name} Vertical</h2>
        <p class="section-summary">
            {len(vertical_ads)} Account Directors | Avg Performance Score: {score_str}/40 | 
            Combined Revenue: {rev_str} | Total Headcount: {hc_str}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 80px;">Performance Grade</th>
                    <th style="width: 60px;">Score</th>
                    <th style="width: 180px;">Accounts Managed</th>
                    <th style="width: 80px;">Revenue</th>
                    <th style="width: 60px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for rank, ad_data in enumerate(vertical_ads, 1):
            row_class = f"rank-{rank}" if rank <= 3 else ""
            letter_grade = ad_data.get('letter_grade', 'N/A')
            grade_badge = f'<span class="{get_grade_class(letter_grade)}">{letter_grade}</span>'
            
            accounts_str = ", ".join(ad_data['accounts'][:3])
            if len(ad_data['accounts']) > 3:
                accounts_str += f" +{len(ad_data['accounts'])-3} more"
            
            revenue_str = format_currency(ad_data['revenue'])
            if ad_data.get('calculated_revenue'):
                revenue_str += "*"
            
            headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
            if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                headcount_str += "*"
            
            html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td>{grade_badge}</td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>{scorecard_str}</td>
                    <td>{headcount_str}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
    html += '</div>'
    
    # PAGE 2: Distribution + Life Science + Finance
    html += '<div class="tier-container" style="page-break-after: always;">'
    for vertical_name in ["Distribution", "Life Science", "Finance"]:
        vertical_ads = vertical_groups.get(vertical_name, [])
        if not vertical_ads:
            continue
        
        vertical_avg_score = sum(ad['total'] for ad in vertical_ads) / len(vertical_ads) if vertical_ads else 0
        vertical_total_revenue = sum(ad['revenue'] for ad in vertical_ads if ad['revenue'] > 0)
        vertical_total_headcount = sum(ad['headcount'] for ad in vertical_ads if ad['headcount'] > 0)
        score_str = f"{vertical_avg_score:.1f}"
        rev_str = format_currency(vertical_total_revenue)
        hc_str = f"{vertical_total_headcount:,}"
        
        html += f"""
    <div class="section">
        <h2>{vertical_name} Vertical</h2>
        <p class="section-summary">
            {len(vertical_ads)} Account Directors | Avg Performance Score: {score_str}/40 | 
            Combined Revenue: {rev_str} | Total Headcount: {hc_str}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 80px;">Performance Grade</th>
                    <th style="width: 60px;">Score</th>
                    <th style="width: 180px;">Accounts Managed</th>
                    <th style="width: 80px;">Revenue</th>
                    <th style="width: 60px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for rank, ad_data in enumerate(vertical_ads, 1):
            row_class = f"rank-{rank}" if rank <= 3 else ""
            letter_grade = ad_data.get('letter_grade', 'N/A')
            grade_badge = f'<span class="{get_grade_class(letter_grade)}">{letter_grade}</span>'
            
            accounts_str = ", ".join(ad_data['accounts'][:3])
            if len(ad_data['accounts']) > 3:
                accounts_str += f" +{len(ad_data['accounts'])-3} more"
            
            revenue_str = format_currency(ad_data['revenue'])
            if ad_data.get('calculated_revenue'):
                revenue_str += "*"
            
            headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
            if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                headcount_str += "*"
            
            html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td>{grade_badge}</td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>{scorecard_str}</td>
                    <td>{headcount_str}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
    html += '</div>'
    
    # PAGE 3: Technology (standalone)
    html += '<div class="tier-container">'
    for vertical_name in ["Technology"]:
        vertical_ads = vertical_groups.get(vertical_name, [])
        if not vertical_ads:
            continue
        
        vertical_avg_score = sum(ad['total'] for ad in vertical_ads) / len(vertical_ads) if vertical_ads else 0
        vertical_total_revenue = sum(ad['revenue'] for ad in vertical_ads if ad['revenue'] > 0)
        vertical_total_headcount = sum(ad['headcount'] for ad in vertical_ads if ad['headcount'] > 0)
        score_str = f"{vertical_avg_score:.1f}"
        rev_str = format_currency(vertical_total_revenue)
        hc_str = f"{vertical_total_headcount:,}"
        
        html += f"""
    <div class="section">
        <h2>{vertical_name} Vertical</h2>
        <p class="section-summary">
            {len(vertical_ads)} Account Directors | Avg Performance Score: {score_str}/40 | 
            Combined Revenue: {rev_str} | Total Headcount: {hc_str}
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th style="width: 120px;">Account Director</th>
                    <th style="width: 80px;">Performance Grade</th>
                    <th style="width: 60px;">Score</th>
                    <th style="width: 180px;">Accounts Managed</th>
                    <th style="width: 80px;">Revenue</th>
                    <th style="width: 60px;">Scorecard</th>
                    <th style="width: 60px;">Headcount</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for rank, ad_data in enumerate(vertical_ads, 1):
            row_class = f"rank-{rank}" if rank <= 3 else ""
            letter_grade = ad_data.get('letter_grade', 'N/A')
            grade_badge = f'<span class="{get_grade_class(letter_grade)}">{letter_grade}</span>'
            
            accounts_str = ", ".join(ad_data['accounts'][:3])
            if len(ad_data['accounts']) > 3:
                accounts_str += f" +{len(ad_data['accounts'])-3} more"
            
            revenue_str = format_currency(ad_data['revenue'])
            if ad_data.get('calculated_revenue'):
                revenue_str += "*"
            
            headcount_str = f"{ad_data['headcount']:,}" if ad_data['headcount'] > 0 else "N/A"
            if ad_data.get('headcount_adjusted') and ad_data['headcount'] > 0:
                headcount_str += "*"
            
            html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td><strong>{ad_data['name']}</strong></td>
                    <td>{grade_badge}</td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td class="accounts-list">{accounts_str}</td>
                    <td>{revenue_str}</td>
                    <td>{scorecard_str}</td>
                    <td>{headcount_str}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
    html += '</div>'
    
    html += """
    
    <div style="margin-top: 2rem; padding: 1rem; background: #f9fafb; border-left: 4px solid #3b82f6; font-size: 8pt;">
        <p style="margin: 0; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">Notes:</p>
        <p style="margin: 0.25rem 0; color: #4b5563;">
            <strong>*Revenue (Calculated):</strong> Revenue figures marked with an asterisk are calculated based on headcount-to-revenue ratios from related portfolios, as these Account Directors manage sub-sections of larger accounts.
        </p>
        <p style="margin: 0.25rem 0; color: #4b5563;">
            <strong>*Headcount (AD-Confirmed):</strong> Headcount figures marked with an asterisk reflect Account Director-confirmed adjustments that differ from system-reported values, ensuring accuracy for performance evaluation.
        </p>
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
    print("Generating Enhanced EOY Report with Tier-Based Rankings...")
    
    print("Loading performance review data...")
    df = load_performance_data()
    
    print("Loading financial data from AD CSVs...")
    financial_data = load_financial_data()
    print(f"  - Loaded financial data for {len(financial_data)} ADs")
    
    print("Applying manual mappings...")
    financial_data = apply_manual_mappings(financial_data)
    
    print("Loading tier data, vertical, and scorecard data from verticals.csv...")
    tier_data, vertical_data, scorecard_data = load_tier_data()
    print(f"  - Loaded tier data for {len(tier_data)} ADs")
    print(f"  - Loaded vertical data for {len(vertical_data)} ADs")
    print(f"  - Loaded scorecard data for {len(scorecard_data)} ADs")
    
    print("Calculating performance rankings...")
    rankings = calculate_rankings(df)
    
    print("Generating enhanced HTML report with performance grades...")
    html_content = generate_enhanced_html(rankings, df, financial_data, tier_data, scorecard_data)
    
    print("Writing report file...")
    with open("EOY_Report_2025_Enhanced.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("\nSUCCESS! Enhanced report generated: EOY_Report_2025_Enhanced.html")
    print("  - Overall Performance Rankings")
    print("  - 5 Revenue Tier Views ($100K to > $1.5M)")
    print("  - 5 Vertical Views (Manufacturing, Life Science, Technology, Distribution, Finance)")
    print("  - 3 Headcount Tier Views (Tier 4, 5, 6 from verticals.csv)")
    print("  - Color-coded letter grades (A=green, B=blue, C=yellow, D/F=red)")
    print("  - Performance scores + Financial KPIs integrated")
    print("\nTo convert to PDF, run:")
    print("  python convert_to_pdf.py")
