"""Utility functions for calculating advanced baseball metrics."""
from __future__ import annotations

import re
import pandas as pd

# Weights sourced from current wOBA scale (approximate)
WALK_WEIGHT = 0.69
HBP_WEIGHT = 0.72
SINGLE_WEIGHT = 0.89
DOUBLE_WEIGHT = 1.27
TRIPLE_WEIGHT = 1.62
HR_WEIGHT = 2.10

def _extract_player_name(description: str) -> str:
    """Best-effort extraction of the batter's name from the Statcast description."""
    match = re.match(r"^([A-Z][^ ]+ [A-Z][^ ]+)", str(description))
    return match.group(1) if match else "Unknown"

def calculate_woba(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate wOBA for each batter in a Statcast data set.

    Parameters
    ----------
    df: pandas.DataFrame
        Raw Statcast pitch-level data. Only rows with a value in ``events`` are
        used when tallying plate appearances.

    Returns
    -------
    pandas.DataFrame
        Columns: ``player_name``, ``batter``, ``pa``, ``woba`` sorted by wOBA
        descending.
    """
    event_df = df[df["events"].notna() & (df["events"] != "")].copy()
    if event_df.empty:
        return pd.DataFrame(columns=["player_name", "batter", "pa", "woba"])

    event_df["player_name"] = event_df["des"].apply(_extract_player_name)
    event_df = event_df[event_df["player_name"] != "Unknown"]

    grouped = event_df.groupby(["batter", "player_name"])['events'].value_counts().unstack(fill_value=0)

    # Ensure all referenced event columns exist
    for col in ["walk", "hit_by_pitch", "single", "double", "triple", "home_run"]:
        if col not in grouped.columns:
            grouped[col] = 0

    result = grouped.reset_index()
    result["woba_numerator"] = (
        result["walk"] * WALK_WEIGHT
        + result["hit_by_pitch"] * HBP_WEIGHT
        + result["single"] * SINGLE_WEIGHT
        + result["double"] * DOUBLE_WEIGHT
        + result["triple"] * TRIPLE_WEIGHT
        + result["home_run"] * HR_WEIGHT
    )

    result["pa"] = grouped.sum(axis=1).values
    result["woba"] = result["woba_numerator"] / result["pa"]

    return result[["player_name", "batter", "pa", "woba"]].sort_values("woba", ascending=False)
