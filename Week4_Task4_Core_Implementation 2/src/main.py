"""
Main entry point for Week 4 Task 4 – core implementation.

The goal is to keep the project structure minimal while still allowing the
pipeline and modelling code to be imported and executed.  A small integration
script is provided so that the user can run ``python -m src`` to verify the
overall set-up.
"""

from pathlib import Path
import logging

# Configure a lightweight logger that honours the ``DEBUG`` flag if set.
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Example: quick sanity check that the required directories exist.
BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

for d in (DATA_DIR, MODEL_DIR, OUTPUT_DIR):
    if not d.exists():
        logger.warning("Expected directory %s does not exist - creating it.", d)
        d.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    # Run the full pipeline when the package is executed directly.
    from .pipeline import run_module1
    from .module2_risk import run_module2

    logger.info("="*60)
    logger.info("GROUNDWATER DEPLETION PREDICTION AND RISK MAPPING")
    logger.info("="*60)

    # Module 1: Prediction
    logger.info("\n--- MODULE 1: Groundwater Level Prediction ---")
    run_module1(root_dir=BASE_DIR)
    logger.info("Module 1 completed.\n")

    # Module 2: Risk Mapping
    logger.info("--- MODULE 2: Depletion Risk Mapping ---")
    result = run_module2(validate=True)

    # Save risk mapping output
    risk_output = OUTPUT_DIR / "module2_risk_mapping.csv"
    result.to_csv(risk_output, index=False)
    logger.info("Risk mapping saved to %s", risk_output)

    logger.info("\n" + "="*60)
    logger.info("ALL MODULES COMPLETED SUCCESSFULLY")
    logger.info("="*60)
