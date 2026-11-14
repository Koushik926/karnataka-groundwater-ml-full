# Week 4 Task 4 – Core Implementation

**Project:** Spatio-Temporal Prediction and Risk Mapping of Groundwater Depletion in Karnataka Using Machine Learning  
**Problem ID:** `CAIML_Shobha_Rani_4_PS_160`  
**Milestone:** ~30 % of the overall project (Module 1 + shared data pipeline)

---

## What is implemented here

This folder contains the **core implementation** of the system described in the
Week 2 / Week 3 design documents:

| Component | Status | Notes |
|-----------|--------|-------|
| Shared data pipeline | ✅ working | `src/pipeline.py` – loads the real CGWB export from `data/raw/`, joins NASA POWER rainfall, builds 15 features. No synthetic fallback. |
| Module 1 – GWL prediction | ✅ working | Trains Random Forest, XGBoost, SVR and a small LSTM; selects the best model on validation RMSE; writes predictions + model metadata |
| Module 2 – risk mapping | planned | AHP-weighted indicators, Jenks classification, Kriging surface |
| Dashboard (Streamlit/Plotly) | ✅ working | `streamlit run dashboard.py` – reads `outputs/` and `models/`, so it cannot drift from the code |

## Directory layout

```
Week4_Task4_Core_Implementation/
├── data/raw/          # CGWB exports, extraction table, NASA POWER rainfall
├── models/            # Best-model metadata (module1_best_model.json)
├── outputs/           # Test predictions (module1_test_predictions.csv)
├── scripts/           # Helper scripts (paper downloads, etc.)
├── src/
│   ├── __init__.py
│   ├── main.py        # Entry point – runs the full Module 1 pipeline
│   └── pipeline.py    # Data loading, model training, evaluation
├── requirements.txt
└── README.md
```

## How to run

```bash
cd Week4_Task4_Core_Implementation
pip install -r requirements.txt
python -m src.main
```

The script will:

1. Load the real CGWB data and build the station feature table.
2. Split chronologically **by observation date**: train 1996–2017,
   validation 2017–2020, test 2020–2024.
3. Train Random Forest, XGBoost and SVR and compare them with a
   last-observed-value baseline.
4. Pick the best model on validation RMSE, refit on train+val, evaluate on the
   most recent seasons.
5. Forecast four quarters ahead per station and compute Mann–Kendall / Sen's
   slope trends.
6. Build taluk indicators and run Module 2, writing
   `outputs/module2_risk_mapping.csv`.

Outputs: `module1_test_predictions.csv`, `module1_station_forecasts.csv`,
`module1_district_trends.csv`, `module2_district_indicators.csv`,
`module2_risk_mapping.csv`, `models/module1_best_model.json`.

## The data

`data/raw/` already holds everything the pipeline needs:

| File | What it is |
|------|------------|
| `gwl_karnataka_1991_2020.csv`, `gwl_karnataka_2021_2025.csv` | CGWB quarterly observations from India-WRIS |
| `gwl_karnataka_clean.csv` | the two exports merged and cleaned (123,391 records, 2,769 stations) |
| `karnataka_gw_extraction_2020.csv` | CGWB Dynamic Groundwater Resources 2020, 227 taluks — used only for validation, never as a model input |
| `rainfall_taluk_daily.csv` | NASA POWER daily rainfall, 1996–2024 |

Re-download the rainfall with `python -m src.rainfall` (about 70 seconds). The feature
table is built in memory by `create_station_features()`; there is no `features.csv`.

## Next steps

* [x] Real data pipeline (CGWB export + NASA POWER rainfall).
* [x] Trend analysis (Mann–Kendall / Sen's slope).
* [x] Module 2 risk mapping, validated against CGWB at taluk level.
* [ ] Fetch the 8 remaining papers listed in `papers/TO_DOWNLOAD.txt`.
* [ ] SHAP explanations and a Kriging risk surface (Phase 2).
* [ ] Deep-well or extraction data to address the 0.45 recall limitation (Phase 2).
