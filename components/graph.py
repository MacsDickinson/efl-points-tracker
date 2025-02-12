import plotly.graph_objects as go
import streamlit as st
from utils.data_processor import get_team_colors


def plot_cumulative_points(points_df):
    """Create an interactive line plot showing cumulative points over time"""
    if points_df.empty:
        st.warning(
            "No match data available for the selected league and season.")
        return go.Figure()

    # Create figure with sophisticated styling
    fig = go.Figure()

    # Sort teams by their final points (using last point for each team)
    final_points = points_df.groupby('team')['points'].last()
    final_points = final_points.sort_values(ascending=False)
    sorted_teams = final_points.index.tolist()

    # Add traces for each team
    for team in sorted_teams:
        team_data = points_df[points_df['team'] == team]
        team_colors_dict = get_team_colors().get(team, {
            'primary': '#808080',
            'secondary': '#404040'
        })

        # Create hover text that includes key stats
        hover_text = [
            f"<b>{team}</b><br>"
            f"Match {row['matches_played']}<br>"
            f"Points: {int(row['points'])}<br>"
            f"GD: {row['goal_difference']:+d}"
            for _, row in team_data.iterrows()
        ]

        fig.add_trace(
            go.Scatter(
                x=team_data['matches_played'],
                y=team_data['points'],
                name=team,
                mode='lines',
                line=dict(
                    color=team_colors_dict[
                        'primary'],  # Use primary color for lines
                    width=3,
                    shape='spline',
                    smoothing=0.8),
                hovertemplate="%{text}<extra></extra>",
                text=hover_text))

    # Enhanced layout with dark theme and forced y-axis range
    min_points = points_df['points'].min()
    max_points = points_df['points'].max()
    y_min = min(0, min_points - 2)
    y_max = max_points + 2

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
            dtick=1,
            range=[0, points_df['matches_played'].max()],
            titlefont=dict(
                color='rgba(200, 200, 200, 1.0)'),  # Lighter title text color
            tickcolor='rgba(200, 200, 200, 1.0)'  # Lighter tick color
        ),
        yaxis=dict(
            title="Points",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=12),
            range=[y_min, y_max],
            titlefont=dict(
                color='rgba(200, 200, 200, 1.0)'),  # Lighter title text color
            tickcolor='rgba(200, 200, 200, 1.0)'  # Lighter tick color
        ),
        hoverlabel=dict(
            bgcolor='rgba(17, 17, 17, 0.95)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            font=dict(size=12,
                      color='rgba(200, 200, 200, 1.0)')  # Lighter font color
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
                color='rgba(200, 200, 200, 1.0)')  # Lighter legend text color
        ),
        margin=dict(l=60, r=160, t=40, b=60))

    return fig
