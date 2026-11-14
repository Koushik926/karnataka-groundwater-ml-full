"""
Entry point - runs the integrated system end to end.

    python -m src.main

Flow (Week 7 consolidation):

    CGWB data -> data_processor -> Module 1 (prediction)
                                      |
                        predicted decline rate per district
                                      v
                 data_processor.create_district_indicators
                                      v
                            Module 2 (risk mapping)
                                      v
                   outputs/module2_risk_mapping.csv

Module 2 now consumes Module 1's forecasts.  Previously the two modules ran
independently: Module 2 generated its own random locations and ignored every
prediction Module 1 made.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

for _d in (DATA_DIR, MODEL_DIR, OUTPUT_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def main() -> None:
    from .data_processor import (create_district_indicators, create_taluk_indicators,
                                 load_extraction_data, load_gwl_data)
    from .module2_risk import run_module2
    from .pipeline import run_module1

    logger.info("=" * 68)
    logger.info("GROUNDWATER DEPLETION PREDICTION AND RISK MAPPING - KARNATAKA")
    logger.info("=" * 68)

    # ---------------- Module 1 ----------------
    logger.info("--- MODULE 1: Groundwater Level Prediction ---")
    m1 = run_module1(root_dir=BASE_DIR)
    logger.info("Module 1 complete (model: %s)", m1["model_name"])

    # ---------------- Integration ----------------
    logger.info("--- INTEGRATION: Module 1 forecasts -> Module 2 indicators ---")
    trends = m1.get("district_trends")
    if trends is None:
        logger.error("Module 1 produced no district trends; Module 2 cannot run on real data.")
        return

    gwl = load_gwl_data()
    extraction = load_extraction_data()

    # Real rainfall (NASA POWER) -> the rainfall-dependence indicator
    rain_dep = None
    try:
        from .rainfall import (DAILY_CSV, attach_to_observations,
                               quarterly_features, rainfall_dependence)
        if DAILY_CSV.exists():
            daily = pd.read_csv(DAILY_CSV, parse_dates=["date"])
            merged = attach_to_observations(gwl, quarterly_features(daily))
            rain_dep = rainfall_dependence(merged)
        else:
            logger.warning("No rainfall cache - run `python -m src.rainfall` first")
    except Exception as exc:
        logger.warning("Rainfall dependence unavailable (%s)", exc)

    # Taluk level: the unit CGWB assesses, so validation is one-to-one
    indicators = create_taluk_indicators(gwl, extraction, rainfall_dep=rain_dep)
    indicators.to_csv(OUTPUT_DIR / "module2_taluk_indicators.csv", index=False)
    logger.info("Indicators for %d taluks -> %s",
                len(indicators), OUTPUT_DIR / "module2_taluk_indicators.csv")

    # District level kept as a coarser summary view
    district = create_district_indicators(gwl, extraction, forecast_trends=trends)
    district.to_csv(OUTPUT_DIR / "module2_district_indicators.csv", index=False)

    # ---------------- Module 2 ----------------
    logger.info("--- MODULE 2: Depletion Risk Mapping ---")
    result = run_module2(indicators, validate=True)

    keep = [c for c in [
        "Taluk", "District", "lat", "lon", "decline_rate", "pct_stations_declining",
        "rainfall_dependence", "n_stations",
        "forecast_trend_m_per_yr", "current_depth", "variability", "seasonal_recovery",
        "extraction_stage", "cgwb_category", "risk_index", "risk_class", "risk_label",
    ] if c in result.columns]
    result[keep].sort_values("risk_index", ascending=False).to_csv(
        OUTPUT_DIR / "module2_risk_mapping.csv", index=False)
    logger.info("Risk mapping -> %s", OUTPUT_DIR / "module2_risk_mapping.csv")

    # ---------------- Action briefs ----------------
    # A ranking says which taluks are worst; it does not say what to do. This
    # joins CGWB's own water balance to our trend and recommends an intervention
    # class with the programme that funds it.
    logger.info("--- ACTION BRIEFS: ranking -> recommended intervention ---")
    from .action_briefs import build as build_briefs, load_water_balance, state_summary
    briefs = build_briefs(OUTPUT_DIR / "module2_risk_mapping.csv")
    summary = state_summary(briefs, load_water_balance())
    logger.info("Karnataka annual overdraft: %.3f BCM across %d of %d CGWB taluks",
                summary["overdraft_bcm"], summary["taluks_overdrawn"],
                summary["taluks_assessed_cgwb"])
    logger.info("Interventions recommended: %s", summary["counts"])

    logger.info("=" * 68)
    logger.info("ALL MODULES COMPLETED")
    logger.info("=" * 68)


if __name__ == "__main__":
    main()
