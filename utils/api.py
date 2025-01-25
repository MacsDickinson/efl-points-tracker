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
    Using a mock API response for demonstration
    In production, replace with actual API calls
    """
    # Mock data generation for demonstration
    teams = ["Arsenal", "Chelsea", "Liverpool", "Man City", "Man United", 
             "Tottenham", "Leicester", "West Ham", "Everton", "Leeds"]

    matches = []
    current_date = datetime(2022, 8, 1)  # Season start date

    # Generate matches for approximately 38 weeks (standard season length)
    for week in range(38):
        # Each week has 5 matches (10 teams = 5 matches per week)
        teams_this_week = teams.copy()
        np.random.shuffle(teams_this_week)

        for i in range(0, len(teams_this_week), 2):
            home_team = teams_this_week[i]
            away_team = teams_this_week[i + 1]

            home_score = np.random.randint(0, 5)
            away_score = np.random.randint(0, 5)

            match = {
                'date': current_date.strftime('%Y-%m-%d'),
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
            }
            matches.append(match)

        # Increment by one week
        current_date = pd.Timestamp(current_date) + pd.DateOffset(days=7)

    return pd.DataFrame(matches)

def get_available_leagues():
    """Return available leagues for selection"""
    return {
        "39": "Premier League",
        "40": "Championship",
    }

def get_available_seasons():
    """Return available seasons for selection"""
    return ["2022", "2021", "2020"]