"""
benchmark.py - how this system compares with the approaches it is competing against.

    python experiments/benchmark.py

Claiming a model is good is not the same as showing it. This runs every serious
alternative on the IDENTICAL chronological split and reports them side by side:

  naive baselines    persistence, seasonal naive, climatology
  classical          ridge regression
  tree ensembles     Random Forest, XGBoost
  kernel             SVR
  deep learning      a true sequence LSTM over the past four quarters

The seasonal-naive baseline matters most. "Same as last quarter" is easy to beat
in a seasonal series; "same quarter as last year" is not, and most published
groundwater papers never report it. If we beat that, the result means something.

It also produces two things a point forecast cannot give a decision-maker:
80% prediction intervals with measured coverage, and an ablation showing what
each group of features is actually worth.

Writes outputs/benchmark_results.json.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import xgboost as xgb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.data_processor import create_station_features, load_gwl_data  # noqa: E402
from src.pipeline import BASE_FEATURES, RAIN_FEATURES, split_by_date  # noqa: E402

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("benchmark")

SEQ = ["GWL_lag4", "GWL_lag3", "GWL_lag2", "GWL_lag1"]   # oldest -> newest
STATIC = ["sin_month", "cos_month", "Latitude", "Longitude",
          "GWL_rolling_mean", "GWL_rolling_std"] + RAIN_FEATURES


def score(y, p) -> dict:
    return {"rmse": float(root_mean_squared_error(y, p)),
            "mae": float(mean_absolute_error(y, p)),
            "r2": float(r2_score(y, p))}


# --------------------------------------------------------------- sequence LSTM
def run_lstm(tr, va, te, med, epochs=12, hidden=64, seed=0):
    """A real LSTM: four quarterly steps through the recurrent layer, static
    features concatenated at the head. The project's original LSTMRegressor fed
    a sequence of length one, which is a gated feedforward net, not a sequence
    model - so it was never a fair test of the deep-learning approach."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed); np.random.seed(seed)
    stat = [c for c in STATIC if c in tr.columns]

    def prep(df, sx=None, ss=None, sy=None):
        X = df[SEQ].fillna(med[SEQ]).to_numpy(np.float32)
        S = df[stat].fillna(med[stat]).to_numpy(np.float32)
        y = df["target_gwl"].to_numpy(np.float32)
        if sx is None:
            sx, ss, sy = StandardScaler(), StandardScaler(), StandardScaler()
            sx.fit(X.reshape(-1, 1)); ss.fit(S); sy.fit(y.reshape(-1, 1))
        Xs = sx.transform(X.reshape(-1, 1)).reshape(-1, 4, 1)
        return (torch.from_numpy(Xs).float(),
                torch.from_numpy(ss.transform(S)).float(),
                torch.from_numpy(sy.transform(y.reshape(-1, 1)).ravel()).float(),
                sx, ss, sy)

    Xtr, Str, ytr, sx, ss, sy = prep(tr)
    Xva, Sva, yva, *_ = prep(va, sx, ss, sy)
    Xte, Ste, _, *_ = prep(te, sx, ss, sy)

    class Net(nn.Module):
        def __init__(self, n_static):
            super().__init__()
            self.lstm = nn.LSTM(1, hidden, num_layers=1, batch_first=True)
            self.head = nn.Sequential(nn.Linear(hidden + n_static, 64),
                                      nn.ReLU(), nn.Dropout(0.1), nn.Linear(64, 1))
        def forward(self, xs, st):
            out, _ = self.lstm(xs)
            return self.head(torch.cat([out[:, -1, :], st], dim=1)).squeeze(-1)

    net = Net(len(stat))
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    lossf = nn.MSELoss()
    ds = torch.utils.data.TensorDataset(Xtr, Str, ytr)
    dl = torch.utils.data.DataLoader(ds, batch_size=512, shuffle=True)

    best, best_state = np.inf, None
    for ep in range(epochs):
        net.train()
        for xb, sb, yb in dl:
            opt.zero_grad(); loss = lossf(net(xb, sb), yb); loss.backward(); opt.step()
        net.eval()
        with torch.no_grad():
            pv = sy.inverse_transform(net(Xva, Sva).numpy().reshape(-1, 1)).ravel()
        rmse = root_mean_squared_error(va["target_gwl"], pv)
        if rmse < best:
            best, best_state = rmse, {k: v.clone() for k, v in net.state_dict().items()}
        log.info("  LSTM epoch %2d  val RMSE %.4f", ep + 1, rmse)
    net.load_state_dict(best_state); net.eval()
    with torch.no_grad():
        pv = sy.inverse_transform(net(Xva, Sva).numpy().reshape(-1, 1)).ravel()
        pt = sy.inverse_transform(net(Xte, Ste).numpy().reshape(-1, 1)).ravel()
    return score(va["target_gwl"], pv), score(te["target_gwl"], pt)


def main():
    log.info("Loading real CGWB data ...")
    feat = create_station_features(load_gwl_data(), with_rainfall=True)
    feat = feat.dropna(subset=["target_gwl"])
    parts = split_by_date(feat)
    tr, va, te = parts["train"], parts["val"], parts["test"]
    cols = [c for c in BASE_FEATURES + RAIN_FEATURES if c in feat.columns]

    med = tr[cols].median()
    Xtr, Xva, Xte = (d[cols].fillna(med) for d in (tr, va, te))
    ytr, yva, yte = (d["target_gwl"] for d in (tr, va, te))

    R = {}

    # ---- naive baselines, no training
    log.info("Naive baselines ...")
    R["persistence"] = {"family": "naive", "val": score(yva, Xva["GWL_lag1"]),
                        "test": score(yte, Xte["GWL_lag1"]), "secs": 0.0,
                        "note": "next quarter = this quarter"}
    R["seasonal_naive"] = {"family": "naive", "val": score(yva, Xva["GWL_lag4"]),
                           "test": score(yte, Xte["GWL_lag4"]), "secs": 0.0,
                           "note": "next quarter = same quarter last year"}
    # climatology: each station's own training-period mean
    smean = tr.groupby("Station")["target_gwl"].mean()
    gmean = float(tr["target_gwl"].mean())
    R["climatology"] = {"family": "naive",
                        "val": score(yva, va["Station"].map(smean).fillna(gmean)),
                        "test": score(yte, te["Station"].map(smean).fillna(gmean)),
                        "secs": 0.0, "note": "station's long-run mean depth"}

    # ---- trained models
    models = {
        "ridge": ("classical", Ridge(alpha=1.0), "linear regression, L2 penalty"),
        "random_forest": ("tree ensemble",
                          RandomForestRegressor(n_estimators=200, max_depth=14,
                                                n_jobs=-1, random_state=42),
                          "Tao et al. 2022 workhorse"),
        "xgboost": ("tree ensemble",
                    xgb.XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.08,
                                     subsample=0.9, colsample_bytree=0.9,
                                     random_state=42, n_jobs=-1),
                    "our selected model"),
    }
    for name, (fam, mdl, note) in models.items():
        log.info("Training %s ...", name)
        t0 = time.time(); mdl.fit(Xtr, ytr); secs = time.time() - t0
        R[name] = {"family": fam, "val": score(yva, mdl.predict(Xva)),
                   "test": score(yte, mdl.predict(Xte)), "secs": round(secs, 1),
                   "note": note}

    log.info("Training svr (subsampled, as in the main pipeline) ...")
    sc = StandardScaler().fit(Xtr)
    idx = np.random.RandomState(0).choice(len(Xtr), min(5000, len(Xtr)), replace=False)
    t0 = time.time()
    svr = SVR(C=10.0, epsilon=0.2).fit(sc.transform(Xtr.iloc[idx]), ytr.iloc[idx])
    R["svr"] = {"family": "kernel", "val": score(yva, svr.predict(sc.transform(Xva))),
                "test": score(yte, svr.predict(sc.transform(Xte))),
                "secs": round(time.time() - t0, 1),
                "note": "subsampled to 5,000 rows; does not scale"}

    log.info("Training sequence LSTM (Supreetha 2020 / Wunsch 2022 family) ...")
    t0 = time.time(); v, t = run_lstm(tr, va, te, med)
    R["lstm_sequence"] = {"family": "deep learning", "val": v, "test": t,
                          "secs": round(time.time() - t0, 1),
                          "note": "true 4-step sequence + static head"}

    # ---- prediction intervals (what a point forecast cannot give a planner)
    log.info("Quantile models for 80% prediction intervals ...")
    qs = {}
    for a, key in ((0.1, "lo"), (0.9, "hi")):
        m = xgb.XGBRegressor(objective="reg:quantileerror", quantile_alpha=a,
                             n_estimators=300, max_depth=6, learning_rate=0.08,
                             random_state=42, n_jobs=-1).fit(Xtr, ytr)
        qs[key] = m.predict(Xte)
    inside = float(((yte >= qs["lo"]) & (yte <= qs["hi"])).mean())
    width = float(np.mean(qs["hi"] - qs["lo"]))
    intervals = {"nominal": 0.80, "empirical_coverage": round(inside, 4),
                 "mean_width_m": round(width, 3)}
    log.info("  80%% interval covers %.1f%% of held-out points, mean width %.2f m",
             inside * 100, width)

    # ---- ablation: what each feature group is worth
    log.info("Ablation ...")
    groups = {
        "lags only": ["GWL_lag1", "GWL_lag2", "GWL_lag3", "GWL_lag4"],
        "+ rolling stats": ["GWL_lag1", "GWL_lag2", "GWL_lag3", "GWL_lag4",
                            "GWL_rolling_mean", "GWL_rolling_std"],
        "+ seasonality": ["GWL_lag1", "GWL_lag2", "GWL_lag3", "GWL_lag4",
                          "GWL_rolling_mean", "GWL_rolling_std", "sin_month", "cos_month"],
        "+ location": BASE_FEATURES,
        "+ rainfall (full)": BASE_FEATURES + RAIN_FEATURES,
    }
    abl = {}
    for label, gcols in groups.items():
        gc = [c for c in gcols if c in feat.columns]
        m = xgb.XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.08,
                             subsample=0.9, colsample_bytree=0.9,
                             random_state=42, n_jobs=-1)
        m.fit(tr[gc].fillna(med[gc]), ytr)
        abl[label] = {"n_features": len(gc),
                      "test": score(yte, m.predict(te[gc].fillna(med[gc])))}
        log.info("  %-20s %2d feats  test RMSE %.4f  R2 %.4f", label, len(gc),
                 abl[label]["test"]["rmse"], abl[label]["test"]["r2"])

    out = {"split": {k: {"rows": len(v),
                         "from": str(v["Date"].min().date()),
                         "to": str(v["Date"].max().date())}
                     for k, v in parts.items()},
           "models": R, "intervals": intervals, "ablation": abl}
    p = ROOT / "outputs" / "benchmark_results.json"
    p.write_text(json.dumps(out, indent=2))

    print("\n" + "=" * 86)
    print(f"{'model':<18}{'family':<16}{'val RMSE':>10}{'test RMSE':>11}{'test R2':>10}{'train s':>9}")
    print("=" * 86)
    for k, v in sorted(R.items(), key=lambda kv: kv[1]["test"]["rmse"]):
        print(f"{k:<18}{v['family']:<16}{v['val']['rmse']:>10.4f}"
              f"{v['test']['rmse']:>11.4f}{v['test']['r2']:>10.4f}{v['secs']:>9.1f}")
    print("=" * 86)
    print(f"\n80% prediction interval: covers {inside*100:.1f}% of held-out points "
          f"(nominal 80%), mean width {width:.2f} m")
    print(f"\nwritten to {p}")


if __name__ == "__main__":
    main()
