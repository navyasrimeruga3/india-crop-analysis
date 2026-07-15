"""
data_preprocessing.py
----------------------
Cleans the raw crop production dataset:
  - trims whitespace / normalizes text case
  - handles missing values (impute Production via Area * mean-yield-by-crop,
    drop rows where imputation isn't possible)
  - removes duplicate rows
  - removes invalid (zero/negative) Area or Production
  - adds derived columns: Yield (t/ha), Decade
  - saves a clean CSV to data/crop_production_clean.csv

Run directly:  python src/data_preprocessing.py
"""

import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_production.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_production_clean.csv")


def load_raw(path=RAW_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    report = {}
    report["rows_raw"] = len(df)

    # 1. Normalize text columns
    text_cols = ["State_Name", "District_Name", "Season", "Crop"]
    for c in text_cols:
        df[c] = df[c].astype(str).str.strip().str.title()

    # 2. Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = before - len(df)

    # 3. Handle missing Area: drop (can't safely impute physical area)
    before = len(df)
    df = df.dropna(subset=["Area"])
    report["rows_missing_area_dropped"] = before - len(df)

    # 4. Impute missing Production using the average yield (Production/Area)
    #    for that Crop, computed from non-missing rows
    yield_lookup = (
        df.dropna(subset=["Production"])
        .assign(_y=lambda d: d["Production"] / d["Area"])
        .groupby("Crop")["_y"].mean()
    )
    missing_mask = df["Production"].isna()
    report["rows_production_imputed"] = int(missing_mask.sum())
    df.loc[missing_mask, "Production"] = df.loc[missing_mask, "Crop"].map(yield_lookup) * df.loc[missing_mask, "Area"]

    # any crop with no lookup available -> drop
    before = len(df)
    df = df.dropna(subset=["Production"])
    report["rows_still_missing_dropped"] = before - len(df)

    # 5. Remove invalid rows (non-positive Area/Production)
    before = len(df)
    df = df[(df["Area"] > 0) & (df["Production"] > 0)]
    report["invalid_rows_removed"] = before - len(df)

    # 6. Derived columns
    df["Yield"] = (df["Production"] / df["Area"]).round(3)
    df["Decade"] = (df["Crop_Year"] // 10 * 10).astype(int)

    # 7. Final dtype cleanup
    df["Crop_Year"] = df["Crop_Year"].astype(int)
    df = df.reset_index(drop=True)

    report["rows_clean"] = len(df)
    return df, report


if __name__ == "__main__":
    raw = load_raw()
    clean_df, report = clean(raw)
    clean_df.to_csv(CLEAN_PATH, index=False)
    print("Preprocessing report:")
    for k, v in report.items():
        print(f"  {k}: {v}")
    print(f"\nSaved cleaned dataset -> {CLEAN_PATH}  ({len(clean_df):,} rows)")
