import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_draft_data, load_draft_values, define_hit, get_position_groups

# Page configuration
st.set_page_config(page_title="NFL Draft Analysis", layout="wide", page_icon="🏈")

st.title("🏈 NFL Draft Analysis Dashboard")
st.markdown("---")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Metrics Explorer", "Hit/Bust Analysis", "Pick #1 & HOF Deep Dive", "Player Comparison"])

# Load data
with st.spinner("Loading draft data..."):
    df = load_draft_data()
    df = get_position_groups(df)

# Home Page
if page == "Home":
    st.header("Welcome to the NFL Draft Analysis Tool")
    st.write("This tool helps analyze historical draft data, player value (CarAV), and team success rates.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Picks Analyzed", len(df))
    col2.metric("Seasons Covered", f"{df['season'].min()} - {df['season'].max()}")
    col3.metric("Total Hall of Famers", df['hof'].eq('yes').sum())

    st.subheader("Picks by Position Group")
    fig = px.pie(df, names='pos_group', title="Distribution of Picks by Position Group")
    st.plotly_chart(fig, use_container_width=True)

# Metrics Explorer
elif page == "Metrics Explorer":
    st.header("CarAV & DrAV Analysis")
    st.write("Explore Career Approximate Value (CarAV) and Value for the Drafting Team (DrAV).")
    
    pos_filter = st.multiselect("Select Positions", options=sorted(df['position'].unique()), default=['QB', 'WR', 'RB', 'DE'])
    
    filtered_df = df[df['position'].isin(pos_filter)]
    
    st.subheader("CarAV vs Pick Number")
    fig = px.scatter(filtered_df, x='pick', y='car_av', color='position', 
                     hover_data=['pfr_player_name', 'season', 'team'],
                     title="Career AV by Draft Pick",
                     labels={'car_av': 'Career AV', 'pick': 'Draft Pick #'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Organization Success: DrAV vs CarAV")
    st.write("A higher DrAV relative to CarAV means the player stayed and succeeded with the team that drafted them.")
    filtered_df['success_ratio'] = filtered_df['dr_av'] / filtered_df['car_av'].replace(0, 1)
    
    fig2 = px.box(filtered_df, x='position', y='success_ratio', points="all",
                  title="Drafting Team Success Ratio (DrAV / CarAV)")
    st.plotly_chart(fig2, use_container_width=True)

# Hit/Bust Analysis
elif page == "Hit/Bust Analysis":
    st.header("Hit vs. Bust Analysis")
    
    with st.expander("Configure 'Hit' Criteria"):
        seasons = st.slider("Minimum Seasons as Starter", 0, 15, 4)
        probowls = st.slider("Minimum Pro Bowls", 0, 10, 1)
    
    df_hit = define_hit(df.copy(), seasons_started=seasons, probowls=probowls)
    
    st.subheader("Hit Rate by Round")
    hit_rate = df_hit.groupby('round')['is_hit'].mean().reset_index()
    hit_rate['is_hit'] *= 100
    
    fig = px.bar(hit_rate, x='round', y='is_hit', title="Hit Rate (%) by Draft Round",
                 labels={'is_hit': 'Hit %', 'round': 'Draft Round'})
    st.plotly_chart(fig, use_container_width=True)

# Pick #1 & HOF Deep Dive
elif page == "Pick #1 & HOF Deep Dive":
    st.header("Hall of Fame & Pick #1 Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Where do HOFers come from?")
        hof_df = df[df['hof'] == 'yes']
        fig_hof = px.histogram(hof_df, x='round', title="HOFers by Round")
        st.plotly_chart(fig_hof)
        
    with col2:
        st.subheader("Pick #1 Success")
        p1_df = df[df['pick'] == 1]
        fig_p1 = px.scatter(p1_df, x='season', y='car_av', color='position',
                            hover_data=['pfr_player_name', 'team'],
                            title="Career AV of #1 Overall Picks")
        st.plotly_chart(fig_p1)

    st.subheader("The 'Pick #1 Curse': Success with Original Team?")
    p1_df['success_with_team'] = p1_df['dr_av'] / p1_df['car_av'].replace(0, 1)
    fig_curse = px.bar(p1_df.sort_values('season'), x='pfr_player_name', y=['dr_av', 'car_av'], 
                       barmode='group', title="Career AV vs Drafting Team AV for #1 Picks")
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
                       (df['pick'] <= player_data['pick'] + 10)]
    
    fig = px.scatter(similar_picks, x='season', y='car_av', 
                     color=(similar_picks['pfr_player_name'] == player_name),
                     hover_data=['pfr_player_name', 'pick'],
                     title=f"CarAV Comparison for {player_data['position']}s in similar draft slots",
                     labels={'color': 'Is Selected Player'})
    st.plotly_chart(fig, use_container_width=True)
