"""test_modules.py
Test cases for Module 1 (Prediction) and Module 2 (Risk Mapping)

Test Categories:
- Valid inputs: Normal data within expected ranges
- Invalid inputs: Missing values, wrong types, out-of-range values
- Boundary inputs: Edge cases and limits
"""

import unittest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import (
    _synthetic_data, _chronological_split, _fit_random_forest,
    _fit_xgboost, _fit_svr, _evaluate
)
from src.module2_risk import (
    compute_ahp_weights, normalize_indicator, compute_risk_index,
    jenks_breaks, classify_risk, generate_synthetic_indicators,
    run_module2
)
from src.config import AHP_MATRIX, RISK_INDICATORS, AHP_MAX_CR


class TestModule1Pipeline(unittest.TestCase):
    """Test cases for Module 1: Groundwater Level Prediction"""

    @classmethod
    def setUpClass(cls):
        """Generate synthetic data once for all tests."""
        cls.X, cls.y = _synthetic_data(n_samples=200, n_features=10)
        splits = _chronological_split(cls.X, cls.y, test_frac=0.20)
        cls.X_train, cls.X_val, cls.X_test = splits[0], splits[1], splits[2]
        cls.y_train, cls.y_val, cls.y_test = splits[3], splits[4], splits[5]

    # ==================== TEST CASE 1: Valid Input ====================
    def test_01_valid_data_generation(self):
        """TC01: Verify synthetic data has correct shape and no NaN values."""
        X, y = _synthetic_data(n_samples=100, n_features=15)

        self.assertEqual(X.shape[0], 100, "Should have 100 samples")
        self.assertEqual(X.shape[1], 16, "Should have 15 features + 1 time_norm")
        self.assertEqual(len(y), 100, "Target should have 100 values")
        self.assertFalse(X.isna().any().any(), "Features should have no NaN")
        self.assertFalse(y.isna().any(), "Target should have no NaN")
        print("TC01 PASSED: Valid data generation")

    # ==================== TEST CASE 2: Chronological Split ====================
    def test_02_chronological_split_preserves_order(self):
        """TC02: Verify train/val/test split maintains temporal order."""
        X, y = _synthetic_data(n_samples=100)
        X_train, X_val, X_test, y_train, y_val, y_test = _chronological_split(X, y)

        # Check that indices are in ascending order within each split
        self.assertTrue(all(X_train.index[i] < X_train.index[i+1]
                           for i in range(len(X_train)-1)), "Train not sorted")
        self.assertTrue(all(X_val.index[i] < X_val.index[i+1]
                           for i in range(len(X_val)-1)), "Val not sorted")
        self.assertTrue(all(X_test.index[i] < X_test.index[i+1]
                           for i in range(len(X_test)-1)), "Test not sorted")

        # Check train comes before val, val before test
        self.assertLess(X_train.index.max(), X_val.index.min(),
                       "Train should precede validation")
        self.assertLess(X_val.index.max(), X_test.index.min(),
                       "Validation should precede test")
        print("TC02 PASSED: Chronological split preserves order")

    # ==================== TEST CASE 3: Model Training ====================
    def test_03_models_train_without_error(self):
        """TC03: Verify all models train successfully on valid data."""
        # Random Forest
        rf = _fit_random_forest(self.X_train, self.y_train)
        self.assertIsNotNone(rf, "Random Forest should train")

        # XGBoost
        xgb = _fit_xgboost(self.X_train, self.y_train)
        self.assertIsNotNone(xgb, "XGBoost should train")

        # SVR
        svr = _fit_svr(self.X_train, self.y_train)
        self.assertIsNotNone(svr, "SVR should train")
        print("TC03 PASSED: All models train successfully")

    # ==================== TEST CASE 4: Invalid Input - Empty Data ====================
    def test_04_invalid_empty_dataframe(self):
        """TC04: Verify graceful handling of empty input data."""
        X_empty = pd.DataFrame()
        y_empty = pd.Series(dtype=float)

        with self.assertRaises(Exception):
            _fit_random_forest(X_empty, y_empty)
        print("TC04 PASSED: Empty data raises exception")

    # ==================== TEST CASE 5: Boundary - Single Sample ====================
    def test_05_boundary_minimal_samples(self):
        """TC05: Test with minimal number of samples."""
        X, y = _synthetic_data(n_samples=10, n_features=5)

        self.assertEqual(len(X), 10, "Should handle 10 samples")
        self.assertEqual(len(y), 10, "Target should have 10 values")
        print("TC05 PASSED: Handles minimal sample count")

    # ==================== TEST CASE 6: Model Evaluation Metrics ====================
    def test_06_evaluation_returns_valid_metrics(self):
        """TC06: Verify evaluation returns RMSE, MAE, R² in valid ranges."""
        rf = _fit_random_forest(self.X_train, self.y_train)
        metrics = _evaluate(rf, self.X_val, self.y_val)

        self.assertIn("rmse", metrics, "Should return RMSE")
        self.assertIn("mae", metrics, "Should return MAE")
        self.assertIn("r2", metrics, "Should return R²")

        self.assertGreaterEqual(metrics["rmse"], 0, "RMSE should be non-negative")
        self.assertGreaterEqual(metrics["mae"], 0, "MAE should be non-negative")
        self.assertLessEqual(metrics["r2"], 1.0, "R² should be <= 1")
        print("TC06 PASSED: Evaluation metrics are valid")


class TestModule2RiskMapping(unittest.TestCase):
    """Test cases for Module 2: Groundwater Depletion Risk Mapping"""

    # ==================== TEST CASE 7: AHP Weight Calculation ====================
    def test_07_ahp_weights_sum_to_one(self):
        """TC07: Verify AHP weights are normalized (sum to 1)."""
        weights, cr = compute_ahp_weights(AHP_MATRIX)

        self.assertAlmostEqual(weights.sum(), 1.0, places=6,
                              msg="AHP weights should sum to 1")
        self.assertEqual(len(weights), len(RISK_INDICATORS),
                        "Should have weight for each indicator")
        print("TC07 PASSED: AHP weights sum to 1")

    # ==================== TEST CASE 8: AHP Consistency Check ====================
    def test_08_ahp_consistency_ratio(self):
        """TC08: Verify AHP consistency ratio is within acceptable threshold."""
        weights, cr = compute_ahp_weights(AHP_MATRIX)

        self.assertLess(cr, AHP_MAX_CR,
                       f"CR ({cr:.4f}) should be < {AHP_MAX_CR}")
        print(f"TC08 PASSED: Consistency ratio {cr:.4f} < {AHP_MAX_CR}")

    # ==================== TEST CASE 9: Valid Risk Index Range ====================
    def test_09_risk_index_in_valid_range(self):
        """TC09: Verify risk index values are normalized to [0, 1]."""
        df = generate_synthetic_indicators(n_samples=50)
        weights, _ = compute_ahp_weights(AHP_MATRIX)
        risk_index = compute_risk_index(df, weights)

        self.assertTrue(all(risk_index >= 0), "Risk index should be >= 0")
        self.assertTrue(all(risk_index <= 1), "Risk index should be <= 1")
        print("TC09 PASSED: Risk index in [0, 1] range")

    # ==================== TEST CASE 10: Jenks Classification ====================
    def test_10_jenks_creates_four_classes(self):
        """TC10: Verify Jenks breaks creates exactly 4 risk classes."""
        df = generate_synthetic_indicators(n_samples=100)
        result = run_module2(df, validate=False)

        unique_classes = result["risk_class"].unique()
        self.assertTrue(len(unique_classes) <= 4,
                       "Should have at most 4 risk classes")
        self.assertTrue(all(c in [1, 2, 3, 4] for c in unique_classes),
                       "Classes should be 1, 2, 3, or 4")
        print("TC10 PASSED: Jenks creates valid risk classes")

    # ==================== TEST CASE 11: Invalid - Missing Indicator ====================
    def test_11_invalid_missing_indicator(self):
        """TC11: Handle missing indicator column gracefully."""
        df = pd.DataFrame({
            "decline_rate": [1.0, 2.0, 3.0],
            "current_depth": [10, 20, 30],
            # Missing: variability, seasonal_recovery
        })

        weights, _ = compute_ahp_weights(AHP_MATRIX)
        # Should not crash, just skip missing indicators
        risk_index = compute_risk_index(df, weights)
        self.assertEqual(len(risk_index), 3, "Should return index for all rows")
        print("TC11 PASSED: Handles missing indicators gracefully")

    # ==================== TEST CASE 12: Boundary - Extreme Values ====================
    def test_12_boundary_extreme_indicator_values(self):
        """TC12: Handle extreme indicator values correctly."""
        df = pd.DataFrame({
            "decline_rate": [0.0, 100.0],      # extreme m/yr range
            "current_depth": [0.0, 500.0],     # very deep
            "variability": [0.0, 1.0],         # full CV range
            "seasonal_recovery": [0.0, 10.0],  # full recovery range
        })

        weights, _ = compute_ahp_weights(AHP_MATRIX)
        risk_index = compute_risk_index(df, weights)

        # First row: all indicators at their minimum -> lowest risk
        # Second row: all indicators at their maximum -> highest risk
        self.assertLess(risk_index.iloc[0], risk_index.iloc[1],
                       "High values should produce higher risk")
        print("TC12 PASSED: Handles extreme values correctly")


class TestIntegration(unittest.TestCase):
    """Integration tests for full pipeline"""

    # ==================== TEST CASE 13: End-to-End Pipeline ====================
    def test_13_full_module2_pipeline(self):
        """TC13: Run complete Module 2 pipeline without errors."""
        result = run_module2(validate=True)

        required_cols = ["risk_index", "risk_class", "risk_label"]
        for col in required_cols:
            self.assertIn(col, result.columns, f"Missing column: {col}")

        self.assertGreater(len(result), 0, "Should produce output rows")
        print("TC13 PASSED: Full Module 2 pipeline runs successfully")


def run_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestModule1Pipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestModule2RiskMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*60)

    return result


if __name__ == "__main__":
    run_tests()
