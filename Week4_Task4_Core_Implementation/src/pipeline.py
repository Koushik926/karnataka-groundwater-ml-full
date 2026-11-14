"""pipeline.py
Module 1 - Groundwater level prediction.

Week 7 revision
---------------
The earlier version of this file always fell back to a *synthetic* dataset
because it looked for ``data/raw/features.csv``, a file that was never created.
Every result reported in Weeks 4 and 5 therefore came from random numbers
(test R2 = -0.10) while 123,391 real CGWB observations sat unused in
``data/raw``.

This version:

1. Builds the feature table from the real CGWB export via ``data_processor``
   (the synthetic generator is kept only as an explicit fallback and for the
   unit tests).
2. Splits the data chronologically **by observation date**, so the test set is
   genuinely the most recent seasons.
3. Trains Random Forest, XGBoost and SVR, compares them against a
   last-observed-value baseline, and selects on validation RMSE.
4. Produces a recursive four-quarter forecast per station and converts it into
   a predicted decline rate (m/year) per district - the input Module 2 needs.

Usage::

    from src.pipeline import run_module1
    result = run_module1()
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.svm import SVR
import xgboost as xgb

# PyTorch is only needed for the optional LSTM.  Importing it unconditionally
# made the whole project unrunnable without a ~2 GB install it never used.
try:  # pragma: no cover - exercised only by environment, not by tests
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    torch = None
    TORCH_AVAILABLE = False

    class _TorchStub:
        class Module:  # minimal stand-in so the class below still defines
            pass

    nn = _TorchStub()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

from .config import Model1Config, TRAIN_FRAC, VAL_FRAC

# Hyper-parameters live in config.py so the report and the code cannot disagree.
CFG = Model1Config()

BASE_FEATURES = [
    "GWL_lag1", "GWL_lag2", "GWL_lag3", "GWL_lag4",
    "GWL_rolling_mean", "GWL_rolling_std",
    "sin_month", "cos_month",
    "Latitude", "Longitude",
]
# Real rainfall (NASA POWER) (see src/rainfall.py).  Used automatically when the
# download has been run; the pipeline still works without it.
RAIN_FEATURES = ["rain_q", "rain_prev_q", "rain_12m", "rain_monsoon",
                 "rain_anomaly_12m"]
FEATURE_COLS = list(BASE_FEATURES)          # kept for backward compatibility


def select_features(df: pd.DataFrame, use_rainfall: bool = True) -> list[str]:
    """Feature columns present in this table."""
    cols = [c for c in BASE_FEATURES if c in df.columns]
    if use_rainfall:
        cols += [c for c in RAIN_FEATURES if c in df.columns]
    return cols

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_feature_table(min_records: int = 20) -> pd.DataFrame:
    """Return the real CGWB feature table (one row per station-date)."""
    from .data_processor import create_station_features, load_gwl_data

    gwl = load_gwl_data()
    logger.info(
        "Real CGWB data loaded - %d records, %d stations, %d districts",
        len(gwl), gwl["Station"].nunique(), gwl["District"].nunique(),
    )
    features = create_station_features(gwl, min_records=min_records)
    return features


def _synthetic_data(n_samples: int = 800, n_features: int = 15,
                    random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series]:
    """Deterministic synthetic dataset.

    Retained only for the unit tests and as a fallback when the CGWB CSVs are
    missing.  It is never used for reported results.
    """
    rng = np.random.default_rng(random_state)
    dates = pd.Index(range(n_samples), name="obs_idx")
    X = pd.DataFrame(rng.normal(size=(n_samples, n_features)), index=dates,
                     columns=[f"feat_{i}" for i in range(n_features)])
    X["time_norm"] = np.linspace(0.0, 1.0, n_samples)
    trend = np.linspace(100, 80, n_samples)
    signal = (X["feat_0"] - X["feat_1"]) * 3.0 + X["feat_2"] * 2.0
    noise = rng.normal(scale=2.0, size=n_samples)
    y = pd.Series(trend + signal + noise, index=dates, name="target_depth")
    logger.info("Synthetic data generated - %d samples, %d features", n_samples, X.shape[1])
    return X, y


def _chronological_split(X: pd.DataFrame, y: pd.Series, test_frac: float = 0.20):
    """Split preserving row order: train | validation | test."""
    n_test = int(len(X) * test_frac)
    X_train_val, X_test = X.iloc[:-n_test], X.iloc[-n_test:]
    y_train_val, y_test = y.iloc[:-n_test], y.iloc[-n_test:]

    n_val = int(0.20 * len(X_train_val))
    X_train, X_val = X_train_val.iloc[:-n_val], X_train_val.iloc[-n_val:]
    y_train, y_val = y_train_val.iloc[:-n_val], y_train_val.iloc[-n_val:]

    logger.info("Data split - train: %d, val: %d, test: %d",
                len(X_train), len(X_val), len(X_test))
    return X_train, X_val, X_test, y_train, y_val, y_test


def split_by_date(features: pd.DataFrame, train_frac: float = TRAIN_FRAC,
                  val_frac: float = VAL_FRAC) -> Dict[str, pd.DataFrame]:
    """Chronological split of the real feature table, ordered by Date.

    Returns a dict with the three frames plus the cut-off dates, so the report
    can state exactly which period each split covers.
    """
    ordered = features.sort_values("Date").reset_index(drop=True)
    n = len(ordered)
    i_train = int(n * train_frac)
    i_val = int(n * (train_frac + val_frac))

    parts = {
        "train": ordered.iloc[:i_train],
        "val": ordered.iloc[i_train:i_val],
        "test": ordered.iloc[i_val:],
    }
    for name, part in parts.items():
        logger.info("%-5s %7d rows   %s -> %s", name, len(part),
                    part["Date"].min().date(), part["Date"].max().date())
    return parts

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

def _fit_random_forest(X: pd.DataFrame, y: pd.Series) -> RandomForestRegressor:
    model = RandomForestRegressor(n_estimators=CFG.random_forest_estimators,
                                  random_state=0, n_jobs=-1)
    model.fit(X, y)
    return model


def _fit_xgboost(X: pd.DataFrame, y: pd.Series) -> xgb.XGBRegressor:
    model = xgb.XGBRegressor(
        n_estimators=CFG.xgboost_estimators, learning_rate=CFG.xgboost_lr,
        max_depth=CFG.xgboost_max_depth,
        subsample=0.8, colsample_bytree=0.8,
        objective="reg:squarederror", n_jobs=-1, random_state=0,
    )
    model.fit(X, y)
    return model


def _fit_svr(X: pd.DataFrame, y: pd.Series, max_rows: int = 5000) -> SVR:
    """RBF-kernel SVR.

    SVR is O(n^2)-ish in the number of samples, so on the full CGWB table it is
    fitted on a chronologically-ordered subsample of the training data.
    """
    if len(X) > max_rows:
        X, y = X.iloc[-max_rows:], y.iloc[-max_rows:]
        logger.info("SVR fitted on the most recent %d training rows", max_rows)
    model = SVR(kernel="rbf", C=CFG.svr_c, epsilon=CFG.svr_epsilon)
    model.fit(X, y)
    return model


class LSTMRegressor(nn.Module):
    """Minimal LSTM regressor (optional - requires PyTorch)."""

    def __init__(self, n_features: int, hidden: int = 64, num_layers: int = 2):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for LSTMRegressor")
        super().__init__()
        self.lstm = nn.LSTM(input_size=n_features, hidden_size=hidden,
                            num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden, 1)
        self.loss_fn = nn.MSELoss()

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]).squeeze(-1)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 10,
            lr: float = 1e-3, batch_size: int = 128):
        self.train()
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        dataset = torch.utils.data.TensorDataset(
            torch.from_numpy(X).float().unsqueeze(1),
            torch.from_numpy(y).float(),
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False)
        for _ in range(epochs):
            for xb, yb in loader:
                optimizer.zero_grad()
                loss = self.loss_fn(self(xb), yb)
                loss.backward()
                optimizer.step()
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            return self(torch.from_numpy(X).float().unsqueeze(1)).cpu().numpy()

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _evaluate(model, X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, float]:
    preds = model.predict(X_val.values) if isinstance(model, LSTMRegressor) else model.predict(X_val)
    return {
        "rmse": float(root_mean_squared_error(y_val, preds)),
        "mae": float(mean_absolute_error(y_val, preds)),
        "r2": float(r2_score(y_val, preds)),
    }


def _baseline_metrics(X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
    """Persistence baseline: next quarter equals the last observed value."""
    preds = X["GWL_lag1"].values
    return {
        "rmse": float(root_mean_squared_error(y, preds)),
        "mae": float(mean_absolute_error(y, preds)),
        "r2": float(r2_score(y, preds)),
    }

# ---------------------------------------------------------------------------
# Recursive forecasting -> district decline rates
# ---------------------------------------------------------------------------

def forecast_station_trends(model, features: pd.DataFrame,
                            horizon: int = 4,
                            feat_cols: list[str] | None = None) -> pd.DataFrame:
    """Forecast ``horizon`` quarters ahead for every station, recursively.

    Each prediction is fed back as the next quarter's lag-1 value, the rolling
    statistics are recomputed from the rolling lag window, and the seasonal
    encoding is advanced by three months.  The predicted decline rate is the
    least-squares slope through the last observed value and the forecast
    points, expressed in metres per year (positive = water table deepening).
    """
    feat_cols = feat_cols or select_features(features)
    latest = features.sort_values("Date").groupby("Station").tail(1).copy()
    rows = []

    for _, row in latest.iterrows():
        lags = [row["GWL_m"], row["GWL_lag1"], row["GWL_lag2"], row["GWL_lag3"]]
        if any(pd.isna(v) for v in lags):
            continue

        month = int(pd.to_datetime(row["Date"]).month)
        times, values = [0.0], [float(row["GWL_m"])]

        for step in range(1, horizon + 1):
            month = (month + 3 - 1) % 12 + 1
            feat = {
                "GWL_lag1": lags[0], "GWL_lag2": lags[1],
                "GWL_lag3": lags[2], "GWL_lag4": lags[3],
                "GWL_rolling_mean": float(np.mean(lags)),
                "GWL_rolling_std": float(np.std(lags, ddof=1)) if len(lags) > 1 else 0.0,
                "sin_month": float(np.sin(2 * np.pi * month / 12)),
                "cos_month": float(np.cos(2 * np.pi * month / 12)),
                "Latitude": row["Latitude"], "Longitude": row["Longitude"],
            }
            # rainfall is held at its last observed value across the horizon
            for rc in RAIN_FEATURES:
                if rc in feat_cols:
                    feat[rc] = row.get(rc, np.nan)
            x = pd.DataFrame([feat])[feat_cols].fillna(0.0)
            pred = float(model.predict(x.values if isinstance(model, LSTMRegressor) else x)[0])
            times.append(step * 0.25)          # quarters -> years
            values.append(pred)
            lags = [pred] + lags[:3]

        slope, _ = np.polyfit(times, values, 1)  # metres per year
        rows.append({
            "Station": row["Station"],
            "District": row["District"],
            "last_observed_m": float(row["GWL_m"]),
            "forecast_q4_m": values[-1],
            "predicted_trend_m_per_yr": float(slope),
        })

    out = pd.DataFrame(rows)
    logger.info("Recursive %d-quarter forecast produced for %d stations", horizon, len(out))
    return out


def district_trends(station_forecasts: pd.DataFrame) -> pd.Series:
    """Mean predicted decline rate (m/year) per district."""
    return (station_forecasts.groupby("District")["predicted_trend_m_per_yr"]
            .mean().rename("predicted_decline_rate"))

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_module1(root_dir: Path | None = None, use_real_data: bool = True,
                horizon: int = 4, use_rainfall: bool = True) -> Dict[str, Any]:
    """Run Module 1 end to end and return its artefacts.

    Returns a dict with the trained model, the metrics table, the per-station
    forecasts and the per-district predicted decline rates (consumed by
    Module 2).
    """
    if root_dir is None:
        root_dir = Path(__file__).resolve().parents[1]
    model_dir, output_dir = root_dir / "models", root_dir / "outputs"
    for d in (model_dir, output_dir):
        d.mkdir(parents=True, exist_ok=True)

    # ---- data ------------------------------------------------------------
    features = None
    if use_real_data:
        # Deliberately NOT wrapped in a try/except that falls back to synthetic
        # data. The original failure of this project was exactly that: a missing
        # file was swallowed, the run continued on generated numbers, and
        # models/module1_best_model.json - which the reports, slides and
        # dashboard all read - was filled with metrics no real run produced.
        # Missing data is now a hard error. Synthetic data is reachable only by
        # asking for it with use_real_data=False, which only the tests do.
        try:
            features = load_feature_table()
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Real CGWB data not found ({exc}). Expected "
                f"data/raw/gwl_karnataka_clean.csv, or the two India-WRIS exports "
                f"to build it from. Refusing to silently substitute synthetic data: "
                f"pass use_real_data=False only if you genuinely want a smoke test."
            ) from exc

    if features is None:
        logger.warning("RUNNING ON SYNTHETIC DATA - results are a smoke test only "
                       "and must never be reported.")
        X, y = _synthetic_data()
        X_train, X_val, X_test, y_train, y_val, y_test = _chronological_split(X, y)
        data_source = "synthetic"
        split_info = {}
    else:
        parts = split_by_date(features)
        feat_cols = select_features(features, use_rainfall)
        logger.info("Using %d features%s", len(feat_cols),
                    " (including real NASA POWER rainfall)"
                    if any(c in feat_cols for c in RAIN_FEATURES) else "")
        X_train = parts["train"][feat_cols]
        # Impute the few remaining gaps (lag3/lag4/rolling_std at the start of a
        # station's record) with TRAINING medians only, so no information from
        # the validation or test periods leaks backwards.
        fill_values = X_train.median()
        n_missing = int(features[feat_cols].isna().sum().sum())
        if n_missing:
            logger.info("Imputing %d missing feature values with training medians", n_missing)
        X_train = X_train.fillna(fill_values)
        X_val = parts["val"][feat_cols].fillna(fill_values)
        X_test = parts["test"][feat_cols].fillna(fill_values)
        y_train = parts["train"]["target_gwl"]
        y_val = parts["val"]["target_gwl"]
        y_test = parts["test"]["target_gwl"]
        data_source = "CGWB (India-WRIS) Karnataka quarterly observations"
        split_info = {
            name: {
                "rows": int(len(p)),
                "from": str(p["Date"].min().date()),
                "to": str(p["Date"].max().date()),
            } for name, p in parts.items()
        }

    # ---- train & compare -------------------------------------------------
    models: Dict[str, Any] = {}
    logger.info("Training Random Forest ...")
    models["random_forest"] = _fit_random_forest(X_train, y_train)
    logger.info("Training XGBoost ...")
    models["xgboost"] = _fit_xgboost(X_train, y_train)
    logger.info("Training SVR ...")
    models["svr"] = _fit_svr(X_train, y_train)

    val_metrics = {name: _evaluate(m, X_val, y_val) for name, m in models.items()}
    if "GWL_lag1" in X_val.columns:
        val_metrics["baseline_last_value"] = _baseline_metrics(X_val, y_val)

    for name, m in val_metrics.items():
        logger.info("%-20s RMSE %.4f  MAE %.4f  R2 %.4f", name, m["rmse"], m["mae"], m["r2"])

    trainable = {k: v for k, v in val_metrics.items() if k in models}
    best_name = min(trainable, key=lambda k: trainable[k]["rmse"])
    logger.info("Best model on validation: %s (RMSE %.4f)", best_name, trainable[best_name]["rmse"])

    # ---- refit on train+val, evaluate on the held-out most recent seasons --
    X_tv = pd.concat([X_train, X_val])
    y_tv = pd.concat([y_train, y_val])
    refit = {"random_forest": _fit_random_forest, "xgboost": _fit_xgboost, "svr": _fit_svr}
    best_model = refit[best_name](X_tv, y_tv)

    test_metrics = _evaluate(best_model, X_test, y_test)
    logger.info("TEST  %-14s RMSE %.4f  MAE %.4f  R2 %.4f",
                best_name, test_metrics["rmse"], test_metrics["mae"], test_metrics["r2"])
    if "GWL_lag1" in X_test.columns:
        base = _baseline_metrics(X_test, y_test)
        logger.info("TEST  baseline       RMSE %.4f  MAE %.4f  R2 %.4f",
                    base["rmse"], base["mae"], base["r2"])
        test_metrics["baseline_rmse"] = base["rmse"]
        test_metrics["baseline_r2"] = base["r2"]

    # ---- persist test predictions ----------------------------------------
    preds = best_model.predict(X_test)
    if features is not None:
        pred_df = parts["test"][["Station", "District", "Date"]].copy()
        pred_df["actual_gwl_m"] = y_test.values
        pred_df["predicted_gwl_m"] = preds
    else:
        pred_df = pd.DataFrame({"prediction": preds}, index=X_test.index)
    pred_path = output_dir / "module1_test_predictions.csv"
    pred_df.to_csv(pred_path, index=False)
    logger.info("Test predictions -> %s", pred_path)

    # ---- forecasts -> district decline rates ------------------------------
    station_fc, trends = None, None
    if features is not None:
        station_fc = forecast_station_trends(best_model, features, horizon=horizon,
                                             feat_cols=feat_cols)
        station_fc.to_csv(output_dir / "module1_station_forecasts.csv", index=False)
        trends = district_trends(station_fc)
        trends.reset_index().to_csv(output_dir / "module1_district_trends.csv", index=False)
        logger.info("District decline rates -> %s", output_dir / "module1_district_trends.csv")

    meta = {
        "data_source": data_source,
        "selected_model": best_name,
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "split": split_info,
        "n_features": len(X_train.columns),
        "feature_columns": list(X_train.columns),
        "forecast_horizon_quarters": horizon,
    }
    with open(model_dir / "module1_best_model.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    logger.info("Model metadata -> %s", model_dir / "module1_best_model.json")

    return {
        "model": best_model, "model_name": best_name, "metrics": meta,
        "test_predictions": pred_df, "station_forecasts": station_fc,
        "district_trends": trends, "features": features,
    }


if __name__ == "__main__":
    run_module1()
