import pandas as pd
from db.database import get_db
from sqlalchemy import or_

def calculate_cumulative_points(matches_df):
    """
    Convert matches dataframe to points progression dataframe.
    This function now exists mainly for backwards compatibility.
    """
    if matches_df.empty:
        return pd.DataFrame()

    # Get database session
    db = next(get_db())

    try:
        points_data = []

        # Get all unique teams
        all_teams = set(matches_df['home_team'].unique()) | set(matches_df['away_team'].unique())

        for team in all_teams:
            # Get team matches in order
            team_matches = matches_df[
                (matches_df['home_team'] == team) | 
                (matches_df['away_team'] == team)
            ].sort_values('date')

            # Add starting point
            points_data.append({
                'team': team,
                'date': matches_df['date'].min(),
                'points': 0,
                'matches_played': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0
            })

            current_points = 0
            goals_for = 0
            goals_against = 0
            matches_count = 0

            for _, match in team_matches.iterrows():
                matches_count += 1

                if match['home_team'] == team:
                    match_goals_for = match['home_score']
                    match_goals_against = match['away_score']
                else:
                    match_goals_for = match['away_score']
                    match_goals_against = match['home_score']

                goals_for += match_goals_for
                goals_against += match_goals_against

                if match_goals_for > match_goals_against:
                    current_points += 3
                elif match_goals_for == match_goals_against:
                    current_points += 1

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