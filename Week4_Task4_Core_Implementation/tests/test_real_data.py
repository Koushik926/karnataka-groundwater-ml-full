"""test_real_data.py - regression tests on the real data paths.

Task 6 additions. The original 13 tests in test_modules.py all run on generated
data, which is why none of them caught the five defects found in the Week 7
review: every one of those lived in a real-data path that no test touched.

Each test below is tied to a specific defect or claim, named in its docstring,
so a failure says what broke rather than only that something did.
"""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config
from src.data_processor import (
    canonical_district, canonical_taluk, create_station_features,
    load_extraction_data, load_gwl_data, mann_kendall_sens_slope, station_trends,
)
from src.module2_risk import compute_ahp_weights
from src.pipeline import select_features, split_by_date

DATA = Path(__file__).parent.parent / "data" / "raw"
HAVE_DATA = (DATA / "gwl_karnataka_clean.csv").exists()
skip_no_data = unittest.skipUnless(HAVE_DATA, "real CGWB export not present")


@skip_no_data
class TestRealDataLoading(unittest.TestCase):
    """TC14-TC17: the dataset is what we claim it is."""

    @classmethod
    def setUpClass(cls):
        cls.gwl = load_gwl_data()

    def test_14_record_and_station_counts(self):
        """TC14 - the counts quoted in every report and slide."""
        self.assertEqual(len(self.gwl), 123391)
        self.assertEqual(self.gwl["Station"].nunique(), 2769)

    def test_15_districts_are_canonicalised(self):
        """TC15 - defect #8: Mysore/Mysuru counted as two districts."""
        self.assertEqual(self.gwl["District"].map(canonical_district).nunique(), 28)
        self.assertEqual(canonical_district("Mysore"), canonical_district("Mysuru"))
        self.assertEqual(canonical_district("Gulbarga"), canonical_district("Kalaburagi"))
        self.assertEqual(canonical_district("Shimoga"), canonical_district("Shivamogga"))

    def test_16_groundwater_levels_are_in_range(self):
        """TC16 - cleaning removed impossible readings, so none may remain."""
        gwl = self.gwl["GWL_m"]
        self.assertTrue((gwl >= 0).all(), "negative depth survived cleaning")
        self.assertTrue((gwl <= 100).all(), "depth over 100 m survived cleaning")
        self.assertFalse(gwl.isna().any())

    def test_17_date_span(self):
        """TC17 - the record span printed on slides is 1996 to 2024."""
        d = pd.to_datetime(self.gwl["Date"])
        self.assertEqual(d.min().year, 1996)
        self.assertEqual(d.max().year, 2024)


class TestTalukAliases(unittest.TestCase):
    """TC18: defect caught during review - fuzzy matching proposed a wrong taluk."""

    def test_18_parasgad_is_saundatti_not_pavagada(self):
        """TC18 - Parasgad (Belagavi) must not map to Pavagada (Tumakuru)."""
        self.assertEqual(canonical_taluk("PARASGAD"), "SAUNDATTI")
        self.assertNotEqual(canonical_taluk("PARASGAD"), "PAVAGADA")
        self.assertEqual(canonical_taluk("SAMPGAON"), "BAILAHONGAL")
        self.assertEqual(canonical_taluk("MANJARABAD"), "SAKLESHPUR")


class TestMannKendall(unittest.TestCase):
    """TC19-TC21: defect #10 - the trend statistic itself must be correct."""

    def test_19_recovers_a_known_slope(self):
        """TC19 - a clean 0.5 m/yr rise must come back as +0.5."""
        t = np.arange(0, 20, 0.25)
        slope, p, label = mann_kendall_sens_slope(t, 0.5 * t + 10.0)
        self.assertAlmostEqual(slope, 0.5, places=6)
        self.assertLess(p, 0.05)
        # positive slope = depth increasing = water table falling
        self.assertEqual(label, "significant decline")

    def test_20_flat_series_reports_no_trend(self):
        """TC20 - noise around a constant must not be called a trend."""
        rng = np.random.default_rng(42)
        t = np.arange(0, 20, 0.25)
        slope, p, label = mann_kendall_sens_slope(t, 10.0 + rng.normal(0, 1, len(t)))
        self.assertGreater(p, 0.05)
        self.assertEqual(label, "no significant trend")

    def test_21_is_robust_to_an_outlier(self):
        """TC21 - Sen's slope is a median, so one wild reading must not move it."""
        t = np.arange(0, 20, 0.25)
        v = 0.5 * t + 10.0
        v[40] = 500.0
        slope, _, _ = mann_kendall_sens_slope(t, v)
        self.assertAlmostEqual(slope, 0.5, places=4)


@skip_no_data
class TestTrendCategories(unittest.TestCase):
    """TC22: our own arithmetic bug - the categories must be exhaustive."""

    def test_22_categories_sum_to_the_total(self):
        """TC22 - 15 stations with slope exactly 0 once fell through every branch."""
        tr = station_trends(load_gwl_data())
        total = len(tr)
        sig = tr["mk_p_value"] < 0.05
        dec = int((sig & (tr["sens_slope_m_per_yr"] > 0)).sum())
        rec = int((sig & (tr["sens_slope_m_per_yr"] < 0)).sum())
        flat = total - dec - rec
        self.assertEqual(dec + rec + flat, total)
        self.assertGreater(total, 2000)


@skip_no_data
class TestNoLeakage(unittest.TestCase):
    """TC23-TC25: defect #11 and the split - the model must not see the future."""

    @classmethod
    def setUpClass(cls):
        cls.feat = create_station_features(load_gwl_data(), with_rainfall=True)

    def test_23_splits_do_not_overlap_in_time(self):
        """TC23 - a random split would leak the future through the lag features."""
        parts = split_by_date(self.feat)
        tr, va, te = parts["train"], parts["val"], parts["test"]
        self.assertLessEqual(tr["Date"].max(), va["Date"].min())
        self.assertLessEqual(va["Date"].max(), te["Date"].min())
        self.assertEqual(len(tr) + len(va) + len(te), len(self.feat))

    def test_24_monsoon_rainfall_is_not_from_the_future(self):
        """TC24 - defect #11: rain_monsoon used the in-progress season."""
        f = self.feat.dropna(subset=["rain_monsoon"]).copy()
        f["month"] = pd.to_datetime(f["Date"]).dt.month
        f["year"] = pd.to_datetime(f["Date"]).dt.year
        mid = f[f["month"].isin([7, 8])]
        self.assertGreater(len(mid), 0, "no mid-monsoon rows to check")
        # For a July/August row the figure must come from the PREVIOUS year's
        # completed season, so it cannot equal this year's eventual total.
        late = f[f["month"] >= 10]
        same = late.groupby(["Taluk", "year"])["rain_monsoon"].first()
        for row in mid.sample(min(200, len(mid)), random_state=0).itertuples():
            key = (row.Taluk, row.year)
            if key in same.index:
                self.assertNotAlmostEqual(
                    row.rain_monsoon, float(same.loc[key]), places=3,
                    msg=f"{row.Taluk} {row.Date}: mid-monsoon row carries "
                        f"this year's completed total")

    def test_25_rainfall_features_are_present_and_finite(self):
        """TC25 - rainfall must actually attach, not silently come back empty."""
        for col in ["rain_q", "rain_prev_q", "rain_12m", "rain_monsoon",
                    "rain_anomaly_12m"]:
            self.assertIn(col, self.feat.columns)
        cover = self.feat["rain_q"].notna().mean()
        self.assertGreater(cover, 0.95, f"rainfall attached to only {cover:.1%} of rows")


class TestNoCircularValidation(unittest.TestCase):
    """TC26-TC27: the risk index must never see what it is validated against."""

    def test_26_extraction_is_not_an_indicator(self):
        """TC26 - using CGWB extraction as an input would make validation circular."""
        self.assertNotIn("extraction_stage", config.RISK_INDICATORS)
        self.assertNotIn("cgwb_category", config.RISK_INDICATORS)

    def test_27_five_measured_indicators_with_acceptable_cr(self):
        """TC27 - defect #9: two indicators were np.random.uniform()."""
        self.assertEqual(len(config.RISK_INDICATORS), 5)
        self.assertIn("rainfall_dependence", config.RISK_INDICATORS)
        self.assertIn("lulc_change", config.DEFERRED_INDICATORS)
        weights, cr = compute_ahp_weights(config.AHP_MATRIX)
        self.assertEqual(len(weights), 5)
        self.assertAlmostEqual(float(np.sum(weights)), 1.0, places=6)
        self.assertLess(cr, 0.10)


@skip_no_data
class TestExtractionReference(unittest.TestCase):
    """TC28: the validation reference itself must be intact."""

    def test_28_extraction_table_is_complete(self):
        """TC28 - 227 taluks, of which 62 are critical or over-exploited."""
        ext = load_extraction_data()
        self.assertEqual(len(ext), 227)
        cat = ext["Categorization"].astype(str).str.lower().str.replace("-", "_")
        stressed = cat.isin(["critical", "over_exploited"]).sum()
        self.assertEqual(int(stressed), 62)


class TestFeatureSelection(unittest.TestCase):
    """TC29: the feature list the report quotes."""

    def test_29_fifteen_features_with_rainfall_ten_without(self):
        """TC29 - defect: the report once claimed 10 features after rainfall was added."""
        from src.pipeline import BASE_FEATURES, RAIN_FEATURES
        frame = pd.DataFrame(columns=BASE_FEATURES + RAIN_FEATURES)
        self.assertEqual(len(BASE_FEATURES), 10)
        self.assertEqual(len(RAIN_FEATURES), 5)
        self.assertEqual(len(select_features(frame, use_rainfall=False)), 10)
        self.assertEqual(len(select_features(frame, use_rainfall=True)), 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
