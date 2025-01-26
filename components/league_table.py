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
        form_html += f'<span style="display: inline-block; text-align: center; width: 24px; color: {color};">{result}</span>'

    return form_html

def display_league_table(team_data):
    """Display league table with all statistics"""
    if not team_data:
        st.warning("No data available for the selected league and season.")
        return

    # Sort teams by points (considering deductions)
    sorted_teams = sorted(
        team_data,
        key=lambda x: (
            x['total_points'],
            x['goal_difference'],
            x['goals_for']
        ),
        reverse=True
    )

    # Create the table header with proper alignment and widths
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
            padding: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .league-table th {
            background-color: rgba(255, 255, 255, 0.05);
            font-weight: bold;
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
        }
        .league-table tr:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }
        .pos-cell { width: 40px; text-align: center; }
        .team-cell { width: 200px; text-align: left; padding-left: 16px; }
        .num-cell { width: 60px; text-align: center; }
        .goals-cell { width: 80px; text-align: center; }
        .form-cell { width: 160px; text-align: center; letter-spacing: 4px; }
        .points-cell { width: 60px; text-align: center; font-weight: bold; }
        </style>
        <table class="league-table">
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
    """, unsafe_allow_html=True)

    # Add rows for each team
    for team in sorted_teams:
        # Calculate W/D/L from matches
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
        st.markdown(row, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)