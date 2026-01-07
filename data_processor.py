"""
Data processing module for Account Director performance reviews.
Handles CSV parsing, score aggregation, and data preparation for the dashboard.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

# Define scoring sections based on CSV structure
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
    "Key Projects",
    "Value Adds",
    "Cost Savings",
    "Innovation",
    "Accountability",
    "2026 Strategy",
    "Personal Goals",
    "Executive Presence"
]

MAX_SCORE_PER_SECTION = 5
TOTAL_MAX_SCORE = len(SCORING_SECTIONS) * MAX_SCORE_PER_SECTION


def load_performance_data(csv_path: str = "data/performance_reviews.csv") -> pd.DataFrame:
    """
    Load and parse the performance review CSV.
    Handles multi-line headers and extracts relevant columns.
    
    Returns:
        DataFrame with cleaned and structured review data
    """
    # Read CSV
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Basic column mapping
    column_mapping = {}
    for col in df.columns:
        if "Account Director Name" in col:
            column_mapping[col] = "Account Director"
        elif "Account Name" in col:
            column_mapping[col] = "Account"
        elif "Email" in col:
            column_mapping[col] = "Reviewer Email"
        elif "Name" in col and "Account" not in col:
            column_mapping[col] = "Reviewer Name"
    
    df = df.rename(columns=column_mapping)
    
    # Extract score and feedback columns
    # Pattern: Columns after "Account Director" alternate between feedback and score
    # Feedback col (with long description), then Score col (with section name)
    
    score_columns = []
    feedback_columns = []
    
    # Find where the scoring section starts (after Account Director column)
    cols_list = list(df.columns)
    start_idx = None
    for i, col in enumerate(cols_list):
        if col == "Account Director":
            start_idx = i + 1
            break
    
    if start_idx is None:
        # Fallback: assume scoring starts at column 7
        start_idx = 7
    
    # From start_idx onwards, pair up columns: feedback (odd positions), score (even positions)
    scoring_cols = cols_list[start_idx:]
    
    for i in range(0, len(scoring_cols) - 1, 2):
        feedback_col = scoring_cols[i]
        score_col = scoring_cols[i + 1]
        
        # The section name is in the score column header
        section_name = score_col.strip()
        
        # Match it to our expected section names
        matched_section = None
        for expected_section in SCORING_SECTIONS:
            if expected_section == section_name or section_name in expected_section:
                matched_section = expected_section
                break
        
        if matched_section:
            score_columns.append((matched_section, score_col))
            feedback_columns.append((matched_section, feedback_col))
    
    return df, score_columns, feedback_columns


def extract_scores_and_feedback(df: pd.DataFrame, score_columns: List, feedback_columns: List) -> pd.DataFrame:
    """
    Extract and structure score and feedback data from the raw DataFrame.
    
    Returns:
        Structured DataFrame with AD, Account, Reviewer, Scores, and Feedback
    """
    structured_data = []
    
    for idx, row in df.iterrows():
        if pd.isna(row.get("Account Director")) or row.get("Account Director") == "Account Director Name":
            continue  # Skip header rows or empty rows
            
        review_data = {
            "Account Director": str(row.get("Account Director", "")).strip(),
            "Account": str(row.get("Account", "")).strip(),
            "Reviewer Name": str(row.get("Reviewer Name", "")).strip(),
            "Reviewer Email": str(row.get("Reviewer Email", "")).strip(),
        }
        
        # Extract scores for each section
        total_score = 0
        for section, score_col in score_columns:
            try:
                score = float(row.get(score_col, 0))
                if pd.isna(score):
                    score = 0
            except (ValueError, TypeError):
                score = 0
            
            review_data[f"{section}_Score"] = score
            total_score += score
        
        review_data["Total Score"] = total_score
        
        # Extract feedback for each section
        for section, feedback_col in feedback_columns:
            feedback = str(row.get(feedback_col, "")).strip()
            if feedback == "nan":
                feedback = ""
            review_data[f"{section}_Feedback"] = feedback
        
        structured_data.append(review_data)
    
    return pd.DataFrame(structured_data)


def aggregate_scores_by_ad(structured_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate scores when multiple reviewers rate the same Account Director.
    Calculates average scores for ranking purposes.
    
    Returns:
        DataFrame with aggregated scores per AD
    """
    if structured_df.empty:
        return pd.DataFrame()
    
    # Group by Account Director and Account
    agg_dict = {
        "Reviewer Name": "count",  # Count of reviews
    }
    
    # Add aggregation for each section score (average)
    for section in SCORING_SECTIONS:
        score_col = f"{section}_Score"
        if score_col in structured_df.columns:
            agg_dict[score_col] = "mean"
    
    agg_dict["Total Score"] = "mean"
    
    aggregated = structured_df.groupby(["Account Director", "Account"], as_index=False).agg(agg_dict)
    aggregated = aggregated.rename(columns={"Reviewer Name": "Review Count"})
    
    # Round scores to 2 decimal places
    for section in SCORING_SECTIONS:
        score_col = f"{section}_Score"
        if score_col in aggregated.columns:
            aggregated[score_col] = aggregated[score_col].round(2)
    
    aggregated["Total Score"] = aggregated["Total Score"].round(2)
    
    # Add vertical data if available
    try:
        verticals_df = pd.read_csv("data/verticals.csv")
        aggregated = aggregated.merge(verticals_df, on="Account Director", how="left")
    except FileNotFoundError:
        aggregated["Vertical"] = None
    
    return aggregated


def get_individual_reviews(structured_df: pd.DataFrame, ad_name: str) -> List[Dict]:
    """
    Get all individual reviews for a specific Account Director.
    
    Args:
        structured_df: The structured review DataFrame
        ad_name: Account Director name
        
    Returns:
        List of review dictionaries with scores and feedback
    """
    ad_reviews = structured_df[structured_df["Account Director"] == ad_name]
    
    reviews = []
    for idx, row in ad_reviews.iterrows():
        review = {
            "reviewer_name": row["Reviewer Name"],
            "reviewer_email": row["Reviewer Email"],
            "account": row["Account"],
            "sections": []
        }
        
        for section in SCORING_SECTIONS:
            section_data = {
                "name": section,
                "score": row[f"{section}_Score"],
                "feedback": row[f"{section}_Feedback"]
            }
            review["sections"].append(section_data)
        
        review["total_score"] = row["Total Score"]
        reviews.append(review)
    
    return reviews


def get_rubric_data() -> List[Dict]:
    """
    Generate rubric reference data showing scoring methodology.
    
    Returns:
        List of dictionaries with section details for rubric display
    """
    # Section descriptions extracted from CSV column headers
    section_descriptions = {
        "Key Projects & Initiatives": "Articulation of major initiatives delivered in 2025, including scope, outcomes, and client impact.",
        "Value Adds & Cost Avoidance": "Demonstration of added value beyond core contract requirements, value-added services, and cost avoidance efforts.",
        "Cost Savings Delivered": "Ownership of operational execution and sustainability, workflow improvements, and repeatable enhancements.",
        "Innovation & Continuous Improvement": "Leadership in evolving service delivery through new processes, tools, or enhancements, and willingness to test and iterate.",
        "Issues, Challenges & Accountability": "Self-awareness and accountability in addressing challenges, reflection on improvements, and corrective actions.",
        "2026 Forward Strategy & Vision": "Strategic thinking and future readiness, including account elevation plans and planned initiatives with timelines.",
        "Personal Goals & Role Maturity": "Professional maturity and development through clear, measurable personal goals aligned to AD expectations.",
        "Executive Presence & Presentation Skills": "Effectiveness in delivering reviews to executive leadership with clear, confident communication and structured flow."
    }
    
    rubric = []
    for section in SCORING_SECTIONS:
        rubric.append({
            "section": section,
            "max_score": MAX_SCORE_PER_SECTION,
            "description": section_descriptions.get(section, ""),
            "criteria": "Scored on a scale of 1-5, where 5 represents exceptional performance and 1 represents needs improvement."
        })
    
    return rubric


def prepare_dashboard_data(csv_path: str = "data/performance_reviews.csv") -> Tuple[pd.DataFrame, pd.DataFrame, List]:
    """
    Main function to prepare all data needed for the dashboard.
    
    Returns:
        Tuple of (aggregated_df, individual_reviews_df, rubric_data)
    """
    # Load raw data
    raw_df, score_columns, feedback_columns = load_performance_data(csv_path)
    
    # Structure the data
    structured_df = extract_scores_and_feedback(raw_df, score_columns, feedback_columns)
    
    # Aggregate scores for rankings
    aggregated_df = aggregate_scores_by_ad(structured_df)
    
    # Get rubric data
    rubric_data = get_rubric_data()
    
    return aggregated_df, structured_df, rubric_data


def get_filter_options(aggregated_df: pd.DataFrame) -> Dict[str, List]:
    """
    Extract unique values for filter dropdowns.
    
    Returns:
        Dictionary with filter options
    """
    verticals = []
    if "Vertical" in aggregated_df.columns:
        verticals = sorted(aggregated_df["Vertical"].dropna().unique().tolist())
    
    return {
        "accounts": sorted(aggregated_df["Account"].dropna().unique().tolist()),
        "verticals": verticals
    }

