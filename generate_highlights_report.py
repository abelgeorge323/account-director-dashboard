"""
Generate Account Director Highlights & Development Report
Includes: Best Practices, Key Achievements, and Follow-Up Items
"""
import json

def load_data():
    """Load best practices and follow-up items"""
    with open("data/best-practices.json", "r", encoding="utf-8") as f:
        best_practices = json.load(f)
    
    with open("data/follow-up-questions.json", "r", encoding="utf-8") as f:
        follow_ups = json.load(f)
    
    return best_practices, follow_ups

def generate_html(best_practices, follow_ups):
    """Generate the highlights report HTML"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Director Highlights & Development Report 2025</title>
    <style>
        @page {
            margin: 0.5in;
            size: letter;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 20px;
            background: white;
            font-size: 10pt;
        }
        
        h1 {
            color: #1a73e8;
            border-bottom: 4px solid #1a73e8;
            padding-bottom: 10px;
            font-size: 28pt;
            margin: 0 0 20px 0;
        }
        
        h2 {
            color: #1a73e8;
            font-size: 20pt;
            margin: 30px 0 15px 0;
            page-break-after: avoid;
        }
        
        h3 {
            color: #555;
            font-size: 14pt;
            margin: 20px 0 10px 0;
            page-break-after: avoid;
        }
        
        h4 {
            color: #666;
            font-size: 11pt;
            margin: 15px 0 8px 0;
            font-weight: 600;
        }
        
        .section {
            page-break-after: always;
        }
        
        .best-practice {
            margin: 20px 0;
            padding: 15px;
            background: #f0f9ff;
            border-left: 5px solid #0ea5e9;
            page-break-inside: avoid;
        }
        
        .best-practice-title {
            font-weight: 700;
            color: #0369a1;
            font-size: 13pt;
            margin-bottom: 10px;
        }
        
        .best-practice-ad {
            color: #0891b2;
            font-size: 10pt;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .leadership-quote {
            background: #fef3c7;
            padding: 12px;
            border-left: 4px solid #f59e0b;
            margin: 10px 0;
            font-style: italic;
        }
        
        .account-highlight {
            margin: 20px 0;
            padding: 15px;
            background: #f0fdf4;
            border-left: 5px solid #10b981;
            page-break-inside: avoid;
        }
        
        .highlight-title {
            font-weight: 700;
            color: #047857;
            font-size: 12pt;
            margin-bottom: 8px;
        }
        
        .highlight-context {
            color: #065f46;
            font-size: 9pt;
            margin-bottom: 8px;
        }
        
        .action-item {
            margin: 15px 0;
            padding: 12px;
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            page-break-inside: avoid;
        }
        
        .action-title {
            font-weight: 600;
            color: #92400e;
            margin-bottom: 5px;
        }
        
        .action-meta {
            color: #78350f;
            font-size: 9pt;
            margin-bottom: 8px;
        }
        
        .quote {
            font-style: italic;
            color: #666;
            margin: 8px 0;
        }
        
        .criteria-box {
            background: #f0fdf4;
            border: 2px solid #10b981;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }
        
        .criteria-box h4 {
            color: #047857;
            margin-top: 0;
        }
        
        .criteria-box ol {
            margin: 10px 0;
            padding-left: 25px;
        }
        
        .criteria-box li {
            margin: 8px 0;
        }
        
        ul, ol {
            margin: 10px 0;
            padding-left: 30px;
        }
        
        li {
            margin: 5px 0;
        }
        
        p {
            margin: 10px 0;
        }
        
        @media print {
            body { padding: 0; }
            .section { page-break-after: always; }
            .best-practice, .account-highlight, .action-item { page-break-inside: avoid; }
            h2, h3, h4 { page-break-after: avoid; }
        }
    </style>
</head>
<body>
"""
    
    # Title Page
    html += """
    <div class="section">
        <h1>Account Director<br>Highlights & Development Report</h1>
        <p style="font-size: 14pt; color: #666; margin-top: 20px;">
            Best Practices, Key Achievements & Action Items<br>
            2025 Year-End Review
        </p>
        <p style="margin-top: 40px; color: #999; font-size: 9pt;">
            Generated: January 2026<br>
            Confidential & Proprietary
        </p>
    </div>
"""
    
    # Best Practices Section
    html += """
    <div class="section">
        <h2>🌟 Company Best Practices</h2>
        
        <div class="criteria-box">
            <h4>What Qualifies as a Best Practice?</h4>
            <p>To be classified as a <strong>Company Best Practice</strong>, an initiative must meet ALL five criteria:</p>
            <ol>
                <li><strong>Repeatable:</strong> Can be executed consistently across different accounts/situations</li>
                <li><strong>Material Impact:</strong> Demonstrates measurable financial, operational, or strategic value</li>
                <li><strong>Portable:</strong> Can be transferred and applied to other accounts or verticals</li>
                <li><strong>Intentionally Designed:</strong> Not accidental; was planned and executed with purpose</li>
                <li><strong>Leadership-Reinforced:</strong> Explicitly praised or endorsed by executive leadership</li>
            </ol>
        </div>
        
        <h3>Top Practices Identified for Enterprise Scaling</h3>
"""
    
    # Collect all best practices across all ADs
    all_practices = []
    for ad_name, practices in best_practices.items():
        for practice in practices:
            all_practices.append({
                "ad": ad_name,
                "title": practice.get("title", ""),
                "description": practice.get("description", ""),
                "context": practice.get("context", ""),
                "leadership_validation": practice.get("leadership_validation", "")
            })
    
    # Display best practices
    for idx, practice in enumerate(all_practices, 1):
        html += f"""
        <div class="best-practice">
            <div class="best-practice-title">{idx}. {practice['title']}</div>
            <div class="best-practice-ad">Account Director: {practice['ad']}</div>
            <p><strong>Description:</strong> {practice['description']}</p>
            <p><strong>Context:</strong> {practice['context']}</p>
"""
        if practice.get('leadership_validation'):
            html += f"""
            <div class="leadership-quote">
                <strong>Leadership Recognition:</strong> {practice['leadership_validation']}
            </div>
"""
        html += """
        </div>
"""
    
    html += """
    </div>
"""
    
    # Account Highlights Section
    html += """
    <div class="section">
        <h2>📊 Key Account Highlights & Achievements</h2>
        <p>Notable accomplishments, metrics, and innovations highlighted in presentations:</p>
"""
    
    # Group best practices by AD for highlights
    for ad_name in sorted(best_practices.keys()):
        if best_practices[ad_name]:
            html += f"""
        <h3>{ad_name}</h3>
"""
            for practice in best_practices[ad_name]:
                html += f"""
        <div class="account-highlight">
            <div class="highlight-title">{practice['title']}</div>
            <div class="highlight-context">{practice.get('context', '')}</div>
            <p>{practice.get('description', '')}</p>
        </div>
"""
    
    html += """
    </div>
"""
    
    # Follow-Up Items Section
    html += """
    <div class="section">
        <h2>📋 Development Focus & Follow-Up Items</h2>
        <p>Action items, challenges, and development areas identified through reviewer feedback:</p>
"""
    
    for ad_name in sorted(follow_ups.keys()):
        if follow_ups[ad_name]:
            html += f"""
        <h3>{ad_name}</h3>
"""
            for item in follow_ups[ad_name]:
                html += f"""
        <div class="action-item">
            <div class="action-title">{item.get('title', '')}</div>
            <div class="action-meta">
                Category: {item.get('category', 'General')} | 
                Reviewer: {item.get('reviewer', 'Anonymous')}
            </div>
            <div class="quote">"{item.get('quote', '')}"</div>
            <p><strong>Action Required:</strong> {item.get('action', '')}</p>
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
    print("🎯 Generating Highlights & Development Report...")
    print("📂 Loading data...")
    best_practices, follow_ups = load_data()
    
    # Count items
    total_practices = sum(len(practices) for practices in best_practices.values())
    total_follow_ups = sum(len(items) for items in follow_ups.values())
    
    print(f"✅ Found {total_practices} best practices")
    print(f"✅ Found {total_follow_ups} follow-up items")
    
    print("📝 Generating HTML...")
    html_content = generate_html(best_practices, follow_ups)
    
    print("💾 Writing report file...")
    with open("AD_Highlights_Report_2025.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("\n✅ SUCCESS! Report generated: AD_Highlights_Report_2025.html")
    print("   - Best Practices section")
    print("   - Account Highlights & Achievements")
    print("   - Development Focus & Follow-Up Items")

