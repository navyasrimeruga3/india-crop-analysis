"""
generate_data.py
-----------------
Generates a realistic SYNTHETIC dataset that mirrors the structure of the
well-known "Crop Production in India (1997-2021)" dataset:

Columns: State_Name, District_Name, Crop_Year, Season, Crop, Area, Production

Why synthetic? No internet/dataset download is available in this environment,
so real historical figures cannot be pulled in. Instead, this script builds
data using realistic crop-yield ranges, state-crop suitability, seasonal
patterns, and year-over-year trend/noise, so every downstream script
(preprocessing, analysis, dashboard) works exactly as it would on the
real dataset. Swap this CSV for the real Kaggle dataset any time --
the rest of the pipeline needs zero changes as long as column names match.
"""

import numpy as np
import pandas as pd
import random

random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------------
# 1. Reference data: states -> districts, crop suitability, yields
# ------------------------------------------------------------------

STATE_DISTRICTS = {
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Meerut", "Varanasi", "Agra"],
    "Punjab": ["Ludhiana", "Amritsar", "Patiala", "Jalandhar"],
    "Haryana": ["Karnal", "Hisar", "Rohtak", "Panipat"],
    "Maharashtra": ["Pune", "Nagpur", "Nashik", "Kolhapur", "Aurangabad"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior"],
    "Karnataka": ["Bengaluru Rural", "Belagavi", "Mysuru", "Ballari"],
    "Andhra Pradesh": ["Guntur", "Krishna", "Anantapur", "Chittoor"],
    "Tamil Nadu": ["Thanjavur", "Coimbatore", "Salem", "Madurai"],
    "West Bengal": ["Bardhaman", "Murshidabad", "Nadia", "Hooghly"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],
    "Gujarat": ["Ahmedabad", "Rajkot", "Surat", "Vadodara"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner"],
    "Odisha": ["Cuttack", "Puri", "Sambalpur", "Balasore"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar"],
    "Kerala": ["Palakkad", "Thrissur", "Kottayam"],
}

# crop -> (typical yield tonnes/ha, seasons grown, suitable states, growth trend %/yr)
CROPS = {
    "Rice":        (2.6, ["Kharif", "Autumn", "Winter"], ["Uttar Pradesh","West Bengal","Tamil Nadu","Punjab","Andhra Pradesh","Odisha","Bihar","Assam"], 0.8),
    "Wheat":       (3.1, ["Rabi"], ["Uttar Pradesh","Punjab","Haryana","Madhya Pradesh","Rajasthan"], 1.0),
    "Maize":       (2.8, ["Kharif","Rabi"], ["Karnataka","Bihar","Madhya Pradesh","Andhra Pradesh"], 1.5),
    "Sugarcane":   (68.0, ["Whole Year"], ["Uttar Pradesh","Maharashtra","Karnataka","Tamil Nadu"], 0.5),
    "Cotton":      (0.45, ["Kharif"], ["Gujarat","Maharashtra","Andhra Pradesh","Punjab"], 1.2),
    "Soybean":     (1.1, ["Kharif"], ["Madhya Pradesh","Maharashtra","Rajasthan"], 2.0),
    "Groundnut":   (1.4, ["Kharif","Rabi"], ["Gujarat","Andhra Pradesh","Tamil Nadu","Karnataka"], 0.6),
    "Jowar":       (1.0, ["Kharif","Rabi"], ["Maharashtra","Karnataka","Madhya Pradesh"], -0.5),
    "Bajra":       (1.2, ["Kharif"], ["Rajasthan","Gujarat","Haryana","Uttar Pradesh"], 0.3),
    "Gram":        (1.0, ["Rabi"], ["Madhya Pradesh","Rajasthan","Uttar Pradesh"], 0.7),
    "Tur":         (0.85, ["Kharif"], ["Maharashtra","Karnataka","Uttar Pradesh"], 0.4),
    "Mustard":     (1.3, ["Rabi"], ["Rajasthan","Haryana","Uttar Pradesh"], 1.0),
    "Potato":      (22.0, ["Rabi"], ["Uttar Pradesh","West Bengal","Bihar"], 1.8),
    "Onion":       (17.0, ["Kharif","Rabi"], ["Maharashtra","Karnataka","Gujarat"], 2.2),
    "Banana":      (35.0, ["Whole Year"], ["Tamil Nadu","Maharashtra","Gujarat","Andhra Pradesh"], 1.4),
    "Coconut":     (9.0, ["Whole Year"], ["Kerala","Tamil Nadu","Karnataka"], 0.5),  # tonnes/ha equivalent
    "Barley":      (2.5, ["Rabi"], ["Uttar Pradesh","Rajasthan","Madhya Pradesh"], -0.3),
    "Sunflower":   (0.9, ["Kharif","Rabi"], ["Karnataka","Andhra Pradesh"], -0.8),
    "Tobacco":     (1.8, ["Kharif"], ["Andhra Pradesh","Gujarat","Karnataka"], -0.2),
    "Jute":        (2.3, ["Kharif"], ["West Bengal","Assam","Odisha"], 0.2),
}

YEARS = list(range(1997, 2022))
SEASON_AREA_SHARE = {"Kharif": 1.0, "Rabi": 1.0, "Whole Year": 1.0, "Autumn": 0.4, "Winter": 0.6}

rows = []
for crop, (base_yield, seasons, states, trend_pct) in CROPS.items():
    for state in states:
        districts = STATE_DISTRICTS[state]
        base_area = np.random.uniform(15000, 90000)  # hectares, state-crop base
        for year in YEARS:
            year_idx = year - 1997
            # long-term trend + cyclical weather variation + random noise
            trend_factor = (1 + trend_pct / 100) ** year_idx
            weather_cycle = 1 + 0.08 * np.sin(year_idx / 3.0 + hash(state) % 5)
            noise = np.random.normal(1.0, 0.07)
            year_area = max(base_area * trend_factor * weather_cycle * noise, 500)

            for season in seasons:
                district = random.choice(districts)
                season_area = year_area * SEASON_AREA_SHARE.get(season, 1.0) / len(seasons)
                season_area = round(max(season_area * np.random.uniform(0.7, 1.3), 100), 1)

                yield_noise = np.random.normal(1.0, 0.10)
                drought_shock = 1.0
                # occasional drought/flood shock years (well-known bad ag years)
                if year in (2002, 2004, 2009, 2014, 2015):
                    drought_shock = np.random.uniform(0.75, 0.9)
                actual_yield = base_yield * trend_factor * yield_noise * drought_shock
                production = round(season_area * actual_yield, 1)

                rows.append({
                    "State_Name": state,
                    "District_Name": district,
                    "Crop_Year": year,
                    "Season": season,
                    "Crop": crop,
                    "Area": season_area,
                    "Production": production,
                })

df = pd.DataFrame(rows)

# ------------------------------------------------------------------
# 2. Inject realistic data-quality issues for the preprocessing step
#    (missing values, a few duplicates, stray whitespace, zero-area rows)
# ------------------------------------------------------------------
n = len(df)
missing_idx = np.random.choice(n, size=int(n * 0.02), replace=False)
df.loc[missing_idx, "Production"] = np.nan

missing_area_idx = np.random.choice(n, size=int(n * 0.005), replace=False)
df.loc[missing_area_idx, "Area"] = np.nan

# a few duplicate rows
dup_rows = df.sample(n=200, random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# stray whitespace / case issues in a subset of season labels
whitespace_idx = np.random.choice(len(df), size=150, replace=False)
df.loc[whitespace_idx, "Season"] = df.loc[whitespace_idx, "Season"].apply(lambda s: f" {s} ")

# shuffle rows
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("/home/claude/india-crop-analysis/data/crop_production.csv", index=False)
print(f"Generated {len(df):,} rows -> data/crop_production.csv")
print(df.head())
