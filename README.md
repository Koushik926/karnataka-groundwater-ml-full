# Spatio-Temporal Prediction and Risk Mapping of Groundwater Depletion in Karnataka

**Problem ID:** `CAIML_Shobha_Rani_4_PS_160`  
**Center:** CAIML – REVA University, School of CSE, Sem VII  
**Guide:** Ms Indhuja Balakrishnan · **Center Lead:** Dr. M. Shobha Rani

---

## Project structure

```
Project/
├── Week1_Task1_Literature_Survey.{docx,pdf}     # 20-paper survey (2017–2026)
├── Week2_Task2_System_Design.{docx,pdf}        # Layered architecture, DFDs, DB schema
├── Week3_Task3_Detailed_Design.{docx,pdf}      # Full design: UML, ER, class diagrams
├── papers/                                      # Downloaded PDFs + TO_DOWNLOAD.txt
├── week2_diagrams/                              # Architecture, DFDs, flowcharts
├── week3_diagrams/                              # UML, ER, component diagrams
└── Week4_Task4_Core_Implementation/             # Core implementation (Week 4)
    ├── data/raw/                                # CGWB exports + NASA POWER rainfall
    ├── models/                                  # Best-model metadata
    ├── outputs/                                 # Predictions
    ├── scripts/                                 # Helpers (paper downloads)
    ├── src/
    │   ├── __init__.py
    │   ├── config.py                            # AHP matrix, risk classes, defaults
    │   ├── main.py                              # Entry point
    │   └── pipeline.py                          # Module 1 training + evaluation
    ├── requirements.txt
    └── README.md
```

## What is implemented

| Component | Status |
|-----------|--------|
| Data pipeline (load/synthesize → split → train → evaluate → save) | ✅ |
| Module 1 – GWL prediction (RF / XGBoost / SVR + optional LSTM) | ✅ |
| Module 2 – risk mapping (AHP, Jenks, Kriging) | planned |
| Dashboard (Streamlit / Folium) | planned |

## Running the core implementation

```bash
cd Week4_Task4_Core_Implementation
pip install -r requirements.txt
python -m src.main
```

The script will:

1. Load the real CGWB export from `data/raw/` and build the station feature table,
   joining 29 years of NASA POWER rainfall. (There is no synthetic fallback: an earlier
   version looked for a `features.csv` that is never created and silently trained on
   generated data instead.)
2. Split the data chronologically (train / val / test).
3. Train Random Forest, XGBoost and SVR (LSTM is optional – see `src/pipeline.py`).
4. Evaluate on validation (RMSE, MAE, R²) and pick the best model.
5. Re-fit on train+val and evaluate on the test set.
6. Write `outputs/module1_test_predictions.csv` and `models/module1_best_model.json`.

## Remaining work

* Fetch the missing papers listed in `papers/TO_DOWNLOAD.txt`.
* Implement the real data pipeline (CGWB/IMD downloads, raster extraction).
* Add SHAP explanation and trend analysis (Mann–Kendall / Sen's slope).
* Build Module 2 once Module 1 predictions are stable.