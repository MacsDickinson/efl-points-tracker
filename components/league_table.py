import streamlit as st


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


def display_league_table(team_data):
    """Display league table with all statistics"""
    if not team_data:
        st.warning("No data available for the selected league and season.")
        return

    # Sort teams by points (considering deductions)
    sorted_teams = sorted(
        team_data,
        key=lambda x:
        (x['total_points'], x['goal_difference'], x['goals_for']),
        reverse=True)

    # First, inject the CSS separately
    st.markdown("""
    <style>
    .league-table {
        font-family: monospace;
        font-size: 14px;
        width: 100%;
        border-collapse: collapse;
        background-color: rgb(17, 17, 17);
    }
    .league-table th, .league-table td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .league-table th {
        background-color: rgba(17, 17, 17, 0.9);
        font-weight: bold;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        white-space: nowrap;
    }
    .league-table tr:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    .pos-cell { width: 50px; text-align: center; }
    .team-cell { width: 250px; text-align: left; padding-left: 24px; }
    .num-cell { width: 70px; text-align: center; }
    .goals-cell { width: 100px; text-align: center; }
    .form-cell { width: 200px; text-align: center; letter-spacing: 6px; }
    .points-cell { width: 70px; text-align: center; font-weight: bold; }
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
        </tr>
    """
    table_rows.append(header_row)

    # Add data rows
    for team in sorted_teams:
        wins = sum(1 for m in team['matches'] if m['result'] == 'win')
        draws = sum(1 for m in team['matches'] if m['result'] == 'draw')
        losses = sum(1 for m in team['matches'] if m['result'] == 'loss')

        form_display = format_form(team['form']) if team['form'] else ""

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
        </tr>
        """
        table_rows.append(row)

    # Combine all rows into a single table
    table_html = f'<table class="league-table">{"".join(table_rows)}</table>'

    # Render the table
    st.markdown(table_html, unsafe_allow_html=True)