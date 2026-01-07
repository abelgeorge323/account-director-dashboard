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


def render_rankings_table(df):
    """Render executive-focused rankings with clean, scannable cards."""
    st.markdown("### 🏆 Account Director Rankings")
    st.markdown("<p style='color: #64748b; font-size: 1.05em; margin-bottom: 1.5rem;'>Click any Account Director to view detailed performance reviews</p>", unsafe_allow_html=True)
    
    # Sorting controls
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        sort_columns = ["Total Score"] + [f"{section}_Score" for section in SCORING_SECTIONS]
        sort_labels = ["Total Score"] + SECTION_SHORT_NAMES
        sort_column_map = dict(zip(sort_labels, sort_columns))
        
        sort_by = st.selectbox(
            "Sort by",
            options=sort_labels,
            index=0
        )
        sort_column = sort_column_map[sort_by]
    
    with col2:
        sort_order = st.selectbox(
            "Order",
            options=["Highest First", "Lowest First"],
            index=0
        )
        ascending = sort_order == "Lowest First"
    
    # Calculate ranks based on current sort
    ranked_df = calculate_ranks(df, sort_column, ascending)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Account Directors", len(ranked_df))
    with col2:
        avg_score = ranked_df['Total Score'].mean()
        st.metric("Average Total Score", f"{avg_score:.2f}", delta=f"{(avg_score/TOTAL_MAX_SCORE)*100:.0f}%")
    with col3:
        st.metric("Highest Score", f"{ranked_df['Total Score'].max():.2f}")
    with col4:
        st.metric("Lowest Score", f"{ranked_df['Total Score'].min():.2f}")
    
    st.markdown("---")
    
    # Render compact, scannable ranking cards with all 8 sections
    for idx, row in ranked_df.iterrows():
        rank = row['Rank']
        ad_name = row['Account Director']
        account = row['Account']
        total_score = row['Total Score']
        
        # Get all section scores
        all_sections = []
        for i, section in enumerate(SCORING_SECTIONS):
            score_col = f"{section}_Score"
            if score_col in row.index:
                all_sections.append((SECTION_SHORT_NAMES[i], row[score_col]))
        
        # Rank badge styling
        if rank == 1:
            rank_bg = "linear-gradient(135deg, #f59e0b 0%, #f97316 100%)"
            rank_shadow = "0 3px 8px rgba(245, 158, 11, 0.4)"
        elif rank == 2:
            rank_bg = "linear-gradient(135deg, #94a3b8 0%, #64748b 100%)"
            rank_shadow = "0 3px 8px rgba(148, 163, 184, 0.4)"
        elif rank == 3:
            rank_bg = "linear-gradient(135deg, #cd7f32 0%, #b87333 100%)"
            rank_shadow = "0 3px 8px rgba(205, 127, 50, 0.4)"
        else:
            rank_bg = "#e2e8f0"
            rank_shadow = "none"
        
        # Score color for border
        border_color = get_score_color(total_score, TOTAL_MAX_SCORE)
        
        # Create collapsible card using expander
        with st.container():
            # Card header (always visible)
            col1, col2, col3 = st.columns([1, 6, 2])
            
            with col1:
                st.markdown(
                    f"<div style='width: 40px; height: 40px; border-radius: 50%; background: {rank_bg}; color: white; display: flex; align-items: center; justify-content: center; font-size: 1.3em; font-weight: 700; box-shadow: {rank_shadow};'>{rank}</div>",
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(f"**<span style='font-size: 1.3em; color: #1e3a8a;'>{ad_name}</span>**", unsafe_allow_html=True)
                st.markdown(f"<span style='color: #64748b; font-size: 0.9em;'>{account}</span>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(
                    f"<div style='text-align: right;'><div style='font-size: 2.2em; font-weight: 700; color: #1e3a8a; line-height: 1;'>{total_score:.2f}</div><div style='color: #64748b; font-size: 0.8em;'>out of {TOTAL_MAX_SCORE}</div></div>",
                    unsafe_allow_html=True
                )
            
            # Expandable section bars
            with st.expander("📊 Show Section Scores", expanded=False):
                # Create 2-column layout for sections
                col_left, col_right = st.columns(2)
                
                # Split sections into two columns
                mid_point = len(all_sections) // 2
                left_sections = all_sections[:mid_point]
                right_sections = all_sections[mid_point:]
                
                with col_left:
                    for name, score in left_sections:
                        bar_color = get_score_color(score, 5)
                        percentage = (score / 5) * 100
                        st.markdown(
                            f"<div style='margin-bottom: 12px;'><div style='display: flex; justify-content: space-between; margin-bottom: 4px;'><span style='color: #475569; font-weight: 500; font-size: 0.9em;'>{name}</span><span style='color: #1e3a8a; font-weight: 600; font-size: 0.9em;'>{score:.1f}</span></div><div style='background: #e2e8f0; border-radius: 10px; height: 8px; overflow: hidden;'><div style='background: {bar_color}; height: 100%; width: {percentage}%; border-radius: 10px;'></div></div></div>",
                            unsafe_allow_html=True
                        )
                
                with col_right:
                    for name, score in right_sections:
                        bar_color = get_score_color(score, 5)
                        percentage = (score / 5) * 100
                        st.markdown(
                            f"<div style='margin-bottom: 12px;'><div style='display: flex; justify-content: space-between; margin-bottom: 4px;'><span style='color: #475569; font-weight: 500; font-size: 0.9em;'>{name}</span><span style='color: #1e3a8a; font-weight: 600; font-size: 0.9em;'>{score:.1f}</span></div><div style='background: #e2e8f0; border-radius: 10px; height: 8px; overflow: hidden;'><div style='background: {bar_color}; height: 100%; width: {percentage}%; border-radius: 10px;'></div></div></div>",
                            unsafe_allow_html=True
                        )
            
            # Add click button
            card_key = f"ad_card_{ad_name.replace(' ', '_')}"
            if st.button(
                "📋 View Detailed Reviews",
                key=card_key,
                use_container_width=True,
                type="primary"
            ):
                st.session_state.selected_ad_for_detail = ad_name
                st.session_state.navigate_to_reviews = True
                st.rerun()
            
            st.markdown("---")
    
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

