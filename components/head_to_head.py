import streamlit as st

from utils.api import fetch_head_to_head_from_api


def display_head_to_head(team_data):
    """Display head-to-head comparison between two selected teams"""
    if not team_data:
        st.warning("No data available for comparison.")
        return

    # Get sorted list of teams
    team_options = [(team['name'], team['id']) for team in team_data]

    # Create two columns for team selection
    col1, spacer, col2 = st.columns([2, 1, 2])

    with col1:
        selected_team1 = st.selectbox("Select First Team",
                                      team_options,
                                      format_func=lambda option: option[0],
                                      key="team1_select")
        team1_name, team1_id = selected_team1

    with spacer:
        st.markdown(
            "<div style='text-align: center; padding-top: 30px;'>VS</div>",
            unsafe_allow_html=True)

    with col2:
        # Filter out first team from second selection
        available_teams = [
            team for team in team_options if team[1] != team1_id
        ]
        selected_team2 = st.selectbox("Select Second Team",
                                      available_teams,
                                      format_func=lambda option: option[0],
                                      key="team2_select")
        team2_name, team2_id = selected_team2

    # Get team data
    team1_data = next((team for team in team_data if team['id'] == team1_id),
                      None)
    team2_data = next((team for team in team_data if team['id'] == team2_id),
                      None)

    if team1_data and team2_data:
        # Create metrics comparison side by side
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(team1_name)
            st.metric(label="Points",
                      value=team1_data['total_points'],
                      delta=team1_data['total_points'] -
                      team2_data['total_points'],
                      delta_color="normal")
            st.metric(label="Goal Difference",
                      value=team1_data['goal_difference'],
                      delta=team1_data['goal_difference'] -
                      team2_data['goal_difference'],
                      delta_color="normal")
            st.metric(label="Position",
                      value=team1_data['position'],
                      delta=team2_data['position'] - team1_data['position'],
                      delta_color="normal")

        with col2:
            st.subheader(team2_name)
            st.metric(label="Points",
                      value=team2_data['total_points'],
                      delta=team2_data['total_points'] -
                      team1_data['total_points'],
                      delta_color="normal")
            st.metric(label="Goal Difference",
                      value=team2_data['goal_difference'],
                      delta=team2_data['goal_difference'] -
                      team1_data['goal_difference'],
                      delta_color="normal")
            st.metric(label="Position",
                      value=team2_data['position'],
                      delta=team1_data['position'] - team2_data['position'],
                      delta_color="normal")

        # Query all matches between the two teams

        h2h_matches = fetch_head_to_head_from_api(team1_data, team2_data)

        if h2h_matches:
            st.markdown("### Head-to-Head Matches")
            for match in h2h_matches:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 2])

                    with col1:
                        st.markdown(f"*{match['date'].strftime('%d %B %Y')}*")
                    with col2:
                        st.write(f"{match['home_team']}")
                    with col3:
                        st.write(
                            f"{match['home_score']} - {match['away_score']}")
                    with col4:
                        st.write(f"{match['away_team']}")
        else:
            st.info("No direct matches found between these teams.")
