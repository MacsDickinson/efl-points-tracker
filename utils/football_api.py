import requests
import pandas as pd
import streamlit as st
import os

FOOTBALL_API_BASE = "https://api-football-v1.p.rapidapi.com/v3"

def fetch_matches_from_api(league_id, season):
    """Fetch match data directly from the API"""
    try:
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        print(f"Fetching matches from API for league {league_id}, season {season}")

        # Get all fixtures for the league and season
        response = requests.get(
            f"{FOOTBALL_API_BASE}/fixtures",
            headers=headers,
            params={
                "league": league_id,
                "season": season
            },
            timeout=10
        )

        if response.status_code == 401:
            st.error("⚠️ Invalid API key. Please check your RapidAPI key.")
            return pd.DataFrame()

        response.raise_for_status()
        data = response.json()

        if "response" not in data:
            st.error("⚠️ Unexpected API response format")
            return pd.DataFrame()

        fixtures = data["response"]
        print(f"Received {len(fixtures)} matches from API")

        if not fixtures:
            st.warning("No matches found for the selected league and season.")
            return pd.DataFrame()

        matches = []
        for fixture in fixtures:
            match = {
                'fixture_id': fixture['fixture']['id'],
                'date': fixture['fixture']['date'][:10],
                'home_team': fixture['teams']['home']['name'],
                'home_team_id': fixture['teams']['home']['id'],
                'away_team': fixture['teams']['away']['name'],
                'away_team_id': fixture['teams']['away']['id'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short'],
                'league_name': fixture['league']['name']
            }
            matches.append(match)

        matches_df = pd.DataFrame(matches)
        print(f"Processed {len(matches_df)} matches into DataFrame")
        return matches_df

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching match data: {str(e)}")
        return pd.DataFrame()

def fetch_standings_from_api(league_id, season):
    """Fetch current standings from the API"""
    try:
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.get(
            f"{FOOTBALL_API_BASE}/standings",
            headers=headers,
            params={
                "league": league_id,
                "season": season
            },
            timeout=10
        )

        if response.status_code == 401:
            st.error("⚠️ Invalid API key. Please check your RapidAPI key.")
            return pd.DataFrame()

        response.raise_for_status()
        data = response.json()

        if "response" not in data or not data["response"]:
            st.error("⚠️ No standings data available")
            return pd.DataFrame()

        # Extract standings from the first league found
        league_standings = data["response"][0]["league"]["standings"]
        if not league_standings:
            return pd.DataFrame()

        # Use the first standings table (in case of multiple groups)
        standings = league_standings[0]

        standings_data = []
        for team in standings:
            standings_data.append({
                'team_name': team['team']['name'],
                'team_id': team['team']['id'],
                'position': team['rank'],
                'points': team['points'],
                'matches_played': team['all']['played'],
                'goals_for': team['all']['goals']['for'],
                'goals_against': team['all']['goals']['against'],
                'goal_difference': team['goalsDiff'],
                'form': team.get('form', '')[-5:] if team.get('form') else None  # Last 5 matches
            })

        return pd.DataFrame(standings_data)

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching standings data: {str(e)}")
        return pd.DataFrame()