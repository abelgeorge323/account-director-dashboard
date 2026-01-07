"""
Individual Reviews component - displays detailed reviews for each Account Director.
"""

import streamlit as st
from data_processor import get_individual_reviews, TOTAL_MAX_SCORE, SCORING_SECTIONS


def get_score_badge_color(score, max_score=5):
    """Return color for score badge based on performance level."""
    ratio = score / max_score
    if ratio >= 0.9:
        return "#10b981"  # Green
    elif ratio >= 0.8:
        return "#3b82f6"  # Blue
    elif ratio >= 0.6:
        return "#f59e0b"  # Orange
    else:
        return "#94a3b8"  # Gray


def render_score_bar(score, max_score=5):
    """Render a horizontal progress bar for a score."""
    percentage = (score / max_score) * 100
    color = get_score_badge_color(score, max_score)
    
    return f"""
        <div style='background: #e2e8f0; border-radius: 8px; height: 24px; position: relative; overflow: hidden;'>
            <div style='background: {color}; height: 100%; width: {percentage}%; 
                        border-radius: 8px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;'>
                <span style='color: white; font-weight: 600; font-size: 0.85em;'>{score:.1f} / {max_score}</span>
            </div>
        </div>
    """


def render_individual_reviews_page(aggregated_df, structured_df, preselected_ad=None):
    """Render the individual reviews page with all Account Directors."""
    
    st.markdown("### 📝 Individual Performance Reviews")
    st.markdown(
        """
        <p style='color: #64748b; font-size: 1.1em; margin-bottom: 2rem;'>
        Detailed section-by-section breakdown with reviewer feedback for each Account Director.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Get unique Account Directors
    ad_list = aggregated_df["Account Director"].tolist()
    
    if not ad_list:
        st.warning("No Account Directors found.")
        return
    
    # Determine default index
    default_index = 0
    if preselected_ad and preselected_ad in ad_list:
        default_index = ad_list.index(preselected_ad)
    
    # Account Director selector
    selected_ad = st.selectbox(
        "Select an Account Director to view their reviews",
        options=ad_list,
        index=default_index
    )
    
    if not selected_ad:
        st.info("Please select an Account Director to view their performance reviews.")
        return
    
    # Get reviews for selected AD
    reviews = get_individual_reviews(structured_df, selected_ad)
    
    if not reviews:
        st.warning(f"No reviews found for {selected_ad}")
        return
    
    # Get aggregated score for context
    ad_row = aggregated_df[aggregated_df["Account Director"] == selected_ad].iloc[0]
    avg_score = ad_row["Total Score"]
    account = ad_row["Account"]
    
    # Header with overall score
    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                    border-radius: 16px; padding: 32px; margin-bottom: 32px; 
                    box-shadow: 0 8px 16px rgba(30, 58, 138, 0.3); text-align: center;'>
            <div style='color: white; font-size: 2.5em; font-weight: 700; margin-bottom: 8px;'>
                {selected_ad}
            </div>
            <div style='color: rgba(255, 255, 255, 0.9); font-size: 1.2em; margin-bottom: 16px;'>
                {account}
            </div>
            <div style='display: flex; justify-content: center; gap: 40px; margin-top: 24px;'>
                <div>
                    <div style='color: rgba(255, 255, 255, 0.8); font-size: 0.9em;'>OVERALL SCORE</div>
                    <div style='color: white; font-size: 3em; font-weight: 700;'>{avg_score:.2f}</div>
                    <div style='color: rgba(255, 255, 255, 0.8); font-size: 1em;'>out of {TOTAL_MAX_SCORE}</div>
                </div>
                <div>
                    <div style='color: rgba(255, 255, 255, 0.8); font-size: 0.9em;'>TOTAL REVIEWS</div>
                    <div style='color: white; font-size: 3em; font-weight: 700;'>{len(reviews)}</div>
                    <div style='color: rgba(255, 255, 255, 0.8); font-size: 1em;'>evaluations</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display all reviews in vertical layout
    for i, review in enumerate(reviews, 1):
        with st.container():
            # Review header
            st.markdown(
                f"""
                <div style='background: white; border-radius: 12px; padding: 24px; 
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); margin-bottom: 24px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
                        <div>
                            <div style='font-size: 1.5em; font-weight: 600; color: #1e3a8a;'>
                                Review #{i}
                            </div>
                            <div style='color: #64748b; margin-top: 4px;'>
                                Reviewer: {review['reviewer_name']} ({review['reviewer_email']})
                            </div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='font-size: 2em; font-weight: 700; color: #1e3a8a;'>
                                {review['total_score']:.2f}
                            </div>
                            <div style='color: #64748b; font-size: 0.9em;'>
                                out of {TOTAL_MAX_SCORE}
                            </div>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True
            )
            
            # Section scores and feedback
            for section_data in review["sections"]:
                section_name = section_data["name"]
                score = section_data["score"]
                feedback = section_data["feedback"]
                
                # Section header with score bar
                st.markdown(
                    f"""
                    <div style='margin-bottom: 20px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <div style='font-weight: 600; color: #1e40af; font-size: 1.05em;'>
                                {section_name}
                            </div>
                        </div>
                        {render_score_bar(score, 5)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Feedback (collapsible)
                if feedback:
                    with st.expander("💬 View Feedback", expanded=False):
                        st.markdown(
                            f"""
                            <div style='color: #475569; line-height: 1.7; padding: 8px 0;'>
                                {feedback}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<p style='color: #94a3b8; font-style: italic; margin-left: 8px; font-size: 0.9em;'>No feedback provided for this section</p>",
                        unsafe_allow_html=True
                    )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

