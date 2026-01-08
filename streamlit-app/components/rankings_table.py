"""
Rankings table component with filtering and visual score cards.
"""

import streamlit as st
import pandas as pd
from data_processor import (
    SCORING_SECTIONS,
    SECTION_SHORT_NAMES,
    TOTAL_MAX_SCORE
)


def render_filters(filter_options):
    """Render the left sidebar filter panel."""
    st.sidebar.markdown("<div class='filter-title'>🔍 Filter Options</div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Vertical filter (comes first in hierarchy)
    st.sidebar.markdown("<p style='font-weight: 500; color: #475569; margin-bottom: 8px;'>Filter by Vertical</p>", unsafe_allow_html=True)
    
    if filter_options["verticals"]:
        selected_verticals = st.sidebar.multiselect(
            "Select verticals",
            options=filter_options["verticals"],
            default=st.session_state.get('filtered_verticals', []),
            key="vertical_filter",
            label_visibility="collapsed"
        )
    else:
        st.sidebar.info("Vertical data not yet configured")
        selected_verticals = []
    
    # Account filter
    st.sidebar.markdown("<p style='font-weight: 500; color: #475569; margin-top: 16px; margin-bottom: 8px;'>Filter by Account</p>", unsafe_allow_html=True)
    selected_accounts = st.sidebar.multiselect(
        "Select accounts",
        options=filter_options["accounts"],
        default=st.session_state.get('filtered_accounts', []),
        key="account_filter",
        label_visibility="collapsed"
    )
    
    # Clear filters button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Clear All Filters", use_container_width=True, key="clear_filters_btn"):
        # Clear session state
        st.session_state.filtered_accounts = []
        st.session_state.filtered_verticals = []
        # Force rerun to reset multiselects
        st.rerun()
    
    # Update session state
    st.session_state.filtered_accounts = selected_accounts
    st.session_state.filtered_verticals = selected_verticals
    
    return selected_accounts, selected_verticals


def apply_filters(df, selected_accounts, selected_verticals):
    """Apply filters to the dataframe."""
    filtered_df = df.copy()
    
    if selected_accounts:
        filtered_df = filtered_df[filtered_df["Account"].isin(selected_accounts)]
    
    # Vertical filtering
    if selected_verticals and "Vertical" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Vertical"].isin(selected_verticals)]
    
    return filtered_df


def calculate_ranks(df, sort_column, ascending):
    """Calculate dynamic ranks based on current sort."""
    sorted_df = df.sort_values(by=sort_column, ascending=ascending).reset_index(drop=True)
    sorted_df.insert(0, "Rank", range(1, len(sorted_df) + 1))
    return sorted_df


def get_score_color(score, max_score=5):
    """Return a color based on score (gradient from blue to gold)."""
    ratio = score / max_score
    if ratio >= 0.9:
        return "#10b981"  # Green for exceptional
    elif ratio >= 0.8:
        return "#3b82f6"  # Blue for strong
    elif ratio >= 0.6:
        return "#f59e0b"  # Orange for good
    else:
        return "#94a3b8"  # Gray for needs improvement


def get_top_sections(row, n=3):
    """Get the top N performing sections for an Account Director."""
    section_scores = []
    for i, section in enumerate(SCORING_SECTIONS):
        score_col = f"{section}_Score"
        if score_col in row.index:
            section_scores.append((SECTION_SHORT_NAMES[i], row[score_col]))
    
    # Sort by score descending and take top N
    section_scores.sort(key=lambda x: x[1], reverse=True)
    return section_scores[:n]


def get_performance_band(score, max_score):
    """Determine performance band based on score percentage."""
    ratio = score / max_score
    if ratio >= 0.9:
        return ("Outstanding", "perf-outstanding")
    elif ratio >= 0.8:
        return ("Strong", "perf-strong")
    elif ratio >= 0.6:
        return ("Solid", "perf-solid")
    else:
        return ("Developing", "perf-developing")


def render_leaderboard_row(row, rank, total_count, key_suffix=""):
    """Render a compact, high-contrast leaderboard row."""
    ad_name = row['Account Director']
    account = row['Account']
    total_score = row['Total Score']
    vertical = row.get('Vertical', 'N/A')
    
    # Performance band
    band_label, band_class = get_performance_band(total_score, TOTAL_MAX_SCORE)
    
    # Rank styling - solid colors for clarity
    if rank == 1:
        rank_bg = "#fbbf24"
        rank_color = "#78350f"
    elif rank == 2:
        rank_bg = "#94a3b8"
        rank_color = "white"
    elif rank == 3:
        rank_bg = "#d97706"
        rank_color = "white"
    else:
        rank_bg = "#e2e8f0"
        rank_color = "#475569"
    
    # Create unique key for this row
    row_key = f"row_{ad_name.replace(' ', '_')}_{key_suffix}"
    
    # Initialize expanded state for this row
    if row_key not in st.session_state:
        st.session_state[row_key] = False
    
    # Collapsed row (always visible)
    with st.container():
        # Compact row header
        col1, col2, col3, col4, col5 = st.columns([0.6, 3, 2, 1.5, 0.5])
        
        with col1:
            st.markdown(
                f"""<div style='
                    width: 36px; height: 36px; border-radius: 50%; 
                    background: {rank_bg}; color: {rank_color}; 
                    display: flex; align-items: center; justify-content: center; 
                    font-size: 1em; font-weight: 700;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
                '>{rank}</div>""",
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(f"<div style='font-size: 1em; font-weight: 600; color: #0f172a; margin-bottom: 2px;'>{ad_name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 0.8em; color: #64748b; font-weight: 500;'>{account}</div>", unsafe_allow_html=True)
        
        with col3:
            if vertical and vertical != 'N/A':
                st.markdown(f"<div style='font-size: 0.8em; color: #64748b; padding-top: 6px;'>📂 {vertical}</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown(
                f"""<div style='text-align: right; padding-top: 2px;'>
                    <div style='font-size: 1.8em; font-weight: 800; color: #0f172a; line-height: 1;'>{total_score:.1f}</div>
                    <div style='font-size: 0.7em; color: #94a3b8; font-weight: 500; margin-top: 2px;'>of {TOTAL_MAX_SCORE}</div>
                    <div style='margin-top: 6px;'><span class='perf-badge {band_class}'>{band_label}</span></div>
                </div>""",
                unsafe_allow_html=True
            )
        
        with col5:
            # Compact toggle
            icon = "▼" if st.session_state[row_key] else "▶"
            if st.button(icon, key=f"toggle_{row_key}", help="Show/hide sections"):
                st.session_state[row_key] = not st.session_state[row_key]
                st.rerun()
        
        # Expanded section (conditionally rendered)
        if st.session_state[row_key]:
            st.markdown("""<div style='margin-top: 12px; padding: 16px; 
                background: #f8fafc; 
                border-radius: 8px;
                border: 1px solid #e2e8f0;'>""", unsafe_allow_html=True)
            
            # Get all section scores
            col_left, col_right = st.columns(2)
            
            sections_left = SCORING_SECTIONS[:4]
            sections_right = SCORING_SECTIONS[4:]
            
            with col_left:
                for i, section in enumerate(sections_left):
                    score_col = f"{section}_Score"
                    if score_col in row.index:
                        score = row[score_col]
                        short_name = SECTION_SHORT_NAMES[i]
                        bar_color = get_score_color(score, 5)
                        percentage = (score / 5) * 100
                        
                        st.markdown(
                            f"""<div style='margin-bottom: 10px;'>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                                    <span style='color: #334155; font-weight: 600; font-size: 0.85em;'>{short_name}</span>
                                    <span style='color: #0f172a; font-weight: 700; font-size: 0.85em;'>{score:.1f}/5</span>
                                </div>
                                <div style='background: #e2e8f0; border-radius: 8px; height: 6px; overflow: hidden;'>
                                    <div style='background: {bar_color}; height: 100%; width: {percentage}%;'></div>
                                </div>
                            </div>""",
                            unsafe_allow_html=True
                        )
            
            with col_right:
                for i, section in enumerate(sections_right, start=4):
                    score_col = f"{section}_Score"
                    if score_col in row.index:
                        score = row[score_col]
                        short_name = SECTION_SHORT_NAMES[i]
                        bar_color = get_score_color(score, 5)
                        percentage = (score / 5) * 100
                        
                        st.markdown(
                            f"""<div style='margin-bottom: 10px;'>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                                    <span style='color: #334155; font-weight: 600; font-size: 0.85em;'>{short_name}</span>
                                    <span style='color: #0f172a; font-weight: 700; font-size: 0.85em;'>{score:.1f}/5</span>
                                </div>
                                <div style='background: #e2e8f0; border-radius: 8px; height: 6px; overflow: hidden;'>
                                    <div style='background: {bar_color}; height: 100%; width: {percentage}%;'></div>
                                </div>
                            </div>""",
                            unsafe_allow_html=True
                        )
            
            # Compact detail button
            if st.button("View Full Reviews", key=f"detail_{row_key}", use_container_width=True):
                st.session_state.selected_ad_for_detail = ad_name
                st.session_state.navigate_to_reviews = True
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Compact divider
        st.markdown("<div style='border-bottom: 1px solid #e2e8f0; margin: 8px 0;'></div>", unsafe_allow_html=True)


def render_rankings_table(df):
    """Render compact, executive leaderboard."""
    st.markdown("### 🏆 Account Director Leaderboard")
    st.markdown("<p style='color: #64748b; font-size: 0.9em; margin-bottom: 1rem;'>Click ▶ to expand • Sorted by total score</p>", unsafe_allow_html=True)
    
    # Compact sorting controls
    col1, col2, spacer = st.columns([2, 2, 6])
    
    with col1:
        sort_columns = ["Total Score"] + [f"{section}_Score" for section in SCORING_SECTIONS]
        sort_labels = ["Total Score"] + SECTION_SHORT_NAMES
        sort_column_map = dict(zip(sort_labels, sort_columns))
        
        sort_by = st.selectbox(
            "Sort by",
            options=sort_labels,
            index=0,
            key="leaderboard_sort",
            label_visibility="visible"
        )
        sort_column = sort_column_map[sort_by]
    
    with col2:
        sort_order = st.selectbox(
            "Order",
            options=["Highest First", "Lowest First"],
            index=0,
            key="leaderboard_order",
            label_visibility="visible"
        )
        ascending = sort_order == "Lowest First"
    
    # Calculate ranks
    ranked_df = calculate_ranks(df, sort_column, ascending)
    total_count = len(ranked_df)
    
    # Compact summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", total_count)
    with col2:
        avg_score = ranked_df['Total Score'].mean()
        st.metric("Avg", f"{avg_score:.1f}")
    with col3:
        st.metric("Top", f"{ranked_df['Total Score'].max():.1f}")
    with col4:
        st.metric("Low", f"{ranked_df['Total Score'].min():.1f}")
    
    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Render leaderboard rows
    for idx, row in ranked_df.iterrows():
        rank = row['Rank']
        render_leaderboard_row(row, rank, total_count, key_suffix=f"{idx}")
    
    return None




def render_rankings_view(aggregated_df, structured_df, filter_options):
    """Main function to render the complete rankings view."""
    
    # Render filters in sidebar
    selected_accounts, selected_verticals = render_filters(filter_options)
    
    # Apply filters
    filtered_df = apply_filters(aggregated_df, selected_accounts, selected_verticals)
    
    # Show filter status
    if selected_accounts or selected_verticals:
        filter_tags = []
        if selected_verticals:
            filter_tags.append(f"Verticals: {', '.join(selected_verticals)}")
        if selected_accounts:
            filter_tags.append(f"Accounts: {', '.join(selected_accounts)}")
        
        st.info(f"🔍 Active Filters: {' | '.join(filter_tags)}")
    
    if filtered_df.empty:
        st.warning("No Account Directors match the selected filters.")
        return
    
    # Render rankings table with visual cards
    render_rankings_table(filtered_df)
    
    # Add helpful tip
    st.markdown("---")
    st.info("💡 **Tip:** Visit the 'Individual Reviews' tab to see detailed feedback for each Account Director.")

