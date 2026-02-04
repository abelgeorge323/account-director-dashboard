import csv
from collections import defaultdict
from datetime import datetime

# Review time data
review_schedule = {
    'Week 1 (Jan 6-10)': {
        'status': 'completed',
        'reviews': [
            ('Benjamin Ehrenberg', 30),
            ('Brian Davis', 30),
            ('Justin Homa', 30)
        ]
    },
    'Week 2 (Jan 13-17)': {
        'status': 'completed',
        'reviews': [
            ('Mark Schlerf', 30), ('Grant Frazier', 30), ('Stuart Kelloff', 30),
            ('Jacqueline Maravilla', 30), ('Paul Rhodes', 30), ('Kimberly Wittekind', 30),
            ('Peggy Shum', 30), ('Taylor Wattenberg', 30), ('Jack Thornton', 30),
            ('Isaac Calderon', 60), ('Patrick Murtha', 30), ('Aaron Simpson', 30),
            ('Justin Dallavis', 30), ('Ana Sabater', 30)
        ]
    },
    'Week 3 (Jan 27-31)': {
        'status': 'completed',
        'reviews': [
            ('David Pergola', 30), ('Thomas Mahoney', 30), ('Giselle Langelier', 30),
            ('Rade Kukobat', 30), ('Gregory DeMedio', 30), ('Peggy Shum Redo', 30),
            ('Logan Newman', 60), ('Luis Cabrera', 30), ('Scott Kimball', 30),
            ('Nick Trenkamp', 30), ('Julie Bianchi', 30), ('Brian Davis Redo', 30),
            ('Jacob Reed', 30), ('Ayesha Nasir', 30), ('Mike Barry', 30),
            ('Siddarth Shah', 40), ('Rafaed Ortiz', 30)
        ]
    },
    'Week 4 (Feb 3-7)': {
        'status': 'planned',
        'reviews': [
            ('Dustin Smith', 45), ('Joshua Grady', 30), ('Collen Doles', 50),
            ('Berenday Escamilla', 30), ('Tiffany Purifoy', 50), ('RJ Ober', 45),
            ('Jeremy Johnson', 30)
        ]
    },
    'Week 5 (Feb 10-14)': {
        'status': 'planned',
        'reviews': [
            ('Corey Wallace', 60), ('Jennifer Segovia', 60), ('Robert Wallen', 30)
        ]
    }
}

# Name normalization - maps review schedule names to verticals.csv names
name_normalize = {
    'Stuart Kellof': 'Stuart Kelloff',
    'Jack Thorton': 'Jack Thornton',
    'Gisell Langelir': 'Giselle Langelier',
    'Kimberley Wittekind': 'Kimberly Wittekind',
    'Peggy Shum McElewee': 'Peggy Shum',
    'Dave Peregola': 'David Pergola',
    'Nick Trenkamp': 'Nicholas Trenkamp',  # Map to verticals.csv name
    'Gregory DeMedio': 'Greg Demedio',      # Map to verticals.csv name
    'Tiffany Puriofy': 'Tiffany Purifoy',
    'Colleen Doles': 'Collen Doles',        # Map to verticals.csv name
    'Peggy Shum Redo': 'Peggy Shum',        # Consolidate redo
    'Brian Davis Redo': 'Brian Davis'       # Consolidate redo
}

# Read verticals data
verticals_data = {}
with open('data/verticals.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ad_name = row['Account Director'].strip()
        verticals_data[ad_name] = {
            'vertical': row['Vertical'].strip(),
            'tier': row['Tier'].strip()
        }

# Read performance reviews to get accounts and reviewers
with open('data/performance_reviews.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    reviews_data = list(reader)

# Build AD info
ad_info = {}
ad_reviewers = defaultdict(set)
ad_accounts = defaultdict(set)

for row in reviews_data:
    ad = row['Account Director Name'].strip()
    
    # Normalize AD names
    ad_normalized = ad
    for old, new in [('Ayesha Nasi', 'Ayesha Nasir'), ('Dave Pergola', 'David Pergola'),
                     ('Gisell Langelier', 'Giselle Langelier'), ('Greg DeMedio', 'Gregory DeMedio'),
                     ('Greg Demedio', 'Gregory DeMedio'), ('Nike Trenkamp', 'Nick Trenkamp'),
                     ('Brian Davis / Justin Homa', 'Brian Davis'), ("Logan Newman's", 'Logan Newman')]:
        if ad == old:
            ad_normalized = new
            break
    
    reviewer = row['Name'].strip() if row['Name'].strip() else row.get('Enter Your Name', '').strip()
    account = row['Account Name'].strip()
    
    if reviewer:
        ad_reviewers[ad_normalized].add(reviewer)
    if account:
        ad_accounts[ad_normalized].add(account)

# Calculate statistics
completed_reviews = []
planned_reviews = []
unique_completed_ads = set()
unique_planned_ads = set()

for week, data in review_schedule.items():
    for ad_name, minutes in data['reviews']:
        # Normalize name
        ad_normalized = name_normalize.get(ad_name, ad_name)
        
        review_info = {
            'name': ad_normalized,
            'original_name': ad_name,
            'minutes': minutes,
            'week': week,
            'status': data['status']
        }
        
        if data['status'] == 'completed':
            completed_reviews.append(review_info)
            unique_completed_ads.add(ad_normalized)
        else:
            planned_reviews.append(review_info)
            unique_planned_ads.add(ad_normalized)

# Count unique ADs
total_unique_ads = len(unique_completed_ads | unique_planned_ads)

# Get vertical/tier stats
vertical_stats = defaultdict(lambda: {'count': 0, 'time': 0})
tier_stats = defaultdict(lambda: {'count': 0, 'time': 0})

for review in completed_reviews + planned_reviews:
    ad_name = review['name']
    if ad_name in verticals_data:
        vert = verticals_data[ad_name]['vertical']
        tier = verticals_data[ad_name]['tier']
        
        vertical_stats[vert]['count'] += 1
        vertical_stats[vert]['time'] += review['minutes']
        
        tier_stats[tier]['count'] += 1
        tier_stats[tier]['time'] += review['minutes']

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EOY Account Director Review Tracking Report - 2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .page {{
            background: white;
            max-width: 1200px;
            margin: 20px auto;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            page-break-after: always;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 4px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            color: #7f8c8d;
        }}
        
        .header .date {{
            font-size: 0.9em;
            color: #95a5a6;
            margin-top: 10px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .summary-card.completed {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .summary-card.planned {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .summary-card.total {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            grid-column: span 2;
        }}
        
        .summary-card h3 {{
            font-size: 1.1em;
            margin-bottom: 15px;
            opacity: 0.9;
        }}
        
        .summary-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 8px 0;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .section {{
            margin: 30px 0;
            page-break-inside: avoid;
        }}
        
        .section h2 {{
            font-size: 1.6em;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #3498db;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
        }}
        
        td {{
            padding: 8px 10px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 0.9em;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .vertical-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        
        .vertical-card {{
            background: white;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .vertical-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .vertical-card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        
        .vertical-card .count {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        
        .vertical-card .time {{
            color: #7f8c8d;
            margin-top: 10px;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
            margin: 20px 0;
        }}
        
        .timeline-item {{
            position: relative;
            padding: 15px;
            margin-bottom: 20px;
            background: white;
            border-left: 4px solid #3498db;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .timeline-item.completed {{
            border-left-color: #27ae60;
        }}
        
        .timeline-item.planned {{
            border-left-color: #e74c3c;
            opacity: 0.8;
        }}
        
        .timeline-item h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .timeline-item .stats {{
            display: flex;
            gap: 30px;
            margin-top: 10px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        
        .ad-card {{
            background: white;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .ad-card h3 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .ad-card-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 15px 0;
        }}
        
        .ad-card-item {{
            display: flex;
            align-items: center;
        }}
        
        .ad-card-item strong {{
            min-width: 120px;
            color: #7f8c8d;
        }}
        
        .reviewers-list {{
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .reviewers-list h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .reviewers-list ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .reviewers-list li {{
            padding: 5px 0;
            color: #555;
        }}
        
        .reviewers-list li:before {{
            content: "✓ ";
            color: #27ae60;
            font-weight: bold;
            margin-right: 5px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge.completed {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge.planned {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .badge.tier {{
            background: #cce5ff;
            color: #004085;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .page {{
                box-shadow: none;
                margin: 0;
                padding: 30px;
            }}
            .section {{
                page-break-inside: avoid;
            }}
            .timeline-item {{
                page-break-inside: avoid;
            }}
            table {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>

<!-- PAGE 1: EXECUTIVE SUMMARY -->
<div class="page">
    <div class="header">
        <h1>End of Year Review Tracking Report</h1>
        <div class="subtitle">Account Director Performance Reviews - 2025</div>
        <div class="date">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>
    
    <div class="summary-grid">
        <div class="summary-card completed">
            <h3>COMPLETED REVIEWS</h3>
            <div class="number">{len(unique_completed_ads)}</div>
            <div class="label">{sum(r['minutes'] for r in completed_reviews)} minutes ({sum(r['minutes'] for r in completed_reviews)/60:.1f} hours)</div>
        </div>
        
        <div class="summary-card planned">
            <h3>PLANNED REVIEWS</h3>
            <div class="number">{len(unique_planned_ads)}*</div>
            <div class="label">{sum(r['minutes'] for r in planned_reviews)} minutes ({sum(r['minutes'] for r in planned_reviews)/60:.1f} hours)*</div>
        </div>
        
        <div class="summary-card total">
            <h3>TOTAL PROGRAM</h3>
            <div class="number">{total_unique_ads}*</div>
            <div class="label">{sum(r['minutes'] for r in completed_reviews + planned_reviews)} minutes ({sum(r['minutes'] for r in completed_reviews + planned_reviews)/60:.1f} hours)* | Avg: {sum(r['minutes'] for r in completed_reviews + planned_reviews)/total_unique_ads:.0f} min/review</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Completion Status</h2>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {len(unique_completed_ads)/total_unique_ads*100:.0f}%">
                {len(unique_completed_ads)/total_unique_ads*100:.0f}% Complete
            </div>
        </div>
        <p style="text-align: center; color: #7f8c8d; margin-top: 10px;">
            {len(unique_completed_ads)} of {total_unique_ads} reviews completed
        </p>
    </div>
    
    <!-- BREAKDOWN BY VERTICAL & TIER (COMBINED ON PAGE 1) -->
    <div class="header" style="margin-top: 50px;">
        <h1 style="font-size: 2em;">Breakdown by Vertical</h1>
    </div>
    
    <div class="vertical-grid">
"""

# Add vertical cards
for vertical in sorted(vertical_stats.keys()):
    stats = vertical_stats[vertical]
    html += f"""
        <div class="vertical-card">
            <h3>{vertical}</h3>
            <div class="count">{stats['count']}</div>
            <div class="label">Account Directors</div>
            <div class="time">{stats['time']/60:.1f} hours</div>
        </div>
"""

html += """
    </div>
    
    <div class="section" style="margin-top: 30px;">
        <h2 style="font-size: 1.5em;">Vertical Details</h2>
        <table style="margin: 15px 0;">
            <thead>
                <tr>
                    <th>Vertical</th>
                    <th>Count</th>
                    <th>Total Time</th>
                    <th>Avg Time</th>
                    <th>% of Total</th>
                </tr>
            </thead>
            <tbody>
"""

total_reviews = len(completed_reviews) + len(planned_reviews)
for vertical in sorted(vertical_stats.keys(), key=lambda x: vertical_stats[x]['count'], reverse=True):
    stats = vertical_stats[vertical]
    avg_time = stats['time'] / stats['count']
    pct = (stats['count'] / total_reviews) * 100
    
    html += f"""
                <tr>
                    <td><strong>{vertical}</strong></td>
                    <td>{stats['count']}</td>
                    <td>{stats['time']} min ({stats['time']/60:.1f} hrs)</td>
                    <td>{avg_time:.0f} min</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""

html += """
            </tbody>
        </table>
    </div>
    
    <div class="section" style="margin-top: 30px;">
        <h2 style="font-size: 1.5em;">Breakdown by Tier</h2>
        <table style="margin: 15px 0;">
            <thead>
                <tr>
                    <th>Tier</th>
                    <th>Count</th>
                    <th>Total Time</th>
                    <th>Avg Time</th>
                    <th>% of Total</th>
                </tr>
            </thead>
            <tbody>
"""

for tier in sorted(tier_stats.keys(), reverse=True):
    stats = tier_stats[tier]
    avg_time = stats['time'] / stats['count']
    pct = (stats['count'] / total_reviews) * 100
    
    html += f"""
                <tr>
                    <td><strong>{tier}</strong></td>
                    <td>{stats['count']}</td>
                    <td>{stats['time']} min ({stats['time']/60:.1f} hrs)</td>
                    <td>{avg_time:.0f} min</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""

html += """
            </tbody>
        </table>
    </div>
</div>

<!-- PAGE 2: WEEKLY TIMELINE & UPCOMING REVIEWS -->
<div class="page">
    <div class="header" style="padding-bottom: 6px; margin-bottom: 10px;">
        <h1 style="font-size: 1.6em;">Review Schedule Overview</h1>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 15px;">
"""

for week, data in review_schedule.items():
    week_time = sum(r[1] for r in data['reviews'])
    status_class = 'completed' if data['status'] == 'completed' else 'planned'
    bg_color = '#d4edda' if status_class == 'completed' else '#f8d7da'
    border_color = '#27ae60' if status_class == 'completed' else '#e74c3c'
    
    html += f"""
        <div style="background: {bg_color}; border-left: 3px solid {border_color}; padding: 6px 8px; font-size: 0.85em; border-radius: 3px;">
            <div style="font-weight: bold; font-size: 0.9em; margin-bottom: 3px;">{week.split('(')[0].strip()}</div>
            <div style="color: #555;">{len(data['reviews'])} reviews</div>
            <div style="color: #555;">{week_time/60:.1f} hrs</div>
        </div>
"""

html += """
    </div>
    
    <!-- UPCOMING REVIEWS (DETAILED) -->
    <div style="margin-top: 10px;">
        <h2 style="font-size: 1.3em; color: #2c3e50; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 3px solid #3498db;">Upcoming Reviews</h2>

"""

# Group planned reviews by week
planned_by_week = defaultdict(list)
for review in planned_reviews:
    planned_by_week[review['week']].append(review)

# Generate weekly sections
for week in sorted(planned_by_week.keys()):
    week_reviews = planned_by_week[week]
    total_time = sum(r['minutes'] for r in week_reviews)
    
    html += f"""
            <div style="margin-bottom: 10px; page-break-inside: avoid;">
                <h3 style="font-size: 0.9em; margin-bottom: 4px; padding: 6px 8px; background: #f8d7da; border-left: 3px solid #e74c3c; border-radius: 2px; font-weight: 600;">{week} <span style="font-size: 0.8em; font-weight: normal;">({len(week_reviews)} reviews, {total_time} min)</span></h3>
                
                <table style="margin: 0; font-size: 0.85em;">
                    <thead>
                        <tr>
                            <th style="padding: 4px 6px; font-size: 0.85em;">Account Director</th>
                            <th style="padding: 4px 6px; font-size: 0.85em;">Vertical</th>
                            <th style="padding: 4px 6px; font-size: 0.85em;">Tier</th>
                            <th style="padding: 4px 6px; font-size: 0.85em;">Time</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for review in week_reviews:
        ad_name = review['name']
        vertical = verticals_data.get(ad_name, {}).get('vertical', 'TBD')
        tier = verticals_data.get(ad_name, {}).get('tier', 'TBD')
        
        html += f"""
                        <tr>
                            <td style="padding: 3px 6px;"><strong>{ad_name}</strong></td>
                            <td style="padding: 3px 6px;">{vertical}</td>
                            <td style="padding: 3px 6px;"><span class="badge tier" style="padding: 2px 5px; font-size: 0.8em;">{tier}</span></td>
                            <td style="padding: 3px 6px;">{review['minutes']} min</td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
            </div>
"""

html += """
    </div>
</div>

</body>
</html>
"""

# Write HTML file
output_file = 'EOY_Review_Tracking_Report_2025.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"SUCCESS: Report generated successfully: {output_file}")
print(f"\nSummary:")
print(f"  - {len(unique_completed_ads)} unique ADs completed ({sum(r['minutes'] for r in completed_reviews)/60:.1f} hours, {len(completed_reviews)} sessions)")
print(f"  - {len(unique_planned_ads)} unique ADs planned ({sum(r['minutes'] for r in planned_reviews)/60:.1f} hours, {len(planned_reviews)} sessions)")
print(f"  - {total_unique_ads} total unique ADs ({sum(r['minutes'] for r in completed_reviews + planned_reviews)/60:.1f} hours)")
print(f"\nOpen the HTML file in your browser to view the report.")
print(f"You can then print to PDF using your browser's print function (Ctrl+P -> Save as PDF)")
