"""Streamlit application for displaying advanced MLB statistics."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.metrics import calculate_woba

st.set_page_config(page_title="MLB Advanced Stats", layout="wide")
st.title("⚾ MLB Advanced Stats Dashboard")

# Locate most recent data file
DATA_DIR = Path("data")
DATA_FILES = sorted(DATA_DIR.glob("mlb_data_filtered_*.csv"))
if not DATA_FILES:
    st.error("No data files available in the 'data' directory.")
else:
    latest = DATA_FILES[-1]
    st.caption(f"Using data file: {latest.name}")
    raw_df = pd.read_csv(latest)

    woba_df = calculate_woba(raw_df)
    if woba_df.empty:
        st.warning("No plate appearance events found in the dataset.")
    else:
        min_pa = st.slider(
            "Minimum plate appearances",
            min_value=1,
            max_value=int(woba_df["pa"].max()),
            value=10,
        )
        filtered = woba_df[woba_df["pa"] >= min_pa]
        st.dataframe(
            filtered[["player_name", "pa", "woba"]].round({"woba": 3}),
            use_container_width=True,
        )
