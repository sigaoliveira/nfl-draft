import nfl_data_py as nfl
import pandas as pd
import streamlit as st

@st.cache_data
def load_draft_data(years=None):
    """
    Loads draft picks data. 
    If years is None, it defaults to a wide range (e.g., 1980 to present).
    """
    if years is None:
        years = list(range(1980, 2026))
    
    df = nfl.import_draft_picks(years)
    
    # Basic cleaning
    df['season'] = df['season'].astype(int)
    df['pick'] = df['pick'].astype(int)
    df['round'] = df['round'].astype(int)
    
    return df

@st.cache_data
def load_draft_values():
    """
    Loads pick value charts (Jimmy Johnson, Chase Stuart, etc.)
    """
    return nfl.import_draft_values()

def define_hit(df, seasons_started=4, probowls=1):
    """
    Adds a 'hit' column based on user-defined criteria.
    """
    df['is_hit'] = (df['seasons_started'] >= seasons_started) | (df['probowls'] >= probowls)
    return df

def get_position_groups(df):
    """
    Groups positions into broader categories if needed.
    """
    pos_map = {
        'QB': 'Offense',
        'RB': 'Offense', 'WR': 'Offense', 'TE': 'Offense', 'FB': 'Offense',
        'T': 'Offense', 'G': 'Offense', 'C': 'Offense', 'OT': 'Offense', 'OG': 'Offense',
        'DE': 'Defense', 'DT': 'Defense', 'NT': 'Defense',
        'LB': 'Defense', 'OLB': 'Defense', 'ILB': 'Defense', 'MLB': 'Defense',
        'CB': 'Defense', 'S': 'Defense', 'DB': 'Defense', 'FS': 'Defense', 'SS': 'Defense',
        'K': 'Special Teams', 'P': 'Special Teams', 'LS': 'Special Teams'
    }
    df['pos_group'] = df['position'].map(pos_map).fillna('Other')
    return df

import os
@st.cache_data
def load_consensus_data():
    """
    Loads the 2026 Consensus Board Excel file if it exists.
    Returns None if the file is not found.
    """
    file_path = '2026 Consensus Board (134 Boards).xlsx'
    if not os.path.exists(file_path):
        return None
    
    try:
        df = pd.read_excel(file_path, header=3)
        # Drop rows where 'Pick' is NaN or 'Ovr' is NaN
        df = df.dropna(subset=['Pick', 'Ovr']).copy()
        
        # Ensure numerical types
        df['Pick'] = pd.to_numeric(df['Pick'], errors='coerce')
        df['Ovr'] = pd.to_numeric(df['Ovr'], errors='coerce')
        
        # Calculate Delta: Positive means Steal (Drafted later than consensus)
        # Negative means Reach (Drafted earlier than consensus)
        df['Delta'] = df['Pick'] - df['Ovr']
        
        return df
    except Exception as e:
        print(f"Error loading consensus data: {e}")
        return None
