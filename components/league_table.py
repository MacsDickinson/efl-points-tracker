import streamlit as st
import base64
from utils.data_processor import get_team_colors

def format_form(form_string):
    """Format the form string with colored indicators"""
    if not form_string:
        return ""

    colors = {
        'W': '#4CAF50',  # Green
        'D': '#FFA726',  # Orange
        'L': '#EF5350',  # Red
    }

    form_html = ""
    for result in form_string:
        color = colors.get(result, '#808080')
        form_html += f'<span style="display: inline-block; text-align: center; width: 32px; color: {color};">{result}</span>'

    return form_html

def create_sparkline(matches, colour="currentColor", max_points=100, width=100, height=30):
    """Create a sparkline SVG from match points progression"""
    if not matches:
        return ""

    # Calculate points for each match
    points = [0]  # Start with 0 points
    current_points = 0
    for match in matches:
        if match['result'] == 'win':
            current_points += 3
        elif match['result'] == 'draw':
            current_points += 1
        points.append(current_points)

    # Calculate min and max for scaling
    min_points = 0
    point_range = max(1, max_points - min_points)  # Avoid division by zero

    # Create point coordinates
    x_step = width / (len(points) - 1) if len(points) > 1 else 0
    points_coords = []

    for i, point in enumerate(points):
        x = i * x_step
        # Scale y to fit height, inverting because SVG y=0 is top
        y = height - ((point - min_points) / point_range * height)
        points_coords.append(f"{x},{y}")

    # Create SVG path
    path = f"M{' L'.join(points_coords)}"

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="display: inline-block; vertical-align: middle;">
        <path 
            d="{path}" 
            stroke="{colour}" 
            stroke-width="2" 
            fill="none" 
            vector-effect="non-scaling-stroke"
        />
    </svg>
    """
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    return r'<img src="data:image/svg+xml;base64,%s"/>' % b64

def display_league_table(team_data):
    """Display league table with all statistics"""
    if not team_data:
        st.warning("No data available for the selected league and season.")
        return

    # Sort teams by points (considering deductions)
    sorted_teams = sorted(team_data,
                         key=lambda x: (x['position']),
                         reverse=False)

    # First, inject the CSS separately
    st.markdown("""
    <style>
    .league-table {
        font-family: monospace;
        font-size: 14px;
        width: 100%;
        border-collapse: collapse;
        background-color: var(--bg-color);
    }
    .league-table th, .league-table td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-color);
    }
    .league-table th {
        background-color: var(--secondary-bg);
        font-weight: bold;
        text-align: center;
        white-space: nowrap;
    }
    .league-table tr:hover {
        background-color: var(--hover-bg);
    }
    .pos-cell { width: 50px; text-align: center; }
    .team-cell { width: 250px; text-align: left; padding-left: 24px; }
    .num-cell { width: 70px; text-align: center; }
    .goals-cell { width: 100px; text-align: center; }
    .form-cell { width: 200px; text-align: center; letter-spacing: 6px; }
    .points-cell { width: 70px; text-align: center; font-weight: bold; }
    .trend-cell { width: 120px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    # Then build and inject the table HTML separately
    table_rows = []

    # Add header row
    header_row = """
        <tr>
            <th class="pos-cell">#</th>
            <th class="team-cell">Team</th>
            <th class="num-cell">P</th>
            <th class="num-cell">W</th>
            <th class="num-cell">D</th>
            <th class="num-cell">L</th>
            <th class="num-cell">DIFF</th>
            <th class="goals-cell">Goals</th>
            <th class="form-cell">Last 5</th>
            <th class="points-cell">PTS</th>
            <th class="trend-cell">Trend</th>
        </tr>
    """
    table_rows.append(header_row)

    # Add data rows
    max_points = max(team['total_points'] for team in sorted_teams) if sorted_teams else 0

    for team in sorted_teams:
        wins = sum(1 for m in team['matches'] if m['result'] == 'win')
        draws = sum(1 for m in team['matches'] if m['result'] == 'draw')
        losses = sum(1 for m in team['matches'] if m['result'] == 'loss')
        team_colour = get_team_colors().get(team['name'], '#808080')

        form_display = format_form(team['form']) if team['form'] else ""
        sparkline = create_sparkline(team['matches'],
                                   colour=team_colour,
                                   max_points=max_points)

        row = f"""
        <tr>
            <td class="pos-cell">{team['position']}</td>
            <td class="team-cell">{team['name']}</td>
            <td class="num-cell">{team['matches_played']}</td>
            <td class="num-cell">{wins}</td>
            <td class="num-cell">{draws}</td>
            <td class="num-cell">{losses}</td>
            <td class="num-cell">{team['goal_difference']:+d}</td>
            <td class="goals-cell">{team['goals_for']}:{team['goals_against']}</td>
            <td class="form-cell">{form_display}</td>
            <td class="points-cell">{team['total_points']}</td>
            <td class="trend-cell">{sparkline}</td>
        </tr>
        """
        table_rows.append(row)

    # Combine all rows into a single table
    table_html = f'<table class="league-table">{"".join(table_rows)}</table>'

    # Render the table
    st.markdown(table_html, unsafe_allow_html=True)