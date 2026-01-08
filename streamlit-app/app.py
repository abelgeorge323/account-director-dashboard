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
        /* Import font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global spacing reduction */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .main {
            background-color: #f8fafc;
        }
        
        /* Reduce default Streamlit padding */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Compact headers */
        h1 {
            color: #0f172a;
            font-weight: 700;
            font-size: 2em;
            margin-bottom: 0.3rem !important;
            line-height: 1.2;
        }
        
        h2 {
            color: #1e293b;
            font-weight: 600;
            font-size: 1.5em;
            margin-bottom: 0.5rem !important;
        }
        
        h3 {
            color: #334155;
            font-weight: 600;
            font-size: 1.2em;
            margin-bottom: 0.5rem !important;
        }
        
        /* Sidebar - clean and simple */
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: #ffffff;
            box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
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
        
        
        
        /* Compact filter title */
        .filter-title {
            color: #0f172a;
            font-weight: 700;
            font-size: 1em;
            margin-bottom: 8px;
        }
        
        /* Compact metrics */
        [data-testid="stMetric"] {
            background: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
        }
        
        [data-testid="stMetricValue"] {
            color: #0f172a;
            font-weight: 700;
            font-size: 1.5em !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #64748b;
            font-weight: 600;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Compact buttons */
        .stButton > button {
            background: #1e40af;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 0.9em;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #1e3a8a;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }
        
        /* Compact view selector */
        .stRadio > div {
            padding: 0;
        }
        
        .stRadio > div[role="radiogroup"] {
            gap: 6px;
        }
        
        .stRadio > div[role="radiogroup"] > label {
            background-color: #f8fafc;
            border-radius: 6px;
            padding: 10px 14px;
            font-weight: 500;
            font-size: 0.9em;
            color: #475569;
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease;
        }
        
        .stRadio > div[role="radiogroup"] > label:hover {
            background-color: #f1f5f9;
            border-color: #cbd5e1;
        }
        
        .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none;
        }
        
        /* Selected view - high contrast */
        .stRadio > div[role="radiogroup"] > label:has(input:checked) {
            background: #1e40af;
            color: white;
            border-color: #1e40af;
            font-weight: 600;
        }
        
        /* Performance badges - high contrast */
        .perf-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .perf-outstanding { 
            background: #10b981; 
            color: white;
        }
        .perf-strong { 
            background: #3b82f6; 
            color: white;
        }
        .perf-solid { 
            background: #f59e0b; 
            color: white;
        }
        .perf-developing { 
            background: #64748b; 
            color: white;
        }
        
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Reduce gap between elements */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Compact expander */
        .streamlit-expanderHeader {
            font-size: 0.9em !important;
            padding: 8px 12px !important;
        }
        
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
    
    # ===== SIDEBAR VIEW SELECTOR =====
    st.sidebar.markdown("### 📊 Dashboard Views")
    st.sidebar.markdown("---")
    
    view_options = [
        "🏆 Rankings & Performance",
        "📝 Individual Reviews",
        "📚 Scoring Rubric"
    ]
    
    # Check if we need to navigate to reviews
    if st.session_state.get('navigate_to_reviews', False):
        st.session_state.active_tab = 1
        st.session_state.navigate_to_reviews = False
    
    selected_view = st.sidebar.radio(
        "Select View",
        options=view_options,
        index=st.session_state.active_tab,
        label_visibility="collapsed",
        key="view_selector"
    )
    
    # Update active tab in session state
    st.session_state.active_tab = view_options.index(selected_view)
    
    st.sidebar.markdown("---")
    
    # ===== MAIN CONTENT AREA =====
    # Compact app header
    st.markdown("<h1>📊 Account Director Performance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.95em; margin-bottom: 1rem;'>Year-End Executive Review • 2025 Performance Evaluation</p>", unsafe_allow_html=True)
    st.markdown("<div style='height: 1px; background: #e2e8f0; margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    # Render the selected view
    if selected_view == "🏆 Rankings & Performance":
        from components.rankings_table import render_rankings_view
        render_rankings_view(aggregated_df, structured_df, filter_options)
    
    elif selected_view == "📝 Individual Reviews":
        from components.individual_reviews import render_individual_reviews_page
        preselected_ad = st.session_state.get('selected_ad_for_detail', None)
        render_individual_reviews_page(aggregated_df, structured_df, preselected_ad)
        if preselected_ad:
            st.session_state.selected_ad_for_detail = None
    
    elif selected_view == "📚 Scoring Rubric":
        from components.rubric_page import render_rubric_page
        render_rubric_page(rubric_data)


if __name__ == "__main__":
    main()

