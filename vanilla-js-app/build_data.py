"""
Build JSON data from CSV for the Account Director Performance Dashboard.
Run this script whenever the CSV is updated.
"""

import pandas as pd
import json
from pathlib import Path

def clean_numeric_value(val):
    """Clean and convert numeric values from CSV"""
    if pd.isna(val) or val == '':
        return None
    try:
        # Remove commas and convert to float
        if isinstance(val, str):
            val = val.replace(',', '')
        return float(val)
    except:
        return None

def load_best_practices(bp_path="../data/best-practices.json"):
    """Load best practices from JSON file."""
    try:
        with open(bp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Best practices file not found: {bp_path}")
        return {}
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON in best practices file: {bp_path}")
        return {}

def normalize_ad_name_for_financial(ad_name):
    """Normalize AD names to match review CSV format"""
    # Specific mappings for known mismatches
    name_map = {
        "Michael Barry": "Mike Barry",
        "Gregory Demedio": "Gregory DeMedio",  # Fix capitalization
    }
    return name_map.get(ad_name, ad_name)

def load_financial_data():
    """Load all AD CSV files and aggregate financial metrics"""
    ad_csvs_dir = Path("../data/ad_csvs")
    ad_financial_data = {}
    
    for csv_file in ad_csvs_dir.glob("*.csv"):
        # Convert filename to AD name (e.g., "aaron-simpson.csv" -> "Aaron Simpson")
        ad_name = csv_file.stem.replace('-', ' ').title()
        # Normalize to match review names
        ad_name = normalize_ad_name_for_financial(ad_name)
        
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
            print(f"⚠️  Error processing {csv_file}: {e}")
            continue
    
    return ad_financial_data

def apply_manual_mappings(financial_data):
    """Apply manual mappings for ADs with special cases"""
    
    # Keith Deuber: Assign Amazon (same as Dustin Smith)
    financial_data["Keith Deuber"] = {
        'accounts': ['Amazon'],
        'num_accounts': 1,
        'revenue_total': 3140,
        'csat_avg': 4.76,
        'headcount_total': 733,
        'red_sites_count': 16,
        'growth_avg': -38.7
    }
    
    # Rade Kukobat: Assign Eli Lilly LCC/LRL (calculated from Chad Boulton's ratio)
    eli_lilly_rev_per_hc = 2075 / 399
    rade_headcount = 83
    rade_revenue = eli_lilly_rev_per_hc * rade_headcount
    financial_data["Rade Kukobat"] = {
        'accounts': ['Eli Lilly LCC/LRL'],
        'num_accounts': 1,
        'revenue_total': rade_revenue,
        'csat_avg': 2.25,
        'headcount_total': rade_headcount,
        'red_sites_count': 1,
        'growth_avg': 55.4
    }
    
    # Gregory DeMedio: Add Abbott Labs
    if "Gregory Demedio" in financial_data:
        gregory_data = financial_data["Gregory Demedio"]
        if "Abbott Labs" not in gregory_data['accounts']:
            gregory_data['accounts'].insert(0, 'Abbott Labs')
            gregory_data['num_accounts'] += 1
            gregory_data['revenue_total'] += 1713
            gregory_data['headcount_total'] += 166
    
    # Stuart Kelloff: Add Adobe
    if "Stuart Kelloff" in financial_data:
        stuart_data = financial_data["Stuart Kelloff"]
        if "Adobe" not in stuart_data['accounts']:
            stuart_data['accounts'].insert(0, 'Adobe')
            stuart_data['num_accounts'] += 1
    
    # Grant Frazier: Add Meta
    if "Grant Frazier" in financial_data:
        grant_data = financial_data["Grant Frazier"]
        if "Meta" not in grant_data['accounts']:
            grant_data['accounts'].insert(0, 'Meta')
            grant_data['num_accounts'] += 1
    
    # Taylor Wattenberg: Add Microsoft
    if "Taylor Wattenberg" in financial_data:
        taylor_data = financial_data["Taylor Wattenberg"]
        if "Microsoft" not in taylor_data['accounts']:
            taylor_data['accounts'].insert(0, 'Microsoft')
            taylor_data['num_accounts'] += 1
    
    # Giselle Langelier: Normalize Gisell -> Giselle
    if "Gisell Langelier" in financial_data:
        financial_data["Giselle Langelier"] = financial_data.pop("Gisell Langelier")
    
    # Peggy Shum: Normalize Peggy Mcelwee -> Peggy Shum
    if "Peggy Mcelwee" in financial_data:
        financial_data["Peggy Shum"] = financial_data.pop("Peggy Mcelwee")
    
    # David Pergola: Add Merck Sodexo (calculated from Brian Davis's Merck ratio)
    merck_rev_per_employee = 4077 / 345  # Brian Davis Merck: Revenue=$4,077K, Headcount=345
    david_headcount = 135
    david_revenue = david_headcount * merck_rev_per_employee
    financial_data["David Pergola"] = {
        'accounts': ['Merck Sodexo'],
        'num_accounts': 1,
        'revenue_total': david_revenue,
        'csat_avg': 4.75,  # Use Brian's Merck CSAT
        'headcount_total': david_headcount,
        'red_sites_count': 0,
        'growth_avg': 8.9  # Use Brian's Merck growth
    }

    # RJ Ober: Alias for Russell Ober (reviews use "RJ Ober", CSV file is russell-ober.csv)
    if "Russell Ober" in financial_data:
        financial_data["RJ Ober"] = financial_data["Russell Ober"].copy()

    # Greyson Wolff: Honda (user will add automotive file later)
    financial_data["Greyson Wolff"] = {
        'accounts': ['Honda'],
        'num_accounts': 1,
        'revenue_total': 0,
        'csat_avg': None,
        'headcount_total': 0,
        'red_sites_count': 0,
        'growth_avg': None
    }

    return financial_data

# Define scoring sections
SCORING_SECTIONS = [
    "Key Projects & Initiatives",
    "Value Adds & Cost Avoidance",
    "Cost Savings Delivered",
    "Innovation & Continuous Improvement",
    "Issues, Challenges & Accountability",
    "2026 Forward Strategy & Vision",
    "Personal Goals & Role Maturity",
    "Executive Presence & Presentation Skills"
]

SECTION_SHORT_NAMES = [
    "Projects",
    "Value Adds",
    "Cost Savings",
    "Innovation",
    "Accountability",
    "Strategy",
    "Goals",
    "Exec Presence"
]

TOTAL_MAX_SCORE = len(SCORING_SECTIONS) * 5

def load_csv_data(csv_path="../data/performance_reviews.csv"):
    """Load and parse the performance review CSV."""
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Rename columns for consistency
    column_mapping = {}
    for col in df.columns:
        if "Account Director Name" in col:
            column_mapping[col] = "Account Director"
        elif "Account Name" in col:
            column_mapping[col] = "Account"
        elif "Email" in col:
            column_mapping[col] = "Reviewer Email"
        elif col == "Enter Your Name":  # This is the actual reviewer name column
            column_mapping[col] = "Reviewer Name"
    
    df = df.rename(columns=column_mapping)
    return df

def extract_scores_and_feedback(df):
    """Extract scores and feedback from the DataFrame."""
    cols_list = list(df.columns)
    
    # AD Name normalization mapping
    AD_NAME_NORMALIZE = {
        "Logan Newman's": "Logan Newman",
        "Ayesha Nasi": "Ayesha Nasir",
        "Gisell Langelier": "Giselle Langelier",
        "Dave Pergola": "David Pergola",
        "Greg DeMedio": "Gregory DeMedio",
        "Greg Demedio": "Gregory DeMedio",
        "Nick Trenkamp": "Nicholas Trenkamp",
        "Nike Trenkamp": "Nicholas Trenkamp"
    }
    
    # New structure: columns 0-7 are metadata, 8+ are feedback/score pairs
    # Pattern: Feedback (col 8), Score (col 9), Feedback (col 10), Score (col 11), etc.
    start_idx = 8  # Start after "Enter Your Name" column
    
    scoring_cols = cols_list[start_idx:]
    
    # Pair up feedback and score columns
    # Pattern: [Feedback, Score, Feedback, Score, ...]
    score_columns = []
    feedback_columns = []
    
    for i in range(0, len(scoring_cols) - 1, 2):
        feedback_col_raw = scoring_cols[i]      # Even indices (0, 2, 4...) = Feedback
        score_col_raw = scoring_cols[i + 1]      # Odd indices (1, 3, 5...) = Score
        
        section_name = score_col_raw.strip()
        
        # Match to expected sections
        matched_section = None
        for expected_section in SCORING_SECTIONS:
            if expected_section == section_name or section_name in expected_section:
                matched_section = expected_section
                break
        
        if matched_section:
            score_columns.append((matched_section, score_col_raw))
            feedback_columns.append((matched_section, feedback_col_raw))
    
    # Extract data
    reviews = []
    for idx, row in df.iterrows():
        if pd.isna(row.get("Account Director")) or str(row.get("Account Director")).strip() == "Account Director Name":
            continue
        
        # Get and normalize AD name
        ad_name = str(row.get("Account Director", "")).strip()
        ad_name = AD_NAME_NORMALIZE.get(ad_name, ad_name)
        
        # Get reviewer name - try "Reviewer Name" (Enter Your Name) first, then fall back to "Name"
        reviewer_name = str(row.get("Reviewer Name", "")).strip()
        if not reviewer_name or reviewer_name.lower() == "nan":
            reviewer_name = str(row.get("Name", "")).strip()
        
        review = {
            "accountDirector": ad_name,
            "account": str(row.get("Account", "")).strip(),
            "reviewerName": reviewer_name,
            "reviewerEmail": str(row.get("Reviewer Email", "")).strip(),
            "scores": {section: 0 for section in SCORING_SECTIONS},  # Initialize all sections
            "feedback": {section: "" for section in SCORING_SECTIONS},  # Initialize all sections
            "totalScore": 0
        }
        
        total = 0
        for section, score_col in score_columns:
            try:
                score = float(row.get(score_col, 0))
                if pd.isna(score):
                    score = 0
            except (ValueError, TypeError):
                score = 0
            
            review["scores"][section] = score
            total += score
        
        for section, feedback_col in feedback_columns:
            feedback = str(row.get(feedback_col, "")).strip()
            if not feedback or feedback.lower() == "nan":
                feedback = "No feedback provided"
            review["feedback"][section] = feedback
        
        review["totalScore"] = total
        
        # Handle joint reviews (e.g., "Brian Davis / Justin Homa")
        # EXCLUDE Justin Homa from joint reviews (per user request)
        if " / " in review["accountDirector"]:
            # Split the names and create separate reviews for each
            names = [name.strip() for name in review["accountDirector"].split(" / ")]
            for name in names:
                # Skip Justin Homa in joint reviews
                if name == "Justin Homa":
                    continue
                individual_review = review.copy()
                individual_review["accountDirector"] = name
                individual_review["scores"] = review["scores"].copy()
                individual_review["feedback"] = review["feedback"].copy()
                reviews.append(individual_review)
        else:
            reviews.append(review)
    
    return reviews

def load_verticals(vertical_path="../data/verticals.csv"):
    """Load vertical, tier, and role mapping."""
    try:
        vertical_df = pd.read_csv(vertical_path)
        # Return dict with vertical, tier, and role
        result = {}
        for idx, row in vertical_df.iterrows():
            ad_name = row["Account Director"].strip() if pd.notna(row["Account Director"]) else ""
            vertical = row["Vertical"].strip() if pd.notna(row["Vertical"]) else "N/A"
            tier = row["Tier"].strip() if pd.notna(row["Tier"]) and str(row["Tier"]).strip() else ""
            role = row["Role"].strip() if "Role" in row and pd.notna(row.get("Role")) and str(row.get("Role")).strip() else "Account Director"
            result[ad_name] = {"vertical": vertical, "tier": tier, "role": role}
        return result
    except FileNotFoundError:
        return {}
    except KeyError:
        # If columns don't exist, fall back
        vertical_df = pd.read_csv(vertical_path)
        result = {}
        for idx, row in vertical_df.iterrows():
            ad_name = row["Account Director"].strip() if pd.notna(row["Account Director"]) else ""
            vertical = row["Vertical"].strip() if pd.notna(row["Vertical"]) else "N/A"
            tier = row["Tier"].strip() if pd.notna(row.get("Tier")) and str(row.get("Tier")).strip() else ""
            role = row["Role"].strip() if "Role" in row and pd.notna(row.get("Role")) and str(row.get("Role")).strip() else "Account Director"
            result[ad_name] = {"vertical": vertical, "tier": tier, "role": role}
        return result

def aggregate_reviews(reviews, verticals, financial_data):
    """Aggregate reviews by Account Director."""
    from collections import defaultdict
    
    ad_reviews = defaultdict(list)
    
    for review in reviews:
        ad_reviews[review["accountDirector"]].append(review)
    
    aggregated = []
    
    for ad_name, ad_review_list in ad_reviews.items():
        # Calculate average scores
        avg_scores = {}
        for section in SCORING_SECTIONS:
            scores = [r["scores"].get(section, 0) for r in ad_review_list]
            avg_scores[section] = sum(scores) / len(scores) if scores else 0
        
        avg_total = sum(avg_scores.values())
        
        # Get vertical and tier data
        vertical_data = verticals.get(ad_name, {"vertical": "N/A", "tier": ""})
        
        # Get financial data
        fin_data = financial_data.get(ad_name, {
            'accounts': [],
            'num_accounts': 0,
            'revenue_total': 0,
            'csat_avg': None,
            'headcount_total': 0,
            'red_sites_count': 0,
            'growth_avg': None
        })
        
        # Get accounts list and create display string
        accounts_list = fin_data.get('accounts', [])
        account_display = ', '.join(accounts_list) if accounts_list else 'undefined'
        
        ad_entry = {
            "accountDirector": ad_name,
            "account": account_display,  # For frontend compatibility (singular, joined string)
            "accounts": accounts_list,  # Keep array for future use
            "numAccounts": fin_data.get('num_accounts', 0),
            "revenue": fin_data.get('revenue_total', 0),
            "csat": fin_data.get('csat_avg'),
            "headcount": fin_data.get('headcount_total', 0),
            "redSites": fin_data.get('red_sites_count', 0),
            "growth": fin_data.get('growth_avg'),
            "vertical": vertical_data.get("vertical", "N/A"),
            "tier": vertical_data.get("tier", ""),
            "role": vertical_data.get("role", "Account Director"),
            "reviewCount": len(ad_review_list),
            "avgScores": avg_scores,
            "avgTotalScore": avg_total,
            "reviews": ad_review_list
        }
        
        aggregated.append(ad_entry)
    
    return aggregated

def build_rubric_data():
    """Build rubric definitions."""
    rubrics = {
        "Key Projects & Initiatives": {
            "definition": "Evaluates ability to articulate meaningful work and outcomes",
            "criteria": {
                "5": "Clearly frames the most important 2025 initiatives, why they mattered, and what changed for the client as a result; demonstrates strong judgment, prioritization, and impact awareness",
                "4": "Presents a clear narrative of key initiatives and outcomes, with minor gaps in impact clarity or measurement",
                "3": "Accurately describes initiatives but focuses more on execution than client outcomes or strategic impact",
                "2": "Mentions projects but lacks ownership, prioritization, or clarity on why they mattered",
                "1": "Unable to clearly articulate major initiatives or their relevance"
            }
        },
        "Value Adds & Cost Avoidance": {
            "definition": "Evaluates ability to demonstrate value beyond contract scope",
            "criteria": {
                "5": "Clearly articulates value delivered beyond contract scope and translates it into estimated financial, operational, or risk-based impact",
                "4": "Provides strong examples of value creation with partial or directional financial framing",
                "3": "Describes value adds but does not translate them into financial or business impact",
                "2": "Examples are vague or lack clarity on value delivered",
                "1": "No meaningful value creation discussed"
            }
        },
        "Cost Savings Delivered": {
            "definition": "Evaluates financial stewardship and operational efficiency",
            "criteria": {
                "5": "Clearly explains how cost savings were created, quantified, and sustained; demonstrates strong financial stewardship",
                "4": "Identifies cost savings with reasonable clarity and some indication of sustainability",
                "3": "Mentions cost savings but with limited explanation or primarily one-time impact",
                "2": "Savings referenced without clear understanding, ownership, or credibility",
                "1": "No cost savings articulated"
            }
        },
        "Innovation & Continuous Improvement": {
            "definition": "Evaluates leadership in evolving service delivery",
            "criteria": {
                "5": "Demonstrates intentional innovation or meaningful pivots, with clear outcomes and lessons learned",
                "4": "Introduced improvements or adaptations that positively impacted the account",
                "3": "Participated in improvement efforts but with limited leadership or ownership",
                "2": "Discusses ideas or concepts without execution or demonstrated impact",
                "1": "No evidence of innovation or continuous improvement"
            }
        },
        "Issues, Challenges & Accountability": {
            "definition": "Evaluates self-awareness, ownership, and executive leadership",
            "criteria": {
                "5": "Fully transparent about challenges, clearly owns gaps, and outlines specific corrective actions with timelines",
                "4": "Identifies challenges and discusses improvement actions with reasonable clarity",
                "3": "Acknowledges issues but provides limited reflection, ownership, or follow-through",
                "2": "Defensive, vague, or minimizes challenges without accountability",
                "1": "Avoids or fails to address challenges altogether"
            }
        },
        "2026 Forward Strategy & Vision": {
            "definition": "Evaluates strategic thinking and future readiness",
            "criteria": {
                "5": "Articulates a clear, compelling 2026 account roadmap tied to retention, growth, and differentiation, with defined priorities and sequencing",
                "4": "Presents a strong forward-looking plan with reasonable clarity and timelines",
                "3": "Shares general goals or aspirations without clear execution detail",
                "2": "Strategy is reactive, unclear, or lacks cohesion",
                "1": "No meaningful forward strategy articulated"
            }
        },
        "Personal Goals & Role Maturity": {
            "definition": "Evaluates professional growth and role ownership",
            "criteria": {
                "5": "Clearly defines measurable leadership goals that demonstrate role maturity, accountability, and impact on account performance",
                "4": "Establishes thoughtful goals with progress and clearly articulated next steps",
                "3": "Shares general development intentions without clear measures or ownership",
                "2": "Goals are vague, unclear, or not actionable",
                "1": "No articulated leadership or development goals"
            }
        },
        "Executive Presence & Presentation Skills": {
            "definition": "Evaluates effectiveness in delivering the review to executive leadership",
            "criteria": {
                "5": "Leads the discussion with confidence and authority; presents a clear, structured account narrative and responds effectively to executive questions",
                "4": "Communicates clearly with logical flow; delivers a cohesive account story with minor gaps in executive presence or impact",
                "3": "Communicates key points but relies heavily on prepared material; executive presence is limited",
                "2": "Communication lacks clarity or structure; executive presence is inconsistent",
                "1": "Unable to effectively lead the discussion at an executive level"
            }
        }
    }
    
    return rubrics

def main():
    """Main function to build data.json."""
    print("Loading CSV data...")
    df = load_csv_data()
    
    print("Extracting scores and feedback...")
    reviews = extract_scores_and_feedback(df)
    
    print("Loading vertical mappings...")
    verticals = load_verticals()
    
    print("Loading financial data from AD CSVs...")
    financial_data = load_financial_data()
    print(f"   - Loaded financial data for {len(financial_data)} Account Directors")
    
    print("Applying manual mappings...")
    financial_data = apply_manual_mappings(financial_data)
    
    print("Aggregating reviews by Account Director...")
    aggregated = aggregate_reviews(reviews, verticals, financial_data)
    
    print("Building rubric data...")
    rubrics = build_rubric_data()
    
    # Load best practices
    print("Loading best practices...")
    best_practices = load_best_practices()
    print(f"   - Loaded best practices for {len(best_practices)} Account Directors")
    
    # Build final data structure
    data = {
        "metadata": {
            "totalMaxScore": TOTAL_MAX_SCORE,
            "scoringSections": SCORING_SECTIONS,
            "sectionShortNames": SECTION_SHORT_NAMES,
            "lastUpdated": pd.Timestamp.now().isoformat()
        },
        "accountDirectors": aggregated,
        "rubrics": rubrics,
        "bestPractices": best_practices
    }
    
    # Write to JSON
    output_path = Path("data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"SUCCESS: Successfully built {output_path}")
    print(f"   - {len(aggregated)} Account Directors")
    print(f"   - {len(reviews)} Total Reviews")
    print(f"   - {len(SCORING_SECTIONS)} Scoring Sections")

if __name__ == "__main__":
    main()

