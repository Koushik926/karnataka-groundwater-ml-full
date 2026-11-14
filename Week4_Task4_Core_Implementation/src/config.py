"""config.py

Project-wide configuration constants.

These values are taken directly from the Week 2 / Week 3 design documents:

* AHP pairwise comparison matrix (Saaty 1–9 scale) for the five risk indicators
  used in Module 2.  The weights are accepted only when the consistency ratio
  (CR) is below 0.1.
* Risk class thresholds and labels.
* Default model hyper-parameters for Module 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


# ---------------------------------------------------------------------------
# Module 1 – model defaults
# ---------------------------------------------------------------------------

@dataclass
class Model1Config:
    """Hyper-parameters for the Module 1 candidate models."""
    random_forest_estimators: int = 200
    xgboost_estimators: int = 300
    xgboost_lr: float = 0.05
    xgboost_max_depth: int = 6
    svr_c: float = 10.0
    svr_epsilon: float = 0.1
    lstm_hidden: int = 64
    lstm_layers: int = 2
    lstm_epochs: int = 30
    lstm_lr: float = 1e-3
    lstm_batch_size: int = 64


# ---------------------------------------------------------------------------
# Module 2 – AHP risk indicators
# ---------------------------------------------------------------------------

# Pairwise comparison matrix (Saaty 1-9 scale) for the five risk indicators.
#
# History: the Week 3 design listed five indicators but two of them
# (rainfall_dependence, lulc_change) were filled with random numbers in the
# Week 4 code, so in Week 7 they were removed and the matrix was cut to 4x4.
# Real rainfall (NASA POWER) (src/rainfall.py) has since been integrated, so
# rainfall_dependence is now measured and the matrix is back to 5x5.
# lulc_change remains deferred - no land-cover raster is integrated yet.
#
# Order: decline_rate, current_depth, variability, rainfall_dependence,
#        seasonal_recovery
AHP_MATRIX = [
    [1.0, 3.0, 5.0, 7.0, 9.0],   # decline_rate (Sen's slope, m/yr)
    [1/3, 1.0, 3.0, 5.0, 7.0],   # current_depth
    [1/5, 1/3, 1.0, 3.0, 5.0],   # variability
    [1/7, 1/5, 1/3, 1.0, 3.0],   # rainfall_dependence (NASA POWER-derived)
    [1/9, 1/7, 1/5, 1/3, 1.0],   # seasonal_recovery
]

RISK_INDICATORS: List[str] = [
    "decline_rate",
    "current_depth",
    "variability",
    "rainfall_dependence",
    "seasonal_recovery",
]

# Still not computable: no land-cover raster integrated yet.
DEFERRED_INDICATORS: List[str] = ["lulc_change"]

# Risk class labels and their mapping to CGWB categories (used for validation).
RISK_CLASSES: Dict[int, str] = {
    1: "Low",
    2: "Moderate",
    3: "High",
    4: "Very High",
}

# Mapping from CGWB assessment category -> risk class (for validation only).
CGWB_TO_RISK: Dict[str, int] = {
    "safe": 1,
    "semi_critical": 2,
    "semi-critical": 2,
    "critical": 3,
    "over_exploited": 4,
    "over-exploited": 4,
}


def normalise_cgwb_category(value) -> str:
    """Return a CGWB category string in the canonical lower-case form."""
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_")


# Maximum acceptable consistency ratio for the AHP weights.
AHP_MAX_CR: float = 0.1


# ---------------------------------------------------------------------------
# Data pipeline defaults
# ---------------------------------------------------------------------------
# These are the rules the code actually applies. An earlier version of this file
# also declared MIN_YEARS, MAX_MISSING_FRAC, TUKEY_K, LULC_RADIUS_M and SEASONS;
# none of them was read anywhere, and TUKEY_K in particular implied a Tukey-fence
# outlier filter that does not exist. They were removed rather than left to
# suggest behaviour the pipeline does not have. What the pipeline really does:

# A reading outside this range is physically impossible for these wells and is
# dropped during cleaning (76 rows in the current CGWB export).
GWL_MIN_M: float = 0.0
GWL_MAX_M: float = 100.0

# A station needs at least this many quarterly readings before it is used, so
# that the four lag features and the rolling statistics are meaningful.
MIN_RECORDS_PER_STATION: int = 20

# Chronological split fractions. Never a random split: with lag features a
# random split puts a row's own neighbours in training and leaks the future.
TRAIN_FRAC: float = 0.70
VAL_FRAC: float = 0.15

# Significance level for the Mann-Kendall trend test.
TREND_ALPHA: float = 0.05
