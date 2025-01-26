import streamlit as st
import pandas as pd
import os
from utils.api import get_league_matches, get_available_leagues, get_available_seasons, get_team_data_with_matches
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats
from db.database import init_db
from utils.dev_mode import log_error
from components.league_table import display_league_table

# Custom CSS for modern design with vibrant gradients
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
            --gradient-1: rgba(255, 102, 196, 0.15);
            --gradient-2: rgba(108, 99, 255, 0.15);
            --gradient-3: rgba(51, 221, 255, 0.15);
            --accent-1: rgb(255, 102, 196);
            --accent-2: rgb(108, 99, 255);
            --accent-3: rgb(51, 221, 255);
        }
    }

    /* Dark mode colors */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: rgb(8, 8, 12);
            --text-color: rgba(255, 255, 255, 0.95);
            --secondary-bg: rgba(20, 20, 30, 0.95);
            --border-color: rgba(255, 255, 255, 0.1);
            --hover-bg: rgba(255, 255, 255, 0.05);
            --gradient-1: rgba(255, 102, 196, 0.2);
            --gradient-2: rgba(108, 99, 255, 0.2);
            --gradient-3: rgba(51, 221, 255, 0.2);
            --accent-1: rgb(255, 122, 216);
            --accent-2: rgb(128, 119, 255);
            --accent-3: rgb(71, 241, 255);
        }
    }

    /* Global styles with enhanced gradients */
    .stApp {
        background: 
            radial-gradient(circle at 10% 90%, var(--gradient-1) 0%, transparent 40%),
            radial-gradient(circle at 90% 10%, var(--gradient-2) 0%, transparent 40%),
            linear-gradient(135deg, var(--gradient-3) 0%, var(--bg-color) 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Container styles with glassmorphism */
    .block-container {
        max-width: 95rem !important;
        padding: 3rem 2rem !important;
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05),
            rgba(255, 255, 255, 0.01));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(12px);
    }

    /* Select box styles */
    .stSelectbox label {
        color: var(--text-color) !important;
        font-weight: 500;
        letter-spacing: -0.02em;
    }

    .stSelectbox div[role="button"] {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05),
            rgba(255, 255, 255, 0.01));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(12px);
    }

    .stSelectbox div[role="button"]:hover {
        border-color: var(--accent-2);
        box-shadow: 0 0 20px rgba(108, 99, 255, 0.2);
    }

    /* Tab styles */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05),
            rgba(255, 255, 255, 0.01));
        backdrop-filter: blur(12px);
        padding: 1rem 1rem 0 1rem;
        border-radius: 16px 16px 0 0;
        gap: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-color);
        font-weight: 500;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2));
        opacity: 0.8;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
        opacity: 0.2;
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
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05),
            rgba(255, 255, 255, 0.01));
        border-radius: 12px;
        backdrop-filter: blur(12px);
    }

    /* Header container */
    .header-container {
        text-align: center;
        margin-bottom: 3rem;
        padding: 3rem;
        background: linear-gradient(135deg, 
            var(--gradient-1),
            var(--gradient-2),
            var(--gradient-3));
        border-radius: 24px;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
                    <stop offset="0%" style="stop-color:var(--accent-1);stop-opacity:1" />
                    <stop offset="50%" style="stop-color:var(--accent-2);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:var(--accent-3);stop-opacity:1" />
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