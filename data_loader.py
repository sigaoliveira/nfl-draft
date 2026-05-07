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
