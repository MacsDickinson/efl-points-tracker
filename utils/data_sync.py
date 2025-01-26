import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import League, Team, Match, Standings
from db.database import get_db
from utils.football_api import fetch_matches_from_api, fetch_standings_from_api
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
            league = League(api_id=league_id,
                            name=api_matches['league_name'].iloc[0])
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
            for m in db.query(Match).filter_by(season=season,
                                               league_id=league.id).all()
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
                        progress_bar.progress(
                            progress,
                            text=
                            f"{progress_text} ({batch_idx + idx + 1}/{total_matches})"
                        )

                        # Get or create teams efficiently
                        home_team = get_or_create_team(db, row['home_team'],
                                                       row['home_team_id'],
                                                       league.id,
                                                       existing_teams)
                        away_team = get_or_create_team(db, row['away_team'],
                                                       row['away_team_id'],
                                                       league.id,
                                                       existing_teams)

                        # Check if match exists using the pre-fetched data
                        match_key = (season, league.id, home_team.id,
                                     away_team.id)
                        match = existing_matches.get(match_key)

                        # Convert scores
                        home_score = int(row['home_score']) if pd.notna(
                            row.get('home_score')) else None
                        away_score = int(row['away_score']) if pd.notna(
                            row.get('away_score')) else None

                        if match:
                            # Update only if scores changed
                            if match.home_score != home_score or match.away_score != away_score:
                                match.home_score = home_score
                                match.away_score = away_score
                                match.status = row['status']
                        else:
                            # Create new match
                            match = Match(api_id=row['fixture_id'],
                                          date=pd.to_datetime(
                                              row['date']).date(),
                                          season=season,
                                          league_id=league.id,
                                          home_team_id=home_team.id,
                                          away_team_id=away_team.id,
                                          home_score=home_score,
                                          away_score=away_score,
                                          status=row['status'])
                            db.add(match)
                            existing_matches[match_key] = match

                    except Exception as e:
                        if is_dev_mode():
                            log_error(
                                f"Error processing match: {row['fixture_id']}",
                                e)
                        continue

            # Commit each batch
            db.commit()

        # Sync standings after matches are synced
        sync_standings(db, league_id, season)

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


def sync_standings(db: Session, league_id: int, season: int):
    """Sync standings data from the API"""
    try:
        # Fetch current standings from API
        standings_df = fetch_standings_from_api(league_id, season)
        if standings_df.empty:
            return

        # Get league
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            return

        # Get existing teams dictionary
        existing_teams = {
            t.api_id: t.id
            for t in db.query(Team).filter_by(league_id=league.id).all()
        }

        # Update standings for each team
        for _, row in standings_df.iterrows():
            team_id = existing_teams.get(row['team_id'])
            if not team_id:
                continue

            # Calculate points deduction by comparing total points with expected points
            matches_played = row['matches_played']
            points_deduction = 0

            # Get all matches for this team to calculate expected points
            team = db.query(Team).get(team_id)
            matches = (db.query(Match).filter((Match.home_team_id == team_id) |
                                              (Match.away_team_id == team_id),
                                              Match.status == 'FT',
                                              Match.season == season).all())

            expected_points = 0
            for match in matches:
                if match.home_team_id == team_id:
                    if match.home_score > match.away_score:
                        expected_points += 3
                    elif match.home_score == match.away_score:
                        expected_points += 1
                else:
                    if match.away_score > match.home_score:
                        expected_points += 3
                    elif match.home_score == match.away_score:
                        expected_points += 1

            # The difference between expected and actual points is the deduction
            points_deduction = expected_points - row['points']
            if points_deduction < 0:  # If negative, assume it's a bonus not a deduction
                points_deduction = 0

            # Get existing standing or create new one
            standing = (db.query(Standings).filter_by(season=season,
                                                      league_id=league.id,
                                                      team_id=team_id).first())

            if standing:
                # Update existing standing
                standing.position = row['position']
                standing.points = row['points']
                standing.points_deduction = points_deduction
                standing.matches_played = row['matches_played']
                standing.goals_for = row['goals_for']
                standing.goals_against = row['goals_against']
                standing.goal_difference = row['goal_difference']
                standing.form = row['form']
                standing.last_updated = datetime.utcnow()
            else:
                # Create new standing
                standing = Standings(season=season,
                                     league_id=league.id,
                                     team_id=team_id,
                                     position=row['position'],
                                     points=row['points'],
                                     points_deduction=points_deduction,
                                     matches_played=row['matches_played'],
                                     goals_for=row['goals_for'],
                                     goals_against=row['goals_against'],
                                     goal_difference=row['goal_difference'],
                                     form=row['form'],
                                     last_updated=datetime.utcnow())
                db.add(standing)

        db.commit()

    except Exception as e:
        db.rollback()
        error_msg = log_error("Failed to sync standings", e)
        if is_dev_mode():
            raise Exception(error_msg) from e


def get_or_create_team(db: Session,
                       team_name: str,
                       team_api_id: int,
                       league_id: int,
                       existing_teams: dict = None):
    """Get or create a team in the database efficiently"""
    if existing_teams is not None:
        # Check in-memory cache first
        team = existing_teams.get((team_api_id, league_id))
        if team:
            return team

    # Check database if not found in cache
    with db.no_autoflush:
        team = db.query(Team).filter_by(api_id=team_api_id,
                                        league_id=league_id).first()
        if not team:
            team = Team(name=team_name,
                        api_id=team_api_id,
                        league_id=league_id)
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
    - There are unfinished matches in the past that need updating
    - Next match is within 24 hours
    """
    season = int(season)
    db = next(get_db())
    try:
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            print(f"League {league_id} not found in the database")
            return True

        # Get latest match in database
        latest_match = (db.query(Match).filter_by(
            league_id=league.id,
            season=season).order_by(Match.date.desc()).first())

        if not latest_match:
            print(f"No match data in league {league_id} and season {season}")
            return True

        # Check for unfinished matches in the past
        unfinished_past_matches = (db.query(Match).filter(
            Match.league_id == league.id, Match.season == season, Match.date
            < datetime.now().date(), Match.status != 'FT').count())

        if unfinished_past_matches > 0:
            print(
                f"Unfinished matches in the past for league {league_id} and season {season}"
            )
            return True

        print("No data sync required")
        
        return False

    finally:
        db.close()
