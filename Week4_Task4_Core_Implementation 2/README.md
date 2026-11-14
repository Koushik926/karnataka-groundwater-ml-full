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
| Shared data pipeline | scaffolded | `src/pipeline.py` – loads a feature table from `data/raw/features.csv` or generates a synthetic fallback |
| Module 1 – GWL prediction | ✅ working | Trains Random Forest, XGBoost, SVR and a small LSTM; selects the best model on validation RMSE; writes predictions + model metadata |
| Module 2 – risk mapping | planned | AHP-weighted indicators, Jenks classification, Kriging surface |
| Dashboard (Streamlit/Folium) | planned | Reads from `outputs/` |

## Directory layout

```
Week4_Task4_Core_Implementation/
├── data/raw/          # Drop the real feature table here (features.csv)
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

1. Look for `data/raw/features.csv`. If absent, generate a synthetic dataset
   (2000 samples × 15 features) so the code can be exercised immediately.
2. Split the data chronologically (train / val / test).
3. Train Random Forest, XGBoost, SVR and an LSTM.
4. Evaluate on the validation set (RMSE, MAE, R²) and pick the best model.
5. Re-fit the best model on train+val and evaluate on the test set.
6. Write `outputs/module1_test_predictions.csv` and
   `models/module1_best_model.json`.

## Adding real data

Place a CSV at `data/raw/features.csv` with:

* one row per well‑date observation,
* feature columns (lags, rainfall, LULC share, elevation, slope, soil, aquifer, …),
* a column named `target_depth` containing the depth at the **next** observation.

The pipeline will use it automatically.

## Next steps

* [ ] Fetch the remaining papers listed in `papers/TO_DOWNLOAD.txt`.
* [ ] Implement the real data pipeline (CGWB/IMD downloads, raster extraction).
* [ ] Add SHAP explanation and trend analysis (Mann–Kendall / Sen's slope).
* [ ] Build Module 2 (risk mapping) once Module 1 predictions are stable.