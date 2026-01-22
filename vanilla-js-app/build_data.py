"""
Build JSON data from CSV for the Account Director Performance Dashboard.
Run this script whenever the CSV is updated.
"""

import pandas as pd
import json
from pathlib import Path

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
        
        review = {
            "accountDirector": str(row.get("Account Director", "")).strip(),
            "account": str(row.get("Account", "")).strip(),
            "reviewerName": str(row.get("Reviewer Name", "")).strip(),
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
        if " / " in review["accountDirector"]:
            # Split the names and create separate reviews for each
            names = [name.strip() for name in review["accountDirector"].split(" / ")]
            for name in names:
                individual_review = review.copy()
                individual_review["accountDirector"] = name
                individual_review["scores"] = review["scores"].copy()
                individual_review["feedback"] = review["feedback"].copy()
                reviews.append(individual_review)
        else:
            reviews.append(review)
    
    return reviews

def load_verticals(vertical_path="../data/verticals.csv"):
    """Load vertical and tier mapping."""
    try:
        vertical_df = pd.read_csv(vertical_path)
        # Return dict with both vertical and tier
        result = {}
        for idx, row in vertical_df.iterrows():
            ad_name = row["Account Director"].strip() if pd.notna(row["Account Director"]) else ""
            vertical = row["Vertical"].strip() if pd.notna(row["Vertical"]) else "N/A"
            tier = row["Tier"].strip() if pd.notna(row["Tier"]) and str(row["Tier"]).strip() else ""
            result[ad_name] = {"vertical": vertical, "tier": tier}
        return result
    except FileNotFoundError:
        return {}
    except KeyError:
        # If Tier column doesn't exist, fall back to vertical only
        vertical_df = pd.read_csv(vertical_path)
        result = {}
        for idx, row in vertical_df.iterrows():
            ad_name = row["Account Director"].strip() if pd.notna(row["Account Director"]) else ""
            vertical = row["Vertical"].strip() if pd.notna(row["Vertical"]) else "N/A"
            result[ad_name] = {"vertical": vertical, "tier": ""}
        return result

def aggregate_reviews(reviews, verticals):
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
        
        aggregated.append({
            "accountDirector": ad_name,
            "account": ad_review_list[0]["account"],
            "vertical": vertical_data.get("vertical", "N/A"),
            "tier": vertical_data.get("tier", ""),
            "reviewCount": len(ad_review_list),
            "avgScores": avg_scores,
            "avgTotalScore": avg_total,
            "reviews": ad_review_list
        })
    
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
    print("🔄 Loading CSV data...")
    df = load_csv_data()
    
    print("📊 Extracting scores and feedback...")
    reviews = extract_scores_and_feedback(df)
    
    print("📁 Loading vertical mappings...")
    verticals = load_verticals()
    
    print("🔢 Aggregating reviews by Account Director...")
    aggregated = aggregate_reviews(reviews, verticals)
    
    print("📚 Building rubric data...")
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
    
    print(f"✅ Successfully built {output_path}")
    print(f"   - {len(aggregated)} Account Directors")
    print(f"   - {len(reviews)} Total Reviews")
    print(f"   - {len(SCORING_SECTIONS)} Scoring Sections")

if __name__ == "__main__":
    main()

