#!/usr/bin/env python3
"""
SATURDAY PRESENTATION DEMO SCRIPT
==================================
Run this script to demonstrate the complete system.

Usage:
    python demo_saturday.py

This will:
1. Show dataset summary
2. Run ML model training
3. Show predictions
4. Run risk classification
5. Display results

Perfect for the Saturday review!
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from datetime import datetime

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_section(text):
    print(f"\n{'─'*50}")
    print(f"  {text}")
    print(f"{'─'*50}")

def pause(msg="Press Enter to continue..."):
    input(f"\n  [{msg}]")

def main():
    print_header("GROUNDWATER DEPLETION PREDICTION & RISK MAPPING")
    print("\n  Project: CAIML_Shobha_Rani_4_PS_160")
    print("  Date:", datetime.now().strftime("%d %B %Y"))
    print("  Team: Nitin, Koushik, Varshith, Karthik, Chandrashekar")

    pause("Start Demo")

    # =============================================
    # 1. DATASET OVERVIEW
    # =============================================
    print_header("1. DATASET COLLECTION")

    from src.data_processor import load_gwl_data, load_extraction_data

    print("\n  Loading real Karnataka CGWB data...")
    gwl = load_gwl_data()
    extraction = load_extraction_data()

    print(f"""
  ┌─────────────────────────────────────────────────────┐
  │  GROUNDWATER LEVEL DATA (CGWB via NWDP)            │
  ├─────────────────────────────────────────────────────┤
  │  Total Records:      {len(gwl):>10,}                    │
  │  Districts:          {gwl['District'].nunique():>10}                    │
  │  Stations:           {gwl['Station'].nunique():>10,}                    │
  │  Date Range:         1996 - 2024                    │
  └─────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │  EXTRACTION DATA (CGWB 2020)                        │
  ├─────────────────────────────────────────────────────┤
  │  Taluks Assessed:    {len(extraction):>10}                    │
  │  Over-exploited:     {(extraction['Categorization'].str.lower() == 'over_exploited').sum():>10}                    │
  │  Critical:           {(extraction['Categorization'].str.lower() == 'critical').sum():>10}                    │
  │  Safe:               {(extraction['Categorization'].str.lower() == 'safe').sum():>10}                    │
  └─────────────────────────────────────────────────────┘
    """)

    print("\n  Sample GWL Records:")
    print(gwl[['Station', 'District', 'Date', 'GWL_m']].head(5).to_string(index=False))

    pause("Continue to Data Preprocessing")

    # =============================================
    # 2. DATA PREPROCESSING
    # =============================================
    print_header("2. DATA PREPROCESSING")

    from src.data_processor import create_station_features, prepare_ml_data

    print("\n  Creating ML features from time-series data...")
    features = create_station_features(gwl, min_records=20)
    X, y = prepare_ml_data(features)

    print(f"""
  Preprocessing Steps:
  ✓ Parsed dates and extracted Year/Month/Quarter
  ✓ Removed {123632 - len(gwl)} records: 76 out of range (GWL < 0 or > 100 m)
    plus 165 missing a level, date or district
  ✓ Created lag features (1-4 quarters)
  ✓ Created rolling statistics (mean, std)
  ✓ Added seasonal encoding (sin/cos month)

  Feature Matrix:
  • Samples: {X.shape[0]:,}
  • Features: {X.shape[1]}

  Features Used:
  {list(X.columns)}
    """)

    pause("Continue to Model Training")

    # =============================================
    # 3. MODEL TRAINING
    # =============================================
    print_header("3. ML MODEL TRAINING")

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.svm import SVR
    import xgboost as xgb
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    # Chronological split - NEVER a random split.
    # These are time series with lag features: a random split puts a row's own
    # neighbours (and therefore its lag values) in the training set, which leaks
    # the future into the past and inflates the scores.
    order = features.sort_values('Date').index
    X, y = X.loc[order], y.loc[order]
    n = len(X)
    i_tr, i_va = int(n * 0.70), int(n * 0.85)
    X_train, y_train = X.iloc[:i_tr], y.iloc[:i_tr]
    X_val, y_val = X.iloc[i_tr:i_va], y.iloc[i_tr:i_va]
    X_test, y_test = X.iloc[i_va:], y.iloc[i_va:]
    fill = X_train.median()
    X_train, X_val, X_test = X_train.fillna(fill), X_val.fillna(fill), X_test.fillna(fill)

    print(f"\n  Data Split:")
    print(f"  • Training:   {len(X_train):,} samples")
    print(f"  • Validation: {len(X_val):,} samples")
    print(f"  • Test:       {len(X_test):,} samples")

    print("\n  Training models...")

    # Train models
    models = {}

    print("  [1/3] Training Random Forest...", end=" ", flush=True)
    models['Random Forest'] = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    models['Random Forest'].fit(X_train, y_train)
    print("Done!")

    print("  [2/3] Training XGBoost...", end=" ", flush=True)
    models['XGBoost'] = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    models['XGBoost'].fit(X_train, y_train)
    print("Done!")

    print("  [3/3] Training SVR...", end=" ", flush=True)
    # Use subset for SVR (faster)
    if len(X_train) > 5000:
        X_svr = X_train.sample(5000, random_state=42)
        y_svr = y_train.loc[X_svr.index]
    else:
        X_svr, y_svr = X_train, y_train
    models['SVR'] = SVR(kernel='rbf', C=10)
    models['SVR'].fit(X_svr, y_svr)
    print("Done!")

    pause("Continue to Model Evaluation")

    # =============================================
    # 4. MODEL EVALUATION
    # =============================================
    print_header("4. MODEL EVALUATION")

    print("\n  Evaluating on validation set...\n")

    results = []
    for name, model in models.items():
        preds = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        mae = mean_absolute_error(y_val, preds)
        r2 = r2_score(y_val, preds)
        results.append({'Model': name, 'RMSE': rmse, 'MAE': mae, 'R²': r2})

    results_df = pd.DataFrame(results)

    print("  ┌────────────────┬──────────┬──────────┬──────────┐")
    print("  │     Model      │   RMSE   │   MAE    │    R²    │")
    print("  ├────────────────┼──────────┼──────────┼──────────┤")
    for _, row in results_df.iterrows():
        print(f"  │ {row['Model']:14} │ {row['RMSE']:8.4f} │ {row['MAE']:8.4f} │ {row['R²']:8.4f} │")
    print("  └────────────────┴──────────┴──────────┴──────────┘")

    best_model_name = results_df.loc[results_df['RMSE'].idxmin(), 'Model']
    best_model = models[best_model_name]

    print(f"\n  ★ Best Model: {best_model_name} (Lowest RMSE)")

    # Test set evaluation
    test_preds = best_model.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
    test_r2 = r2_score(y_test, test_preds)

    print(f"\n  Test Set Performance ({best_model_name}):")
    print(f"  • RMSE: {test_rmse:.4f} meters")
    print(f"  • R²:   {test_r2:.4f}")

    pause("Continue to Sample Predictions")

    # =============================================
    # 5. SAMPLE PREDICTIONS
    # =============================================
    print_header("5. SAMPLE PREDICTIONS")

    sample_idx = X_test.head(10).index
    sample_preds = best_model.predict(X_test.loc[sample_idx])
    sample_actual = y_test.loc[sample_idx].values

    print("\n  Comparing Predicted vs Actual Groundwater Levels:")
    print("\n  ┌─────┬──────────────┬──────────────┬──────────────┐")
    print("  │  #  │  Actual (m)  │ Predicted (m)│   Error (m)  │")
    print("  ├─────┼──────────────┼──────────────┼──────────────┤")
    for i, (actual, pred) in enumerate(zip(sample_actual, sample_preds)):
        error = pred - actual
        print(f"  │ {i+1:3} │ {actual:12.2f} │ {pred:12.2f} │ {error:+12.2f} │")
    print("  └─────┴──────────────┴──────────────┴──────────────┘")

    pause("Continue to Risk Classification")

    # =============================================
    # 6. RISK CLASSIFICATION (MODULE 2)
    # =============================================
    print_header("6. RISK CLASSIFICATION (Module 2)")

    from src.module2_risk import run_module2
    from src.data_processor import create_district_indicators

    print("\n  Computing district-level risk indicators...")
    indicators = create_district_indicators(gwl, extraction)

    print("\n  Running AHP-weighted risk classification...")
    risk_result = run_module2(indicators, validate=True)

    print("\n  Risk Class Distribution:")
    dist = risk_result['risk_label'].value_counts()

    print("\n  ┌─────────────────┬─────────┬────────────┐")
    print("  │   Risk Class    │  Count  │ Percentage │")
    print("  ├─────────────────┼─────────┼────────────┤")
    for label in ['Low', 'Moderate', 'High', 'Very High']:
        count = dist.get(label, 0)
        pct = count / len(risk_result) * 100
        print(f"  │ {label:15} │ {count:7} │ {pct:9.1f}% │")
    print("  └─────────────────┴─────────┴────────────┘")

    print("\n  High-Risk Districts:")
    high_risk = risk_result[risk_result['risk_class'] >= 3][['District', 'risk_index', 'risk_label']].head(10)
    print(high_risk.to_string(index=False))

    pause("Continue to Summary")

    # =============================================
    # 7. SUMMARY
    # =============================================
    print_header("DEMO COMPLETE - SUMMARY")

    print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                    PROJECT ACHIEVEMENTS                          ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  ✓ Real CGWB data: {len(gwl):,} groundwater records               ║
  ║  ✓ 33 districts, 2,769 monitoring stations                       ║
  ║  ✓ 28 years of historical data (1996-2024)                       ║
  ║                                                                  ║
  ║  ✓ 3 ML models trained and compared                              ║
  ║  ✓ Best model: {best_model_name:12} (RMSE: {test_rmse:.2f}m)               ║
  ║                                                                  ║
  ║  ✓ AHP risk classification completed                             ║
  ║  ✓ {(risk_result['risk_class'] >= 3).sum()} districts identified as High/Very High risk          ║
  ║                                                                  ║
  ║  ✓ Interactive dashboard ready                                   ║
  ║  ✓ 10 EDA visualizations generated                               ║
  ╚══════════════════════════════════════════════════════════════════╝

  To launch the dashboard:
    $ streamlit run dashboard.py

  Thank you!
    """)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n  Error: {e}")
        raise
