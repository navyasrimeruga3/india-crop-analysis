"""
app.py - India Agricultural Crop Production Analysis Dashboard
-----------------------------------------------------------------
An interactive Streamlit dashboard (fully local, no Tableau required)
covering the same insights the original Tableau Dashboards/Story would:
production trends, seasonal variation, regional distribution, and the
three project scenarios (Farmer / Policy Analyst / Investor).

Run:
    streamlit run dashboard/app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd
import plotly.express as px

from data_analysis import (
    load_clean, top_crops_by_production, seasonal_trends,
    state_yield_ranking, yearly_production_trend, crop_growth_rate,
    consistent_growth_states, emerging_crops, low_yield_state_crop_pairs,
    best_crops_for_state,
)

st.set_page_config(
    page_title="India Crop Production Analysis",
    page_icon="🌾",
    layout="wide",
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_production_clean.csv")


@st.cache_data
def get_data():
    return load_clean(DATA_PATH)


df = get_data()

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.title("🌾 Filters")
st.sidebar.caption("Filter the whole dashboard by year, state, crop & season.")

year_range = st.sidebar.slider(
    "Crop Year range",
    int(df["Crop_Year"].min()), int(df["Crop_Year"].max()),
    (int(df["Crop_Year"].min()), int(df["Crop_Year"].max())),
)

states = st.sidebar.multiselect("State", sorted(df["State_Name"].unique()))
crops = st.sidebar.multiselect("Crop", sorted(df["Crop"].unique()))
seasons = st.sidebar.multiselect("Season", sorted(df["Season"].unique()))

f = df[(df["Crop_Year"] >= year_range[0]) & (df["Crop_Year"] <= year_range[1])]
if states:
    f = f[f["State_Name"].isin(states)]
if crops:
    f = f[f["Crop"].isin(crops)]
if seasons:
    f = f[f["Season"].isin(seasons)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Rows in view:** {len(f):,} / {len(df):,}")

# ---------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------
st.title("India's Agricultural Crop Production Analysis")
st.caption(
    "A visual exploration of crop production, seasonal variation, regional "
    "distribution and long-term trends (1997-2021) — built with Python & "
    "Streamlit instead of Tableau."
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Production (t)", f"{f['Production'].sum():,.0f}")
k2.metric("Total Area (ha)", f"{f['Area'].sum():,.0f}")
k3.metric("Avg. Yield (t/ha)", f"{f['Yield'].mean():.2f}" if not f.empty else "—")
k4.metric("Crops Tracked", f"{f['Crop'].nunique()}")

st.markdown("---")

# ---------------------------------------------------------------
# Empty-state guard: stop here with a clear message instead of
# rendering broken/blank charts when the filter combo has no rows.
# ---------------------------------------------------------------
if f.empty:
    st.warning(
        "⚠️ No data matches the current filter combination "
        f"(Years {year_range[0]}–{year_range[1]}"
        + (f", States: {', '.join(states)}" if states else "")
        + (f", Crops: {', '.join(crops)}" if crops else "")
        + (f", Seasons: {', '.join(seasons)}" if seasons else "")
        + "). Try widening the year range or removing a filter."
    )
    with st.expander("💡 See which combinations actually exist in the data"):
        st.write("Available State + Crop + Season combinations:")
        combo_cols = ["State_Name", "Crop", "Season"]
        st.dataframe(
            df[combo_cols].drop_duplicates().sort_values(combo_cols).reset_index(drop=True),
            use_container_width=True,
        )
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "👨‍🌾 Scenario 1: Farmer",
    "🏛️ Scenario 2: Policy Analyst",
    "💰 Scenario 3: Investor",
])

# ---------------------------------------------------------------
# TAB 1 — Overview
# ---------------------------------------------------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Production Trend Over Time")
        yearly = f.groupby("Crop_Year")["Production"].sum().reset_index()
        fig = px.line(yearly, x="Crop_Year", y="Production", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Production by Season")
        seas = f.groupby("Season")["Production"].sum().reset_index()
        fig = px.pie(seas, names="Season", values="Production", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top 10 Crops by Production")
        top = f.groupby("Crop")["Production"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top, x="Production", y="Crop", orientation="h", color="Production",
                     color_continuous_scale="Greens")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Regional Distribution (State-wise Production)")
        state_prod = f.groupby("State_Name")["Production"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(state_prod, x="Production", y="State_Name", orientation="h", color="Production",
                     color_continuous_scale="Blues")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Crop vs Decade Production Heatmap")
    pivot = f.pivot_table(index="Crop", columns="Decade", values="Production", aggfunc="sum", fill_value=0)
    if not pivot.empty:
        pivot_norm = pivot.div(pivot.max(axis=1).replace(0, 1), axis=0)
        fig = px.imshow(pivot_norm, color_continuous_scale="YlGnBu", aspect="auto",
                         labels=dict(color="Relative Intensity"))
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔍 View filtered raw data"):
        st.dataframe(f, use_container_width=True)

# ---------------------------------------------------------------
# TAB 2 — Farmer scenario
# ---------------------------------------------------------------
with tab2:
    st.markdown(
        "**Rajesh, a small-scale farmer in Uttar Pradesh**, wants to know which "
        "crops/seasons perform best so he can reduce risk and maximize yield."
    )
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Seasonal Crop Trends")
        seas_stats = seasonal_trends(f)
        st.dataframe(seas_stats.style.format("{:,.2f}"), use_container_width=True)

    with colB:
        state_choice = st.selectbox(
            "Pick a state to see its best-performing crops (by yield)",
            sorted(f["State_Name"].unique()) if not f.empty else [],
        )
        if state_choice:
            best = best_crops_for_state(f, state_choice).reset_index()
            best.columns = ["Crop", "Avg Yield (t/ha)"]
            fig = px.bar(best, x="Avg Yield (t/ha)", y="Crop", orientation="h", color="Avg Yield (t/ha)",
                         color_continuous_scale="Greens")
            st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Takeaway for farmers:** Favor crops with consistently higher yield "
        "in your state/season combination, and diversify across Kharif/Rabi "
        "to spread weather risk."
    )

# ---------------------------------------------------------------
# TAB 3 — Policy analyst scenario
# ---------------------------------------------------------------
with tab3:
    st.markdown(
        "**Ananya, a Ministry of Agriculture policy analyst**, needs to spot "
        "low-yield regions and long-term trends to guide resource allocation."
    )

    colA, colB = st.columns(2)
    with colA:
        st.subheader("States Ranked by Average Yield (lowest first)")
        yld = state_yield_ranking(f).reset_index()
        yld.columns = ["State", "Avg Yield (t/ha)"]
        fig = px.bar(yld, x="Avg Yield (t/ha)", y="State", orientation="h", color="Avg Yield (t/ha)",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.subheader("Long-term National Production Trend")
        yearly = yearly_production_trend(f).reset_index()
        yearly.columns = ["Year", "Total Production"]
        fig = px.area(yearly, x="Year", y="Total Production")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Lowest-Yield State–Crop Pairs (candidates for intervention)")
    low_pairs = low_yield_state_crop_pairs(f)
    st.dataframe(low_pairs.head(15), use_container_width=True)

    st.info(
        "**Takeaway for policymakers:** States/crops in the table above show the "
        "weakest yields and may benefit most from irrigation, subsidy, or "
        "extension-service investment."
    )

# ---------------------------------------------------------------
# TAB 4 — Investor scenario
# ---------------------------------------------------------------
with tab4:
    st.markdown(
        "**Vikram, an agribusiness investor**, wants high-growth crops and "
        "regions with consistent, low-risk production growth."
    )

    colA, colB = st.columns(2)
    with colA:
        st.subheader(f"Crop CAGR ({int(f['Crop_Year'].min()) if not f.empty else '-'}–"
                      f"{int(f['Crop_Year'].max()) if not f.empty else '-'})")
        cagr = crop_growth_rate(f).reset_index()
        cagr.columns = ["Crop", "CAGR (%)"]
        fig = px.bar(cagr, x="CAGR (%)", y="Crop", orientation="h", color="CAGR (%)",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.subheader("Emerging Crops (recent growth)")
        emerging = emerging_crops(f).reset_index()
        emerging.columns = ["Crop", "Recent Growth (%)"]
        fig = px.bar(emerging, x="Recent Growth (%)", y="Crop", orientation="h", color="Recent Growth (%)",
                     color_continuous_scale="Purples")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Most Consistent (Low-Risk) States by Production")
    cv = consistent_growth_states(f).reset_index()
    st.dataframe(cv, use_container_width=True)

    st.info(
        "**Takeaway for investors:** High CAGR + low coefficient-of-variation "
        "(cv) signals a crop/region combination with strong, steady growth — "
        "generally lower risk for investment."
    )

st.markdown("---")
st.caption("Built with Python, Pandas, Plotly & Streamlit — no Tableau license required.")