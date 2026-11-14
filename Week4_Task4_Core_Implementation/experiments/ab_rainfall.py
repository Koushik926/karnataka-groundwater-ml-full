"""
ab_rainfall.py - does real rainfall actually improve the prediction?

    python experiments/ab_rainfall.py

Trains Module 1 twice on identical splits, once with the ten base features and
once with those plus the five NASA POWER rainfall features, and prints the
difference. Run this before claiming rainfall helps - the honest answer is
whatever this prints.
"""
import sys, json, logging
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
logging.basicConfig(level=logging.WARNING)

from src.pipeline import run_module1  # noqa: E402

rows = []
for use_rain, label in [(False, "base features only"), (True, "base + NASA POWER rain")]:
    r = run_module1(root_dir=BASE, use_rainfall=use_rain)
    m, v = r["metrics"]["test_metrics"], r["metrics"]["validation_metrics"]
    rows.append((label, r["model_name"], r["metrics"]["n_features"],
                 v[r["model_name"]]["rmse"], v[r["model_name"]]["r2"],
                 m["rmse"], m["r2"]))

print(f"\n{'variant':<24}{'model':<14}{'feats':>6}{'val RMSE':>10}{'val R2':>9}"
      f"{'test RMSE':>11}{'test R2':>9}")
print("-" * 83)
for r in rows:
    print(f"{r[0]:<24}{r[1]:<14}{r[2]:>6}{r[3]:>10.3f}{r[4]:>9.3f}{r[5]:>11.3f}{r[6]:>9.3f}")
if len(rows) == 2:
    print(f"\nrainfall changes test RMSE by {rows[1][5]-rows[0][5]:+.3f} m "
          f"and test R2 by {rows[1][6]-rows[0][6]:+.3f}")
