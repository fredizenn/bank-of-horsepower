import pandas as pd
import numpy as np
from pathlib import Path
import pandas as pd

# Constructors' champions by season, from the historical record.
# Source: https://en.wikipedia.org/wiki/List_of_Formula_One_World_Constructors%27_Champions
# The Kaggle source never flags Red Bull Racing (champions 2010-2013, 2022-2023).
# 2026 is deliberately absent: the season is not decided yet.

CHAMPIONS: dict[int, str] = {
    **{season: "Red Bull Racing" for season in range(2010, 2014)},
    **{season: "Mercedes" for season in range(2014, 2022)},
    2022: "Red Bull Racing",
    2023: "Red Bull Racing",
    2024: "McLaren",
    2025: "McLaren",
}

def apply_champion_labels(df: pd.DataFrame, champions: dict[int, str] = CHAMPIONS) -> pd.DataFrame:
    """Replacing the source labels with the historical record.

    Seasons missing from ``champions`` get NaN, meaning "not known yet", so they
    can never be used as training examples by mistake.
    """
    
    unknown_teams = set(champions.values()) - set(df["team_name"])
    if unknown_teams:
        raise ValueError(f"Unknown team(s) in champions: {sorted(unknown_teams)}")
    out = df.copy()
    known = out["season"].isin(champions)
    out["is_constructors_champion"] = np.where(
        known, (out["team_name"] == out["season"].map(champions)).astype(float), np.nan
    )
    return out

    


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"


def load_raw() -> dict[str, pd.DataFrame]:
    return {
        "constructor_finances": pd.read_csv(RAW_DIR / "constructor_finances.csv"),
        "f1_business": pd.read_csv(RAW_DIR / "f1_business.csv"),
    }
    
