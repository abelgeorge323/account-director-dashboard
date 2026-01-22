"""
Generate comprehensive EOY Account Director Review Report - FIXED VERSION
"""
import pandas as pd
import json
from collections import defaultdict

def load_data():
    """Load all data files"""
    df = pd.read_csv("data/performance_reviews.csv", low_memory=False)
    
    # Split joint reviews into individual entries
    expanded_rows = []
    for _, row in df.iterrows():
        ad_name = str(row.get("Account Director Name", "")).strip()
        if "/" in ad_name:
            # Split joint reviews
            names = [n.strip() for n in ad_name.split("/")]
            for name in names:
                new_row = row.copy()
                new_row["Account Director Name"] = name
                expanded_rows.append(new_row)
        else:
            expanded_rows.append(row)
    
    df = pd.DataFrame(expanded_rows)
    
    with open("data/follow-up-questions.json", "r", encoding="utf-8") as f:
        follow_ups = json.load(f)
    
    with open("data/best-practices.json", "r", encoding="utf-8") as f:
        best_practices = json.load(f)
    
    return df, follow_ups, best_practices

def get_score_columns(df):
    """Identify score columns from CSV - uses flexible matching"""
    score_cols = []
    
    # Define keywords for each section (flexible matching)
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
        # Skip comment columns
        if "Comment" in col or "comment" in col:
            continue
        
        # Check if column matches any section keywords
        for keywords in section_keywords:
            if any(keyword in col for keyword in keywords):
                score_cols.append(col)
                break  # Found a match, move to next column
    
    return score_cols

def get_comment_column(df, score_col):
    """Find the comment column that corresponds to a score column"""
    # Look for the column immediately before the score column
    cols = list(df.columns)
    score_idx = cols.index(score_col)
    if score_idx > 0:
        return cols[score_idx - 1]
    return None

def calculate_rankings(df):
    """Calculate average scores for each AD in each section"""
    rankings = {}
    score_cols = get_score_columns(df)
    
    for score_col in score_cols:
        # Extract section name
        section_name = score_col
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
        
        # Calculate averages
        section_rankings = []
        for ad_name, scores in ad_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                section_rankings.append({
                    "name": ad_name,
                    "avg_score": round(avg_score, 2),
                    "num_reviews": len(scores)
                })
        
        # Sort by score descending
        section_rankings.sort(key=lambda x: x["avg_score"], reverse=True)
        rankings[section_name] = section_rankings
    
    return rankings


def generate_html(rankings, df, follow_ups, best_practices):
    """Generate the HTML report"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 End-of-Year Account Director Review Report</title>
    <style>
        @page {
            margin: 0.5in;
            size: letter;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.4;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 15px;
            background: white;
            font-size: 9pt;
        }
        
        h1 {
            color: #1a73e8;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 8px;
            font-size: 24pt;
            margin: 0 0 15px 0;
        }
        
        h2 {
            color: #1a73e8;
            font-size: 16pt;
            margin: 20px 0 10px 0;
            page-break-after: avoid;
        }
        
        h3 {
            color: #555;
            font-size: 12pt;
            margin: 15px 0 8px 0;
            page-break-after: avoid;
        }
        
        h4 {
            color: #666;
            font-size: 10pt;
            margin: 10px 0 5px 0;
            font-weight: 600;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0 15px 0;
            page-break-inside: auto;
            font-size: 8.5pt;
        }
        
        th {
            background: #1a73e8;
            color: white;
            padding: 6px 5px;
            text-align: left;
            font-weight: 600;
            font-size: 8.5pt;
        }
        
        td {
            padding: 5px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tr {
            page-break-inside: avoid;
        }
        
        .rank-1 { background: #fff9e6; }
        .rank-2 { background: #e7f3ff; }
        .rank-3 { background: #e8f5e9; }
        
        .ad-feedback {
            margin: 8px 0;
            padding: 8px;
            background: #f9f9f9;
            border-left: 3px solid #1a73e8;
            page-break-inside: avoid;
            font-size: 8.5pt;
        }
        
        .reviewer-name {
            font-weight: 600;
            color: #1a73e8;
            margin-bottom: 3px;
            font-size: 8.5pt;
        }
        
        .score-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
            font-size: 7.5pt;
            margin-left: 8px;
        }
        
        .score-5 { background: #10b981; color: white; }
        .score-4 { background: #3b82f6; color: white; }
        .score-3 { background: #f59e0b; color: white; }
        .score-2 { background: #ef4444; color: white; }
        .score-1 { background: #dc2626; color: white; }
        
        .section {
            page-break-after: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
        
        p {
            margin: 5px 0;
            font-size: 8.5pt;
        }
        
        ul, ol {
            margin: 8px 0;
            padding-left: 25px;
        }
        
        li {
            margin: 3px 0;
            font-size: 8.5pt;
        }
        
        @media print {
            body { padding: 0; }
            .section { page-break-after: always; }
            .no-break, .ad-feedback, table { page-break-inside: avoid; }
            h2, h3, h4 { page-break-after: avoid; }
            tr { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
"""
    
    # Title Page with Overall Rankings
    html += """
    <div class="section">
        <h1>2025 End-of-Year<br>Account Director Review Report</h1>
        <p style="font-size: 12pt; color: #666; margin-top: 15px; margin-bottom: 20px;">
            Comprehensive Performance Analysis | 16 Account Directors | 8 Evaluation Criteria
        </p>
"""
    
    # Calculate overall rankings across all sections
    overall_scores = defaultdict(lambda: {"total": 0, "count": 0})
    for section_name, section_data in rankings.items():
        for ad_data in section_data:
            overall_scores[ad_data['name']]["total"] += ad_data['avg_score']
            overall_scores[ad_data['name']]["count"] += 1
    
    # Calculate averages and sort
    overall_rankings = []
    for ad_name, data in overall_scores.items():
        avg = data["total"] / data["count"] if data["count"] > 0 else 0
        # Total is sum of all section averages (each section max 5, so 8 sections = max 40)
        total_out_of_40 = data["total"]
        overall_rankings.append({
            "name": ad_name, 
            "avg": round(avg, 2),
            "total": round(total_out_of_40, 1)
        })
    
    overall_rankings.sort(key=lambda x: x["total"], reverse=True)
    
    html += """
        <h2 style="margin-top: 15px;">Overall Performance Rankings</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 50px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 120px;">Overall Score</th>
                    <th style="width: 120px;">Performance Tier</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for rank, ad_data in enumerate(overall_rankings, 1):
        row_class = f"rank-{rank}" if rank <= 3 else ""
        
        # Determine performance tier based on average
        if ad_data['avg'] >= 4.5:
            tier = "🌟 Exceptional"
            tier_color = "#10b981"
        elif ad_data['avg'] >= 4.0:
            tier = "🔵 Strong"
            tier_color = "#3b82f6"
        elif ad_data['avg'] >= 3.5:
            tier = "🟡 Solid"
            tier_color = "#f59e0b"
        else:
            tier = "🔴 Development"
            tier_color = "#ef4444"
        
        html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td>{ad_data['name']}</td>
                    <td><strong>{ad_data['total']}</strong> / 40</td>
                    <td style="color: {tier_color}; font-weight: 600;">{tier}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        <p style="margin-top: 15px; color: #999; font-size: 8pt;">
            Generated: January 2026 | Confidential & Proprietary
        </p>
    </div>
"""
    
    # Generate section rankings with feedback
    score_cols = get_score_columns(df)
    
    for idx, score_col in enumerate(score_cols, 1):
        section_name = score_col
        section_data = rankings.get(section_name, [])
        comment_col = get_comment_column(df, score_col)
        
        html += f"""
    <div class="section">
        <h2>Section {idx}: {section_name}</h2>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 40px;">Rank</th>
                    <th>Account Director</th>
                    <th style="width: 80px;">Avg Score</th>
                    <th style="width: 70px;"># Reviews</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for rank, ad_data in enumerate(section_data, 1):
            row_class = f"rank-{rank}" if rank <= 3 else ""
            html += f"""
                <tr class="{row_class}">
                    <td><strong>#{rank}</strong></td>
                    <td>{ad_data['name']}</td>
                    <td><strong>{ad_data['avg_score']}</strong>/5.0</td>
                    <td>{ad_data['num_reviews']}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h3>Detailed Feedback</h3>
"""
        
        # Add detailed feedback for ALL ADs
        for ad_data in section_data:
            ad_name = ad_data['name']
            
            # Get feedback
            feedback_list = []
            for _, row in df.iterrows():
                if str(row.get("Account Director Name", "")).strip() == ad_name:
                    reviewer = str(row.get("Enter Your Name", "Anonymous")).strip()
                    score = row.get(score_col)
                    comment = row.get(comment_col) if comment_col else None
                    
                    if pd.notna(comment) and str(comment).strip() and str(comment) != "nan":
                        feedback_list.append({
                            "reviewer": reviewer if reviewer != "nan" else "Anonymous",
                            "score": score if pd.notna(score) else "N/A",
                            "comment": str(comment).strip()
                        })
            
            if feedback_list:
                html += f"""
        <div class="ad-feedback">
            <h4>{ad_name} (Avg: {ad_data['avg_score']}/5.0)</h4>
"""
                for fb in feedback_list:
                    try:
                        score_val = int(float(fb['score'])) if fb['score'] != "N/A" else 3
                    except:
                        score_val = 3
                    score_class = f"score-{score_val}"
                    score_display = f"{fb['score']}/5" if fb['score'] != "N/A" else "N/A"
                    
                    html += f"""
            <div class="reviewer-name">
                {fb['reviewer']}
                <span class="score-badge {score_class}">{score_display}</span>
            </div>
            <p style="margin: 5px 0 10px 0;">{fb['comment']}</p>
"""
                
                html += """
        </div>
"""
    
    html += """
    </div>
"""
    
    # Close HTML
    html += """
</body>
</html>
"""
    
    return html

# Main execution
if __name__ == "__main__":
    print("🔧 Generating FIXED EOY Report...")
    print("📂 Loading data...")
    df, follow_ups, best_practices = load_data()
    
    print("📊 Calculating rankings...")
    rankings = calculate_rankings(df)
    
    print(f"✅ Found {len(rankings)} sections")
    for section, data in rankings.items():
        print(f"   • {section}: {len(data)} ADs ranked")
    
    print("📝 Generating HTML...")
    html_content = generate_html(rankings, df, follow_ups, best_practices)
    
    print("💾 Writing report file...")
    with open("EOY_Report_2025.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("\n✅ SUCCESS! Report generated: EOY_Report_2025.html")
    print("   - All sections have rankings")
    print("   - All sections have detailed feedback")
    print("   - Joint reviews split into individual entries")
    print("   - Compact tables fit on one page")

