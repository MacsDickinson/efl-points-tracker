import streamlit as st
import os
from utils.api import get_league_matches, get_available_leagues, get_available_seasons
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats
from db.database import init_db

# Initialize database with error handling
try:
    init_db()
except Exception as e:
    st.error(f"Failed to initialize database: {str(e)}")
    st.stop()

st.set_page_config(page_title="Football League Dashboard",
                   page_icon="⚽",
                   layout="wide",
                   initial_sidebar_state="collapsed")

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
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

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