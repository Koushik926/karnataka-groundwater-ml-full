# Debugging Log
## Groundwater Depletion Prediction and Risk Mapping System

**Project ID:** CAIML_Shobha_Rani_4_PS_160  
**Week 5 Task 5:** Complete, Refine & Debug Implementation  
**Date:** 31 October 2026

---

## 1. Issues Identified and Fixed

### Issue #1: SVR Model Negative R² Score
**Type:** Logical Error  
**Severity:** Medium  
**File:** `src/pipeline.py`

**Description:**  
The SVR model consistently produced negative R² values (-0.14) on validation data, indicating predictions worse than the mean baseline.

**Root Cause:**  
SVR with RBF kernel is sensitive to feature scaling. The synthetic data features had different scales (e.g., normalized time 0-1 vs. random normal values).

**Fix Applied:**  
For production use, added note to apply StandardScaler before SVR training. Current implementation accepts lower SVR performance since XGBoost is auto-selected as best model.

**Status:** Documented; XGBoost selected as primary model.

---

### Issue #2: Jenks Breaks Algorithm Edge Case
**Type:** Runtime Error  
**Severity:** High  
**File:** `src/module2_risk.py`

**Description:**  
`jenks_breaks()` raised `IndexError` when input array had fewer samples than requested classes (n_classes=4).

**Root Cause:**  
Algorithm attempted to create 4 breaks from less than 4 unique values.

**Fix Applied:**
```python
if n <= n_classes:
    return list(values)
```
Added early return to handle edge case gracefully.

**Status:** Fixed and tested (TC10, TC12).

---

### Issue #3: Missing Indicator Column Handling
**Type:** Validation Error  
**Severity:** Medium  
**File:** `src/module2_risk.py`

**Description:**  
`compute_risk_index()` raised `KeyError` when input DataFrame lacked some risk indicator columns.

**Root Cause:**  
Direct column access without existence check.

**Fix Applied:**
```python
if indicator not in df.columns:
    logger.warning("Indicator '%s' not found in data, skipping", indicator)
    continue
```
Added column existence check with warning log.

**Status:** Fixed and tested (TC11).

---

### Issue #4: AHP Consistency Ratio Calculation
**Type:** Logical Error  
**Severity:** Low  
**File:** `src/module2_risk.py`

**Description:**  
Initial AHP implementation calculated incorrect CR when n=2 (division by zero in RI lookup).

**Root Cause:**  
Random Index (RI) for n=2 is 0, causing division by zero.

**Fix Applied:**
```python
ri = RI_TABLE.get(n, 1.49)
cr = ci / ri if ri > 0 else 0.0
```
Added zero-check before division.

**Status:** Fixed; CR now correctly calculated as 0.0542.

---

### Issue #5: CGWB Category Mapping Case Sensitivity
**Type:** Validation Error  
**Severity:** Low  
**File:** `src/module2_risk.py`

**Description:**  
CGWB categories were case-sensitive, causing mismatches with varied input formats ("Safe" vs "safe").

**Root Cause:**  
Direct string comparison without normalization.

**Fix Applied:**  
Used consistent lowercase keys in `CGWB_TO_RISK` mapping. Input data should be lowercased before validation.

**Status:** Fixed; validation accuracy improved to 68%.

---

## 2. Test Cases Summary

| TC# | Category | Description | Input Type | Status |
|-----|----------|-------------|------------|--------|
| TC01 | Valid | Data generation shape and NaN check | Valid | ✅ PASS |
| TC02 | Valid | Chronological split preserves order | Valid | ✅ PASS |
| TC03 | Valid | All models train successfully | Valid | ✅ PASS |
| TC04 | Invalid | Empty DataFrame handling | Invalid | ✅ PASS |
| TC05 | Boundary | Minimal sample count (10) | Boundary | ✅ PASS |
| TC06 | Valid | Evaluation metrics validity | Valid | ✅ PASS |
| TC07 | Valid | AHP weights sum to 1 | Valid | ✅ PASS |
| TC08 | Valid | AHP consistency ratio < 0.1 | Valid | ✅ PASS |
| TC09 | Valid | Risk index in [0,1] range | Valid | ✅ PASS |
| TC10 | Valid | Jenks creates 4 risk classes | Valid | ✅ PASS |
| TC11 | Invalid | Missing indicator columns | Invalid | ✅ PASS |
| TC12 | Boundary | Extreme indicator values | Boundary | ✅ PASS |
| TC13 | Integration | Full Module 2 pipeline | Valid | ✅ PASS |

**Test Execution:**
```
Ran 13 tests in 0.618s
OK
```

---

## 3. Performance Metrics

### Module 1: Prediction Models

| Model | Validation RMSE | Validation MAE | Validation R² |
|-------|----------------|----------------|---------------|
| Random Forest | 3.9006 | 3.2118 | 0.3092 |
| **XGBoost** | **3.6261** | **3.0093** | **0.4030** |
| SVR | 5.0142 | 4.3076 | -0.1416 |

**Best Model:** XGBoost (auto-selected based on lowest RMSE)

### Module 2: Risk Classification

| Metric | Value |
|--------|-------|
| AHP Consistency Ratio | 0.0542 (< 0.1 threshold) |
| CGWB Validation Accuracy | 68.0% |
| Cohen's Kappa | 0.536 (moderate agreement) |

---

## 4. Known Limitations

1. **Synthetic Data:** Current implementation uses synthetic data for demonstration. Real CGWB/IMD data integration pending.

2. **LSTM Disabled:** LSTM model is scaffolded but disabled by default due to CPU training time. Enable with `USE_LSTM = True` in pipeline.py.

3. **Spatial Interpolation:** Kriging for spatial surface not yet implemented; planned for final version.

4. **Dashboard:** Requires `streamlit run dashboard.py` to launch; no deployment configured.

---

## 5. Files Modified

| File | Changes |
|------|---------|
| `src/main.py` | Updated to run both Module 1 and Module 2 |
| `src/pipeline.py` | No changes (stable) |
| `src/module2_risk.py` | NEW - AHP, Jenks, risk classification |
| `src/config.py` | No changes (AHP matrix already defined) |
| `tests/test_modules.py` | NEW - 13 test cases |
| `dashboard.py` | NEW - Streamlit visualization |
| `requirements.txt` | Added streamlit, plotly |

---

**Prepared by:** Team CAIML_Shobha_Rani_4_PS_160  
**Verified by:** Ms Indhuja Balakrishnan (Faculty Guide)

---

## 2. Week 7 Consolidation - Integration Defects Found and Fixed

Found while integrating Module 1 with Module 2 (Task 7). All five were silent:
the code ran and produced plausible-looking output every time.

### Issue #6: Pipeline never used the real CGWB data
**Type:** Logical · **Severity:** Critical · **File:** `src/pipeline.py`

*Symptom:* every reported metric came from random numbers; test R² was −0.098
(worse than predicting the mean).
*Root cause:* `_load_real_data()` looked for `data/raw/features.csv`, a file
that is never created. The `None` return silently triggered the synthetic
fallback, while 123,391 real observations sat unused in the same folder.
*Fix:* `load_feature_table()` now builds the feature table from the CGWB export
via `data_processor`; synthetic data is an explicit, warned fallback.
*Evidence:* test R² −0.098 → **0.576** (XGBoost), baseline 0.449.

### Issue #7: Module 2 ignored Module 1 entirely
**Type:** Integration · **Severity:** Critical · **File:** `src/main.py`

*Symptom:* risk map listed `LOC_000 … LOC_099`, not Karnataka districts.
*Root cause:* `main.py` called `run_module2()` with no arguments, so Module 2
generated its own synthetic indicators. The modules never exchanged data.
*Fix:* Module 1 → district trends → `create_district_indicators()` → Module 2.
*Evidence:* output is now 27 named districts with measured indicators.

### Issue #8: District join silently produced all-NaN categories
**Type:** Data · **Severity:** High · **File:** `src/data_processor.py`

*Symptom:* CGWB validation ran on 0 of 32 districts.
*Root cause:* the level export uses "Bagalkot"/"Mysore" while the extraction
sheet uses "BAGALKOT"/"MYSURU" and truncates to 13 characters. The level data
also contains **both** the old and new spellings, so single districts were
being split in two (33 "districts" for 31 real ones).
*Fix:* `canonical_district()` with a 20-entry alias map, applied at load time.
*Evidence:* 33 → 28 unique districts; unmatched categories 17 → 0.

### Issue #9: Two risk indicators were random numbers
**Type:** Validity · **Severity:** Critical · **File:** `src/data_processor.py`

*Symptom:* risk index changed meaninglessly between runs.
*Root cause:* `rainfall_dependence` and `lulc_change` were filled with
`np.random.uniform(...)` because IMD rainfall and LULC rasters are not yet
integrated; together they carried 10% of the AHP weight.
*Fix:* both removed and documented in `DEFERRED_INDICATORS`. Added
`seasonal_recovery` (pre-monsoon minus post-monsoon depth), which is measurable
from the CGWB data. AHP matrix reduced to 4×4; CR re-checked = 0.0439 < 0.1.

### Issue #10: "Predicted decline rate" was a mean-reversion artefact
**Type:** Logical · **Severity:** High · **Files:** `src/pipeline.py`, `src/data_processor.py`

*Symptom:* 17 of 27 districts showed rising water tables, and Chitradurga
(over-exploited, 107% extraction) was ranked the *lowest* risk district.
*Root cause:* the decline rate was the slope of a recursive four-quarter
forecast. Feeding predictions back as lags pulls the series toward the training
mean, so the slope encoded "how far the last reading sat from average", not
depletion. Diagnostics: 76.3% of stations' forecasts moved toward the overall
mean; corr(last observed depth, "trend") = **−0.665**; the predicted trends
were *anti-correlated* with observed trends (Spearman −0.21). This indicator
carried 55.8% of the AHP weight.
*Fix:* the trend indicator is now the **Mann–Kendall test with Sen's slope** on
the observed series, as the Week 3 design specified. Module 1's validated
one-step forecast is retained as a cross-check column only.
*Evidence:* 2,042 stations trended — 312 significant decline, 460 significant
recovery, 1,255 no significant trend. Kolar (189% extraction) now ranks #1.
Binary agreement with CGWB rose to 77.8% (precision 0.62, recall 0.62).

### Note on validation metrics
Exact 4-class agreement with CGWB is only 18.5% (κ = 0.063) and this is
expected, not a defect: our Jenks classes are *relative* to the 27 districts
assessed, whereas CGWB categories are *absolute* thresholds on the stage of
extraction (18 of 27 districts are "safe"). Binary agreement and Spearman rank
correlation (0.359 vs CGWB category) are therefore reported alongside.
