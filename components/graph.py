import plotly.graph_objects as go
import streamlit as st
from utils.data_processor import get_team_colors

def plot_cumulative_points(points_df):
    """Create an interactive line plot showing cumulative points over time"""
    if points_df.empty:
        st.warning("No match data available for the selected league and season.")
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
        team_colors_dict = get_team_colors().get(team, {'primary': '#808080', 'secondary': '#404040'})

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
                    color=team_colors_dict['primary'],  # Use primary color for lines
                    width=3,
                    shape='spline',
                    smoothing=0.8
                ),
                hovertemplate="%{text}<extra></extra>",
                text=hover_text
            )
        )

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
            range=[0, points_df['matches_played'].max()]
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
            range=[y_min, y_max]
        ),
        hoverlabel=dict(
            bgcolor='rgba(17, 17, 17, 0.95)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            font=dict(size=12)
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
        margin=dict(l=60, r=160, t=40, b=60)
    )

    return fig

def display_team_stats(points_df):
    """Display key statistics for each team"""
    if points_df.empty:
        return

    # Get final standings for each team efficiently
    final_data = points_df.groupby('team').last().reset_index()
    final_standings = final_data.sort_values(
        ['points', 'goal_difference', 'goals_for'],
        ascending=[False, False, False]
    )

    team_colors = get_team_colors()

    # Create columns for layout
    cols = st.columns(3)

    for i, row in final_standings.iterrows():
        col_idx = i % 3
        with cols[col_idx]:
            team_color = team_colors.get(row['team'], {'primary': '#ffffff'})['primary']
            st.markdown(
                f"""<div style='
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    margin: 0.5rem 0;
                    background-color: rgba(17, 17, 17, 0.8);
                    '>
                    <h3 style='
                        color: {team_color};
                        margin: 0;
                        font-size: 1.1rem;
                        '>{row['team']}</h3>
                    <p style='
                        color: rgba(255, 255, 255, 0.9);
                        font-size: 1.5rem;
                        font-weight: bold;
                        margin: 0.5rem 0 0 0;
                        '>{int(row['points'])} pts</p>
                    <p style='
                        color: rgba(255, 255, 255, 0.7);
                        font-size: 0.9rem;
                        margin: 0.2rem 0 0 0;
                        '>GD: {row['goal_difference']:+d} | GF: {row['goals_for']}</p>
                    </div>""",
                unsafe_allow_html=True
            )