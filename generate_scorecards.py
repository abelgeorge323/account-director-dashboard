"""
Generate individual HTML scorecards for Account Directors.
Includes sections from CSV reviews, best practices from transcripts, and follow-up questions.
"""

import json
import pandas as pd
from datetime import datetime

# Section names matching the CSV
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

def load_review_data():
    """Load performance review data from CSV."""
    df = pd.read_csv("data/performance_reviews.csv", low_memory=False)
    return df

def load_best_practices():
    """Load best practices from JSON."""
    with open("data/best-practices.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_follow_up_questions():
    """Load follow-up questions from JSON."""
    with open("data/follow-up-questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_verticals():
    """Load tier data from verticals.csv."""
    try:
        df = pd.read_csv("data/verticals.csv")
        verticals = {}
        for _, row in df.iterrows():
            ad_name = str(row.get("Account Director", "")).strip()
            tier = str(row.get("Tier", "")).strip()
            verticals[ad_name] = tier if tier else "Unassigned"
        return verticals
    except Exception as e:
        print(f"Warning: Could not load verticals.csv: {e}")
        return {}

def calculate_aggregate_scores(df, ad_name):
    """Calculate aggregate scores for an AD across all their reviews."""
    # Strip trailing spaces from AD name in comparison
    ad_reviews = df[df["Account Director Name"].str.strip() == ad_name.strip()]
    
    # ALSO include joint reviews that contain this AD's name
    # e.g., "Brian Davis / Justin Homa" should be included for both Brian and Justin
    joint_reviews = df[df["Account Director Name"].str.contains("/", na=False)]
    for idx, row in joint_reviews.iterrows():
        joint_name = str(row["Account Director Name"]).strip()
        # Check if this AD is part of the joint review
        if ad_name.strip() in joint_name:
            # Add this joint review to ad_reviews
            ad_reviews = pd.concat([ad_reviews, pd.DataFrame([row])], ignore_index=True)
    
    if ad_reviews.empty:
        return None
    
    scores = {}
    feedback = {}
    
    for idx, section in enumerate(SCORING_SECTIONS):
        score_col = section
        # The pattern in CSV: Comment column, then Score column
        # Score columns are at indices 9, 11, 13, 15, 17, 19, 21, 23
        score_col_idx = 9 + (idx * 2)
        
        section_scores = []
        section_feedback = []
        
        for _, row in ad_reviews.iterrows():
            try:
                # Get score
                if score_col_idx < len(row):
                    score = row.iloc[score_col_idx]
                    if pd.notna(score) and str(score).strip():
                        try:
                            section_scores.append(float(score))
                        except (ValueError, TypeError):
                            pass
                
                # Get feedback (one column before score)
                feedback_col_idx = score_col_idx - 1
                if feedback_col_idx < len(row):
                    fb = str(row.iloc[feedback_col_idx])
                    if fb and fb.lower() not in ['nan', 'none', '']:
                        reviewer_name = str(row.get("Enter Your Name", "")).strip()
                        if not reviewer_name or reviewer_name.lower() == "nan":
                            reviewer_name = "Anonymous"
                        section_feedback.append({
                            "reviewer": reviewer_name,
                            "text": fb.strip()
                        })
            except Exception as e:
                print(f"Error processing row for {ad_name}, section {section}: {e}")
                continue
        
        # Calculate average score (skip if no scores, don't use 0)
        if section_scores:
            scores[section] = round(sum(section_scores) / len(section_scores), 2)
        else:
            scores[section] = None  # Not scored, will display as N/A
        
        feedback[section] = section_feedback
    
    # Calculate total score - only count sections that were actually scored
    scored_sections = [s for s in scores.values() if s is not None]
    total_score = sum(scored_sections) if scored_sections else 0
    max_possible = len(scored_sections) * 5  # 5 points per section
    
    # Extract reviewer names
    reviewers = []
    for _, row in ad_reviews.iterrows():
        reviewer_name = str(row.get("Enter Your Name", "")).strip()
        # Handle NaN, empty, or missing values
        if not reviewer_name or reviewer_name.lower() == "nan":
            reviewer_name = "Anonymous"
        if reviewer_name not in reviewers:
            reviewers.append(reviewer_name)
    
    return {
        "ad_name": ad_name.strip(),
        "account": ad_reviews.iloc[0].get("Account Name", "N/A"),
        "review_count": len(ad_reviews),
        "reviewers": reviewers,
        "total_score": round(total_score, 2),
        "max_possible": max_possible,
        "avg_score": round(total_score / max_possible, 2) if max_possible > 0 else 0,
        "scores": scores,
        "feedback": feedback
    }

# Best practices removed from scorecards per user request

def render_follow_ups_html(follow_ups):
    """Render follow-up questions section as HTML."""
    if not follow_ups:
        return ""
    
    html = """
    <div class="follow-up-section">
        <h2>🎯 2026 Development Focus & Follow-Up Items</h2>
        <p class="follow-up-intro">
            Based on your year-end presentation and executive feedback, the following areas have been identified 
            for focused development and follow-through in 2026.
        </p>
    """
    
    for fq in follow_ups:
        reviewer_display = '' if fq.get('reviewer') == 'Anonymous Reviewer' else f"— {fq.get('reviewer', '')}"
        html += f"""
        <div class="follow-up-item">
            <div class="follow-up-header">
                <span class="follow-up-category">{fq['category']}</span>
                <span class="follow-up-source">{reviewer_display}</span>
            </div>
            <h3>{fq['title']}</h3>
            <p class="follow-up-quote">"{fq['quote']}"</p>
            <p class="follow-up-action"><strong>Action:</strong> {fq['action']}</p>
        </div>
        """
    
    html += "</div>"
    return html

def synthesize_feedback(feedback_list, section_name):
    """Synthesize feedback from multiple reviewers into Ben's format with Overall Assessment, Strengths, Development Areas, and Recommendation."""
    if not feedback_list:
        return "<p><em>No specific feedback provided.</em></p>"
    
    # Separate positive and developmental feedback based on content analysis
    strengths = []
    development_areas = []
    all_feedback = []
    
    for fb in feedback_list:
        text = fb['text']
        all_feedback.append(text)
        
        # Simple heuristic: if feedback contains positive keywords, it's a strength
        positive_keywords = ['strong', 'excellent', 'great', 'good', 'clear', 'well', 'demonstrated', 'effectively', 'impressive', 'love', 'outstanding']
        developmental_keywords = ['could', 'should', 'would', 'opportunity', 'challenge', 'gap', 'need', 'lacking', 'missing', 'improve', 'better', 'more']
        
        text_lower = text.lower()
        
        # Check if it's primarily developmental
        if any(keyword in text_lower for keyword in ['however', 'but ', 'would like', 'could have', 'should', 'opportunity to', 'lacking', 'missing']):
            development_areas.append(text)
        # Check if it's primarily positive
        elif any(keyword in text_lower for keyword in positive_keywords):
            strengths.append(text)
        else:
            # Default to development if unclear
            development_areas.append(text)
    
    # Build the synthesized format
    html = """
    <div class="combined-feedback">
        <h4>Combined Feedback from Leadership Reviews</h4>
        <div class="feedback-synthesis">
    """
    
    # Overall Assessment (first sentence from first feedback)
    if all_feedback:
        first_feedback = all_feedback[0]
        # Take first sentence or first 200 chars
        assessment = first_feedback.split('.')[0] + '.' if '.' in first_feedback else first_feedback[:200] + '...'
        html += f"""
            <p><strong>Overall Assessment:</strong> {assessment}</p>
        """
    
    # Strengths
    if strengths:
        html += """
            <p><strong>Strengths:</strong></p>
            <ul class="synthesis-list">
        """
        for strength in strengths:
            html += f"<li>{strength}</li>"
        html += "</ul>"
    
    # Areas for Development / Critical Development Areas
    if development_areas:
        html += """
            <p><strong>Areas for Development:</strong></p>
            <ul class="synthesis-list">
        """
        for area in development_areas:
            html += f"<li>{area}</li>"
        html += "</ul>"
    
    html += """
        </div>
    </div>
    """
    return html

def generate_scorecard_html(ad_data, best_practices, follow_ups):
    """Generate complete scorecard HTML for an AD."""
    
    # Build sections HTML (no page breaks)
    sections_html = ""
    for section in SCORING_SECTIONS:
        score = ad_data['scores'].get(section)
        feedback = ad_data['feedback'].get(section, [])
        
        # Skip sections with no score and no feedback
        if score is None and not feedback:
            continue
        
        score_display = f"{score}/5" if score is not None else "N/A"
        
        sections_html += f"""
        <div class="scored-section">
            <h2>{section}</h2>
            <div class="score-display">
                <span class="score-label">Average Score:</span>
                <span class="score-value">{score_display}</span>
            </div>
            
            {synthesize_feedback(feedback, section)}
        </div>
        """
    
    # Build score table for summary
    score_rows = ""
    for section in SCORING_SECTIONS:
        score = ad_data['scores'].get(section)
        score_display = score if score is not None else "N/A"
        score_rows += f"""
        <tr>
            <td>{section}</td>
            <td style="text-align: center; font-weight: 600;">{score_display}</td>
        </tr>
        """
    
    # Add overall score row at bottom
    score_rows += f"""
        <tr style="background: #e8f5e9; border-top: 3px solid #2c5282;">
            <td style="font-weight: 700; text-transform: uppercase;">Overall Score</td>
            <td style="text-align: center; font-weight: 700; font-size: 1.2rem; color: #2c5282;">{ad_data['total_score']}/{ad_data['max_possible']}</td>
        </tr>
        """
    
    # Follow-ups at the END only
    follow_ups_html = render_follow_ups_html(follow_ups)
    
    # Format tier with color coding
    tier_text = ad_data.get('tier', 'Unassigned')
    tier_colors = {
        'Tier 4': '#f97316',  # Orange
        'Tier 5': '#6366f1',  # Indigo
        'Tier 6': '#10b981',  # Green
        'Unassigned': '#94a3b8'  # Gray
    }
    tier_color = tier_colors.get(tier_text, '#94a3b8')
    tier = f'<span style="background: {tier_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 12px; font-weight: 600; font-size: 0.9rem;">{tier_text}</span>'
    
    # Build complete HTML with proper page breaks
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 Year-End Scorecard - {ad_data['ad_name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #ffffff;
            padding: 2rem;
            max-width: 8.5in;
            margin: 0 auto;
        }}

        h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 0.5rem;
        }}

        h2 {{
            font-size: 1.35rem;
            font-weight: 600;
            color: #2c5282;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }}

        h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        h4 {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #4a5568;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }}

        .header-section {{
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}

        .header-section h1 {{
            color: white;
            margin-bottom: 1.5rem;
            font-size: 1.85rem;
        }}

        .header-metadata {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8rem;
            margin-top: 1.2rem;
        }}

        .metadata-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 0.6rem;
            border-radius: 4px;
        }}

        .metadata-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.8;
            margin-bottom: 0.25rem;
        }}

        .metadata-value {{
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
        }}

        .score-summary-first-page {{
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}

        .score-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: white;
        }}

        .score-table th {{
            background: #2c5282;
            color: white;
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
        }}

        .score-table td {{
            padding: 0.75rem;
            border: 1px solid #e2e8f0;
        }}

        .score-table tr:nth-child(even) {{
            background: #f7fafc;
        }}


        /* Follow-Up Questions Section */
        .follow-up-section {{
            background: #fff8e1;
            border-left: 4px solid #ff9800;
            padding: 24px;
            margin: 32px 0;
            border-radius: 8px;
            page-break-inside: avoid;
        }}

        .follow-up-intro {{
            color: #e65100;
            margin-bottom: 1rem;
        }}

        .follow-up-item {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 16px 0;
        }}

        .follow-up-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .follow-up-category {{
            background: #2196f3;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
        }}

        .follow-up-source {{
            color: #666;
            font-size: 14px;
            font-style: italic;
        }}

        .follow-up-quote {{
            background: #f5f5f5;
            border-left: 3px solid #ff9800;
            padding: 12px 16px;
            margin: 12px 0;
            font-style: italic;
            color: #333;
        }}

        .follow-up-action {{
            margin-top: 12px;
            color: #333;
        }}

        /* Scored Section - One section per page */
        .scored-section {{
            page-break-after: always;
            page-break-inside: avoid;
            margin: 1.5rem 0;
            padding: 1.5rem;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            min-height: 400px;
        }}

        .score-display {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 1rem 0;
            padding: 1rem;
            background: #f7fafc;
            border-radius: 4px;
        }}

        .score-label {{
            font-weight: 600;
            color: #4a5568;
        }}

        .score-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c5282;
        }}

        .combined-feedback {{
            background: #f8f9fa;
            border-left: 4px solid #2c5282;
            padding: 1.25rem;
            margin: 1rem 0;
            border-radius: 4px;
        }}

        .combined-feedback h4 {{
            color: #2c5282;
            margin-bottom: 0.75rem;
            font-size: 1rem;
        }}

        .feedback-synthesis {{
            margin-top: 0.75rem;
        }}

        .feedback-point {{
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #2c5282;
            line-height: 1.6;
        }}

        .feedback-point strong {{
            color: #2c5282;
            font-size: 0.9rem;
        }}

        .synthesis-list {{
            margin: 0.75rem 0 1rem 1.5rem;
            padding-left: 1rem;
        }}

        .synthesis-list li {{
            margin-bottom: 0.5rem;
            line-height: 1.6;
            color: #2d3748;
        }}

        .feedback-synthesis p {{
            margin: 0.75rem 0;
            line-height: 1.6;
        }}

        .feedback-synthesis strong {{
            color: #2c5282;
            font-weight: 600;
        }}

        @media print {{
            * {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            body {{
                padding: 0.25in;
                font-size: 9pt;
                line-height: 1.3;
            }}
            
            h1 {{
                font-size: 16pt;
                margin-bottom: 0.3rem;
            }}
            
            h2 {{
                font-size: 12pt;
                margin-top: 0.5rem;
                margin-bottom: 0.4rem;
                page-break-after: avoid;
            }}
            
            h3 {{
                font-size: 10pt;
                margin-top: 0.4rem;
                margin-bottom: 0.3rem;
            }}
            
            .header-section {{
                padding: 1rem;
                margin-bottom: 1rem;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            .header-metadata {{
                gap: 0.5rem;
            }}
            
            .metadata-item {{
                padding: 0.4rem;
            }}
            
            .metadata-label {{
                font-size: 7pt;
            }}
            
            .metadata-value {{
                font-size: 9pt;
            }}
            
            .score-summary-first-page {{
                page-break-after: always;
                padding: 0.75rem;
                margin-bottom: 1rem;
            }}
            
            .score-table {{
                margin: 0.75rem 0;
                font-size: 9pt;
            }}
            
            .score-table th,
            .score-table td {{
                padding: 0.35rem;
            }}
            
            .scored-section {{
                page-break-after: always;
                page-break-inside: avoid;
                margin: 0.5rem 0;
                padding: 0.75rem;
                border: 1px solid #e2e8f0;
                min-height: unset;
            }}
            
            .score-display {{
                margin: 0.5rem 0;
                padding: 0.5rem;
            }}
            
            .score-label {{
                font-size: 9pt;
            }}
            
            .score-value {{
                font-size: 14pt;
            }}
            
            .combined-feedback {{
                padding: 0.75rem;
                margin: 0.5rem 0;
            }}
            
            .combined-feedback h4 {{
                font-size: 9pt;
                margin-bottom: 0.4rem;
            }}
            
            .feedback-synthesis p {{
                margin: 0.4rem 0;
                line-height: 1.4;
                font-size: 9pt;
            }}
            
            .feedback-synthesis strong {{
                font-size: 9pt;
            }}
            
            .synthesis-list {{
                margin: 0.4rem 0 0.5rem 1rem;
                padding-left: 0.5rem;
            }}
            
            .synthesis-list li {{
                margin-bottom: 0.25rem;
                line-height: 1.4;
                font-size: 8.5pt;
            }}
            
            .follow-up-section {{
                page-break-before: always;
                page-break-inside: avoid;
                padding: 1rem;
                margin: 1rem 0;
            }}
            
            .follow-up-item {{
                padding: 0.75rem;
                margin: 0.75rem 0;
            }}
            
            .follow-up-quote {{
                padding: 0.5rem;
                margin: 0.5rem 0;
                font-size: 8.5pt;
            }}
        }}
    </style>
</head>
<body>
    <div class="header-section">
        <h1>2025 Year-End Account Review & 2026 QBR Readiness Scorecard</h1>
        <div class="header-metadata">
            <div class="metadata-item">
                <div class="metadata-label">Account Director</div>
                <div class="metadata-value">{ad_data['ad_name']}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Account</div>
                <div class="metadata-value">{ad_data['account']}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Tier</div>
                <div class="metadata-value">{tier}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Review Date</div>
                <div class="metadata-value">January 2026</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Total Reviews</div>
                <div class="metadata-value">{ad_data['review_count']}</div>
            </div>
        </div>
    </div>

    <div class="score-summary-first-page">
        <h2>Executive Summary</h2>

        <table class="score-table">
            <thead>
                <tr>
                    <th>Evaluation Category</th>
                    <th style="text-align: center;">Average Score</th>
                </tr>
            </thead>
            <tbody>
                {score_rows}
            </tbody>
        </table>
    </div>

    {sections_html}

    {follow_ups_html}

</body>
</html>
"""
    
    return html

def generate_all_scorecards():
    """Generate scorecards for all Account Directors."""
    print("Loading data...")
    df = load_review_data()
    follow_up_data = load_follow_up_questions()
    verticals_data = load_verticals()
    
    # Get unique AD names
    ad_names = df["Account Director Name"].unique()
    ad_names = [name for name in ad_names if pd.notna(name) and str(name).strip() != "" and name != "Account Director Name"]
    
    # Filter out joint review names (e.g., "Brian Davis / Justin Homa")
    # We'll add those reviews to each individual AD's report
    ad_names = [name for name in ad_names if '/' not in str(name)]
    
    print(f"Found {len(ad_names)} Account Directors")
    
    for ad_name in ad_names:
        print(f"\nGenerating scorecard for {ad_name}...")
        
        # Get aggregate data
        ad_data = calculate_aggregate_scores(df, ad_name)
        if not ad_data:
            print(f"  No review data found for {ad_name}")
            continue
        
        # Add tier data
        ad_data['tier'] = verticals_data.get(ad_name.strip(), 'Unassigned')
        
        # Get follow-ups (no best practices in scorecards)
        follow_ups = follow_up_data.get(ad_name.strip(), [])
        
        print(f"  Found {len(follow_ups)} follow-up items")
        print(f"  Total Score: {ad_data['total_score']}/40.0")
        
        # Generate HTML
        html = generate_scorecard_html(ad_data, [], follow_ups)
        
        # Save to file with sanitized filename
        safe_name = ad_name.strip().lower().replace(' ', '-').replace('/', '-').replace('\\', '-')
        filename = f"reports/{safe_name}-scorecard.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"  ✅ Saved to {filename}")
    
    print("\n🎉 All scorecards generated!")

if __name__ == "__main__":
    generate_all_scorecards()

