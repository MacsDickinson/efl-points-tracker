import streamlit as st
from utils.api import get_league_matches, get_available_leagues, get_available_seasons
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats

st.set_page_config(page_title="Football League Dashboard",
                   page_icon="⚽",
                   layout="wide",
                   initial_sidebar_state="collapsed")

# Custom CSS to hide the default menu button and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}
    .main > div {padding-top: 2rem;}
    </style>
    """,
            unsafe_allow_html=True)


def main():
    st.title("⚽ Football League Points Progression")

    # Create top navigation using columns
    col1, col2, spacer, info = st.columns([2, 2, 4, 2])

    leagues = get_available_leagues()
    with col1:
        selected_league = st.selectbox("Select League",
                                       options=list(leagues.keys()),
                                       format_func=lambda x: leagues[x],
                                       key="league_selector")

    seasons = get_available_seasons()
    with col2:
        selected_season = st.selectbox("Select Season",
                                       options=list(seasons.keys()),
                                       format_func=lambda x: seasons[x],
                                       key="season_selector")

    with info:
        with st.expander("ℹ️ About"):
            st.markdown("""
            This dashboard visualizes the cumulative points 
            progression for football teams throughout 
            the season.
            """)

    # Main content
    with st.spinner("Loading match data..."):
        matches_df = get_league_matches(selected_league, selected_season)
        points_df = calculate_cumulative_points(matches_df)

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📈 Points Progression", "📊 Team Statistics"])

    with tab1:
        # Plot cumulative points
        fig = plot_cumulative_points(points_df)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("🎮 How to use this graph"):
            st.markdown("""
            - **Hover** over lines to see exact points
            - **Click** team names in legend to show/hide
            - **Double click** team names to isolate
            - **Drag** to zoom, double click to reset
            """)

    with tab2:
        # Display team statistics
        display_team_stats(points_df)


if __name__ == "__main__":
    main()
