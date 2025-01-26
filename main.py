import streamlit as st
import pandas as pd
import os
from utils.api import get_league_matches, get_available_leagues, get_available_seasons, get_team_data_with_matches
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats
from db.database import init_db
from utils.dev_mode import log_error
from components.league_table import display_league_table

# Custom CSS for theme support
st.markdown("""
    <style>
    /* Theme variables */
    :root {
        color-scheme: light dark;
    }

    /* Light mode colors */
    :root[data-theme="light"] {
        --bg-color: rgb(255, 255, 255);
        --text-color: rgb(49, 51, 63);
        --secondary-bg: rgb(247, 248, 249);
        --border-color: rgba(49, 51, 63, 0.1);
        --hover-bg: rgba(49, 51, 63, 0.05);
    }

    /* Dark mode colors */
    :root[data-theme="dark"] {
        --bg-color: rgb(17, 17, 17);
        --text-color: rgba(255, 255, 255, 0.9);
        --secondary-bg: rgba(17, 17, 17, 0.9);
        --border-color: rgba(255, 255, 255, 0.1);
        --hover-bg: rgba(255, 255, 255, 0.05);
    }

    /* Default to system preference */
    @media (prefers-color-scheme: dark) {
        :root:not([data-theme]) {
            --bg-color: rgb(17, 17, 17);
            --text-color: rgba(255, 255, 255, 0.9);
            --secondary-bg: rgba(17, 17, 17, 0.9);
            --border-color: rgba(255, 255, 255, 0.1);
            --hover-bg: rgba(255, 255, 255, 0.05);
        }
    }

    /* Theme toggle button */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        padding: 0.5rem;
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        color: var(--text-color);
        cursor: pointer;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
    }

    .theme-toggle:hover {
        background: var(--hover-bg);
    }

    .theme-toggle svg {
        width: 1.25rem;
        height: 1.25rem;
        fill: currentColor;
    }

    /* Show/hide icons based on theme */
    :root[data-theme="dark"] .sun-icon,
    :root:not([data-theme="light"]) .sun-icon {
        display: none;
    }

    :root[data-theme="light"] .moon-icon,
    :root:not([data-theme="dark"]) .moon-icon {
        display: none;
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

    <!-- Theme toggle button -->
    <div class="theme-toggle" data-theme-toggle>
        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.414-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/>
        </svg>
        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
        </svg>
    </div>

    <!-- Theme toggle script -->
    <script>
        document.addEventListener('click', function(event) {
            const toggle = event.target.closest('[data-theme-toggle]');
            if (!toggle) return;

            const root = document.documentElement;
            const currentTheme = root.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            root.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });

        // Set initial theme
        (function() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-theme', savedTheme);
            }
        })();
    </script>
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