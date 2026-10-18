import pandas as pd

from boh.data import apply_champion_labels, load_raw


constructor_df = load_raw()["constructor_finances"]
labelled = apply_champion_labels(constructor_df)


def test_one_champion_per_known_season():
    known = labelled[labelled["season"] <= 2025]
    assert (known.groupby("season")["is_constructors_champion"].sum() == 1).all()


def test_wrong_seasons_are_fixed():
    champion_2012 = labelled.loc[(labelled["season"] == 2012) & (labelled["is_constructors_champion"] == 1), "team_name"]
    assert champion_2012.tolist() == ["Red Bull Racing"]


def test_unfinished_season_is_unknown():
    assert labelled.loc[labelled["season"] == 2026, "is_constructors_champion"].isna().all()


def test_input_is_not_changed():
    before = constructor_df.copy()
    apply_champion_labels(constructor_df)
    pd.testing.assert_frame_equal(constructor_df, before)
