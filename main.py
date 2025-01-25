import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(page_title="Football League Dashboard",
                   page_icon="⚽",
                   layout="wide",
                   initial_sidebar_state="collapsed")

import os
from utils.api import get_league_matches, get_available_leagues, get_available_seasons
from utils.data_processor import calculate_cumulative_points, calculate_league_positions
from components.graph import plot_cumulative_points, plot_league_positions, display_team_stats
from db.database import init_db
from utils.dev_mode import log_error

# Custom CSS for dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: rgb(17, 17, 17);
        color: rgba(255, 255, 255, 0.9);
    }
    .stSelectbox label, .stSelectbox div[role="button"] {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    .stSelectbox div[role="button"] {
        background-color: rgba(17, 17, 17, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}
    .main > div {padding-top: 2rem;}
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(17, 17, 17, 0.9);
        padding: 1rem 1rem 0 1rem;
        border-radius: 1rem 1rem 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.7);
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .stMarkdown div {
        color: rgba(255, 255, 255, 0.9);
    }
    </style>
    """,
        unsafe_allow_html=True)

# Initialize database with error handling
try:
    if not init_db():
        error_msg = log_error("Database initialization failed")
        st.error(error_msg)
        st.stop()
except Exception as e:
    error_msg = log_error("Failed to initialize database", e)
    st.error(error_msg)
    st.stop()

def main():
    st.title("⚽ Football League Points Progression")

    # Create top navigation using columns
    col1, col2, spacer, col3, info = st.columns([2, 2, 2, 2, 2])

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

    with col3:
        view_mode = st.selectbox(
            "Select View",
            options=["Points Progression", "League Position"],
            key="view_selector"
        )

    with info:
        with st.expander("ℹ️ About"):
            st.markdown("""
            This dashboard visualizes team performance throughout 
            the season, showing either points progression or 
            league position over time.
            """)

    # Main content
    with st.spinner("Loading match data..."):
        matches_df = get_league_matches(selected_league, selected_season)

        if view_mode == "Points Progression":
            points_df = calculate_cumulative_points(matches_df)
            tab1, tab2 = st.tabs(["📈 Points Progression", "📊 Team Statistics"])

            with tab1:
                fig = plot_cumulative_points(points_df)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

                with st.expander("🎮 How to use this graph"):
                    st.markdown("""
                    - **Hover** over lines to see exact points
                    - **Click** team names in legend to show/hide
                    - **Double click** team names to isolate
                    - **Drag** to zoom, double click to reset
                    """)
        else:
            positions_df = calculate_league_positions(matches_df)
            tab1, tab2 = st.tabs(["📈 League Positions", "📊 Team Statistics"])

            with tab1:
                fig = plot_league_positions(positions_df)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

                with st.expander("🎮 How to use this graph"):
                    st.markdown("""
                    - **Hover** over lines to see exact positions
                    - **Click** team names in legend to show/hide
                    - **Double click** team names to isolate
                    - **Drag** to zoom, double click to reset
                    - Note: Position 1 is top of the league
                    """)

        with tab2:
            # Display team statistics
            display_team_stats(points_df if view_mode == "Points Progression" else positions_df)

if __name__ == "__main__":
    main()