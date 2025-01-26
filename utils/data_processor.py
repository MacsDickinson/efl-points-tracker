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
    """Return consistent primary and secondary colors for teams across all leagues"""
    return {
        # Premier League Teams
        "Arsenal": {"primary": "#EF0107", "secondary": "#063672"},
        "Aston Villa": {"primary": "#670E36", "secondary": "#95BFE5"},
        "Bournemouth": {"primary": "#DA291C", "secondary": "#000000"},
        "Brentford": {"primary": "#e30613", "secondary": "#FBB800"},
        "Brighton": {"primary": "#0057B8", "secondary": "#FFCD00"},
        "Burnley": {"primary": "#6C1D45", "secondary": "#99D6EA"},
        "Chelsea": {"primary": "#034694", "secondary": "#DBA111"},
        "Crystal Palace": {"primary": "#1B458F", "secondary": "#C4122E"},
        "Everton": {"primary": "#003399", "secondary": "#FFFFFF"},
        "Fulham": {"primary": "#000000", "secondary": "#CC0000"},
        "Liverpool": {"primary": "#C8102E", "secondary": "#00B2A9"},
        "Luton": {"primary": "#F78F1E", "secondary": "#1C2033"},
        "Manchester City": {"primary": "#6CABDD", "secondary": "#1C2C5B"},
        "Manchester United": {"primary": "#DA291C", "secondary": "#FBE122"},
        "Newcastle": {"primary": "#241F20", "secondary": "#F1BE48"},
        "Nottingham Forest": {"primary": "#DD0000", "secondary": "#FFFFFF"},
        "Sheffield United": {"primary": "#EE2737", "secondary": "#000000"},
        "Tottenham": {"primary": "#132257", "secondary": "#FFFFFF"},
        "West Ham": {"primary": "#7A263A", "secondary": "#1BB1E7"},
        "Wolves": {"primary": "#FDB913", "secondary": "#231F20"},

        # Championship Teams
        "Birmingham": {"primary": "#0000FF", "secondary": "#FFFFFF"},
        "Blackburn": {"primary": "#009EE0", "secondary": "#FFFFFF"},
        "Bristol City": {"primary": "#E21C38", "secondary": "#1C223A"},
        "Cardiff": {"primary": "#0070B5", "secondary": "#D61E49"},
        "Coventry": {"primary": "#78D0F3", "secondary": "#FFFFFF"},
        "Hull": {"primary": "#F18A00", "secondary": "#000000"},
        "Ipswich": {"primary": "#0044A9", "secondary": "#FFFFFF"},
        "Leeds": {"primary": "#FFFFFF", "secondary": "#1D1D1B"},
        "Leicester": {"primary": "#003090", "secondary": "#FDBE11"},
        "Middlesbrough": {"primary": "#E21C38", "secondary": "#1C223A"},
        "Millwall": {"primary": "#001D5E", "secondary": "#FFFFFF"},
        "Norwich": {"primary": "#00A650", "secondary": "#FFF200"},
        "Plymouth": {"primary": "#007B5F", "secondary": "#000000"},
        "Preston": {"primary": "#B2B2B2", "secondary": "#FFFFFF"},
        "QPR": {"primary": "#005CAB", "secondary": "#FFFFFF"},
        "Rotherham": {"primary": "#DD1E3E", "secondary": "#FFFFFF"},
        "Sheffield Wednesday": {"primary": "#0066B3", "secondary": "#FFFFFF"},
        "Southampton": {"primary": "#D71920", "secondary": "#130C0E"},
        "Stoke": {"primary": "#E03A3E", "secondary": "#FFFFFF"},
        "Sunderland": {"primary": "#FF0000", "secondary": "#FFFFFF"},
        "Swansea": {"primary": "#121212", "secondary": "#FFFFFF"},
        "Watford": {"primary": "#FBEE23", "secondary": "#ED2127"},
        "West Brom": {"primary": "#122F67", "secondary": "#FFFFFF"},
    }