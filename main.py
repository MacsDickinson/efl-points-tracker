import streamlit as st
import pandas as pd
from utils.api import get_available_leagues, get_available_seasons, get_team_data_with_matches
from components.graph import plot_cumulative_points
from db.database import init_db
from utils.dev_mode import log_error
from components.league_table import display_league_table
from components.head_to_head import display_head_to_head

st.set_page_config(page_title="⚽️ Footy Stats",
                   page_icon="sports_soccer",
                   initial_sidebar_state="collapsed")

# Custom CSS for system theme support
st.markdown("""
    <style>
    :root {
        color-scheme: light dark;
    }
    
    /* Base styles */
    * {
        box-sizing: border-box;
        -webkit-tap-highlight-color: transparent;
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

    /* Mobile optimizations */
    @media screen and (max-width: 768px) {
        .block-container {
            padding: 1rem !important;
        }
        
        .stApp {
            font-size: 14px;
        }

        .league-table {
            font-size: 12px !important;
        }

        .pos-cell { width: 30px !important; }
        .team-cell { width: 120px !important; }
        .num-cell { width: 40px !important; }
        .goals-cell { width: 60px !important; }
        .form-cell { width: 100px !important; letter-spacing: 3px !important; }
        .points-cell { width: 40px !important; }
        .trend-cell { width: 80px !important; }
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
        overflow-x: auto;
    }
    /* Table container for horizontal scrolling */
    .element-container {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    /* Better touch targets */
    .stSelectbox [data-baseweb="select"], 
    .stMultiSelect [data-baseweb="select"],
    button {
        min-height: 44px;
    }
    .stSelectbox label, .stSelectbox div[role="button"] {
        color: var(--text-color) !important;
    }
    .stSelectbox div[role="button"] {
        background-color: var(--secondary-bg);
        border: 1px solid var(--border-color);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-color);
        border-right: 1px solid var(--border-color);
    }

    /* Multiselect styling */
    .stMultiSelect {
        background: var(--bg-color);
    }
    .stMultiSelect label {
        color: var(--text-color) !important;
        font-weight: 600;
    }
    .stMultiSelect [data-baseweb="select"] {
        background: linear-gradient(135deg, #FF5F6D 0%, #FE90AF 100%);
        padding: 2px;
        border-radius: 4px;
    }
    .stMultiSelect [data-baseweb="select"] > div {
        background: var(--bg-color);
        border: none !important;
        border-radius: 2px;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #FF5F6D 0%, #FE90AF 100%);
        color: var(--bg-color);
    }
    .stMultiSelect [data-baseweb="tag"]:hover {
        background: linear-gradient(135deg, #b5d980 0%, #e57c99 100%);
    }

    /* Filter icon styling */
    .filter-icon {
        vertical-align: middle;
        margin-right: 8px;
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
    .stMarkdown div, .stMarkdown p, .stMarkdown span,
    .element-container, .stTextInput label, 
    .stSelectbox label, .stNumberInput label,
    .css-1dp5vir, .css-81oif8, .css-10trblm {
        color: var(--text-color) !important;
    }
    
    div[data-testid="stToolbar"] {
        color: var(--text-color);
    }
    .stMetric > label, .stMetric > .egzej5g3 {
        color: var(--text-color) !important;
    }
    .st-emotion-cache-qsoh6x {
        fill: url(#headerGradient)
    }
    .st-emotion-cache-xp32gg {
        -webkit-box-shadow:0px 0px 15px 3px rgba(255,196,113,0.6);
        -moz-box-shadow: 0px 0px 15px 3px rgba(255,196,113,0.6);
        box-shadow: 0px 0px 15px 3px rgba(255,196,113,0.6);
    }
    .st-emotion-cache-asde8h {
        display: inline;
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
    # Create and embed the header image
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
        <svg width="600" height="100" viewBox="0 0 600 100">
            <defs>
                <linearGradient id="headerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#FF5F6D;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#FFC371;stop-opacity:1" />
                </linearGradient>
            </defs>
            <g>
                <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
                    fill="url(#headerGradient)" 
                    style="font-size: 3.6rem; font-weight: bold; font-family: 'Orbitron', system-ui;">
                    Footy Stats
                </text>
            </g>
        </svg>
    </div>
    """,
                unsafe_allow_html=True)

    # Create sidebar selectors
    leagues = get_available_leagues()
    selected_league = st.sidebar.selectbox("Select League",
                                           options=list(leagues.keys()),
                                           format_func=lambda x: leagues[x],
                                           key="league_selector")

    seasons = get_available_seasons()
    selected_season = st.sidebar.selectbox("Select Season",
                                           options=list(seasons.keys()),
                                           format_func=lambda x: seasons[x],
                                           key="season_selector")

    # Main content
    with st.spinner("Syncing match data..."):
        team_data = get_team_data_with_matches(int(selected_league),
                                               int(selected_season))

        # Get all team names for filtering and sort alphabetically
        all_teams = sorted([team['name'] for team in team_data])

        with st.sidebar.expander("Filter Teams",
                                 expanded=True,
                                 icon=":material/filter_alt:"):
            selected_teams = st.multiselect("Select teams to display",
                                            options=all_teams,
                                            default=all_teams,
                                            key="team_filter")

        # Filter team data based on selection
        filtered_team_data = [
            team for team in team_data if team['name'] in selected_teams
        ]

        points_data = []
        for team in filtered_team_data:
            points_data.append({
                'team':
                team['name'],
                'date':
                team['matches'][0]['date'] if team['matches'] else None,
                'points':
                -team['points_deduction'],
                'matches_played':
                0,
                'goals_for':
                0,
                'goals_against':
                0,
                'goal_difference':
                0
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

        tab1, tab2, tab3 = st.tabs(
            ["📈 Points Progression", "📊 League Table", "🤝 Head-to-Head"])

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
            display_league_table(filtered_team_data)

        with tab3:
            display_head_to_head(filtered_team_data)


if __name__ == "__main__":
    main()
