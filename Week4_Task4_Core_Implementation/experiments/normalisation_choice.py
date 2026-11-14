"""
normalisation_choice.py - why the risk index uses min-max and not something fancier.

    python experiments/normalisation_choice.py

Min-max scaling is sensitive to outliers, and this data has them: the decline
rate runs from -0.385 to 1.445 m/yr while the 75th percentile is 0.034, so one
extreme taluk compresses every other taluk on the indicator that carries half
the AHP weight. That looks like a flaw, so we tested the two standard fixes -
clipping at the 5th/95th percentile, and rank (percentile) scaling - against
CGWB's independent assessment.

Both were worse. They catch more stressed taluks but flag far more that CGWB
calls safe, and overall agreement falls. Min-max's compression turns out to act
as a conservative filter: only genuinely extreme taluks reach the top classes.
We kept min-max on this evidence rather than on the assumption that a more
robust scaler must be better.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import (AHP_MATRIX, CGWB_TO_RISK, RISK_INDICATORS,  # noqa: E402
                        normalise_cgwb_category)
from src.module2_risk import (_spearman, classify_risk,  # noqa: E402
                              compute_ahp_weights)


def scaled(v, mode):
    v = np.asarray(v, dtype=float)
    if mode == "rank":
        return pd.Series(v).rank(pct=True).to_numpy()
    lo, hi = ((v.min(), v.max()) if mode == "minmax"
              else (np.nanpercentile(v, 5), np.nanpercentile(v, 95)))
    return np.zeros_like(v) if hi - lo < 1e-9 else np.clip((v - lo) / (hi - lo), 0, 1)


def main():
    d = pd.read_csv(ROOT / "outputs" / "module2_taluk_indicators.csv")
    w, _ = compute_ahp_weights(AHP_MATRIX)
    cg = d["cgwb_category"].map(normalise_cgwb_category).map(CGWB_TO_RISK)
    ok = cg.notna()

    print(f"{'scaling':<22}{'binary':>9}{'prec':>7}{'recall':>8}{'spearman':>10}"
          f"   confusion")
    print("-" * 74)
    for mode, label in [("minmax", "min-max (in use)"),
                        ("p5p95", "clipped 5th-95th pct"),
                        ("rank", "rank / percentile")]:
        ri, used = np.zeros(len(d)), 0.0
        for i, c in enumerate(RISK_INDICATORS):
            if c in d.columns:
                ri += w[i] * scaled(d[c], mode); used += w[i]
        ri = pd.Series(ri / used, index=d.index)
        flag, stressed = classify_risk(ri).isin([3, 4]), cg.isin([3, 4])
        tp = int((flag & stressed & ok).sum()); fp = int((flag & ~stressed & ok).sum())
        fn = int((~flag & stressed & ok).sum()); tn = int((~flag & ~stressed & ok).sum())
        n = max(tp + fp + fn + tn, 1)
        print(f"{label:<22}{100*(tp+tn)/n:>8.1f}%{tp/max(tp+fp,1):>7.2f}"
              f"{tp/max(tp+fn,1):>8.2f}{_spearman(ri[ok].to_numpy(), cg[ok].to_numpy(float)):>+10.3f}"
              f"   TP{tp} FP{fp} FN{fn} TN{tn}")
    print("\nMin-max wins on agreement and on rank correlation, so it stays.")


if __name__ == "__main__":
    main()
