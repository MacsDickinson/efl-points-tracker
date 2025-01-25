import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import League, Team, Match
from db.database import get_db
from utils.football_api import fetch_matches_from_api

def sync_matches(league_id: int, season: int):
    """
    Sync matches for a specific league and season.
    - Fetches all matches (past and future)
    - Updates existing matches
    - Adds new matches
    """
    # Convert season to int if it's a string
    season = int(season)
    db = next(get_db())

    try:
        # Fetch matches from API
        api_matches = fetch_matches_from_api(league_id, season)

        if api_matches.empty:
            return

        # Get or create league
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            league = League(api_id=league_id, name=api_matches['league_name'].iloc[0])
            db.add(league)
            db.commit()

        # Process each match
        for _, row in api_matches.iterrows():
            # Get or create teams with their API IDs
            home_team = get_or_create_team(db, row['home_team'], row['home_team_id'], league.id)
            away_team = get_or_create_team(db, row['away_team'], row['away_team_id'], league.id)

            # Update or create match
            match = db.query(Match).filter_by(api_id=row['fixture_id']).first()

            # Convert scores to integers or None for not started matches
            home_score = int(row['home_score']) if pd.notna(row.get('home_score')) else None
            away_score = int(row['away_score']) if pd.notna(row.get('away_score')) else None

            if match:
                # Update existing match
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

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_or_create_team(db: Session, team_name: str, team_api_id: int, league_id: int):
    """Get or create a team in the database"""
    team = db.query(Team).filter_by(api_id=team_api_id, league_id=league_id).first()
    if not team:
        team = Team(
            name=team_name,
            api_id=team_api_id,
            league_id=league_id
        )
        db.add(team)
        db.commit()
    return team

def needs_refresh(league_id: int, season: int) -> bool:
    """
    Check if we need to refresh data for a league and season.
    Returns True if:
    - No data exists
    - Last match was over 24 hours ago and there are unfinished matches
    - Next match is within 24 hours
    """
    # Convert season to int if it's a string
    season = int(season)
    db = next(get_db())
    try:
        # Get league from database
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