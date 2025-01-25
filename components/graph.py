import plotly.express as px
import streamlit as st
from utils.data_processor import get_team_colors

def plot_cumulative_points(points_df):
    """Create an interactive line plot showing cumulative points over time"""
    fig = px.line(
        points_df,
        x='date',
        y='points',
        color='team',
        color_discrete_map=get_team_colors(),
        title='Cumulative Points Over Time',
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Points",
        hovermode='x unified',
        legend_title="Teams",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
    )
    
    fig.update_traces(
        mode='lines+markers',
        hovertemplate='Points: %{y}<br>Date: %{x}<extra></extra>'
    )
    
    return fig

def display_team_stats(points_df):
    """Display key statistics for each team"""
    latest_points = points_df.groupby('team')['points'].last().sort_values(ascending=False)
    
    st.subheader("Current Standings")
    
    cols = st.columns(2)
    for i, (team, points) in enumerate(latest_points.items()):
        col_idx = i % 2
        with cols[col_idx]:
            st.metric(
                label=team,
                value=f"{points} pts"
            )
