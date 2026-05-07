import pandas as pd
import plotly.express as px
from data_loader import load_draft_data, get_position_groups

df = load_draft_data()
df = get_position_groups(df)

# Test Metrics Explorer
try:
    print("Testing Metrics Explorer...")
    pos_filter = ['QB', 'WR', 'RB', 'DE']
    filtered_df = df[df['position'].isin(pos_filter)].copy()
    filtered_df['car_av'] = filtered_df['car_av'].astype(float)
    filtered_df['dr_av'] = filtered_df['dr_av'].astype(float)
    
    fig = px.scatter(filtered_df, x='pick', y='car_av', color='position', 
                     hover_data=['pfr_player_name', 'season', 'team'],
                     title="Career AV by Draft Pick",
                     labels={'car_av': 'Career AV', 'pick': 'Draft Pick #'})
                     
    filtered_df['success_ratio'] = filtered_df['dr_av'] / filtered_df['car_av'].replace(0, 1)
    
    fig2 = px.box(filtered_df, x='position', y='success_ratio', points="all",
                  title="Drafting Team Success Ratio (DrAV / CarAV)")
    print("Metrics Explorer test passed.")
except Exception as e:
    print(f"Metrics Explorer failed: {e}")

# Test Player Comparison
try:
    print("Testing Player Comparison...")
    player_name = "Peyton Manning"
    player_data = df[df['pfr_player_name'] == player_name].iloc[0]
    
    similar_picks = df[(df['position'] == player_data['position']) & 
                       (df['pick'] >= player_data['pick'] - 10) & 
                       (df['pick'] <= player_data['pick'] + 10)].copy()
    
    similar_picks['car_av'] = similar_picks['car_av'].astype(float)
    
    fig = px.scatter(similar_picks, x='season', y='car_av', 
                     color=(similar_picks['pfr_player_name'] == player_name).astype(str),
                     hover_data=['pfr_player_name', 'pick'],
                     title=f"CarAV Comparison for {player_data['position']}s in similar draft slots",
                     labels={'color': 'Is Selected Player'})
    print("Player Comparison test passed.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Player Comparison failed: {e}")
