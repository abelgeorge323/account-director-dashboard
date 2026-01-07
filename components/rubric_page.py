"""
Rubric reference page component.
Displays scoring methodology and evaluation criteria.
"""

import streamlit as st
import pandas as pd
from data_processor import TOTAL_MAX_SCORE, MAX_SCORE_PER_SECTION


# Define detailed rubric criteria matching the HTML scorecard
DETAILED_RUBRICS = {
    "Key Projects & Initiatives": {
        "definition": "Evaluates ability to articulate meaningful work and outcomes",
        "criteria": {
            5: "Clearly frames the most important 2025 initiatives, why they mattered, and what changed for the client as a result; demonstrates strong judgment, prioritization, and impact awareness",
            4: "Presents a clear narrative of key initiatives and outcomes, with minor gaps in impact clarity or measurement",
            3: "Accurately describes initiatives but focuses more on execution than client outcomes or strategic impact",
            2: "Mentions projects but lacks ownership, prioritization, or clarity on why they mattered",
            1: "Unable to clearly articulate major initiatives or their relevance"
        }
    },
    "Value Adds & Cost Avoidance": {
        "definition": "Evaluates ability to demonstrate value beyond contract scope",
        "criteria": {
            5: "Clearly articulates value delivered beyond contract scope and translates it into estimated financial, operational, or risk-based impact",
            4: "Provides strong examples of value creation with partial or directional financial framing",
            3: "Describes value adds but does not translate them into financial or business impact",
            2: "Examples are vague or lack clarity on value delivered",
            1: "No meaningful value creation discussed"
        }
    },
    "Cost Savings Delivered": {
        "definition": "Evaluates financial stewardship and operational efficiency",
        "criteria": {
            5: "Clearly explains how cost savings were created, quantified, and sustained; demonstrates strong financial stewardship",
            4: "Identifies cost savings with reasonable clarity and some indication of sustainability",
            3: "Mentions cost savings but with limited explanation or primarily one-time impact",
            2: "Savings referenced without clear understanding, ownership, or credibility",
            1: "No cost savings articulated"
        }
    },
    "Innovation & Continuous Improvement": {
        "definition": "Evaluates leadership in evolving service delivery",
        "criteria": {
            5: "Demonstrates intentional innovation or meaningful pivots, with clear outcomes and lessons learned",
            4: "Introduced improvements or adaptations that positively impacted the account",
            3: "Participated in improvement efforts but with limited leadership or ownership",
            2: "Discusses ideas or concepts without execution or demonstrated impact",
            1: "No evidence of innovation or continuous improvement"
        }
    },
    "Issues, Challenges & Accountability": {
        "definition": "Evaluates self-awareness, ownership, and executive leadership",
        "criteria": {
            5: "Fully transparent about challenges, clearly owns gaps, and outlines specific corrective actions with timelines",
            4: "Identifies challenges and discusses improvement actions with reasonable clarity",
            3: "Acknowledges issues but provides limited reflection, ownership, or follow-through",
            2: "Defensive, vague, or minimizes challenges without accountability",
            1: "Avoids or fails to address challenges altogether"
        }
    },
    "2026 Forward Strategy & Vision": {
        "definition": "Evaluates strategic thinking and future readiness",
        "criteria": {
            5: "Articulates a clear, compelling 2026 account roadmap tied to retention, growth, and differentiation, with defined priorities and sequencing",
            4: "Presents a strong forward-looking plan with reasonable clarity and timelines",
            3: "Shares general goals or aspirations without clear execution detail",
            2: "Strategy is reactive, unclear, or lacks cohesion",
            1: "No meaningful forward strategy articulated"
        }
    },
    "Personal Goals & Role Maturity": {
        "definition": "Evaluates professional growth and role ownership",
        "criteria": {
            5: "Clearly defines measurable leadership goals that demonstrate role maturity, accountability, and impact on account performance",
            4: "Establishes thoughtful goals with progress and clearly articulated next steps",
            3: "Shares general development intentions without clear measures or ownership",
            2: "Goals are vague, unclear, or not actionable",
            1: "No articulated leadership or development goals"
        }
    },
    "Executive Presence & Presentation Skills": {
        "definition": "Evaluates effectiveness in delivering the review to executive leadership",
        "criteria": {
            5: "Leads the discussion with confidence and authority; presents a clear, structured account narrative and responds effectively to executive questions",
            4: "Communicates clearly with logical flow; delivers a cohesive account story with minor gaps in executive presence or impact",
            3: "Communicates key points but relies heavily on prepared material; executive presence is limited",
            2: "Communication lacks clarity or structure; executive presence is inconsistent",
            1: "Unable to effectively lead the discussion at an executive level"
        }
    }
}


def render_rubric_page(rubric_data):
    """Render the scoring rubric reference page."""
    
    st.markdown("### 📋 Performance Evaluation Rubric")
    st.markdown(
        """
        <p style='color: #64748b; font-size: 1.05em; margin-bottom: 2rem;'>
        This rubric defines the scoring methodology used for Account Director performance evaluations. 
        Each section is scored on a scale of 1-5, with detailed criteria outlined below.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Overall scoring summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
            padding: 24px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(30, 58, 138, 0.3);'>
                <div style='font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;'>TOTAL SECTIONS</div>
                <div style='font-size: 2.5em; font-weight: 700;'>{len(rubric_data)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); 
            padding: 24px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);'>
                <div style='font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;'>POINTS PER SECTION</div>
                <div style='font-size: 2.5em; font-weight: 700;'>{MAX_SCORE_PER_SECTION}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
            padding: 24px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);'>
                <div style='font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;'>MAXIMUM SCORE</div>
                <div style='font-size: 2.5em; font-weight: 700;'>{TOTAL_MAX_SCORE}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Score interpretation guide
    st.markdown("### 🎯 Score Interpretation Guide")
    
    score_guide_col1, score_guide_col2 = st.columns(2)
    
    with score_guide_col1:
        st.markdown(
            """
            <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);'>
                <h4 style='color: #1e3a8a; margin-bottom: 16px;'>Individual Section Scores</h4>
                <ul style='color: #475569; line-height: 1.8;'>
                    <li><strong>5 - Exceptional:</strong> Exceeds all expectations with measurable impact</li>
                    <li><strong>4 - Strong:</strong> Consistently meets and often exceeds expectations</li>
                    <li><strong>3 - Meets Expectations:</strong> Solid performance across key areas</li>
                    <li><strong>2 - Developing:</strong> Some gaps, requires improvement</li>
                    <li><strong>1 - Needs Improvement:</strong> Significant development required</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with score_guide_col2:
        st.markdown(
            """
            <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);'>
                <h4 style='color: #1e3a8a; margin-bottom: 16px;'>Total Score Ranges</h4>
                <ul style='color: #475569; line-height: 1.8;'>
                    <li><strong>36-40:</strong> Outstanding overall performance</li>
                    <li><strong>32-35:</strong> Strong overall performance</li>
                    <li><strong>24-31:</strong> Solid, meets expectations</li>
                    <li><strong>16-23:</strong> Developing, improvement needed</li>
                    <li><strong>8-15:</strong> Significant development required</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='margin: 48px 0;'></div>", unsafe_allow_html=True)
    
    # Detailed section rubrics with HTML tables
    st.markdown("### 📊 Detailed Section Criteria")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    # Get section names from rubric_data
    section_names = [
        "Key Projects & Initiatives",
        "Value Adds & Cost Avoidance",
        "Cost Savings Delivered",
        "Innovation & Continuous Improvement",
        "Issues, Challenges & Accountability",
        "2026 Forward Strategy & Vision",
        "Personal Goals & Role Maturity",
        "Executive Presence & Presentation Skills"
    ]
    
    for i, section_name in enumerate(section_names, 1):
        if section_name in DETAILED_RUBRICS:
            rubric = DETAILED_RUBRICS[section_name]
            
            with st.expander(f"**{i}. {section_name}** (Max Score: 5)", expanded=(i == 1)):
                # Section definition
                st.markdown(
                    f"**Definition:** *{rubric['definition']}*",
                    unsafe_allow_html=False
                )
                
                st.markdown("")  # Spacing
                
                # Create a clean dataframe for the rubric table
                rubric_df = pd.DataFrame([
                    {"Score": score, "Criteria": rubric['criteria'][score]} 
                    for score in [5, 4, 3, 2, 1]
                ])
                
                # Style the dataframe
                st.dataframe(
                    rubric_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Score": st.column_config.NumberColumn(
                            "Score",
                            width="small",
                            help="Performance level"
                        ),
                        "Criteria": st.column_config.TextColumn(
                            "Criteria",
                            width="large",
                            help="Detailed evaluation criteria"
                        )
                    }
                )
    
    st.markdown("<div style='margin: 64px 0;'></div>", unsafe_allow_html=True)

