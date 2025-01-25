import requests
import pandas as pd
from datetime import datetime
import streamlit as st
import os

FOOTBALL_API_BASE = "https://api-football-v1.p.rapidapi.com/v3"


@st.cache_data(ttl=3600)
def get_league_matches(league_id, season):
    """
    Fetch match data for a specific league and season
    """
    try:
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        st.write("Fetching match data")  # Debug log

        # Get all fixtures for the league and season
        response = requests.get(
            f"{FOOTBALL_API_BASE}/fixtures",
            headers=headers,
            params={
                "league": league_id,
                "season": season,
                "status": "FT"  # Only completed matches
            },
            timeout=10  # Add timeout to prevent hanging
        )

        if response.status_code == 401:
            st.error("⚠️ Invalid API key. Please check your RapidAPI key.")
            return pd.DataFrame(columns=[
                'date', 'home_team', 'away_team', 'home_score', 'away_score'
            ])

        response.raise_for_status()
        data = response.json()

        if "response" not in data:
            st.error("⚠️ Unexpected API response format")
            st.write("API Response:", data)  # Debug log
            return pd.DataFrame(columns=[
                'date', 'home_team', 'away_team', 'home_score', 'away_score'
            ])

        fixtures = data["response"]
        if not fixtures:
            st.warning("No matches found for the selected league and season.")
            return pd.DataFrame(columns=[
                'date', 'home_team', 'away_team', 'home_score', 'away_score'
            ])

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

        df = pd.DataFrame(matches)
        st.write(f"Found {len(df)} matches")  # Debug log
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching match data: {str(e)}")
        return pd.DataFrame(columns=[
            'date', 'home_team', 'away_team', 'home_score', 'away_score'
        ])
    except KeyError as e:
        st.error(f"⚠️ Error processing API response: {str(e)}")
        return pd.DataFrame(columns=[
            'date', 'home_team', 'away_team', 'home_score', 'away_score'
        ])


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
    return {
        "2024": "24/25",
        "2023": "23/24",
        "2022": "22/23",
        "2021": "21/22",
        "2020": "20/21",
    }
