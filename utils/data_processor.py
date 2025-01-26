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
        "Manchester": {"primary": "#DA291C", "secondary": "#FBE122"},
        "Newcastle": {"primary": "#241F20", "secondary": "#F1BE48"},
        "Nottingham Forest": {"primary": "#DD0000", "secondary": "#FFFFFF"},
        "Tottenham": {"primary": "#132257", "secondary": "#FFFFFF"},
        "West Ham": {"primary": "#7A263A", "secondary": "#1BB1E7"},
        "Wolves": {"primary": "#FDB913", "secondary": "#231F20"},

        # Championship Teams
        "Birmingham": {"primary": "#0000FF", "secondary": "#FFFFFF"},
        "Blackburn": {"primary": "#009EE0", "secondary": "#FFFFFF"},
        "Bristol City": {"primary": "#E21C38", "secondary": "#1C223A"},
        "Cardiff": {"primary": "#0070B5", "secondary": "#D61E49"},
        "Coventry": {"primary": "#78D0F3", "secondary": "#FFFFFF"},
        "Hull City": {"primary": "#F18A00", "secondary": "#000000"},
        "Ipswich": {"primary": "#0044A9", "secondary": "#FFFFFF"},
        "Leeds": {"primary": "#FFE100", "secondary": "#005FAA"},
        "Leicester": {"primary": "#003090", "secondary": "#FDBE11"},
        "Middlesbrough": {"primary": "#E21C38", "secondary": "#1C223A"},
        "Millwall": {"primary": "#001D5E", "secondary": "#FFFFFF"},
        "Norwich": {"primary": "#00A650", "secondary": "#FFF200"},
        "Plymouth": {"primary": "#007B5F", "secondary": "#000000"},
        "Preston": {"primary": "#B2B2B2", "secondary": "#FFFFFF"},
        "QPR": {"primary": "#005CAB", "secondary": "#FFFFFF"},
        "Rotherham": {"primary": "#DD1E3E", "secondary": "#FFFFFF"},
        "Sheffield Wednesday": {"primary": "#0066B3", "secondary": "#FFFFFF"},
        "Sheffield Utd": {"primary": "#EC2227", "secondary": "#010101"},
        "Southampton": {"primary": "#D71920", "secondary": "#130C0E"},
        "Stoke City": {"primary": "#E03A3E", "secondary": "#FFFFFF"},
        "Sunderland": {"primary": "#FF0000", "secondary": "#FFFFFF"},
        "Swansea": {"primary": "#FFFFFF", "secondary": "#121212"},
        "Watford": {"primary": "#FBEE23", "secondary": "#ED2127"},
        "West Brom": {"primary": "#122F67", "secondary": "#FFFFFF"},

        
        "Sunderland": {"primary": "#EB172C", "secondary": "#FFFFFF"},
        "Bristol Rovers": {"primary": "#0000FF", "secondary": "#FFFFFF"},
        "Fleetwood Town": {"primary": "#FF0000", "secondary": "#FFFFFF"},
        "Burton Albion": {"primary": "#FFFF00", "secondary": "#000000"},
        "Northampton": {"primary": "#7F1734", "secondary": "#FFF200"},
        "AFC Wimbledon": {"primary": "#0033A0", "secondary": "#FDB930"},
        "Gillingham": {"primary": "#094D8D", "secondary": "#FFFFFF"},
        "Swindon Town": {"primary": "#BA1F2A", "secondary": "#FFD700"},
        "Rochdale": {"primary": "#0033A0", "secondary": "#FFFFFF"},
        "Doncaster": {"primary": "#C8102E", "secondary": "#FFFFFF"},
        "Portsmouth": {"primary": "#003087", "secondary": "#FFFFFF"},
        "Shrewsbury": {"primary": "#FED102", "secondary": "#1E1E1E"},
        "Plymouth": {"primary": "#003F4D", "secondary": "#00A040"},
        "Blackpool": {"primary": "#FF5E00", "secondary": "#FFFFFF"},
        "Accrington ST": {"primary": "#F5191C", "secondary": "#FFFFFF"},
        "Peterborough": {"primary": "#005BAC", "secondary": "#FFFFFF"},
        "Crewe": {"primary": "#BB2527", "secondary": "#FFD700"},
        "Charlton": {"primary": "#A6192E", "secondary": "#FFFFFF"},
        "Wigan": {"primary": "#005CA8", "secondary": "#FFFFFF"},
        "Barnsley": {"primary": "#EE3224", "secondary": "#FFFFFF"},
        "Huddersfield": {"primary": "#0076BE", "secondary": "#FFFFFF"},
        "Reading": {"primary": "#000066", "secondary": "#FFFFFF"},
        "Rotherham": {"primary": "#E4062E", "secondary": "#FFFFFF"},
        "Wycombe": {"primary": "#1B365D", "secondary": "#FFFFFF"},
        "Leyton Orient": {"primary": "#E41C2D", "secondary": "#000000"},
        "Cheltenham": {"primary": "#9C1F2E", "secondary": "#ededed"},
        "Cambridge United": {"primary": "#FFCC00", "secondary": "#333333"},


        "Internacional": {"primary": "#940F24", "secondary": "#FFFFFF"},
        "Criciuma": {"primary": "#FFD700", "secondary": "#000000"},
        "Fluminense": {"primary": "#9C1C34", "secondary": "#00591C"},
        "Sao Paulo": {"primary": "#C00000", "secondary": "#000000"},
        "Atletico Paranaense": {"primary": "#DD0031", "secondary": "#000000"},
        "Atletico Goianiense": {"primary": "#CC0000", "secondary": "#000000"},
        "Cruzeiro": {"primary": "#003DA5", "secondary": "#FFFFFF"},
        "Vitoria": {"primary": "#D30613", "secondary": "#F2E623"},
        "Bahia": {"primary": "#003DA5", "secondary": "#D6001C"},
        "Gremio": {"primary": "#1C2F60", "secondary": "#80C7EE"},
        "RB Bragantino": {"primary": "#FFFFFF", "secondary": "#000000"},
        "Palmeiras": {"primary": "#1E5147", "secondary": "#CBE000"},
        "Juventude": {"primary": "#008C5F", "secondary": "#FFFFFF"},
        "Fortaleza EC": {"primary": "#0068AC", "secondary": "#DB1E36"},
        "Atletico-MG": {"primary": "#1C1C1C", "secondary": "#FFFFFF"},
        "Flamengo": {"primary": "#DD0031", "secondary": "#000000"},
        "Botafogo": {"primary": "#1C1C1C", "secondary": "#FFFFFF"},
        "Cuiaba": {"primary": "#00843D", "secondary": "#F3D003"},
        "America Mineiro": {"primary": "#006847", "secondary": "#FFFFFF"},
        "Santos": {"primary": "#2B2A29", "secondary": "#FFFFFF"},
        "Coritiba": {"primary": "#007A33", "secondary": "#000000"},
        "Goias": {"primary": "#009A44", "secondary": "#FFFFFF"},
        
        "LE Havre": {"primary": "#15317E", "secondary": "#FFFFFF"},
        "Stade Brestois 29": {"primary": "#FF0000", "secondary": "#FFFFFF"},
        "Reims": {"primary": "#F71A1A", "secondary": "#FFFFFF"},
        "Monaco": {"primary": "#D3151C", "secondary": "#FFFFFF"},
        "Auxerre": {"primary": "#005BAC", "secondary": "#FFFFFF"},
        "Montpellier": {"primary": "#004D98", "secondary": "#F46B22"},
        "Toulouse": {"primary": "#9B1C31", "secondary": "#FFFFFF"},
        "Rennes": {"primary": "#ED1C24", "secondary": "#000000"},
        "Paris Saint Germain": {"primary": "#004170", "secondary": "#DA0A2A"},
        "Lyon": {"primary": "#122F67", "secondary": "#DA291C"},
        "Lille": {"primary": "#D20000", "secondary": "#005BAC"},
        "Saint Etienne": {"primary": "#14B04B", "secondary": "#FFFFFF"},
        "Lens": {"primary": "#F1D102", "secondary": "#D70A10"},
        "Nantes": {"primary": "#FFCC00", "secondary": "#007540"},
        "Nice": {"primary": "#EE1C25", "secondary": "#000000"},
        "Strasbourg": {"primary": "#005BAC", "secondary": "#FFFFFF"},
        "Marseille": {"primary": "#00A9E6", "secondary": "#FFFFFF"},
        "Clermont Foot": {"primary": "#8B1D2D", "secondary": "#1D2E4A"},
        "Metz": {"primary": "#862633", "secondary": "#FFFFFF"},
        "Lorient": {"primary": "#E65F0F", "secondary": "#000000"},
        "Avai": {"primary": "#0066A2", "secondary": "#FFFFFF"},
        "Ajaccio": {"primary": "#ED1C24", "secondary": "#FFFFFF"},
        "Estac Troyes": {"primary": "#007DC5", "secondary": "#FFFFFF"},
        "Eintracht Frankfurt": {"primary": "#DD1D2F", "secondary": "#FFFFFF"},
        "VfL Wolfsburg": {"primary": "#65B32E", "secondary": "#FFFFFF"},
        "Borussia Monchengladbach": {"primary": "#FFFFFF", "secondary": "#000000"},
        "FC Augsburg": {"primary": "#BA3733", "secondary": "#FFFFFF"},
        "Vfl Bochum": {"primary": "#1C63B9", "secondary": "#FFFFFF"},
        "Union Berlin": {"primary": "#EE2E24", "secondary": "#FFFFFF"},
        "Borussia Dortmund": {"primary": "#FFCC00", "secondary": "#000000"},
        "VfB Stuttgart": {"primary": "#EE1C25", "secondary": "#FFFFFF"},
        "1.FC Köln": {"primary": "#EC1C24", "secondary": "#FFFFFF"},
        "SC Freiburg": {"primary": "#E30613", "secondary": "#FFFFFF"},
        "Hertha Berlin": {"primary": "#004C9B", "secondary": "#FFFFFF"},
        "Werder Bremen": {"primary": "#2F7466", "secondary": "#FFFFFF"},
        "1899 Hoffenheim": {"primary": "#005CA9", "secondary": "#FFFFFF"},
        "Bayer Leverkusen": {"primary": "#E32238", "secondary": "#FFFFFF"},
        "RB Leipzig": {"primary": "#DD1E2F", "secondary": "#FFFFFF"},
        "FC Schalke 04": {"primary": "#0671B7", "secondary": "#FFFFFF"},
        "FSV Mainz 05": {"primary": "#C8173C", "secondary": "#FFFFFF"},
        "Bayern Munich": {"primary": "#DD1A32", "secondary": "#FFFFFF"},
        "Hamburger SV": {"primary": "#0A0A0A", "secondary": "#FFFFFF"},
        "FC Heidenheim": {"primary": "#D21626", "secondary": "#002147"},
        "SV Darmstadt 98": {"primary": "#0E3E94", "secondary": "#FFFFFF"},
        "Fortuna Dusseldorf": {"primary": "#EF5050", "secondary": "#FFFFFF"},
        "FC St. Pauli": {"primary": "#4C1E1E", "secondary": "#FFFFFF"},
        "Holstein Kiel": {"primary": "#2C2865", "secondary": "#EB1C24"},
    }