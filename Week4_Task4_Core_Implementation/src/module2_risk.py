"""module2_risk.py
Module 2: Groundwater Depletion Risk Mapping

This module implements:
1. AHP (Analytic Hierarchy Process) weight calculation for risk indicators
2. Risk index computation using weighted indicators
3. Jenks Natural Breaks classification into 4 risk zones
4. Validation against CGWB assessment categories

The five risk indicators (from Week 3 design):
- predicted_decline_rate: Rate of groundwater level decline from Module 1
- current_depth: Current depth to groundwater (deeper = more risk)
- variability: Coefficient of variation in groundwater levels
- rainfall_dependence: Correlation between rainfall and GWL recovery
- lulc_change: Land use change index (urbanization pressure)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from .config import (AHP_MATRIX, RISK_INDICATORS, RISK_CLASSES, CGWB_TO_RISK,
                     AHP_MAX_CR, normalise_cgwb_category)

logger = logging.getLogger(__name__)

# Random Index values for AHP consistency check (n=1 to 10)
RI_TABLE = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def compute_ahp_weights(matrix: List[List[float]]) -> Tuple[np.ndarray, float]:
    """Compute AHP weights from pairwise comparison matrix.

    Returns:
        weights: Normalized priority vector
        cr: Consistency ratio (should be < 0.1 for acceptable consistency)
    """
    A = np.array(matrix)
    n = A.shape[0]

    # Normalize columns and compute weights (geometric mean method)
    col_sums = A.sum(axis=0)
    A_norm = A / col_sums
    weights = A_norm.mean(axis=1)

    # Compute consistency
    Aw = A @ weights
    lambda_max = (Aw / weights).mean()
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = RI_TABLE.get(n, 1.49)
    cr = ci / ri if ri > 0 else 0.0

    logger.info("AHP weights computed: %s", dict(zip(RISK_INDICATORS, weights.round(4))))
    logger.info("Consistency Ratio: %.4f (threshold: %.2f)", cr, AHP_MAX_CR)

    if cr > AHP_MAX_CR:
        logger.warning("CR exceeds threshold! Matrix may be inconsistent.")

    return weights, cr


def normalize_indicator(values: np.ndarray, higher_is_riskier: bool = True) -> np.ndarray:
    """Min-max normalize indicator values to [0, 1] range.

    Args:
        values: Raw indicator values
        higher_is_riskier: If True, higher values mean more risk
    """
    vmin, vmax = values.min(), values.max()
    if vmax - vmin < 1e-9:
        return np.zeros_like(values)

    normalized = (values - vmin) / (vmax - vmin)
    if not higher_is_riskier:
        normalized = 1.0 - normalized
    return normalized


def compute_risk_index(df: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Compute composite risk index from normalized indicators.

    Args:
        df: DataFrame with columns matching RISK_INDICATORS
        weights: AHP weights for each indicator

    Returns:
        Series of risk index values (0-1 scale)
    """
    # Define which indicators have higher values = more risk
    higher_is_riskier = {
        "decline_rate": True,             # faster deepening = more risk
        "predicted_decline_rate": True,   # legacy name, same direction
        "current_depth": True,            # deeper water table = more risk
        "variability": True,              # less stable supply = more risk
        "seasonal_recovery": True,        # larger monsoon swing = more monsoon-dependent
        # retained so older frames (and TC12) still score correctly
        "rainfall_dependence": True,
        "lulc_change": True,
    }

    risk_index = np.zeros(len(df))
    used_weight = 0.0

    for i, indicator in enumerate(RISK_INDICATORS):
        if indicator not in df.columns:
            logger.warning("Indicator '%s' not found in data, skipping", indicator)
            continue

        values = df[indicator].values
        normalized = normalize_indicator(values, higher_is_riskier.get(indicator, True))
        risk_index += weights[i] * normalized
        used_weight += float(weights[i])

    if used_weight <= 0:
        raise ValueError("No risk indicators present in the table - cannot score.")
    # Renormalise by the weight actually used. With all five indicators this is
    # 1.0 and changes nothing; when one is absent (the district view has no
    # rainfall_dependence) it keeps the index on a comparable 0-1 scale instead
    # of silently shrinking it.
    if used_weight < 0.999:
        logger.warning("Only %.1f%% of the AHP weight was available; "
                       "renormalising the index over the indicators present.",
                       used_weight * 100)
    risk_index /= used_weight

    return pd.Series(risk_index, index=df.index, name="risk_index")


def jenks_breaks(values: np.ndarray, n_classes: int = 4) -> List[float]:
    """Compute Jenks Natural Breaks for classification.

    Uses Fisher-Jenks algorithm to find optimal class boundaries
    that minimize within-class variance.
    """
    values = np.sort(values[~np.isnan(values)])
    n = len(values)

    if n <= n_classes:
        return list(values)

    # Initialize matrices
    mat1 = np.zeros((n + 1, n_classes + 1))
    mat2 = np.full((n + 1, n_classes + 1), np.inf)

    for i in range(1, n_classes + 1):
        mat1[1, i] = 1
        mat2[1, i] = 0

    # Fill matrices
    for l in range(2, n + 1):
        s1, s2 = 0.0, 0.0
        for m in range(1, l + 1):
            i3 = l - m + 1
            val = values[i3 - 1]
            s2 += val * val
            s1 += val
            v = s2 - (s1 * s1) / m

            if i3 > 1:
                for j in range(2, n_classes + 1):
                    if mat2[l, j] >= v + mat2[i3 - 1, j - 1]:
                        mat1[l, j] = i3
                        mat2[l, j] = v + mat2[i3 - 1, j - 1]

        mat1[l, 1] = 1
        mat2[l, 1] = v

    # Extract breaks
    breaks = [values[-1]]
    k = n
    for j in range(n_classes, 1, -1):
        idx = int(mat1[k, j]) - 1
        breaks.insert(0, values[idx])
        k = int(mat1[k, j]) - 1
    breaks.insert(0, values[0])

    return breaks


def classify_risk(risk_index: pd.Series, n_classes: int = 4) -> pd.Series:
    """Classify risk index into discrete risk zones using Jenks breaks.

    Returns:
        Series of risk class labels (1=Low, 2=Moderate, 3=High, 4=Very High)
    """
    values = risk_index.values
    breaks = jenks_breaks(values, n_classes)

    logger.info("Jenks breaks: %s", [round(b, 4) for b in breaks])

    risk_class = np.ones(len(values), dtype=int)
    for i, val in enumerate(values):
        for c in range(1, n_classes):
            if val > breaks[c]:
                risk_class[i] = c + 1

    return pd.Series(risk_class, index=risk_index.index, name="risk_class")


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation (no SciPy dependency)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~np.isnan(a) & ~np.isnan(b)
    if ok.sum() < 3:
        return float("nan")
    ra = pd.Series(a[ok]).rank().values
    rb = pd.Series(b[ok]).rank().values
    return float(np.corrcoef(ra, rb)[0, 1])


def validate_against_cgwb(predicted_class: pd.Series, cgwb_category: pd.Series,
                          risk_index: pd.Series | None = None,
                          extraction_stage: pd.Series | None = None) -> Dict[str, float]:
    """Validate the risk classes against the CGWB assessment.

    Three complementary measures are reported, because exact four-class
    agreement is a misleading yardstick here:

    * ``accuracy`` / ``kappa`` - exact agreement on the 4-class scale.  Our
      classes come from Jenks breaks and are therefore *relative* to the 27
      districts assessed, while CGWB categories are *absolute* thresholds on
      the stage of extraction.  The two distributions differ by construction
      (CGWB: mostly "safe"), so exact agreement is low even when the ranking
      is sensible.
    * ``binary_*`` - High/Very High vs CGWB critical/over-exploited, which is
      the decision a planner actually makes.
    * ``spearman_*`` - rank agreement, the fairest test of the ordering.
    """
    cgwb_numeric = (cgwb_category.map(normalise_cgwb_category)
                    .map(CGWB_TO_RISK))

    mask = ~cgwb_numeric.isna()
    pred = predicted_class[mask].values
    actual = cgwb_numeric[mask].values.astype(int)

    if len(pred) == 0:
        logger.warning("No valid CGWB categories for validation")
        return {"accuracy": np.nan, "kappa": np.nan}

    accuracy = float((pred == actual).mean())

    n = len(pred)
    classes = np.array([1, 2, 3, 4])
    po = accuracy
    pe = sum((pred == c).sum() * (actual == c).sum() for c in classes) / (n * n)
    kappa = float((po - pe) / (1 - pe)) if (1 - pe) > 0 else 0.0

    # Binary: "needs intervention" vs not
    ours_high = pred >= 3
    cgwb_stressed = actual >= 3
    tp = int((ours_high & cgwb_stressed).sum())
    fp = int((ours_high & ~cgwb_stressed).sum())
    fn = int((~ours_high & cgwb_stressed).sum())
    tn = int((~ours_high & ~cgwb_stressed).sum())
    results = {
        "accuracy": accuracy,
        "kappa": kappa,
        "n_samples": n,
        "binary_accuracy": float((tp + tn) / n),
        "binary_precision": float(tp / (tp + fp)) if (tp + fp) else float("nan"),
        "binary_recall": float(tp / (tp + fn)) if (tp + fn) else float("nan"),
        "confusion_tp_fp_fn_tn": [tp, fp, fn, tn],
    }

    if risk_index is not None:
        results["spearman_vs_cgwb_category"] = _spearman(
            risk_index[mask].values, actual)
        if extraction_stage is not None:
            results["spearman_vs_extraction_stage"] = _spearman(
                risk_index.values, extraction_stage.values)

    logger.info("Validation (4-class)  accuracy %.1f%%  kappa %.3f",
                accuracy * 100, kappa)
    logger.info("Validation (binary)   accuracy %.1f%%  precision %.2f  recall %.2f  "
                "[TP %d FP %d FN %d TN %d]",
                results["binary_accuracy"] * 100, results["binary_precision"],
                results["binary_recall"], tp, fp, fn, tn)
    if "spearman_vs_cgwb_category" in results:
        logger.info("Validation (rank)     Spearman vs CGWB category %.3f | vs extraction stage %.3f",
                    results["spearman_vs_cgwb_category"],
                    results.get("spearman_vs_extraction_stage", float("nan")))
    return results


def generate_synthetic_indicators(n_samples: int = 100, random_state: int = 42) -> pd.DataFrame:
    """Synthetic indicator data - used by the unit tests only.

    Real runs pass measured district indicators from ``data_processor``; this
    helper exists so Module 2 can be tested without the full CGWB download.
    """
    rng = np.random.default_rng(random_state)
    ranges = {
        "decline_rate": (0.1, 2.5),             # m/year
        "predicted_decline_rate": (0.1, 2.5),   # m/year
        "current_depth": (5, 50),               # metres
        "variability": (0.05, 0.4),             # coefficient of variation
        "seasonal_recovery": (0.1, 3.0),        # metres
        "rainfall_dependence": (0.2, 0.9),
        "lulc_change": (0.0, 0.3),
    }

    df = pd.DataFrame({"location_id": [f"LOC_{i:03d}" for i in range(n_samples)]})
    for name in RISK_INDICATORS:
        lo, hi = ranges.get(name, (0.0, 1.0))
        df[name] = rng.uniform(lo, hi, n_samples)

    trend_col = "decline_rate" if "decline_rate" in df.columns else "predicted_decline_rate"
    risk_proxy = (df[trend_col] + df["current_depth"] / 20) / 2
    df["cgwb_category"] = pd.cut(
        risk_proxy, bins=4,
        labels=["safe", "semi_critical", "critical", "over_exploited"],
    )
    return df


def run_module2(indicators_df: pd.DataFrame = None, validate: bool = True) -> pd.DataFrame:
    """Run the complete Module 2 risk mapping pipeline.

    Args:
        indicators_df: DataFrame with risk indicator columns. If None, uses synthetic data.
        validate: If True and cgwb_category column exists, validates against CGWB.

    Returns:
        DataFrame with risk_index and risk_class columns added
    """
    logger.info("Starting Module 2: Risk Mapping")

    # Use synthetic data if none provided
    if indicators_df is None:
        logger.warning(
            "No indicator table supplied - falling back to SYNTHETIC indicators. "
            "Results from this run are for testing only and must not be reported."
        )
        indicators_df = generate_synthetic_indicators()

    # Compute AHP weights
    weights, cr = compute_ahp_weights(AHP_MATRIX)

    # Compute risk index
    risk_index = compute_risk_index(indicators_df, weights)

    # Classify into risk zones
    risk_class = classify_risk(risk_index)

    # Add results to dataframe
    result = indicators_df.copy()
    result["risk_index"] = risk_index
    result["risk_class"] = risk_class
    result["risk_label"] = risk_class.map(RISK_CLASSES)

    # Log distribution
    dist = result["risk_label"].value_counts()
    logger.info("Risk class distribution:\n%s", dist.to_string())

    # Validate if CGWB categories available
    if validate and "cgwb_category" in result.columns:
        validate_against_cgwb(
            risk_class, result["cgwb_category"],
            risk_index=result["risk_index"],
            extraction_stage=result["extraction_stage"] if "extraction_stage" in result else None,
        )

    logger.info("Module 2 completed successfully")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    result = run_module2()
    print("\nSample output (first 10 rows):")
    print(result[["location_id", "risk_index", "risk_class", "risk_label"]].head(10))
