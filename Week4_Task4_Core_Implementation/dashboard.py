"""
Streamlit dashboard - Karnataka groundwater depletion prediction and risk mapping.

Run with:  streamlit run dashboard.py

Every number shown here is read from the pipeline's own output files
(`outputs/`, `models/`).  Nothing is hard-coded, so the dashboard can never
drift away from the last real run - the earlier version displayed figures that
had been copied in by hand and were no longer true.

Chart rules followed throughout (review feedback):
  * every colour is explained by a legend or an axis label,
  * every bar/point carries its value,
  * units are stated (metres, m/year, %).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Karnataka Groundwater Risk Dashboard",
                   page_icon="💧", layout="wide")

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"

RISK_COLOURS = {"Low": "#2E7D32", "Moderate": "#F9A825",
                "High": "#EF6C00", "Very High": "#C62828"}
RISK_ORDER = ["Low", "Moderate", "High", "Very High"]

# Plotly renamed the tile-map API: px.scatter_mapbox (<=5.x) became px.scatter_map
# (>=6), and the old name was removed in 7.  requirements.txt pins 5.24.0, but an
# examiner running a newer plotly would otherwise hit an AttributeError mid-demo,
# so pick whichever exists and use the matching layout key.
if hasattr(px, "scatter_mapbox"):
    _scatter_map, _map_style_key = px.scatter_mapbox, "mapbox_style"
else:
    _scatter_map, _map_style_key = px.scatter_map, "map_style"


@st.cache_data
def load_metadata():
    path = MODEL_DIR / "module1_best_model.json"
    return json.loads(path.read_text()) if path.exists() else None


@st.cache_data
def load_csv(name: str):
    path = OUTPUT_DIR / name
    return pd.read_csv(path) if path.exists() else None


meta = load_metadata()
risk = load_csv("module2_risk_mapping.csv")
preds = load_csv("module1_test_predictions.csv")
trends = load_csv("module1_district_trends.csv")

st.title("💧 Karnataka Groundwater Depletion Risk Dashboard")
st.caption("Spatio-temporal prediction and risk mapping · CAIML_Shobha_Rani_4_PS_160")

if meta is None:
    st.error("No model metadata found. Run `python -m src.main` first.")
    st.stop()

st.sidebar.header("Navigation")
page = st.sidebar.radio("Select view",
                        ["Overview", "Module 1: Prediction", "Module 2: Risk Mapping"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Data source: {meta.get('data_source', 'unknown')}")

test = meta.get("test_metrics", {})
val = meta.get("validation_metrics", {})
split = meta.get("split", {})

# ===========================================================================
if page == "Overview":
    st.subheader("What this system does")
    c1, c2 = st.columns(2)
    c1.markdown(
        "**Module 1 — Groundwater level prediction**  \n"
        "Predicts the next quarter's depth to water for every CGWB station, and "
        "estimates each district's long-term trend with the Mann–Kendall test and "
        "Sen's slope."
    )
    c2.markdown(
        "**Module 2 — Depletion risk mapping**  \n"
        "Turns Module 1's district trends plus current conditions into a composite "
        "risk index (AHP weights, Jenks classes) and validates it against the CGWB "
        "assessment categories."
    )

    st.markdown("---")
    st.subheader("Headline numbers from the last run")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Best model", meta.get("selected_model", "–").upper())
    k2.metric("Test RMSE", f"{test.get('rmse', float('nan')):.3f} m",
              help="Error on the most recent held-out seasons. Lower is better.")
    k3.metric("Test R²", f"{test.get('r2', float('nan')):.3f}",
              delta=f"{test.get('r2', 0) - test.get('baseline_r2', 0):+.3f} vs baseline",
              help="Baseline = predict the last observed value.")
    if risk is not None:
        high = int((risk["risk_class"] >= 3).sum())
        k4.metric("Taluks at High/Very High risk",
                  f"{high} of {len(risk)}", f"{high / len(risk) * 100:.0f}%")

    if split:
        st.caption(
            f"Chronological split — train {split['train']['from']} to {split['train']['to']} "
            f"({split['train']['rows']:,} rows) · "
            f"validation {split['val']['from']} to {split['val']['to']} "
            f"({split['val']['rows']:,}) · "
            f"test {split['test']['from']} to {split['test']['to']} "
            f"({split['test']['rows']:,})"
        )

# ===========================================================================
elif page == "Module 1: Prediction":
    st.subheader("Model comparison on the validation set")
    rows = [{"Model": k.replace("_", " ").title(),
             "RMSE (m)": round(v["rmse"], 3),
             "MAE (m)": round(v["mae"], 3),
             "R²": round(v["r2"], 3)} for k, v in val.items()]
    table = pd.DataFrame(rows).sort_values("RMSE (m)")
    st.dataframe(table, use_container_width=True, hide_index=True)

    fig = px.bar(table, x="Model", y="RMSE (m)", text="RMSE (m)",
                 color="Model",
                 title="Validation RMSE by model — lower is better (metres)")
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="RMSE (metres)",
                      legend_title_text="Model (colour)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Selected model: **{meta.get('selected_model','–').upper()}** (lowest validation RMSE). "
        "The baseline predicts that the next reading equals the last observed reading; "
        "a useful model must beat it."
    )

    st.markdown("---")
    st.subheader("Held-out test performance")
    t1, t2, t3 = st.columns(3)
    t1.metric("RMSE", f"{test.get('rmse', float('nan')):.3f} m",
              f"{test.get('rmse',0)-test.get('baseline_rmse',0):+.3f} vs baseline")
    t2.metric("MAE", f"{test.get('mae', float('nan')):.3f} m")
    t3.metric("R²", f"{test.get('r2', float('nan')):.3f}",
              f"{test.get('r2',0)-test.get('baseline_r2',0):+.3f} vs baseline")

    if preds is not None and {"actual_gwl_m", "predicted_gwl_m"}.issubset(preds.columns):
        st.subheader("Predicted vs actual depth on the test set")
        sample = preds.sample(min(3000, len(preds)), random_state=0)
        fig = px.scatter(sample, x="actual_gwl_m", y="predicted_gwl_m",
                         opacity=0.35,
                         labels={"actual_gwl_m": "Actual depth (metres below ground)",
                                 "predicted_gwl_m": "Predicted depth (metres below ground)"},
                         title="Each point is one station-quarter; the dashed line is a perfect prediction")
        lo = float(min(sample["actual_gwl_m"].min(), sample["predicted_gwl_m"].min()))
        hi = float(max(sample["actual_gwl_m"].max(), sample["predicted_gwl_m"].max()))
        fig.add_shape(type="line", x0=lo, y0=lo, x1=hi, y1=hi,
                      line=dict(dash="dash", color="#C62828"))
        st.plotly_chart(fig, use_container_width=True)

    if trends is not None:
        st.subheader("Predicted trend by district (Sen's slope, metres per year)")
        t = trends.sort_values("predicted_decline_rate", ascending=False)
        t["Direction"] = t["predicted_decline_rate"].apply(
            lambda v: "Deepening (depletion)" if v > 0 else "Rising (recovery)")
        fig = px.bar(t, x="predicted_decline_rate", y="District", orientation="h",
                     text=t["predicted_decline_rate"].round(3),
                     color="Direction",
                     color_discrete_map={"Deepening (depletion)": "#C62828",
                                         "Rising (recovery)": "#2E7D32"},
                     title="Positive = water table deepening · Negative = water table rising")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=750, xaxis_title="Trend (metres per year)",
                          legend_title_text="Direction (colour)")
        st.plotly_chart(fig, use_container_width=True)

# ===========================================================================
elif page == "Module 2: Risk Mapping":
    if risk is None:
        st.warning("No risk mapping found. Run `python -m src.main` first.")
        st.stop()

    st.subheader("Risk class by taluk")
    counts = (risk["risk_label"].value_counts()
              .reindex(RISK_ORDER).fillna(0).astype(int).reset_index())
    counts.columns = ["Risk class", "Districts"]
    fig = px.bar(counts, x="Risk class", y="Districts", text="Districts",
                 color="Risk class", color_discrete_map=RISK_COLOURS,
                 category_orders={"Risk class": RISK_ORDER},
                 title="Number of taluks in each risk class")
    fig.update_traces(textposition="outside")
    fig.update_layout(legend_title_text="Risk class (colour)",
                      yaxis_title="Number of taluks")
    st.plotly_chart(fig, use_container_width=True)

    if {"lat", "lon"}.issubset(risk.columns):
        st.subheader("Where the risk is")
        fig = _scatter_map(
            risk, lat="lat", lon="lon", color="risk_label",
            color_discrete_map=RISK_COLOURS,
            category_orders={"risk_label": RISK_ORDER},
            size=risk["risk_index"].clip(lower=0.05) * 30,
            hover_name="Taluk",
            hover_data={"risk_index": ":.3f", "current_depth": ":.2f",
                        "decline_rate": ":.3f", "lat": False, "lon": False},
            zoom=5.3, height=560,
            # plotly 5 auto-fitted the view to the points; plotly 7 does not, and
            # without an explicit centre the map opens at (0, 0) in the Atlantic.
            center={"lat": float(risk["lat"].mean()),
                    "lon": float(risk["lon"].mean())},
            title="Taluk centroids, coloured by risk class and sized by risk index")
        fig.update_layout(**{_map_style_key: "carto-positron"},
                          legend_title_text="Risk class (colour)",
                          margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Composite risk index by taluk")
    r = risk.sort_values("risk_index", ascending=False)
    r = r.assign(unit=r["Taluk"].str.title() + " (" + r["District"].str.title() + ")")
    fig = px.bar(r, x="risk_index", y="unit", orientation="h",
                 text=r["risk_index"].round(3),
                 color="risk_label", color_discrete_map=RISK_COLOURS,
                 category_orders={"risk_label": RISK_ORDER},
                 title="Risk index (0 = lowest risk, 1 = highest) with AHP-weighted indicators")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=750, xaxis_title="Composite risk index (0–1)",
                      legend_title_text="Risk class (colour)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full district table")
    st.dataframe(r, use_container_width=True, hide_index=True)
    st.caption(
        "decline_rate = Sen's slope in metres/year (positive = deepening) · "
        "current_depth = mean depth over the last three years (m) · "
        "variability = coefficient of variation · "
        "seasonal_recovery = pre-monsoon minus post-monsoon depth (m) · "
        "cgwb_category and extraction_stage are used for validation only, never as inputs."
    )

st.markdown("---")
st.caption("CAIML_Shobha_Rani_4_PS_160 · REVA University · figures read live from the "
           "latest pipeline run")
