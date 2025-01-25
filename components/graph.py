import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.data_processor import get_team_colors

def plot_cumulative_points(points_df):
    """Create an interactive line plot showing cumulative points over time"""
    # Create figure with more sophisticated styling
    fig = px.line(
        points_df,
        x='date',
        y='points',
        color='team',
        color_discrete_map=get_team_colors(),
        title='',  # We'll use streamlit's title instead
    )

    # Enhanced layout
    fig.update_layout(
        xaxis=dict(
            title="Match Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211, 211, 211, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(0,0,0,0.2)',
        ),
        yaxis=dict(
            title="Points",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211, 211, 211, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(0,0,0,0.2)',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(0,0,0,0.2)',
        ),
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="rgb(50, 50, 50)"
        ),
        margin=dict(l=60, r=160, t=40, b=60),
        showlegend=True,
    )

    # Enhanced traces
    fig.update_traces(
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{customdata}</b><br>" +
                     "Date: %{x}<br>" +
                     "Points: %{y}<extra></extra>"
    )

    # Add custom hover data
    fig.update_traces(customdata=points_df['team'])

    return fig

def display_team_stats(points_df):
    """Display key statistics for each team"""
    latest_points = points_df.groupby('team')['points'].last().sort_values(ascending=False)
    team_colors = get_team_colors()

    st.subheader("📊 Current Standings")

    # Create three columns for better spacing
    cols = st.columns(3)
    for i, (team, points) in enumerate(latest_points.items()):
        col_idx = i % 3
        with cols[col_idx]:
            st.markdown(
                f"""<div style='
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border: 1px solid {team_colors.get(team, '#000000')}30;
                    margin: 0.5rem 0;
                    background-color: white;
                    '>
                    <h3 style='
                        color: {team_colors.get(team, '#000000')};
                        margin: 0;
                        font-size: 1.1rem;
                        '>{team}</h3>
                    <p style='
                        font-size: 1.5rem;
                        font-weight: bold;
                        margin: 0.5rem 0 0 0;
                        '>{int(points)} pts</p>
                    </div>""",
                unsafe_allow_html=True
            )