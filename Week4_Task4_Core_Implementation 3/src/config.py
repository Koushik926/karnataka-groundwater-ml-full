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

# Pairwise comparison matrix (Saaty 1–9 scale) for the five indicators.
# Order: predicted_decline_rate, current_depth, variability, rainfall_dependence,
#        lulc_change
AHP_MATRIX = [
    [1.0, 3.0, 5.0, 7.0, 9.0],   # predicted_decline_rate
    [1/3, 1.0, 3.0, 5.0, 7.0],   # current_depth
    [1/5, 1/3, 1.0, 3.0, 5.0],   # variability
    [1/7, 1/5, 1/3, 1.0, 3.0],   # rainfall_dependence
    [1/9, 1/7, 1/5, 1/3, 1.0],   # lulc_change
]

# Indicator names (must match the order used in AHP_MATRIX).
RISK_INDICATORS: List[str] = [
    "predicted_decline_rate",
    "current_depth",
    "variability",
    "rainfall_dependence",
    "lulc_change",
]

# Risk class labels and their mapping to CGWB categories (used for validation).
RISK_CLASSES: Dict[int, str] = {
    1: "Low",
    2: "Moderate",
    3: "High",
    4: "Very High",
}

# Mapping from CGWB assessment category → risk class (for validation only).
CGWB_TO_RISK: Dict[str, int] = {
    "safe": 1,
    "semi-critical": 2,
    "critical": 3,
    "over-exploited": 4,
}

# Maximum acceptable consistency ratio for the AHP weights.
AHP_MAX_CR: float = 0.1


# ---------------------------------------------------------------------------
# Data pipeline defaults
# ---------------------------------------------------------------------------

# Minimum years of records a well must have to be used in Module 1.
MIN_YEARS = 10
# Maximum fraction of missing seasonal readings allowed.
MAX_MISSING_FRAC = 0.30
# Tukey fence multiplier for outlier removal.
TUKEY_K = 1.5
# Radius (metres) used when extracting LULC share around a well.
LULC_RADIUS_M = 1000.0
# Seasons used in the system (CGWB observation schedule).
SEASONS = ["January", "May", "August", "November"]