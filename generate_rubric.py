"""
Generate a standalone rubric PDF for Account Director evaluations.
No scores - just the evaluation criteria to share with reviewers.
"""

def generate_rubric_html():
    """Generate HTML for the evaluation rubric."""
    
    rubric_sections = {
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
    
    # Build sections HTML
    sections_html = ""
    for i, (section_name, section_data) in enumerate(rubric_sections.items(), 1):
        sections_html += f"""
        <div class="rubric-section">
            <h2>{i}. {section_name}</h2>
            <p class="definition"><strong>Definition:</strong> {section_data['definition']}</p>
            
            <table class="criteria-table">
                <thead>
                    <tr>
                        <th style="width: 10%; text-align: center;">Score</th>
                        <th style="width: 90%;">Criteria</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add criteria rows (5 to 1)
        for score in ["5", "4", "3", "2", "1"]:
            score_class = f"score-{score}"
            sections_html += f"""
                    <tr class="{score_class}">
                        <td style="text-align: center; font-weight: 700; font-size: 1.2rem;">{score}</td>
                        <td>{section_data['criteria'][score]}</td>
                    </tr>
            """
        
        sections_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Complete HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 Account Director Leadership Evaluation Rubric</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: #f8f9fa;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 3rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .title-page {{
            text-align: center;
            padding: 4rem 2rem;
            border-bottom: 3px solid #2c5282;
            margin-bottom: 3rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            color: #2c5282;
            margin-bottom: 1rem;
        }}
        
        .subtitle {{
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }}
        
        .rubric-section {{
            margin-bottom: 3rem;
            page-break-inside: avoid;
        }}
        
        h2 {{
            color: #2c5282;
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .definition {{
            color: #555;
            font-style: italic;
            margin-bottom: 1rem;
            padding: 0.75rem;
            background: #f7fafc;
            border-left: 4px solid #2c5282;
        }}
        
        .criteria-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        .criteria-table th {{
            background: #2c5282;
            color: white;
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
        }}
        
        .criteria-table td {{
            padding: 0.75rem;
            border: 1px solid #e2e8f0;
        }}
        
        .criteria-table tbody tr:hover {{
            background: #f7fafc;
        }}
        
        .score-5 {{
            background: #ecfdf5;
        }}
        
        .score-4 {{
            background: #f0fdf4;
        }}
        
        .score-3 {{
            background: #fffbeb;
        }}
        
        .score-2 {{
            background: #fef2f2;
        }}
        
        .score-1 {{
            background: #fef2f2;
        }}
        
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }}
        
        @media print {{
            * {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            body {{
                padding: 0;
                background: white;
            }}
            
            .container {{
                box-shadow: none;
                padding: 0.5in;
            }}
            
            .rubric-section {{
                page-break-inside: avoid;
            }}
            
            h1 {{
                font-size: 24pt;
            }}
            
            h2 {{
                font-size: 14pt;
                page-break-after: avoid;
            }}
            
            .criteria-table {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title-page">
            <h1>2025 Account Director Leadership Evaluation</h1>
            <p class="subtitle">Scoring Rubric & Evaluation Criteria</p>
            <p style="color: #888; margin-top: 2rem;">
                This rubric defines the evaluation criteria for the 2025 Year-End Account Director Reviews.<br>
                Each section is scored on a scale of 1-5, with a total possible score of 40 points.
            </p>
        </div>
        
        {sections_html}
        
        <div class="footer">
            <p><strong>Total Possible Score: 40 points</strong> (8 sections × 5 points each)</p>
            <p style="margin-top: 0.5rem;">Generated: January 2026 | SBM Management Services</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Generate the rubric HTML file."""
    print("=" * 70)
    print("GENERATING EVALUATION RUBRIC")
    print("=" * 70)
    
    print("\n📄 Creating rubric HTML...")
    html = generate_rubric_html()
    
    # Save HTML
    output_file = "Evaluation_Rubric_2025.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Rubric saved: {output_file}")
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("1. Open the HTML file in your browser")
    print("2. Print to PDF (Ctrl+P or Cmd+P)")
    print("3. Share with reviewers!")
    print("=" * 70)


if __name__ == "__main__":
    main()

