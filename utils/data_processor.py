import pandas as pd

def calculate_cumulative_points(matches_df):
    """Calculate cumulative points and goal statistics for each team over time"""
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
        cumulative_goals_for = 0
        cumulative_goals_against = 0
        matches_played = 0

        for _, match in team_matches.iterrows():
            matches_played += 1
            if match['home_team'] == team:
                team_goals = match['home_score']
                opponent_goals = match['away_score']
                if team_goals > opponent_goals:
                    points_earned = 3
                elif team_goals == opponent_goals:
                    points_earned = 1
                else:
                    points_earned = 0
            else:  # team is away
                team_goals = match['away_score']
                opponent_goals = match['home_score']
                if team_goals > opponent_goals:
                    points_earned = 3
                elif team_goals == opponent_goals:
                    points_earned = 1
                else:
                    points_earned = 0

            cumulative_points += points_earned
            cumulative_goals_for += team_goals
            cumulative_goals_against += opponent_goals
            goal_difference = cumulative_goals_for - cumulative_goals_against

            points.append({
                'team': team,
                'date': match['date'],
                'points': cumulative_points,
                'matches_played': matches_played,
                'goals_for': cumulative_goals_for,
                'goals_against': cumulative_goals_against,
                'goal_difference': goal_difference
            })

        points_data.extend(points)

    return pd.DataFrame(points_data)

def calculate_league_positions(matches_df):
    """Calculate league positions for each team over time"""
    if matches_df.empty:
        return pd.DataFrame()

    # Get points data first
    points_df = calculate_cumulative_points(matches_df)

    # Calculate positions for each date
    all_dates = sorted(points_df['date'].unique())
    position_data = []

    for date in all_dates:
        # Get standings for this date
        date_standings = points_df[points_df['date'] == date].copy()

        # Create a list for manual sorting and position assignment
        teams = []
        for _, row in date_standings.iterrows():
            teams.append({
                'team': row['team'],
                'date': date,
                'points': row['points'],
                'goal_difference': row['goal_difference'],
                'goals_for': row['goals_for'],
                'matches_played': row['matches_played']
            })

        # Sort teams by points, goal difference, goals for
        teams.sort(key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for']))

        # Assign positions sequentially
        for position, team_data in enumerate(teams, 1):
            team_data['position'] = position
            position_data.append(team_data)

    return pd.DataFrame(position_data)

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
        "Barnsley": "#E41E26",
        "Blackpool": "#FF6634",
        "Bolton": "#012169",
        "Burton": "#FDE725",
        "Cambridge United": "#FFCD00",
        "Carlisle": "#0066B3",
        "Charlton": "#FF0000",
        "Cheltenham": "#FF0000",
        "Derby": "#000000",
        "Exeter": "#E31837",
        "Fleetwood": "#FF0000",
        "Lincoln": "#E31837",
        "Northampton": "#7B2C3A",
        "Oxford United": "#FFF200",
        "Peterborough": "#002E60",
        "Port Vale": "#0066B3",
        "Portsmouth": "#001489",
        "Reading": "#004494",
        "Shrewsbury": "#002F87",
        "Stevenage": "#FF0000",
        "Wigan": "#009EE0",
        "Wycombe": "#1C3C7D",
        "AFC Wimbledon": "#002A5C",
        "Accrington": "#A51D35",
        "Bradford": "#FF0000",
        "Colchester": "#00529F",
        "Crawley": "#FF0000",
        "Crewe": "#DD0000",
        "Doncaster": "#FF0000",
        "Forest Green": "#0F4D2B",
        "Gillingham": "#002F87",
        "Grimsby": "#1B1B1B",
        "Harrogate": "#FED204",
        "Leyton Orient": "#EE2737",
        "Mansfield": "#FDB913",
        "MK Dons": "#FF0000",
        "Morecambe": "#FF0000",
        "Newport": "#FDB913",
        "Notts County": "#000000",
        "Oldham": "#004494",
        "Salford": "#FF0000",
        "Stockport": "#004494",
        "Sutton": "#FDB913",
        "Swindon": "#FF0000",
        "Tranmere": "#004494",
        "Wrexham": "#FF0000"
    }