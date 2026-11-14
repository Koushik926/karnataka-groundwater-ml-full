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

**Status:** Fixed. (The "68%" quoted here was measured on synthetic data; the real binary agreement is 77.3% — see section 3.)

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

> **Replaced 7 November 2026.** The table that stood here (RMSE 3.6261, R² 0.4030,
> "68.0% CGWB validation accuracy", kappa 0.536) was produced by `_synthetic_data()`,
> not by the CGWB files. No real run ever produced those numbers. The figures below
> come from `python -m src.main` on the real data and regenerate with it.

### Module 1: Prediction Models (validation set, 2017–2020)

| Model | Validation RMSE | Validation MAE | Validation R² |
|-------|----------------|----------------|---------------|
| Random Forest | 3.9216 | 2.3868 | 0.6941 |
| **XGBoost** | **3.9131** | **2.3486** | **0.6954** |
| SVR | 5.8963 | 3.6737 | 0.3084 |
| Persistence baseline | 4.9612 | 3.1169 | 0.5104 |

**Best Model:** XGBoost (auto-selected on lowest validation RMSE)

**Held-out test period (Nov 2020 – Aug 2024, 16,976 rows):**
RMSE **3.1364 m**, MAE 1.9862 m, R² **0.6320** —
against a persistence baseline of RMSE 3.8382 and R² 0.4489.

### Module 2: Risk Classification (177 taluks)

| Metric | Value |
|--------|-------|
| AHP Consistency Ratio | 0.0542 (< 0.1 threshold) |
| Exact 4-class agreement | 23.9% (κ = 0.001) |
| **Binary agreement vs CGWB** | **77.3%** (precision 0.66, recall 0.45) |
| Spearman rank vs CGWB category | 0.276 |

The 4-class figure is low by construction: Jenks classes are *relative* to the taluks
assessed, CGWB categories are *absolute* extraction thresholds. Binary agreement and
rank correlation are the measures that test whether the right taluks rank at the top.

---

## 4. Known Limitations

1. **Deep-aquifer blindness:** the index is built from shallow monitored wells, so it misses 28 taluks that CGWB rates stressed but whose shallow water table is flat (5.25 m mean depth, 122% mean extraction). Recall is 0.45 for this reason. Addressing it needs deep-well or extraction data — a Phase 2 objective.

   *(This slot previously read "Current implementation uses synthetic data". That was fixed on 6 November 2026; the pipeline now loads the real CGWB files by default and the synthetic fallback has been removed.)*

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
*Evidence:* test R² −0.098 → **0.576** (XGBoost), baseline 0.449. *(0.576 was the figure before rainfall was added; it is now 0.632.)*

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
from the CGWB data. AHP matrix reduced to 4×4; CR re-checked = 0.0439 < 0.1. *(Superseded: rainfall_dependence is now measured from NASA POWER data, so the matrix is back to 5×5 with CR 0.0542.)*

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
recovery, 1,270 no significant trend (the three categories are exhaustive: an
earlier count said 1,255, because 15 stations with a Sen's slope of exactly
zero fell through every branch). Kolar (189% extraction) now ranks #1.
Binary agreement with CGWB rose to 77.8% (precision 0.62, recall 0.62) at district level. *(Module 2 now works at taluk level: 77.3%, precision 0.66, recall 0.45 across 177 taluks.)*

### Note on validation metrics
*Current figures, taluk level, from the run on 13 November 2026.* Exact 4-class
agreement with CGWB is 23.9% (κ = 0.001) and this is expected, not a defect: our
Jenks classes are *relative* to the 177 taluks assessed, whereas CGWB categories
are *absolute* thresholds on the stage of extraction, and most taluks are "safe".
The two distributions cannot align by construction, and κ collapses under that
class imbalance. Binary agreement (77.3%, precision 0.66, recall 0.45) and the
Spearman rank correlation (0.276) are therefore reported alongside, because they
test what actually matters — whether the right taluks rank at the top.

*(The 18.5% / κ 0.063 / Spearman 0.359 figures previously quoted here were the
district-level run, which is superseded and which also used only four of the five
indicators.)*

### Note on the normalisation choice
Min-max scaling is outlier-sensitive and this data has outliers, so in November
2026 we tested the two standard alternatives against CGWB: clipping at the
5th/95th percentile gave 67.6% binary agreement and rank scaling 63.6%, against
77.3% for min-max. Both raised recall but cost far more in precision. Min-max was
kept on that evidence. Reproduce with `python experiments/normalisation_choice.py`.
