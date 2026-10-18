import pandas as pd
import numpy as np
from pathlib import Path
import pandas as pd

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




# The project root, found from this file's location. data.py lives at
# <root>/src/boh/data.py, so the root is three levels up.
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"


def load_raw() -> dict[str, pd.DataFrame]:
    return {
        "constructor_finances": pd.read_csv(RAW_DIR / "constructor_finances.csv"),
        "f1_business": pd.read_csv(RAW_DIR / "f1_business.csv"),
    }