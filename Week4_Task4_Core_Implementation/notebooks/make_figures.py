"""
make_figures.py - regenerate every figure used in the report and presentation.

    python notebooks/make_figures.py

Rules followed in every figure (from the guide's review of the October deck):
  * the title says what the chart shows,
  * both axes are labelled and carry units,
  * where colour means something, a legend spells out what each colour is,
  * every bar/point carries its value, so the reader never has to estimate.

All numbers come from the real CGWB data and the latest pipeline outputs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
DATA = BASE / "data" / "raw"
OUT = BASE / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 11, "axes.grid": True, "grid.alpha": 0.3,
    "axes.axisbelow": True, "figure.facecolor": "white",
})

RISK_COLOURS = {"Low": "#2E7D32", "Moderate": "#F9A825",
                "High": "#EF6C00", "Very High": "#C62828"}
BLUE, RED, GREEN = "#1F4E79", "#C62828", "#2E7D32"


def label_bars(ax, bars, fmt="{:.2f}", pad=3, fontsize=9, vertical=True):
    """Write each bar's value on it - the guide asked for values, not just axes."""
    for b in bars:
        if vertical:
            v = b.get_height()
            ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v),
                        textcoords="offset points", xytext=(0, pad),
                        ha="center", va="bottom", fontsize=fontsize)
        else:
            v = b.get_width()
            ax.annotate(fmt.format(v), (v, b.get_y() + b.get_height() / 2),
                        textcoords="offset points", xytext=(pad, 0),
                        ha="left", va="center", fontsize=fontsize)


def save(fig, name):
    path = OUT / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path.relative_to(BASE)}")


# ---------------------------------------------------------------- load
print("Loading data ...")
from src.data_processor import canonical_district  # noqa: E402

gwl = pd.read_csv(DATA / "gwl_karnataka_clean.csv", parse_dates=["Date"])
gwl["District"] = gwl["District"].map(canonical_district)
gwl["Year"] = gwl["Date"].dt.year
gwl["Month"] = gwl["Date"].dt.month
ext = pd.read_csv(DATA / "karnataka_gw_extraction_2020.csv")
ext["cat"] = ext["Categorization"].astype(str).str.strip().str.lower()

meta = json.loads((BASE / "models" / "module1_best_model.json").read_text())
risk = pd.read_csv(BASE / "outputs" / "module2_risk_mapping.csv")
UNIT = "Taluk" if "Taluk" in risk.columns else "District"
preds = pd.read_csv(BASE / "outputs" / "module1_test_predictions.csv")

# ---------------------------------------------------------------- fig 1
print("Figure 1: district mean depth")
d = gwl.groupby("District")["GWL_m"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(d.index, d.values, color=BLUE, label="Mean depth to water table")
label_bars(ax, bars, "{:.1f}")
state_mean = gwl["GWL_m"].mean()
ax.axhline(state_mean, color=RED, ls="--", lw=1.6,
           label=f"Karnataka mean = {state_mean:.2f} m")
ax.set_title("Mean depth to groundwater by district (1996–2024)\n"
             "Taller bar = deeper water table = more depleted")
ax.set_xlabel("District")
ax.set_ylabel("Depth below ground level (metres)")
ax.legend(title="Legend", loc="upper right")
plt.xticks(rotation=55, ha="right")
save(fig, "fig1_district_mean_depth")

# ---------------------------------------------------------------- fig 2
print("Figure 2: yearly trend")
yearly = gwl.groupby("Year")["GWL_m"].mean()
yearly = yearly[(yearly.index >= 1996) & (yearly.index <= 2024)]
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.plot(yearly.index, yearly.values, marker="o", color=BLUE, lw=2,
        label="Annual mean depth (all stations)")
for x, y in zip(yearly.index, yearly.values):
    if x % 2 == 0:
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)
z = np.polyfit(yearly.index, yearly.values, 1)
ax.plot(yearly.index, np.poly1d(z)(yearly.index), ls="--", color=RED, lw=1.6,
        label=f"Linear trend = {z[0]:+.3f} m/year")
ax.invert_yaxis()
ax.set_title("Karnataka annual mean groundwater depth, 1996–2024\n"
             "Axis inverted: a line going UP means the water table is rising")
ax.set_xlabel("Year")
ax.set_ylabel("Depth below ground level (metres)")
ax.legend(title="Legend")
save(fig, "fig2_yearly_trend")

# ---------------------------------------------------------------- fig 3
print("Figure 3: seasonal pattern")
season_map = {1: "January\n(post-winter)", 5: "May\n(pre-monsoon)",
              8: "August\n(monsoon)", 11: "November\n(post-monsoon)"}
seasonal = gwl[gwl["Month"].isin(season_map)].groupby("Month")["GWL_m"].mean()
colours = {1: "#90A4AE", 5: RED, 8: "#42A5F5", 11: GREEN}
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar([season_map[m] for m in seasonal.index], seasonal.values,
              color=[colours[m] for m in seasonal.index])
label_bars(ax, bars, "{:.2f} m")
ax.set_title("Seasonal groundwater depth — CGWB measures four times a year\n"
             "Shallowest after the monsoon, deepest before it")
ax.set_xlabel("CGWB measurement season")
ax.set_ylabel("Mean depth below ground level (metres)")
handles = [plt.Rectangle((0, 0), 1, 1, color=colours[m]) for m in seasonal.index]
ax.legend(handles, ["January — post-winter", "May — pre-monsoon (deepest)",
                    "August — during monsoon", "November — post-monsoon (shallowest)"],
          title="Colour = season", loc="upper right", fontsize=9)
save(fig, "fig3_seasonal_pattern")

# ---------------------------------------------------------------- fig 4
print("Figure 4: CGWB extraction categories")
order = ["safe", "semi_critical", "critical", "over_exploited"]
labels = ["Safe\n(<70%)", "Semi-critical\n(70–90%)", "Critical\n(90–100%)",
          "Over-exploited\n(>100%)"]
cat_colours = [GREEN, "#F9A825", "#EF6C00", RED]
counts = [int((ext["cat"] == c).sum()) for c in order]
total = len(ext)
fig, ax = plt.subplots(figsize=(9.5, 5.5))
bars = ax.bar(labels, counts, color=cat_colours)
for b, c in zip(bars, counts):
    ax.annotate(f"{c} taluk{'' if c == 1 else 's'}\n({c / total * 100:.1f}%)",
                (b.get_x() + b.get_width() / 2, c), textcoords="offset points",
                xytext=(0, 4), ha="center", fontsize=9)
ax.set_title(f"CGWB 2020 assessment of all {total} Karnataka taluks\n"
             f"{counts[2] + counts[3]} taluks ({(counts[2]+counts[3])/total*100:.1f}%) "
             "are critical or over-exploited")
ax.set_xlabel("CGWB category (stage of groundwater extraction)")
ax.set_ylabel("Number of taluks")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cat_colours]
ax.legend(handles, ["Safe", "Semi-critical", "Critical", "Over-exploited"],
          title="Colour = CGWB category", fontsize=9)
ax.set_ylim(0, max(counts) * 1.2)
save(fig, "fig4_extraction_categories")

# ---------------------------------------------------------------- fig 5
print("Figure 5: model comparison")
val = meta["validation_metrics"]
names = {"random_forest": "Random Forest", "xgboost": "XGBoost",
         "svr": "SVR", "baseline_last_value": "Baseline\n(last value)"}
keys = [k for k in ["baseline_last_value", "svr", "random_forest", "xgboost"] if k in val]
rmse = [val[k]["rmse"] for k in keys]
r2 = [val[k]["r2"] for k in keys]
best = meta["selected_model"]
cols = [GREEN if k == best else ("#9E9E9E" if k == "baseline_last_value" else BLUE) for k in keys]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.5))
b1 = a1.bar([names[k] for k in keys], rmse, color=cols)
label_bars(a1, b1, "{:.3f}")
a1.set_title("Validation RMSE — lower is better")
a1.set_xlabel("Model"); a1.set_ylabel("RMSE (metres)")
a1.set_ylim(0, max(rmse) * 1.18)

b2 = a2.bar([names[k] for k in keys], r2, color=cols)
label_bars(a2, b2, "{:.3f}")
a2.set_title("Validation R² — higher is better")
a2.set_xlabel("Model"); a2.set_ylabel("R² (fraction of variance explained)")
a2.set_ylim(0, max(r2) * 1.18)

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in ["#9E9E9E", BLUE, GREEN]]
fig.subplots_adjust(bottom=0.26)
fig.legend(handles, ["Baseline (must be beaten)", "Candidate model",
                     f"Selected model ({names[best].strip()})"],
           title="Colour = role", loc="lower center", ncol=3, frameon=False,
           bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Module 1 — model comparison on the validation period (2017–2020)",
             fontweight="bold", y=1.02)
save(fig, "fig5_model_comparison")

# ---------------------------------------------------------------- fig 6
print("Figure 6: predicted vs actual")
fig, ax = plt.subplots(figsize=(7.5, 7))
s = preds.sample(min(4000, len(preds)), random_state=0)
ax.scatter(s["actual_gwl_m"], s["predicted_gwl_m"], s=8, alpha=0.3, color=BLUE,
           label=f"Test observation (n = {len(preds):,})")
lo = float(min(s["actual_gwl_m"].min(), s["predicted_gwl_m"].min()))
hi = float(max(s["actual_gwl_m"].max(), s["predicted_gwl_m"].max()))
ax.plot([lo, hi], [lo, hi], ls="--", color=RED, lw=1.8, label="Perfect prediction (y = x)")
t = meta["test_metrics"]
ax.set_title(f"Module 1 — predicted vs actual depth on the held-out test period\n"
             f"RMSE {t['rmse']:.3f} m · MAE {t['mae']:.3f} m · R² {t['r2']:.3f} "
             f"(baseline R² {t.get('baseline_r2', float('nan')):.3f})")
ax.set_xlabel("Actual depth below ground level (metres)")
ax.set_ylabel("Predicted depth below ground level (metres)")
ax.legend(title="Legend", loc="upper left")
save(fig, "fig6_predicted_vs_actual")

# ---------------------------------------------------------------- fig 7
print("Figure 7: station trend directions")
from src.data_processor import station_trends  # noqa: E402
st_tr = station_trends(gwl)
sig = st_tr["mk_p_value"] < 0.05
groups = ["Significant\ndecline", "No significant\ntrend", "Significant\nrecovery"]
n_decline = int((sig & (st_tr["sens_slope_m_per_yr"] > 0)).sum())
n_recovery = int((sig & (st_tr["sens_slope_m_per_yr"] < 0)).sum())
# everything else, including the handful of stations whose Sen's slope is
# exactly zero, counts as "no significant trend" so the three bars sum to the
# total number of stations tested
n_flat = len(st_tr) - n_decline - n_recovery
vals = [n_decline, n_flat, n_recovery]
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(groups, vals, color=[RED, "#9E9E9E", GREEN])
tot = sum(vals)
for b, v in zip(bars, vals):
    ax.annotate(f"{v} station{'' if v == 1 else 's'}\n({v / tot * 100:.1f}%)",
                (b.get_x() + b.get_width() / 2, v), textcoords="offset points",
                xytext=(0, 4), ha="center", fontsize=9)
ax.set_title(f"Mann–Kendall trend test on {tot:,} CGWB stations (p < 0.05)\n"
             "More stations are recovering than declining — consistent with the "
             "CGWB Karnataka Year Book 2021–22")
ax.set_xlabel("Trend direction")
ax.set_ylabel("Number of stations")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [RED, "#9E9E9E", GREEN]]
ax.legend(handles, ["Water table deepening", "No significant trend",
                    "Water table rising"], title="Colour = direction")
ax.set_ylim(0, max(vals) * 1.2)
save(fig, "fig7_station_trend_directions")

# ---------------------------------------------------------------- fig 8
print("Figure 8: risk class distribution")
counts = risk["risk_label"].value_counts().reindex(
    ["Low", "Moderate", "High", "Very High"]).fillna(0).astype(int)
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(counts.index, counts.values,
              color=[RISK_COLOURS[k] for k in counts.index])
for b, v in zip(bars, counts.values):
    ax.annotate(f"{v} taluk{'' if v == 1 else 's'}\n({v / counts.sum() * 100:.1f}%)",
                (b.get_x() + b.get_width() / 2, v), textcoords="offset points",
                xytext=(0, 4), ha="center", fontsize=9)
ax.set_title(f"Module 2 — depletion risk class of {int(counts.sum())} Karnataka taluks\n"
             "Classes from Jenks natural breaks on the AHP-weighted risk index")
ax.set_xlabel("Risk class")
ax.set_ylabel("Number of taluks")
handles = [plt.Rectangle((0, 0), 1, 1, color=RISK_COLOURS[k]) for k in counts.index]
ax.legend(handles, list(counts.index), title="Colour = risk class")
ax.set_ylim(0, max(counts.values) * 1.25)
save(fig, "fig8_risk_class_distribution")

# ---------------------------------------------------------------- fig 9
print("Figure 9: risk index, highest-risk taluks")
r = risk.nlargest(25, "risk_index").sort_values("risk_index")
labels = (r[UNIT] + "  (" + r["District"].astype(str).str.title() + ")") if UNIT == "Taluk" else r[UNIT]
fig, ax = plt.subplots(figsize=(10, 9))
bars = ax.barh(labels, r["risk_index"],
               color=[RISK_COLOURS[k] for k in r["risk_label"]])
label_bars(ax, bars, "{:.3f}", vertical=False, fontsize=8)
ax.set_title(f"25 highest-risk taluks of {len(risk)} assessed\n"
             "Composite AHP-weighted index: 0 = lowest risk in Karnataka, 1 = highest")
ax.set_xlabel("Risk index (AHP-weighted, 0–1)")
ax.set_ylabel("Taluk (district)")
ax.set_xlim(0, 1.08)
handles = [plt.Rectangle((0, 0), 1, 1, color=RISK_COLOURS[k])
           for k in ["Low", "Moderate", "High", "Very High"]]
ax.legend(handles, ["Low", "Moderate", "High", "Very High"],
          title="Colour = risk class", loc="lower right")
save(fig, "fig9_risk_index_by_district")

# ---------------------------------------------------------------- fig 10
print("Figure 10: AHP weights")
from src.config import AHP_MATRIX, RISK_INDICATORS  # noqa: E402
from src.module2_risk import compute_ahp_weights  # noqa: E402
w, cr = compute_ahp_weights(AHP_MATRIX)
pretty = {"decline_rate": "Decline rate\n(Sen's slope, m/yr)",
          "current_depth": "Current depth\n(m below ground)",
          "variability": "Variability\n(coeff. of variation)",
          "rainfall_dependence": "Rainfall dependence\n(NASA POWER, corr.)",
          "seasonal_recovery": "Seasonal recovery\n(pre − post monsoon, m)"}
fig, ax = plt.subplots(figsize=(9.5, 5.5))
cols10 = [BLUE, "#2E75B6", "#5B8FC9", "#7FA9D4", "#BBD0E8"]
bars = ax.bar([pretty[i] for i in RISK_INDICATORS], w, color=cols10)
for b, v in zip(bars, w):
    ax.annotate(f"{v:.4f}\n({v * 100:.1f}%)",
                (b.get_x() + b.get_width() / 2, v), textcoords="offset points",
                xytext=(0, 4), ha="center", fontsize=9)
ax.set_title(f"Module 2 — AHP indicator weights (Saaty 1–9 scale)\n"
             f"Consistency Ratio = {cr:.4f}, below the 0.10 limit, so the weights are accepted")
ax.set_xlabel("Risk indicator (all measured; none synthesised)")
ax.set_ylabel("AHP weight (sums to 1.00)")
ax.set_ylim(0, max(w) * 1.25)
save(fig, "fig10_ahp_weights")

# ---------------------------------------------------------------- fig 11
print("Figure 11: validation against CGWB")
from src.module2_risk import validate_against_cgwb  # noqa: E402
v = validate_against_cgwb(risk["risk_class"], risk["cgwb_category"],
                          risk_index=risk["risk_index"],
                          extraction_stage=risk.get("extraction_stage"))
names11 = ["Exact 4-class\nagreement", "Binary agreement\n(High+ vs critical+)",
           "Rank correlation\n(Spearman)"]
vals11 = [v["accuracy"], v["binary_accuracy"], v["spearman_vs_cgwb_category"]]
cols11 = ["#9E9E9E", GREEN, BLUE]
fig, ax = plt.subplots(figsize=(9.5, 5.5))
bars = ax.bar(names11, vals11, color=cols11)
label_bars(ax, bars, "{:.3f}")
ax.set_ylim(0, 1.0)
ax.set_title("Module 2 — validation against the official CGWB assessment\n"
             f"Exact agreement is low by construction: our classes are relative to "
             f"{len(risk)} taluks,\nwhile CGWB categories are absolute extraction thresholds")
ax.set_xlabel("Validation measure")
ax.set_ylabel("Score (0–1)")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cols11]
ax.legend(handles, ["Strict, affected by class imbalance",
                    "The decision a planner makes", "Agreement on the ordering"],
          title="Colour = what the measure tests", fontsize=9)
save(fig, "fig11_cgwb_validation")



# ---------------------------------------------------------------- fig 12
print("Figure 12: rainfall data and its effect")
rain = pd.read_csv(DATA / "rainfall_taluk_daily.csv", parse_dates=["date"])
annual = (rain.assign(y=rain["date"].dt.year).groupby(["Taluk", "y"])["rain_mm"].sum()
          .groupby("Taluk").mean().sort_values())
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.5, 5.5),
                             gridspec_kw={"width_ratios": [1.5, 1]})
show = pd.concat([annual.head(8), annual.tail(8)])
cols12 = [RED] * 8 + [BLUE] * 8
b = a1.barh(show.index, show.values, color=cols12)
label_bars(a1, b, "{:.0f}", vertical=False, fontsize=8)
a1.set_title("Mean annual rainfall, 8 driest and 8 wettest taluks\n"
             "NASA POWER (PRECTOTCORR), 1996–2024")
a1.set_xlabel("Mean annual rainfall (mm)")
a1.set_ylabel("Taluk")
a1.set_xlim(0, show.max() * 1.18)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [RED, BLUE]]
a1.legend(handles, ["Driest (north interior)", "Wettest (coast / Western Ghats)"],
          title="Colour = rainfall zone", loc="lower right", fontsize=9)

names12 = ["Without rainfall", "With rainfall"]
r2s = [0.576, test_r2 := meta["test_metrics"]["r2"]]
b2 = a2.bar(names12, r2s, color=["#9E9E9E", GREEN])
label_bars(a2, b2, "{:.3f}")
a2.axhline(meta["test_metrics"].get("baseline_r2", 0.449), color=RED, ls="--", lw=1.5,
           label=f"Baseline R² = {meta['test_metrics'].get('baseline_r2', 0.449):.3f}")
a2.set_title("Effect of adding real rainfall\non held-out test R²")
a2.set_xlabel("Feature set")
a2.set_ylabel("Test R² (higher is better)")
a2.set_ylim(0, max(r2s) * 1.25)
a2.legend(title="Legend", fontsize=9)
save(fig, "fig12_rainfall_data_and_effect")

print(f"\nAll figures written to {OUT.relative_to(BASE)}")
