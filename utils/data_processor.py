import pandas as pd


def calculate_cumulative_points(matches_df):
    """Calculate cumulative points for each team over time"""
    if matches_df.empty:
        return pd.DataFrame()

    # Sort matches by actual date played
    matches_df = matches_df.sort_values('date')

    teams = set(matches_df['home_team'].unique()) | set(
        matches_df['away_team'].unique())
    points_data = []

    for team in teams:
        # Get all matches involving this team
        team_matches = matches_df[(matches_df['home_team'] == team) | (
            matches_df['away_team'] == team)].sort_values('date')

        points = []
        cumulative_points = 0
        matches_played = 0

        for _, match in team_matches.iterrows():
            matches_played += 1
            if match['home_team'] == team:
                if match['home_score'] > match['away_score']:
                    points_earned = 3
                elif match['home_score'] == match['away_score']:
                    points_earned = 1
                else:
                    points_earned = 0
            else:  # team is away
                if match['away_score'] > match['home_score']:
                    points_earned = 3
                elif match['home_score'] == match['away_score']:
                    points_earned = 1
                else:
                    points_earned = 0

            cumulative_points += points_earned
            points.append({
                'team': team,
                'date': match['date'],
                'points': cumulative_points,
                'matches_played': matches_played
            })

        points_data.extend(points)

    return pd.DataFrame(points_data)


def get_team_colors():
    """Return consistent colors for teams"""
    return {
        "Arsenal": "#EF0107",
        "Chelsea": "#034694",
        "Liverpool": "#C8102E",
        "Man City": "#6CABDD",
        "Man United": "#DA291C",
        "Tottenham": "#132257",
        "Leicester": "#003090",
        "West Ham": "#7A263A",
        "Everton": "#003399",
        "Leeds": "#DDD"
    }