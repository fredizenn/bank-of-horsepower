import pandas as pd
import numpy as np

CHAMPIONS: dict[int, str] = {
    **{season: "Red Bull Racing" for season in range(2010, 2014)},
    **{season: "Mercedes" for season in range(2014, 2022)},
    2022: "Red Bull Racing",
    2023: "Red Bull Racing",
    2024: "McLaren",
    2025: "McLaren",
}

def apply_champion_labels(df: pd.DataFrame, champions: dict[int, str] = CHAMPIONS) -> pd.DataFrame:
    """Replace the source labels with the historical record.

    Seasons missing from ``champions`` get NaN, meaning "not known yet", so they
    can never be used as training examples by mistake.
    """
    out = df.copy()
    known = out["season"].isin(champions)
    out["is_constructors_champion"] = np.where(
        known, (out["team_name"] == out["season"].map(champions)).astype(float), np.nan
    )
    return out