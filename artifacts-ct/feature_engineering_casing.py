
import pandas as pd

NUMERIC_COLS = [
    "speeddown",
    "speedup",
    "stppress",
    "mudflowin",
    "hklda",
    "blockpos",
    "bitdepth",
    "md"
]


def preprocess_drilling_activity(df, feature_cols):
    df = df.copy()
    df[NUMERIC_COLS] = df[NUMERIC_COLS].astype(float)

    df["other_activity_signal"] = (
        df["bitdepth"] == df["md"]
    ).astype(int)

    df = df.dropna(subset=feature_cols).reset_index(drop=True)

    X_raw = df[feature_cols]

    return X_raw, df
