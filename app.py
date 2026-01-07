"""
Executive Performance Dashboard for Account Directors
A modern, executive-facing dashboard for year-end performance reviews.
"""

import streamlit as st
import pandas as pd
from data_processor import (
    prepare_dashboard_data,
    get_filter_options,
    get_individual_reviews,
    SCORING_SECTIONS,
    SECTION_SHORT_NAMES,
    TOTAL_MAX_SCORE
)

# Page configuration
st.set_page_config(
    page_title="Account Director Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive styling
def load_custom_css():
    st.markdown("""
        <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main app background */
        .main {
            background-color: #f8fafc;
        }
        
        /* Header styling */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            color: #1e40af;
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        
        h3 {
            color: #475569;
            font-weight: 600;
        }
        
        /* Sidebar styling */
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: #ffffff;
            box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
        }
        
        /* Score badge styling */
        .score-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            font-weight: 600;
            font-size: 1.1em;
            box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
        }
        
        .score-badge-large {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 12px;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            font-weight: 700;
            font-size: 1.8em;
            box-shadow: 0 4px 8px rgba(30, 58, 138, 0.3);
            margin: 8px 0;
        }
        
        .score-badge-small {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
            color: white;
            font-weight: 500;
            font-size: 0.9em;
        }
        
        /* Table styling */
        .dataframe {
            border: none !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .dataframe thead tr th {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
            color: white !important;
            font-weight: 600;
            padding: 12px 16px;
            border: none !important;
        }
        
        .dataframe tbody tr td {
            padding: 12px 16px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .dataframe tbody tr:hover {
            background-color: #f1f5f9;
            cursor: pointer;
        }
        
        /* Card styling */
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            margin-bottom: 16px;
        }
        
        .card-header {
            color: #1e3a8a;
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        /* Section score display */
        .section-score {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 4px solid #3b82f6;
        }
        
        .section-name {
            font-weight: 500;
            color: #334155;
        }
        
        .section-score-value {
            font-weight: 600;
            color: #1e3a8a;
            font-size: 1.1em;
        }
        
        /* Feedback box */
        .feedback-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-top: 8px;
            color: #475569;
            line-height: 1.6;
        }
        
        /* Filter section */
        .filter-title {
            color: #1e3a8a;
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 8px;
        }
        
        /* Metric styling */
        [data-testid="stMetric"] {
            background: white;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        [data-testid="stMetricValue"] {
            color: #1e3a8a;
            font-weight: 700;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 24px;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 0 4px 8px rgba(30, 58, 138, 0.3);
            transform: translateY(-1px);
        }
        
        /* Tab styling (Radio buttons styled as colored boxes) */
        .stRadio > div {
            background-color: transparent;
            padding: 0;
            margin-bottom: 24px;
        }
        
        .stRadio > div[role="radiogroup"] {
            display: flex;
            gap: 12px;
            flex-direction: row;
        }
        
        .stRadio > div[role="radiogroup"] > label {
            background-color: white;
            border-radius: 8px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 1.05em;
            color: #64748b;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            flex: 1;
            text-align: center;
        }
        
        .stRadio > div[role="radiogroup"] > label:hover {
            background-color: #f8fafc;
            border-color: #cbd5e1;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
        }
        
        .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none;
        }
        
        /* Selected tab */
        .stRadio > div[role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            border-color: #1e3a8a;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
            transform: translateY(-2px);
        }
        
        /* Rank badge */
        .rank-badge {
            display: inline-block;
            width: 36px;
            height: 36px;
            line-height: 36px;
            text-align: center;
            border-radius: 50%;
            background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
            color: white;
            font-weight: 700;
            box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
        }
        
        /* Drawer styling */
        .drawer {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        </style>
    """, unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if 'selected_ad' not in st.session_state:
        st.session_state.selected_ad = None
    if 'show_drawer' not in st.session_state:
        st.session_state.show_drawer = False
    if 'filtered_accounts' not in st.session_state:
        st.session_state.filtered_accounts = []
    if 'filtered_verticals' not in st.session_state:
        st.session_state.filtered_verticals = []
    if 'selected_ad_for_detail' not in st.session_state:
        st.session_state.selected_ad_for_detail = None
    if 'navigate_to_reviews' not in st.session_state:
        st.session_state.navigate_to_reviews = False
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0


# Load data with caching
@st.cache_data
def load_data():
    return prepare_dashboard_data()


def main():
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Load data
    aggregated_df, structured_df, rubric_data = load_data()
    filter_options = get_filter_options(aggregated_df)
    
    # App header
    st.markdown("<h1>📊 Account Director Performance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.1em; margin-bottom: 2rem;'>Year-End Executive Review • 2025 Performance Evaluation</p>", unsafe_allow_html=True)
    
    # Check if we need to navigate to reviews tab
    if st.session_state.get('navigate_to_reviews', False):
        st.session_state.active_tab = 1  # Switch to Individual Reviews tab
        st.session_state.navigate_to_reviews = False
    
    # Create tabs for different views
    tab_names = ["Rankings & Performance", "Individual Reviews", "Scoring Rubric"]
    
    # Manual tab selection with session state
    selected_tab = st.radio(
        "Navigation",
        options=tab_names,
        index=st.session_state.active_tab,
        horizontal=True,
        label_visibility="collapsed",
        key="tab_selector"
    )
    
    # Update active tab in session state
    st.session_state.active_tab = tab_names.index(selected_tab)
    
    st.markdown("---")
    
    # Render the selected tab
    if selected_tab == "Rankings & Performance":
        # Import and render rankings view
        from components.rankings_table import render_rankings_view
        render_rankings_view(aggregated_df, structured_df, filter_options)
    
    elif selected_tab == "Individual Reviews":
        # Import and render individual reviews page
        from components.individual_reviews import render_individual_reviews_page
        
        # Pass the pre-selected AD if coming from rankings
        preselected_ad = st.session_state.get('selected_ad_for_detail', None)
        render_individual_reviews_page(aggregated_df, structured_df, preselected_ad)
        
        # Clear the pre-selection after rendering
        if preselected_ad:
            st.session_state.selected_ad_for_detail = None
    
    elif selected_tab == "Scoring Rubric":
        # Import and render rubric view
        from components.rubric_page import render_rubric_page
        render_rubric_page(rubric_data)


if __name__ == "__main__":
    main()

