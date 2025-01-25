import requests
import pandas as pd
from datetime import datetime
import streamlit as st
import os
from db.database import get_db
from db.models import League, Match
from utils.data_sync import sync_matches, needs_refresh
from utils.football_api import fetch_matches_from_api

@st.cache_data(ttl=3600)
def get_league_matches(league_id, season):
    """
    Get match data for a specific league and season.
    Checks database first, refreshes from API if needed.
    """
    # Check if we need to refresh data
    if needs_refresh(league_id, season):
        sync_matches(league_id, season)

    db = next(get_db())
    try:
        # Get matches from database
        matches = (
            db.query(Match)
            .filter_by(league_id=league_id, season=season)
            .order_by(Match.date)
            .all()
        )

        # Convert to DataFrame
        matches_data = []
        for match in matches:
            if match.status == 'FT':  # Only include finished matches
                matches_data.append({
                    'date': match.date.strftime('%Y-%m-%d'),
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'home_score': match.home_score,
                    'away_score': match.away_score
                })

        return pd.DataFrame(matches_data)

    finally:
        db.close()

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
    return {
        "2024": "24/25",
        "2023": "23/24",
        "2022": "22/23",
        "2021": "21/22",
        "2020": "20/21",
    }