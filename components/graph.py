import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.data_processor import get_team_colors

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

    # Add traces for each team
    for team in points_df['team'].unique():
        team_data = points_df[points_df['team'] == team].sort_values('date')
        team_color = get_team_colors().get(team, '#ffffff')

        fig.add_trace(
            go.Scatter(
                x=team_data['date'],
                y=team_data['points'],
                name=team,
                mode='lines',
                line=dict(
                    color=team_color,
                    width=3,
                    shape='spline',  # Curved lines
                    smoothing=0.8
                ),
                fill='tonexty',  # Add gradient fill
                fillcolor=f'rgba{tuple(int(team_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}',
                hovertemplate="<b>%{text}</b><br>" +
                            "Date: %{x}<br>" +
                            "Points: %{y}<extra></extra>",
                text=[team] * len(team_data)
            )
        )

    # Enhanced layout with dark theme
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(17, 17, 17, 0.9)',
        paper_bgcolor='rgba(17, 17, 17, 0.9)',
        xaxis=dict(
            title="Match Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=12)
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
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(17, 17, 17, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1,
            font=dict(size=12)
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