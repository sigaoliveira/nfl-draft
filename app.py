import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_draft_data, load_draft_values, define_hit, get_position_groups, load_consensus_data

# Page configuration
st.set_page_config(page_title="NFL Draft Analysis", layout="wide", page_icon="🏈")

st.title("🏈 NFL Draft Analysis Dashboard")
st.markdown("---")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Metrics Explorer", "Hit/Bust Analysis", "Pick #1 & HOF Deep Dive", "Player Comparison", "2026 Consensus Alignment"])

# Load data
with st.spinner("Loading draft data..."):
    df = load_draft_data()
    df = get_position_groups(df)

st.sidebar.markdown("---")
st.sidebar.header("Global Filters")
min_year, max_year = int(df['season'].min()), int(df['season'].max())
selected_years = st.sidebar.slider("Select Draft Years", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Apply global filter
df = df[(df['season'] >= selected_years[0]) & (df['season'] <= selected_years[1])]

# Home Page
if page == "Home":
    st.header("Welcome to the NFL Draft Analysis Tool")
    st.write("This tool helps analyze historical draft data, player value (wAV), and team success rates.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Picks Analyzed", len(df))
    col2.metric("Seasons Covered", f"{df['season'].min()} - {df['season'].max()}")
    col3.metric("Total Hall of Famers", df['hof'].eq(True).sum())

    st.subheader("Picks by Position Group")
    fig = px.pie(df, names='pos_group', title="Distribution of Picks by Position Group")
    st.plotly_chart(fig, use_container_width=True)

# Metrics Explorer
elif page == "Metrics Explorer":
    st.header("wAV & DrAV Analysis")
    st.write("Explore Weighted Approximate Value (wAV) and Value for the Drafting Team (DrAV).")
    
    col_pos, col_team = st.columns(2)
    with col_pos:
        pos_filter = st.multiselect("Select Positions", options=sorted(df['position'].unique()), default=['QB', 'WR', 'RB', 'DE'])
    with col_team:
        team_filter = st.multiselect("Select Teams (Leave empty for all)", options=sorted(df['team'].dropna().unique()), default=[])
    
    filtered_df = df[df['position'].isin(pos_filter)].copy()
    if team_filter:
        filtered_df = filtered_df[filtered_df['team'].isin(team_filter)]
    filtered_df['w_av'] = filtered_df['w_av'].astype(float)
    filtered_df['dr_av'] = filtered_df['dr_av'].astype(float)
    
    st.subheader("wAV vs Pick Number")
    fig = px.scatter(filtered_df, x='pick', y='w_av', color='position', 
                     hover_data=['pfr_player_name', 'season', 'team'],
                     title="Weighted AV by Draft Pick",
                     labels={'w_av': 'Weighted AV', 'pick': 'Draft Pick #'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Organization Success: DrAV vs wAV")
    st.write("A higher DrAV relative to wAV means the player stayed and succeeded with the team that drafted them.")
    filtered_df['success_ratio'] = filtered_df['dr_av'] / filtered_df['w_av'].replace(0, 1)
    
    fig2 = px.box(filtered_df, x='position', y='success_ratio', points="all",
                  title="Drafting Team Success Ratio (DrAV / wAV)")
    st.plotly_chart(fig2, use_container_width=True)

# Hit/Bust Analysis
elif page == "Hit/Bust Analysis":
    st.header("Hit vs. Bust Analysis")
    
    with st.expander("Configure 'Hit' Criteria"):
        seasons = st.slider("Minimum Seasons as Starter", 0, 15, 4)
        probowls = st.slider("Minimum Pro Bowls", 0, 10, 1)
    
    team_filter_hb = st.multiselect("Select Teams (Leave empty for all)", options=sorted(df['team'].dropna().unique()), default=[])
    df_hit = define_hit(df.copy(), seasons_started=seasons, probowls=probowls)
    
    if team_filter_hb:
        df_hit = df_hit[df_hit['team'].isin(team_filter_hb)]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hit Rate by Round")
        hit_rate = df_hit.groupby('round')['is_hit'].mean().reset_index()
        hit_rate['is_hit'] *= 100
        fig = px.bar(hit_rate, x='round', y='is_hit', title="Hit Rate (%) by Draft Round",
                     labels={'is_hit': 'Hit %', 'round': 'Draft Round'})
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Hit Rate by Team")
        team_hit_rate = df_hit.groupby('team').agg(
            hits=('is_hit', 'sum'),
            total=('is_hit', 'count'),
            hit_rate=('is_hit', 'mean')
        ).reset_index()
        team_hit_rate['hit_rate'] *= 100
        # Filter out teams with too few picks if we aren't filtering specific teams
        if not team_filter_hb:
            team_hit_rate = team_hit_rate[team_hit_rate['total'] >= 20]
        
        team_hit_rate = team_hit_rate.sort_values('hit_rate', ascending=False)
        fig_team = px.bar(team_hit_rate.head(15), x='team', y='hit_rate', 
                          title="Top Teams by Hit Rate (%)",
                          labels={'hit_rate': 'Hit %', 'team': 'Team'})
        st.plotly_chart(fig_team, use_container_width=True)

# Pick #1 & HOF Deep Dive
elif page == "Pick #1 & HOF Deep Dive":
    st.header("Hall of Fame & Pick #1 Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Where do HOFers come from?")
        hof_df = df[df['hof'] == True]
        fig_hof = px.histogram(hof_df, x='round', title="HOFers by Round")
        st.plotly_chart(fig_hof)
        
    with col2:
        st.subheader("Pick #1 Success")
        p1_df = df[df['pick'] == 1].copy()
        fig_p1 = px.scatter(p1_df, x='season', y='w_av', color='position',
                            hover_data=['pfr_player_name', 'team'],
                            title="Weighted AV of #1 Overall Picks")
        st.plotly_chart(fig_p1)

    st.subheader("The 'Pick #1 Curse': Success with Original Team?")
    p1_df['success_with_team'] = p1_df['dr_av'] / p1_df['w_av'].replace(0, 1)
    p1_df['dr_av'] = p1_df['dr_av'].astype(float)
    p1_df['w_av'] = p1_df['w_av'].astype(float)
    fig_curse = px.bar(p1_df.sort_values('season'), x='pfr_player_name', y=['dr_av', 'w_av'], 
                       barmode='group', title="Weighted AV vs Drafting Team AV for #1 Picks")
    st.plotly_chart(fig_curse, use_container_width=True)

# Player Comparison
elif page == "Player Comparison":
    st.header("Player Comparison Tool")
    
    all_players = sorted(df['pfr_player_name'].dropna().unique())
    player_name = st.selectbox("Select a Player", options=all_players)
    
    player_data = df[df['pfr_player_name'] == player_name].iloc[0]
    
    st.write(f"### {player_data['pfr_player_name']}")
    st.write(f"**Drafted:** {player_data['season']} | **Pick:** #{player_data['pick']} | **Team:** {player_data['team']}")
    
    st.subheader("Comparison with Similar Picks")
    st.write(f"Comparing with other **{player_data['position']}**s drafted within +/- 10 picks.")
    
    similar_picks = df[(df['position'] == player_data['position']) & 
                       (df['pick'] >= player_data['pick'] - 10) & 
                       (df['pick'] <= player_data['pick'] + 10)].copy()
    
    similar_picks['w_av'] = similar_picks['w_av'].astype(float)
    
    fig = px.scatter(similar_picks, x='season', y='w_av', 
                     color=(similar_picks['pfr_player_name'] == player_name).astype(str),
                     hover_data=['pfr_player_name', 'pick'],
                     title=f"wAV Comparison for {player_data['position']}s in similar draft slots",
                     labels={'color': 'Is Selected Player'})
    st.plotly_chart(fig, use_container_width=True)

# 2026 Consensus Alignment
elif page == "2026 Consensus Alignment":
    st.header("2026 Consensus Alignment")
    st.write("Compare the 2026 draft picks to the pre-draft Consensus Big Board (134 combined boards).")
    
    consensus_df = load_consensus_data()
    
    if consensus_df is None:
        st.error("Consensus Board file not found or could not be loaded. Please ensure '2026 Consensus Board (134 Boards).xlsx' is in the directory.")
    else:
        st.subheader("Draft Value vs Consensus")
        st.write("A **positive** Delta means the team drafted the player *later* than their consensus rank (Steal). A **negative** Delta means they drafted them *earlier* (Reach).")
        
        fig = px.scatter(consensus_df, x='Pick', y='Ovr', color='Team',
                         hover_data=['Player', 'Position', 'School', 'Delta'],
                         title="Actual Draft Pick vs Consensus Rank",
                         labels={'Pick': 'Actual Pick', 'Ovr': 'Consensus Rank'})
                         
        # Add a y=x reference line
        fig.add_trace(go.Scatter(x=[1, consensus_df['Pick'].max()], y=[1, consensus_df['Pick'].max()],
                                 mode='lines', name='Perfect Alignment', line=dict(color='white', dash='dash')))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Team Analysis: Steals & Reaches")
        team_delta = consensus_df.groupby('Team')['Delta'].sum().reset_index().sort_values('Delta', ascending=False)
        
        fig_team = px.bar(team_delta, x='Team', y='Delta',
                          color='Delta', color_continuous_scale='RdYlGn',
                          title="Aggregate Consensus Delta by Team",
                          labels={'Delta': 'Total Delta (Positive = Value/Steals)'})
        st.plotly_chart(fig_team, use_container_width=True)

