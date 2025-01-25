import streamlit as st
from utils.api import get_league_matches
from utils.data_processor import calculate_cumulative_points
from components.graph import plot_cumulative_points, display_team_stats
from components.sidebar import create_sidebar

st.set_page_config(
    page_title="Football League Dashboard",
    page_icon="⚽",
    layout="wide"
)

def main():
    # Setup sidebar and get selected options
    selected_league, selected_season = create_sidebar()
    
    # Main content
    st.title("Football League Points Progression")
    
    # Fetch and process data
    with st.spinner("Loading match data..."):
        matches_df = get_league_matches(selected_league, selected_season)
        points_df = calculate_cumulative_points(matches_df)
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Points Progression", "Team Statistics"])
    
    with tab1:
        # Plot cumulative points
        fig = plot_cumulative_points(points_df)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("How to use this graph"):
            st.markdown("""
            - **Hover** over lines to see exact points
            - **Click** team names in legend to show/hide
            - **Double click** team names to isolate
            - **Drag** to zoom, double click to reset
            """)
    
    with tab2:
        # Display team statistics
        display_team_stats(points_df)

if __name__ == "__main__":
    main()
