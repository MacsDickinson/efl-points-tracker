import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import League, Team, Match
from db.database import get_db
from utils.football_api import fetch_matches_from_api
from utils.dev_mode import log_error, is_dev_mode
import streamlit as st

def sync_matches(league_id: int, season: int):
    """
    Sync matches for a specific league and season with progress tracking.
    """
    season = int(season)
    db = next(get_db())

    try:
        # Fetch matches from API
        api_matches = fetch_matches_from_api(league_id, season)
        if api_matches.empty:
            return

        # Show progress bar
        progress_text = "Loading match data..."
        total_matches = len(api_matches)
        progress_bar = st.progress(0, text=progress_text)

        # Get or create league (with error handling)
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            league = League(api_id=league_id, name=api_matches['league_name'].iloc[0])
            db.add(league)
            db.commit()

        # Pre-fetch existing teams for this league to reduce database queries
        existing_teams = {
            (t.api_id, t.league_id): t 
            for t in db.query(Team).filter_by(league_id=league.id).all()
        }

        # Pre-fetch existing matches to avoid duplicates
        existing_matches = {
            (m.season, m.league_id, m.home_team_id, m.away_team_id): m
            for m in db.query(Match).filter_by(season=season, league_id=league.id).all()
        }

        # Process matches in batches
        batch_size = 50
        for batch_idx in range(0, len(api_matches), batch_size):
            batch_end = min(batch_idx + batch_size, len(api_matches))
            batch = api_matches.iloc[batch_idx:batch_end]

            with db.begin_nested():  # Create savepoint
                for idx, row in batch.iterrows():
                    try:
                        # Update progress
                        progress = (batch_idx + idx + 1) / total_matches
                        progress_bar.progress(progress, text=f"{progress_text} ({batch_idx + idx + 1}/{total_matches})")

                        # Get or create teams efficiently
                        home_team = get_or_create_team(db, row['home_team'], row['home_team_id'], 
                                                     league.id, existing_teams)
                        away_team = get_or_create_team(db, row['away_team'], row['away_team_id'], 
                                                     league.id, existing_teams)

                        # Check if match exists using the pre-fetched data
                        match_key = (season, league.id, home_team.id, away_team.id)
                        match = existing_matches.get(match_key)

                        # Convert scores
                        home_score = int(row['home_score']) if pd.notna(row.get('home_score')) else None
                        away_score = int(row['away_score']) if pd.notna(row.get('away_score')) else None

                        if match:
                            # Update only if scores changed
                            if match.home_score != home_score or match.away_score != away_score:
                                match.home_score = home_score
                                match.away_score = away_score
                                match.status = row['status']
                        else:
                            # Create new match
                            match = Match(
                                api_id=row['fixture_id'],
                                date=pd.to_datetime(row['date']).date(),
                                season=season,
                                league_id=league.id,
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                home_score=home_score,
                                away_score=away_score,
                                status=row['status']
                            )
                            db.add(match)
                            existing_matches[match_key] = match

                    except Exception as e:
                        if is_dev_mode():
                            log_error(f"Error processing match: {row['fixture_id']}", e)
                        continue

            # Commit each batch
            db.commit()

        # Clear progress bar
        progress_bar.empty()

    except Exception as e:
        db.rollback()
        error_msg = log_error("Failed to sync matches", e)
        if is_dev_mode():
            raise Exception(error_msg) from e
        else:
            raise Exception("Failed to update match data") from e
    finally:
        db.close()

def get_or_create_team(db: Session, team_name: str, team_api_id: int, league_id: int, 
                      existing_teams: dict = None):
    """Get or create a team in the database efficiently"""
    if existing_teams is not None:
        # Check in-memory cache first
        team = existing_teams.get((team_api_id, league_id))
        if team:
            return team

    # Check database if not found in cache
    with db.no_autoflush:
        team = db.query(Team).filter_by(api_id=team_api_id, league_id=league_id).first()
        if not team:
            team = Team(
                name=team_name,
                api_id=team_api_id,
                league_id=league_id
            )
            db.add(team)
            db.commit()
            if existing_teams is not None:
                existing_teams[(team_api_id, league_id)] = team
    return team

def needs_refresh(league_id: int, season: int) -> bool:
    """
    Check if we need to refresh data for a league and season.
    Returns True if:
    - No data exists
    - Last match was over 24 hours ago and there are unfinished matches
    - Next match is within 24 hours
    """
    season = int(season)
    db = next(get_db())
    try:
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            return True

        # Get latest match in database
        latest_match = (
            db.query(Match)
            .filter_by(league_id=league.id, season=season)
            .order_by(Match.date.desc())
            .first()
        )

        if not latest_match:
            return True

        # Check for unfinished matches in the past
        unfinished_past_matches = (
            db.query(Match)
            .filter(
                Match.league_id == league.id,
                Match.season == season,
                Match.date < datetime.now().date(),
                Match.status != 'FT'
            )
            .count()
        )

        if unfinished_past_matches > 0:
            return True

        # Check for upcoming matches within 24 hours
        next_match = (
            db.query(Match)
            .filter(
                Match.league_id == league.id,
                Match.season == season,
                Match.date >= datetime.now().date(),
                Match.status == 'NS'
            )
            .order_by(Match.date)
            .first()
        )

        if next_match and next_match.date <= (datetime.now() + timedelta(days=1)).date():
            return True

        return False

    finally:
        db.close()