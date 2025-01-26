import requests
import pandas as pd
import streamlit as st
import os
from db.database import get_db
from db.models import League, Match, Team, Standings
from utils.data_sync import sync_matches, needs_refresh
from utils.football_api import fetch_matches_from_api
from utils.dev_mode import is_dev_mode
from sqlalchemy import text

def get_team_data_with_matches(league_id: int, season: int):
    """
    Get team data including matches in an efficient structure.
    Returns a list of team objects with their matches and standings data.
    """
    # Check if data needs refresh
    if needs_refresh(league_id, season):
        sync_matches(league_id, season)

    db = next(get_db())
    try:
        # Get league from database
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            return []

        # Get all teams with their standings for this league and season
        teams_with_standings = (
            db.query(Team, Standings)
            .join(Standings, Team.id == Standings.team_id)
            .filter(
                Standings.league_id == league.id,
                Standings.season == season
            )
            .all()
        )

        team_data = []
        for team, standing in teams_with_standings:
            # Get all matches for this team
            matches = (
                db.query(Match)
                .filter(
                    Match.league_id == league.id,
                    Match.season == season,
                    Match.status == 'FT',
                    ((Match.home_team_id == team.id) | (Match.away_team_id == team.id))
                )
                .order_by(Match.date)
                .all()
            )

            # Process matches into required format
            processed_matches = []
            cumulative_points = 0

            for match in matches:
                is_home = match.home_team_id == team.id
                opponent_id = match.away_team_id if is_home else match.home_team_id
                team_score = match.home_score if is_home else match.away_score
                opp_score = match.away_score if is_home else match.home_score

                # Calculate result and points
                if team_score > opp_score:
                    result = 'win'
                    cumulative_points += 3
                elif team_score == opp_score:
                    result = 'draw'
                    cumulative_points += 1
                else:
                    result = 'loss'

                # Apply points deduction to cumulative total
                adjusted_points = cumulative_points - standing.points_deduction

                processed_matches.append({
                    'date': match.date,
                    'gameweek': len(processed_matches) + 1,
                    'result': result,
                    'side': 'home' if is_home else 'away',
                    'opponent': opponent_id,
                    'goals': {
                        'home': match.home_score,
                        'away': match.away_score
                    },
                    'cumulative_total': adjusted_points
                })

            # Create team object with standings and matches data
            team_data.append({
                'id': team.id,
                'api_id': team.api_id,
                'name': team.name,
                'position': standing.position,
                'total_points': standing.points,
                'matches_played': standing.matches_played,
                'goals_for': standing.goals_for,
                'goals_against': standing.goals_against,
                'goal_difference': standing.goal_difference,
                'points_deduction': standing.points_deduction,
                'form': standing.form,
                'matches': processed_matches
            })

        return team_data

    finally:
        db.close()

@st.cache_data(ttl=3600)  # Cache for 1 hour by default
def get_league_matches(league_id, season):
    """
    Get match data for a specific league and season.
    Now uses the new team_data structure but returns dataframe for compatibility.
    """
    team_data = get_team_data_with_matches(league_id, season)

    # Convert team_data into matches dataframe for backward compatibility
    matches_data = []
    for team in team_data:
        for match in team['matches']:
            if match['side'] == 'home':  # Only add matches where team is home to avoid duplicates
                matches_data.append({
                    'date': match['date'],
                    'home_team': team['name'],
                    'away_team': next(t['name'] for t in team_data if t['id'] == match['opponent']),
                    'home_score': match['goals']['home'],
                    'away_score': match['goals']['away']
                })

    return pd.DataFrame(matches_data)

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