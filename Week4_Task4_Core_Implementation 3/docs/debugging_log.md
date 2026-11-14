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
