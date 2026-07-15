"""
data_analysis.py
------------------
Analytical functions covering the three project scenarios:

  1. Small-scale farmer  -> seasonal trends, regional productivity, top crops
  2. Policy analyst      -> low-yield regions, long-term trends, seasonal impact
  3. Agribusiness investor -> growth rates, profitable/emerging crops, consistent-growth regions

Import these functions from the dashboard, or run this file directly to
print a full text summary to the console.
"""

import pandas as pd
import os

CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_production_clean.csv")


def load_clean(path=CLEAN_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


# ---------- Scenario 1: Farmer ----------

def top_crops_by_production(df, n=10):
    return (df.groupby("Crop")["Production"].sum()
              .sort_values(ascending=False).head(n))


def seasonal_trends(df):
    return df.groupby("Season").agg(
        Total_Area=("Area", "sum"),
        Total_Production=("Production", "sum"),
        Avg_Yield=("Yield", "mean"),
    ).sort_values("Total_Production", ascending=False)


def best_crops_for_state(df, state, n=5):
    sub = df[df["State_Name"] == state]
    return (sub.groupby("Crop")["Yield"].mean()
               .sort_values(ascending=False).head(n))


# ---------- Scenario 2: Policy Analyst ----------

def state_yield_ranking(df):
    """Average yield per state -- lowest first (candidates for intervention)."""
    return (df.groupby("State_Name")["Yield"].mean()
              .sort_values(ascending=True))


def yearly_production_trend(df):
    return df.groupby("Crop_Year")["Production"].sum()


def season_impact_by_decade(df):
    return df.groupby(["Decade", "Season"])["Production"].sum().unstack(fill_value=0)


def low_yield_state_crop_pairs(df, threshold_percentile=0.25):
    grp = df.groupby(["State_Name", "Crop"])["Yield"].mean().reset_index()
    threshold = grp["Yield"].quantile(threshold_percentile)
    return grp[grp["Yield"] <= threshold].sort_values("Yield")


# ---------- Scenario 3: Investor ----------

def crop_growth_rate(df):
    """CAGR of production per crop from first to last available year."""
    results = {}
    first_year, last_year = df["Crop_Year"].min(), df["Crop_Year"].max()
    n_years = last_year - first_year
    for crop, sub in df.groupby("Crop"):
        start = sub[sub["Crop_Year"] == first_year]["Production"].sum()
        end = sub[sub["Crop_Year"] == last_year]["Production"].sum()
        if start > 0 and n_years > 0:
            cagr = ((end / start) ** (1 / n_years) - 1) * 100
            results[crop] = cagr
    return pd.Series(results).sort_values(ascending=False)


def consistent_growth_states(df, crop=None):
    """States with the steadiest (lowest variance, positive-trend) year-over-year production."""
    sub = df if crop is None else df[df["Crop"] == crop]
    yearly = sub.groupby(["State_Name", "Crop_Year"])["Production"].sum().reset_index()
    stats = yearly.groupby("State_Name")["Production"].agg(["mean", "std"])
    stats["cv"] = (stats["std"] / stats["mean"]).round(3)  # coefficient of variation, lower = steadier
    return stats.sort_values("cv")


def emerging_crops(df, recent_years=5):
    """Crops whose production grew fastest in the most recent N years."""
    max_year = df["Crop_Year"].max()
    recent = df[df["Crop_Year"] > max_year - recent_years]
    trend = recent.groupby(["Crop_Year", "Crop"])["Production"].sum().reset_index()
    growth = {}
    for crop, sub in trend.groupby("Crop"):
        sub = sub.sort_values("Crop_Year")
        if len(sub) >= 2 and sub["Production"].iloc[0] > 0:
            growth[crop] = (sub["Production"].iloc[-1] / sub["Production"].iloc[0] - 1) * 100
    return pd.Series(growth).sort_values(ascending=False)


if __name__ == "__main__":
    df = load_clean()

    print("=" * 60)
    print("SCENARIO 1: FARMER - Top 10 crops by total production")
    print("=" * 60)
    print(top_crops_by_production(df))

    print("\nSeasonal trends:")
    print(seasonal_trends(df))

    print("\n" + "=" * 60)
    print("SCENARIO 2: POLICY ANALYST - Lowest-yield states (need support)")
    print("=" * 60)
    print(state_yield_ranking(df).head(5))

    print("\n" + "=" * 60)
    print("SCENARIO 3: INVESTOR - Crop CAGR (1997-2021)")
    print("=" * 60)
    print(crop_growth_rate(df).head(10))

    print("\nEmerging crops (last 5 years growth %):")
    print(emerging_crops(df).head(10))
