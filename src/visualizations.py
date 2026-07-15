"""
visualizations.py
-------------------
Generates a set of static PNG charts into outputs/charts/, covering
production trends, seasonal variation, regional distribution, and
top-crop/growth analysis (mirrors what the Tableau dashboards/story
would have shown).

Run:  python src/visualizations.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from data_analysis import (
    load_clean, top_crops_by_production, seasonal_trends,
    state_yield_ranking, yearly_production_trend, crop_growth_rate,
    consistent_growth_states,
)

sns.set_theme(style="whitegrid")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "charts")
os.makedirs(OUT_DIR, exist_ok=True)


def savefig(name):
    path = os.path.join(OUT_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    print(f"  saved {name}")


def main():
    df = load_clean()

    # 1. Yearly national production trend
    yearly = yearly_production_trend(df)
    plt.figure(figsize=(10, 5))
    yearly.plot(marker="o", color="#2e7d32")
    plt.title("India: Total Crop Production by Year (1997-2021)")
    plt.xlabel("Year"); plt.ylabel("Total Production (tonnes)")
    savefig("01_yearly_production_trend.png")

    # 2. Top 10 crops by total production
    top = top_crops_by_production(df, n=10)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top.values, y=top.index, palette="YlGn_r")
    plt.title("Top 10 Crops by Total Production (1997-2021)")
    plt.xlabel("Total Production (tonnes)")
    savefig("02_top_crops_production.png")

    # 3. Seasonal distribution of production
    seas = seasonal_trends(df)
    plt.figure(figsize=(7, 5))
    sns.barplot(x=seas.index, y=seas["Total_Production"], palette="Oranges_r")
    plt.title("Total Production by Season")
    plt.ylabel("Total Production (tonnes)")
    savefig("03_seasonal_production.png")

    # 4. State-wise production (regional distribution)
    state_prod = df.groupby("State_Name")["Production"].sum().sort_values(ascending=False)
    plt.figure(figsize=(9, 6))
    sns.barplot(x=state_prod.values, y=state_prod.index, palette="Blues_r")
    plt.title("Total Production by State (1997-2021)")
    plt.xlabel("Total Production (tonnes)")
    savefig("04_state_production.png")

    # 5. Average yield ranking by state (policy lens)
    yld = state_yield_ranking(df)
    plt.figure(figsize=(9, 6))
    sns.barplot(x=yld.values, y=yld.index, palette="RdYlGn")
    plt.title("Average Crop Yield by State (lowest = needs support)")
    plt.xlabel("Average Yield (t/ha, mixed-unit crops distort scale)")
    savefig("05_state_yield_ranking.png")

    # 6. Crop growth rate (investor lens)
    cagr = crop_growth_rate(df)
    plt.figure(figsize=(9, 6))
    colors = ["#2e7d32" if v >= 0 else "#c62828" for v in cagr.values]
    sns.barplot(x=cagr.values, y=cagr.index, palette=colors)
    plt.title("Crop Production CAGR, 1997-2021 (%)")
    plt.xlabel("CAGR (%)")
    savefig("06_crop_growth_cagr.png")

    # 7. Heatmap: production by crop vs decade
    pivot = df.pivot_table(index="Crop", columns="Decade", values="Production", aggfunc="sum", fill_value=0)
    pivot_norm = pivot.div(pivot.max(axis=1), axis=0)  # normalize per crop for visibility
    plt.figure(figsize=(8, 9))
    sns.heatmap(pivot_norm, cmap="YlGnBu", linewidths=0.4)
    plt.title("Relative Production Intensity: Crop vs Decade")
    savefig("07_crop_decade_heatmap.png")

    # 8. Consistency of growth by state (investor lens) - lower CV = steadier
    cv = consistent_growth_states(df)["cv"].sort_values().head(10)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=cv.values, y=cv.index, palette="PuBu_r")
    plt.title("Most Consistent States by Production (lower = steadier growth)")
    plt.xlabel("Coefficient of Variation (lower = more stable)")
    savefig("08_state_growth_consistency.png")

    print(f"\nAll charts saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
