import streamlit as st
import pandas as pd
import os
from utils.api import get_league_matches, get_available_leagues, get_available_seasons, get_team_data_with_matches
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats
from db.database import init_db
from utils.dev_mode import log_error
from components.league_table import display_league_table

# Custom CSS for modern design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        color-scheme: light dark;
    }

    /* Light mode colors */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: rgb(255, 255, 255);
            --text-color: rgb(20, 20, 20);
            --secondary-bg: rgb(247, 248, 249);
            --border-color: rgba(20, 20, 20, 0.1);
            --hover-bg: rgba(20, 20, 20, 0.05);
            --gradient-start: rgba(108, 99, 255, 0.1);
            --gradient-end: rgba(255, 99, 195, 0.1);
            --accent-color: rgb(108, 99, 255);
        }
    }

    /* Dark mode colors */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: rgb(10, 10, 15);
            --text-color: rgba(255, 255, 255, 0.95);
            --secondary-bg: rgba(20, 20, 30, 0.95);
            --border-color: rgba(255, 255, 255, 0.1);
            --hover-bg: rgba(255, 255, 255, 0.05);
            --gradient-start: rgba(108, 99, 255, 0.2);
            --gradient-end: rgba(255, 99, 195, 0.2);
            --accent-color: rgb(138, 129, 255);
        }
    }

    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, 
            var(--gradient-start) 0%, 
            var(--bg-color) 25%, 
            var(--bg-color) 75%, 
            var(--gradient-end) 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Container styles */
    .block-container {
        max-width: 95rem !important;
        padding: 3rem 2rem !important;
        background: var(--bg-color);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
    }

    /* Select box styles */
    .stSelectbox label {
        color: var(--text-color) !important;
        font-weight: 500;
        letter-spacing: -0.02em;
    }

    .stSelectbox div[role="button"] {
        background-color: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }

    .stSelectbox div[role="button"]:hover {
        border-color: var(--accent-color);
    }

    /* Tab styles */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-bg);
        padding: 1rem 1rem 0 1rem;
        border-radius: 16px 16px 0 0;
        gap: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-color);
        font-weight: 500;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--accent-color);
        opacity: 0.1;
    }

    /* Hide unnecessary elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}

    /* Expander styles */
    .streamlit-expanderHeader {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-color);
    }

    /* Header container */
    .header-container {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, 
            var(--gradient-start), 
            var(--gradient-end));
        border-radius: 24px;
        backdrop-filter: blur(12px);
    }

    </style>
    """, unsafe_allow_html=True)

def main():
    # Create modern header with SVG
    st.markdown("""
    <div class="header-container">
        <svg width="700" height="120" viewBox="0 0 700 120">
            <defs>
                <linearGradient id="headerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:var(--accent-color);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--text-color);stop-opacity:0.8" />
                </linearGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <g>
                <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
                    fill="url(#headerGradient)" filter="url(#glow)"
                    style="font-size: 48px; font-weight: bold; font-family: 'Inter', system-ui;">
                    Football League Points
                </text>
                <text x="50%" y="80%" dominant-baseline="middle" text-anchor="middle" 
                    fill="var(--text-color)" style="font-size: 24px; font-weight: 500; font-family: 'Inter', system-ui; opacity: 0.8">
                    Real-time Performance Tracking
                </text>
            </g>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # Create top navigation using columns with modern styling
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
            Track football teams' performance through an 
            interactive visualization of points progression 
            throughout the season.
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