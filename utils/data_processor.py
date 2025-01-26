import pandas as pd
from db.database import get_db
from db.models import Standings, Team
from sqlalchemy import or_

def calculate_cumulative_points(matches_df):
    """Calculate cumulative points and goal statistics for each team over time"""
    if matches_df.empty:
        return pd.DataFrame()

    # Sort matches by date played
    matches_df = matches_df.sort_values('date')

    # Get database session
    db = next(get_db())

    try:
        # Get all unique teams
        all_teams = set(matches_df['home_team'].unique()) | set(matches_df['away_team'].unique())

        # Get latest standings for all teams in one query
        team_standings = {}
        standings_query = (
            db.query(Standings)
            .join(Team)
            .filter(or_(*[Team.name == name for name in all_teams]))
            .all()
        )

        for standing in standings_query:
            team_standings[standing.team.name] = standing

        points_data = []

        # Initialize all teams with their starting points (0 or deduction)
        for team in all_teams:
            standing = team_standings.get(team)
            points_deduction = standing.points_deduction if standing else 0

            # Add starting point at match day 0
            points_data.append({
                'team': team,
                'date': matches_df['date'].min(),
                'points': -points_deduction,  # Negative because deductions reduce points
                'matches_played': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0
            })

            # Process matches for this team
            current_points = -points_deduction  # Start with deduction
            goals_for = 0
            goals_against = 0
            matches_count = 0

            # Get all matches for this team
            team_matches = matches_df[
                (matches_df['home_team'] == team) | 
                (matches_df['away_team'] == team)
            ].sort_values('date')

            for _, match in team_matches.iterrows():
                matches_count += 1

                # Calculate points from this match
                if match['home_team'] == team:
                    match_goals_for = match['home_score']
                    match_goals_against = match['away_score']
                else:
                    match_goals_for = match['away_score']
                    match_goals_against = match['home_score']

                # Update running totals
                goals_for += match_goals_for
                goals_against += match_goals_against

                # Update points based on result
                if match_goals_for > match_goals_against:
                    current_points += 3
                elif match_goals_for == match_goals_against:
                    current_points += 1

                # Record the state after this match
                points_data.append({
                    'team': team,
                    'date': match['date'],
                    'points': current_points,
                    'matches_played': matches_count,
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'goal_difference': goals_for - goals_against
                })

        return pd.DataFrame(points_data)

    finally:
        db.close()

def get_team_colors():
    """Return consistent colors for teams across all leagues"""
    return {
        "Arsenal": "#EF0107",
        "Aston Villa": "#670E36",
        "Bournemouth": "#DA291C",
        "Brentford": "#e30613",
        "Brighton": "#0057B8",
        "Burnley": "#6C1D45",
        "Chelsea": "#034694",
        "Crystal Palace": "#1B458F",
        "Everton": "#003399",
        "Fulham": "#000000",
        "Liverpool": "#C8102E",
        "Luton": "#F78F1E",
        "Man City": "#6CABDD",
        "Man United": "#DA291C",
        "Newcastle": "#241F20",
        "Nottingham Forest": "#DD0000",
        "Sheffield United": "#EE2737",
        "Tottenham": "#132257",
        "West Ham": "#7A263A",
        "Wolves": "#FDB913",
        # Championship teams
        "Birmingham": "#0000FF",
        "Blackburn": "#009EE0",
        "Bristol City": "#E21C38",
        "Cardiff": "#0070B5",
        "Coventry": "#78D0F3",
        "Hull": "#F18A00",
        "Ipswich": "#0044A9",
        "Leeds": "#FFFFFF",
        "Leicester": "#003090",
        "Middlesbrough": "#E21C38",
        "Millwall": "#001D5E",
        "Norwich": "#00A650",
        "Plymouth": "#007B5F",
        "Preston": "#B2B2B2",
        "QPR": "#005CAB",
        "Rotherham": "#DD1E3E",
        "Sheffield Wednesday": "#0066B3",
        "Southampton": "#D71920",
        "Stoke": "#E03A3E",
        "Sunderland": "#FF0000",
        "Swansea": "#121212",
        "Watford": "#FBEE23",
        "West Brom": "#122F67",
    }