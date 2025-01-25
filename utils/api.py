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
    current_date = datetime(2022, 8, 1)

    for month in range(9):
        for team1_idx in range(len(teams)):
            for team2_idx in range(team1_idx + 1, len(teams)):
                home_score = np.random.randint(0, 5)
                away_score = np.random.randint(0, 5)

                match = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'home_team': teams[team1_idx],
                    'away_team': teams[team2_idx],
                    'home_score': home_score,
                    'away_score': away_score,
                }
                matches.append(match)

        current_date = pd.Timestamp(current_date) + pd.DateOffset(days=30)

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