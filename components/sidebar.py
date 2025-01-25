import streamlit as st
from utils.api import get_available_leagues, get_available_seasons

def create_sidebar():
    """Create sidebar with league and season selection"""
    st.sidebar.title("⚽ League Dashboard")
    
    leagues = get_available_leagues()
    selected_league = st.sidebar.selectbox(
        "Select League",
        options=list(leagues.keys()),
        format_func=lambda x: leagues[x]
    )
    
    seasons = get_available_seasons()
    selected_season = st.sidebar.selectbox(
        "Select Season",
        options=seasons
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### About
    This dashboard shows the cumulative points 
    progression for football teams throughout 
    the season.
    """)
    
    return selected_league, selected_season
