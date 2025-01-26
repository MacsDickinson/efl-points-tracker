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
        form_html += f'<span style="color: {color}; margin: 0 2px;">{result}</span>'
    
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

    # Create the table header
    st.markdown("""
        <style>
        .league-table {
            font-size: 14px;
            width: 100%;
            border-collapse: collapse;
            background-color: rgb(17, 17, 17);
        }
        .league-table th, .league-table td {
            padding: 8px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .league-table th {
            background-color: rgba(255, 255, 255, 0.05);
            font-weight: bold;
            color: rgba(255, 255, 255, 0.9);
        }
        .league-table tr:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }
        .team-cell {
            text-align: left !important;
            white-space: nowrap;
        }
        .form-cell {
            letter-spacing: 2px;
        }
        </style>
        <table class="league-table">
        <tr>
            <th>#</th>
            <th class="team-cell">Team</th>
            <th>P</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>DIFF</th>
            <th>Goals</th>
            <th>Last 5</th>
            <th>PTS</th>
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
            <td>{team['position']}</td>
            <td class="team-cell">{team['name']}</td>
            <td>{team['matches_played']}</td>
            <td>{wins}</td>
            <td>{draws}</td>
            <td>{losses}</td>
            <td>{team['goal_difference']:+d}</td>
            <td>{team['goals_for']}:{team['goals_against']}</td>
            <td class="form-cell">{form_display}</td>
            <td>{team['total_points']}</td>
        </tr>
        """
        st.markdown(row, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)
