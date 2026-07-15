# India's Agricultural Crop Production Analysis (1997–2021)

A Tableau-free recreation of the project — same brief, same three stakeholder
scenarios, done entirely in **Python** so you can run it locally without any
BI software license.

| Original (Tableau) | This version |
|---|---|
| Tableau Desktop | Pandas + NumPy (analysis) |
| Tableau Dashboards | Streamlit interactive dashboard |
| Tableau Story | Static PNG chart set + Jupyter notebook |

## What's inside

```
india-crop-analysis/
├── data/
│   ├── crop_production.csv          # raw (synthetic) dataset
│   └── crop_production_clean.csv    # cleaned dataset (generated)
├── src/
│   ├── generate_data.py             # builds the dataset
│   ├── data_preprocessing.py        # cleaning / missing values / dedup
│   ├── data_analysis.py             # analysis functions (3 scenarios)
│   └── visualizations.py            # generates static PNG charts
├── dashboard/
│   └── app.py                       # interactive Streamlit dashboard
├── notebooks/
│   └── EDA.ipynb                    # exploratory analysis notebook
├── outputs/
│   └── charts/                      # generated PNGs land here
├── requirements.txt
└── README.md
```

### ⚠️ About the data
No dataset file or internet download was available while building this, so
`src/generate_data.py` **generates a realistic synthetic dataset** that
mirrors the structure of the well-known "Crop Production in India" dataset
(`State_Name, District_Name, Crop_Year, Season, Crop, Area, Production`) —
20 crops, 15 states, 1997–2021, with realistic yields, seasonal patterns,
drought-year dips, and injected data-quality issues (missing values,
duplicates, whitespace) so the preprocessing step has real work to do.

**If you have the real Kaggle "Crop Production in India" CSV**, just drop it
into `data/crop_production.csv` with the same column names and skip
`generate_data.py` — every other script works unchanged.

## Setup (run these once)

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the dataset
python src/generate_data.py

# 4. Clean it
python src/data_preprocessing.py

# 5. Generate static charts (optional — dashboard doesn't need this)
python src/visualizations.py
```

## Run the interactive dashboard

```bash
streamlit run dashboard/app.py
```

This opens a browser tab at `http://localhost:8501` with:
- **Overview tab** — production trend, seasonal split, top crops, regional map, decade heatmap
- **Scenario 1 (Farmer)** — seasonal trends, best crops per state
- **Scenario 2 (Policy Analyst)** — lowest-yield states, long-term trend, weak state–crop pairs
- **Scenario 3 (Investor)** — crop CAGR, emerging crops, most consistent (low-risk) states

All filters (year range, state, crop, season) in the sidebar update every
chart and KPI on the page.

## Explore the notebook

```bash
jupyter notebook notebooks/EDA.ipynb
```

## Skills demonstrated (maps to the original project's skill list)

| Skill | Where |
|---|---|
| Data Preprocessing | `src/data_preprocessing.py` |
| Data Analysis | `src/data_analysis.py`, `notebooks/EDA.ipynb` |
| Data Visualization | `src/visualizations.py` (static), `dashboard/app.py` (interactive) |
| Dashboard | `dashboard/app.py` (Streamlit, replaces Tableau Dashboard) |
| "Story" / narrative | Scenario tabs in the dashboard + this README |

---

## 📌 Adding your Demo and GitHub links (for your mentor)

I can't create a GitHub account or a live hosted demo on your behalf — but
here's exactly how to get both links in about 10 minutes:

### 1. GitHub link
```bash
cd india-crop-analysis
git init
git add .
git commit -m "India Crop Production Analysis - Python/Streamlit version"
# create a new empty repo on github.com first, then:
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```
Your GitHub link is then: `https://github.com/<your-username>/<repo-name>`

### 2. Demo link (free, no server needed)
The easiest free option is **Streamlit Community Cloud**:
1. Push this project to GitHub (step 1 above).
2. Go to https://share.streamlit.io → "New app".
3. Pick your repo, set the main file path to `dashboard/app.py`.
4. Click Deploy. You'll get a public URL like
   `https://<your-app>.streamlit.app` — that's your demo link.

Once you have both, add them to your project workspace/overview page as
requested:
- **GitHub:** `https://github.com/<your-username>/<repo-name>`
- **Demo:** `https://<your-app>.streamlit.app`

---

## Notes on the synthetic data
Values are generated, not official government statistics — good for
demonstrating the full pipeline (generation → cleaning → analysis →
visualization → dashboard) and for your mentor review, but don't cite the
numbers as real agricultural statistics. Swap in the real dataset any time
using the same column names to get real-world results.
