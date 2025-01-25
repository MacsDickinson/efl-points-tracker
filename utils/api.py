import requests
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

FOOTBALL_API_BASE = "https://api-football-v1.p.rapidapi.com/v3"

@st.cache_data(ttl=3600)
def get_league_matches(league_id, season):
    """
    Fetch match data for a specific league and season
    """
    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    try:
        # Get all fixtures for the league and season
        response = requests.get(
            f"{FOOTBALL_API_BASE}/fixtures",
            headers=headers,
            params={
                "league": league_id,
                "season": season,
                "status": "FT"  # Only completed matches
            }
        )
        response.raise_for_status()

        fixtures = response.json()["response"]
        matches = []

        for fixture in fixtures:
            match = {
                'date': fixture['fixture']['date'][:10],  # YYYY-MM-DD format
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
            }
            matches.append(match)

        return pd.DataFrame(matches)

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching match data: {str(e)}")
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['date', 'home_team', 'away_team', 'home_score', 'away_score'])

@st.cache_data(ttl=3600)
def get_available_leagues():
    """Return available leagues for selection"""
    return {
        "39": "Premier League",
        "40": "Championship",
        "41": "League One",
        "42": "League Two",
    }

def get_available_seasons():
    """Return available seasons for selection"""
    current_year = datetime.now().year
    # Return last 4 seasons including current
    return [str(year) for year in range(current_year - 3, current_year + 1)]