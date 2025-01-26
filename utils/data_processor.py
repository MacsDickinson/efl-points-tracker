import pandas as pd
from db.database import get_db
from db.models import Standings

def calculate_cumulative_points(matches_df):
    """Calculate cumulative points and goal statistics for each team over time"""
    if matches_df.empty:
        return pd.DataFrame()

    # Sort matches by actual date played
    matches_df = matches_df.sort_values('date')

    # Get database session
    db = next(get_db())

    try:
        # Get teams and their points deductions at the start
        teams_deductions = {}
        points_data = []

        # Get all unique teams
        all_teams = set(matches_df['home_team'].unique()) | set(matches_df['away_team'].unique())

        # Get initial points deductions for each team
        for team in all_teams:
            # Get latest standings for the team
            latest_standing = (
                db.query(Standings)
                .join(Standings.team)
                .filter(Standings.team.has(name=team))
                .order_by(Standings.last_updated.desc())
                .first()
            )
            deduction = latest_standing.points_deduction if latest_standing else 0
            teams_deductions[team] = deduction

            # Add initial point (with deduction) for gameweek 0
            points_data.append({
                'team': team,
                'date': matches_df['date'].min(),  # First date in dataset
                'points': -abs(deduction),  # Start with negative points if there's a deduction
                'matches_played': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'form': latest_standing.form if latest_standing else None
            })

        # Get all dates where we have matches
        all_dates = sorted(matches_df['date'].unique())

        # Process each date
        for date in all_dates:
            # Get matches up to this date
            matches_to_date = matches_df[matches_df['date'] <= date]

            for team in all_teams:
                # Get all matches involving this team up to this date
                team_matches = matches_to_date[
                    (matches_to_date['home_team'] == team) | 
                    (matches_to_date['away_team'] == team)
                ].sort_values('date')

                matches_played = len(team_matches)

                if matches_played == 0:
                    continue  # Skip if no matches played (already handled in initial points)

                # Calculate goals and points from matches
                cumulative_goals_for = 0
                cumulative_goals_against = 0
                calculated_points = -abs(teams_deductions.get(team, 0))  # Start with deduction

                for _, match in team_matches.iterrows():
                    if match['home_team'] == team:
                        team_goals = match['home_score']
                        opponent_goals = match['away_score']
                        if team_goals > opponent_goals:
                            calculated_points += 3
                        elif team_goals == opponent_goals:
                            calculated_points += 1
                    else:  # team is away
                        team_goals = match['away_score']
                        opponent_goals = match['home_score']
                        if team_goals > opponent_goals:
                            calculated_points += 3
                        elif team_goals == opponent_goals:
                            calculated_points += 1

                    cumulative_goals_for += team_goals
                    cumulative_goals_against += opponent_goals

                goal_difference = cumulative_goals_for - cumulative_goals_against

                # Get the latest standings for this team
                latest_standing = (
                    db.query(Standings)
                    .join(Standings.team)
                    .filter(Standings.team.has(name=team))
                    .order_by(Standings.last_updated.desc())
                    .first()
                )

                # Use official standings points if matches played match
                points = latest_standing.points if (latest_standing and 
                    latest_standing.matches_played == matches_played) else calculated_points

                points_data.append({
                    'team': team,
                    'date': date,
                    'points': points,
                    'matches_played': matches_played,
                    'goals_for': cumulative_goals_for,
                    'goals_against': cumulative_goals_against,
                    'goal_difference': goal_difference,
                    'form': latest_standing.form if latest_standing else None
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