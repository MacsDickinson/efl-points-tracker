import streamlit as st
import pandas as pd
import os
from utils.api import get_league_matches, get_available_leagues, get_available_seasons, get_team_data_with_matches
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats
from db.database import init_db
from utils.dev_mode import log_error
from components.league_table import display_league_table

# Custom CSS for system theme support
st.markdown("""
    <style>
    :root {
        color-scheme: light dark;
    }

    /* Light mode colors */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: rgb(255, 255, 255);
            --text-color: rgb(49, 51, 63);
            --secondary-bg: rgb(247, 248, 249);
            --border-color: rgba(49, 51, 63, 0.1);
            --hover-bg: rgba(49, 51, 63, 0.05);
        }
    }

    /* Dark mode colors */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: rgb(17, 17, 17);
            --text-color: rgba(255, 255, 255, 0.9);
            --secondary-bg: rgba(17, 17, 17, 0.9);
            --border-color: rgba(255, 255, 255, 0.1);
            --hover-bg: rgba(255, 255, 255, 0.05);
        }
    }

    /* Rest of the styles */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    .block-container {
        max-width: 95rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .stSelectbox label, .stSelectbox div[role="button"] {
        color: var(--text-color) !important;
    }
    .stSelectbox div[role="button"] {
        background-color: var(--secondary-bg);
        border: 1px solid var(--border-color);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}
    .main > div {padding-top: 2rem;}
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-bg);
        padding: 1rem 1rem 0 1rem;
        border-radius: 1rem 1rem 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-color);
        opacity: 0.7;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--hover-bg);
    }
    .stMarkdown div {
        color: var(--text-color);
    }
    </style>
    """, unsafe_allow_html=True)

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
    # Create and embed the header image
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <svg width="600" height="100" viewBox="0 0 600 100">
            <defs>
                <linearGradient id="headerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:var(--text-color);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--text-color);stop-opacity:0.7" />
                </linearGradient>
            </defs>
            <g>
                <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
                    fill="url(#headerGradient)" 
                    style="font-size: 36px; font-weight: bold; font-family: system-ui;">
                    ⚽ Football League Points Progression
                </text>
                <path d="M50,80 L550,80" stroke="var(--text-color)" stroke-width="2" stroke-opacity="0.3"/>
            </g>
        </svg>
    </div>
    """, unsafe_allow_html=True)

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
        team_data = get_team_data_with_matches(int(selected_league), int(selected_season))

        points_data = []
        for team in team_data:
            points_data.append({
                'team': team['name'],
                'date': team['matches'][0]['date'] if team['matches'] else None,
                'points': -team['points_deduction'],
                'matches_played': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0
            })

            for match in team['matches']:
                points_data.append({
                    'team': team['name'],
                    'date': match['date'],
                    'points': match['cumulative_total'],
                    'matches_played': match['gameweek'],
                    'goals_for': team['goals_for'],
                    'goals_against': team['goals_against'],
                    'goal_difference': team['goal_difference']
                })

        points_df = pd.DataFrame(points_data)

        tab1, tab2 = st.tabs(["📈 Points Progression", "📊 League Table"])

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

        with tab2:
            display_league_table(team_data)

if __name__ == "__main__":
    main()