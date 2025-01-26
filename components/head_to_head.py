import streamlit as st
import pandas as pd

def display_head_to_head(team_data):
    """Display head-to-head comparison between two selected teams"""
    if not team_data:
        st.warning("No data available for comparison.")
        return
    
    # Get sorted list of teams
    teams = sorted([team['name'] for team in team_data])
    
    # Create two columns for team selection
    col1, spacer, col2 = st.columns([2, 1, 2])
    
    with col1:
        team1 = st.selectbox("Select First Team", teams, key="team1_select")
    
    with spacer:
        st.markdown("<div style='text-align: center; padding-top: 30px;'>VS</div>", unsafe_allow_html=True)
    
    with col2:
        # Filter out first team from second selection
        available_teams = [team for team in teams if team != team1]
        team2 = st.selectbox("Select Second Team", available_teams, key="team2_select")
    
    # Get team data
    team1_data = next((team for team in team_data if team['name'] == team1), None)
    team2_data = next((team for team in team_data if team['name'] == team2), None)
    
    if team1_data and team2_data:
        # Create metrics comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Points", 
                     value=team1_data['total_points'],
                     delta=team1_data['total_points'] - team2_data['total_points'])
        
        with col2:
            st.metric(label="Goal Difference",
                     value=team1_data['goal_difference'],
                     delta=team1_data['goal_difference'] - team2_data['goal_difference'])
        
        with col3:
            st.metric(label="Position",
                     value=team1_data['position'],
                     delta=team2_data['position'] - team1_data['position'])
        
        # Find head-to-head matches
        h2h_matches = []
        for match in team1_data['matches']:
            if match['home_team'] == team2 or match['away_team'] == team2:
                h2h_matches.append(match)
        
        if h2h_matches:
            st.markdown("### Head-to-Head Matches")
            for match in h2h_matches:
                with st.container():
                    col1, col2, col3 = st.columns([2,1,2])
                    home_team = match['home_team']
                    away_team = match['away_team']
                    
                    with col1:
                        st.write(f"{home_team}")
                    with col2:
                        st.write(f"{match['home_score']} - {match['away_score']}")
                    with col3:
                        st.write(f"{away_team}")
                    
                    st.markdown(f"*{match['date'].strftime('%d %B %Y')}*")
                    st.divider()
        else:
            st.info("No direct matches found between these teams.")