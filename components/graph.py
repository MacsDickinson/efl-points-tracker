import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.data_processor import get_team_colors
import pandas as pd

def plot_cumulative_points(points_df):
    """Create an interactive line plot showing cumulative points over time"""
    if points_df.empty:
        st.warning("No match data available for the selected league and season.")
        # Return an empty figure
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Date",
            yaxis_title="Points",
            template="plotly_dark"
        )
        return fig

    # Create figure with sophisticated styling
    fig = go.Figure()

    # Prepare hover data for each match number
    max_matches = points_df['matches_played'].max()
    hover_data = {}

    # Create hover data dictionary for each match number
    for match in range(1, max_matches + 1):
        match_data = points_df[points_df['matches_played'] == match]
        if not match_data.empty:
            teams_points = match_data[['team', 'points']].values.tolist()
            # Sort by points in descending order
            teams_points.sort(key=lambda x: x[1], reverse=True)
            # Format as "position. team - points"
            hover_data[match] = "<br>".join([f"{pos+1}. {team} - {int(points)}" 
                                             for pos, (team, points) in enumerate(teams_points)])

    # Sort teams by their final points
    final_points = points_df.groupby('team')['points'].last().sort_values(ascending=False)
    sorted_teams = final_points.index.tolist()

    # Add traces for each team in order of final points
    for team in sorted_teams:
        team_data = points_df[points_df['team'] == team].sort_values('matches_played')
        team_color = get_team_colors().get(team, '#808080')  # Default to gray if no color defined

        # Create hover text list
        hover_text = [hover_data.get(match, "") for match in team_data['matches_played']]

        fig.add_trace(
            go.Scatter(
                x=team_data['matches_played'],
                y=team_data['points'],
                name=team,
                mode='lines',
                line=dict(
                    color=team_color,
                    width=3,
                    shape='spline',  # Curved lines
                    smoothing=0.8
                ),
                hovertemplate="<b>Gameweek %{x}</b><br><br>%{text}<extra></extra>",
                text=hover_text
            )
        )

    # Enhanced layout with dark theme
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(17, 17, 17, 0.9)',
        paper_bgcolor='rgba(17, 17, 17, 0.9)',
        xaxis=dict(
            title="Matches Played",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=12),
            dtick=1  # Show every match number
        ),
        yaxis=dict(
            title="Points",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=12)
        ),
        hoverdistance=100,  # Reduce hover "catch" distance
        hovermode='closest',  # Change to closest instead of unified
        hoverlabel=dict(
            bgcolor='rgba(17, 17, 17, 0.95)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            font=dict(size=12, family="Arial, sans-serif")
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(17, 17, 17, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1,
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="rgba(255, 255, 255, 0.9)"  # Set legend text color to white
            )
        ),
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="rgba(255, 255, 255, 0.9)"
        ),
        margin=dict(l=60, r=160, t=40, b=60),
        showlegend=True,
    )

    return fig

def plot_league_positions(positions_df):
    """Create an interactive line plot showing league positions over time"""
    if positions_df.empty:
        st.warning("No match data available for the selected league and season.")
        # Return an empty figure
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Matches Played",
            yaxis_title="League Position",
            template="plotly_dark"
        )
        return fig

    # Create figure
    fig = go.Figure()

    # Prepare hover data for each match number
    max_matches = positions_df['matches_played'].max()
    hover_data = {}

    # Create hover data dictionary for each match number
    for match in range(1, max_matches + 1):
        match_data = positions_df[positions_df['matches_played'] == match]
        if not match_data.empty:
            teams_info = match_data[['team', 'position', 'points', 'goal_difference', 'goals_for']].values.tolist()
            # Sort by position (ascending, since 1 is best)
            teams_info.sort(key=lambda x: x[1])
            # Format hover text with detailed stats
            hover_data[match] = "<br>".join([
                f"{pos}. {team} ({pts}pts, GD:{gd:+d}, GF:{gf})" 
                for team, pos, pts, gd, gf in teams_info
            ])

    # Sort teams by their final positions (ascending)
    final_positions = positions_df.groupby('team')['position'].last().sort_values()
    sorted_teams = final_positions.index.tolist()

    # Add traces for each team
    for team in sorted_teams:
        team_data = positions_df[positions_df['team'] == team].sort_values('matches_played')
        team_color = get_team_colors().get(team, '#808080')

        # Create hover text list
        hover_text = [hover_data.get(match, "") for match in team_data['matches_played']]

        fig.add_trace(
            go.Scatter(
                x=team_data['matches_played'],
                y=team_data['position'],
                name=team,
                mode='lines',
                line=dict(
                    color=team_color,
                    width=3,
                    shape='spline',
                    smoothing=0.8
                ),
                hovertemplate="<b>Gameweek %{x}</b><br><br>%{text}<extra></extra>",
                text=hover_text
            )
        )

    # Enhanced layout with dark theme
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(17, 17, 17, 0.9)',
        paper_bgcolor='rgba(17, 17, 17, 0.9)',
        xaxis=dict(
            title="Matches Played",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=12),
            dtick=1
        ),
        yaxis=dict(
            title="League Position",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=12),
            autorange="reversed",  # Reverse y-axis so position 1 is at the top
            tickmode="linear",
            dtick=1
        ),
        hoverdistance=100,
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='rgba(17, 17, 17, 0.95)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            font=dict(size=12, family="Arial, sans-serif")
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(17, 17, 17, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        ),
        margin=dict(l=60, r=160, t=40, b=60),
        showlegend=True
    )

    return fig

def display_team_stats(points_df):
    """Display key statistics for each team"""
    if points_df.empty:
        return

    latest_points = points_df.groupby('team')['points'].last().sort_values(ascending=False)
    team_colors = get_team_colors()

    st.markdown("""
        <style>
        .team-stats-container {
            background-color: rgba(17, 17, 17, 0.9);
            padding: 1.5rem;
            border-radius: 1rem;
            margin-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="team-stats-container">', unsafe_allow_html=True)
    st.subheader("📊 Current Standings")

    # Create three columns for better spacing
    cols = st.columns(3)
    for i, (team, points) in enumerate(latest_points.items()):
        col_idx = i % 3
        with cols[col_idx]:
            st.markdown(
                f"""<div style='
                    padding: 1.5rem;
                    border-radius: 1rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    margin: 0.5rem 0;
                    background-color: rgba(17, 17, 17, 0.8);
                    backdrop-filter: blur(10px);
                    '>
                    <h3 style='
                        color: {team_colors.get(team, '#ffffff')};
                        margin: 0;
                        font-size: 1.1rem;
                        '>{team}</h3>
                    <p style='
                        color: rgba(255, 255, 255, 0.9);
                        font-size: 1.5rem;
                        font-weight: bold;
                        margin: 0.5rem 0 0 0;
                        '>{int(points)} pts</p>
                    </div>""",
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)