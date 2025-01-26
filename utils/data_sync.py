import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
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

        print(f"\nStarting sync for league {league_id}, season {season}")
        print(f"Retrieved {len(api_matches)} matches from API")

        # Show progress bar
        progress_text = "Loading match data..."
        total_matches = len(api_matches)
        progress_bar = st.progress(0, text=progress_text)

        # Get or create league
        league = db.query(League).filter_by(api_id=league_id).first()
        if not league:
            league = League(api_id=league_id,
                          name=api_matches['league_name'].iloc[0])
            db.add(league)
            db.commit()

        # Get all unique teams from the API data
        unique_teams = pd.concat([
            api_matches[['home_team', 'home_team_id']].rename(
                columns={'home_team': 'name', 'home_team_id': 'api_id'}),
            api_matches[['away_team', 'away_team_id']].rename(
                columns={'away_team': 'name', 'away_team_id': 'api_id'})
        ]).drop_duplicates(subset=['api_id'])

        # Process all teams at once
        all_api_ids = unique_teams['api_id'].tolist()
        existing_teams = {
            t.api_id: t
            for t in db.query(Team).filter(Team.api_id.in_(all_api_ids)).all()
        }

        # Create any missing teams
        new_teams = []
        for _, team_data in unique_teams.iterrows():
            if team_data['api_id'] not in existing_teams:
                try:
                    team = Team(
                        api_id=team_data['api_id'],
                        name=team_data['name']
                    )
                    db.add(team)
                    db.commit()
                    existing_teams[team_data['api_id']] = team
                except Exception as e:
                    db.rollback()
                    print(f"Error creating team {team_data['name']}: {str(e)}")
                    continue

        # Pre-fetch existing matches
        existing_matches = {
            (m.season, m.league_id, m.home_team_id, m.away_team_id): m
            for m in db.query(Match).filter_by(season=season,
                                             league_id=league.id).all()
        }

        print(f"Found {len(existing_matches)} existing matches in database")
        new_matches_count = 0
        updated_matches_count = 0
        processed_matches = 0

        # Process matches in batches
        batch_size = 50
        total_batches = (len(api_matches) + batch_size - 1) // batch_size

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(api_matches))
            batch = api_matches.iloc[start_idx:end_idx]

            print(f"Processing batch {batch_idx + 1}/{total_batches} (matches {start_idx + 1}-{end_idx})")
            new_matches = []

            for _, row in batch.iterrows():
                try:
                    processed_matches += 1
                    progress = processed_matches / total_matches
                    progress_bar.progress(
                        progress,
                        text=f"{progress_text} ({processed_matches}/{total_matches})"
                    )

                    home_team = existing_teams[row['home_team_id']]
                    away_team = existing_teams[row['away_team_id']]
                    match_key = (season, league.id, home_team.id, away_team.id)
                    match = existing_matches.get(match_key)

                    home_score = int(row['home_score']) if pd.notna(
                        row['home_score']) else None
                    away_score = int(row['away_score']) if pd.notna(
                        row['away_score']) else None

                    if match:
                        if match.home_score != home_score or match.away_score != away_score:
                            match.home_score = home_score
                            match.away_score = away_score
                            match.status = row['status']
                            updated_matches_count += 1
                    else:
                        new_match = Match(
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
                        new_matches.append(new_match)
                        existing_matches[match_key] = new_match
                        new_matches_count += 1

                except Exception as e:
                    print(f"Error processing match {row['fixture_id']}: {str(e)}")
                    continue

            if new_matches:
                db.bulk_save_objects(new_matches)
            db.commit()

            print(f"Batch {batch_idx + 1} complete: {len(new_matches)} new, {updated_matches_count} updated")

        print(f"\nSync complete:")
        print(f"- Processed {processed_matches}/{total_matches} matches")
        print(f"- {new_matches_count} new matches added")
        print(f"- {updated_matches_count} existing matches updated")
        print(f"- {len(existing_matches)} total matches in database")

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