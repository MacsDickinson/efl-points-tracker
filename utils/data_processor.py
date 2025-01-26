import pandas as pd
from db.database import get_db
from db.models import Standings, Team
from sqlalchemy import or_

def calculate_cumulative_points(matches_df):
    """Calculate cumulative points and goal statistics for each team over time"""
    if matches_df.empty:
        return pd.DataFrame()

    # Sort matches by actual date played
    matches_df = matches_df.sort_values('date')

    # Get database session
    db = next(get_db())

    try:
        # Get all unique teams and their latest standings in a single query
        all_teams = set(matches_df['home_team'].unique()) | set(matches_df['away_team'].unique())

        # Fetch all standings for all teams in one query
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

        # Initialize points data with deductions
        for team in all_teams:
            standing = team_standings.get(team)
            deduction = standing.points_deduction if standing else 0

            # Add initial point (with deduction) for gameweek 0
            points_data.append({
                'team': team,
                'date': matches_df['date'].min(),
                'points': -abs(deduction),
                'matches_played': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'form': standing.form if standing else None
            })

            # Process each team's matches
            team_matches = matches_df[
                (matches_df['home_team'] == team) | 
                (matches_df['away_team'] == team)
            ].sort_values('date')

            cumulative_points = -abs(deduction)
            cumulative_goals_for = 0
            cumulative_goals_against = 0

            for _, match in team_matches.iterrows():
                is_home = match['home_team'] == team
                team_goals = match['home_score'] if is_home else match['away_score']
                opponent_goals = match['away_score'] if is_home else match['home_score']

                if team_goals > opponent_goals:
                    cumulative_points += 3
                elif team_goals == opponent_goals:
                    cumulative_points += 1

                cumulative_goals_for += team_goals
                cumulative_goals_against += opponent_goals

                points_data.append({
                    'team': team,
                    'date': match['date'],
                    'points': cumulative_points,
                    'matches_played': len(points_data) - 1,  # -1 for initial point
                    'goals_for': cumulative_goals_for,
                    'goals_against': cumulative_goals_against,
                    'goal_difference': cumulative_goals_for - cumulative_goals_against,
                    'form': standing.form if standing else None
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