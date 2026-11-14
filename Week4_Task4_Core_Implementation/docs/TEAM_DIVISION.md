# Team Work Division and Viva Preparation

**Project:** Spatio-Temporal Prediction and Risk Mapping of Groundwater Depletion in Karnataka
**Problem statement:** CAIML_Shobha_Rani_4_PS_160

> **Regenerated 7 November 2026** from a clean `python -m src.main` run. Every number below
> was printed by that run. Two earlier versions of this file were wrong in ways worth knowing
> about: the first scripted answers claiming synthetic metrics came from real CGWB data, and
> the second was left behind when rainfall was added and risk mapping moved from districts to
> taluks. **Re-run `python -m src.main` and read the real output before the viva — never
> memorise numbers from an older document.**

---

## MODULE 1: Groundwater Level Prediction
### KOUSHIK (R23EJ096) + KARTHIK (R23EJ168)

### Files
```
src/data_processor.py   data loading, cleaning, feature engineering, Mann-Kendall/Sen
src/rainfall.py         NASA POWER rainfall download and rainfall features
src/pipeline.py         model training, selection, forecasting
src/config.py           hyper-parameters
outputs/module1_*.csv   predictions, station forecasts, district trends
```

### Q&A

**Q: Where did the data come from?**
> Real CGWB quarterly observations for Karnataka, downloaded from the India-WRIS / National
> Water Data Portal. Two exports, 1991–2020 and 2021–2025, combined to 123,632 rows. After
> cleaning, 123,391 records from 2,769 stations, spanning January 1996 to August 2024.
> Rainfall comes from **NASA POWER** (PRECTOTCORR, bias-corrected MERRA-2 precipitation):
> 29 years of daily rainfall, 1996–2024, over the 105 grid cells covering Karnataka.

**Q: How did you clean it?**
> We removed 241 rows: **76** where the level was impossible (below 0 m or above 100 m) and
> **165** missing a level, date or district. Be precise about this split — an earlier version
> of our own report attributed all 241 to the out-of-range rule, which was wrong.

**Q: How many districts?**
> 28. The raw file contains 33 district labels, but Karnataka renamed several districts and
> the file carries both spellings — Mysore and Mysuru, Gulbarga and Kalaburagi, Shimoga and
> Shivamogga — so single districts were being counted twice. `canonical_district()` maps every
> spelling to one name.

**Q: What features?**
> Fifteen. Ten from the groundwater record: the previous four quarters' levels (lag 1–4), a
> four-quarter rolling mean and standard deviation, sine and cosine of the month to capture
> the monsoon cycle, and latitude and longitude. Five from rainfall: `rain_q` (the three
> months to the observation), `rain_prev_q`, `rain_12m`, `rain_monsoon` (the last **completed**
> June–September season) and `rain_anomaly_12m`. The target is the next quarter's depth.

**Q: Why not use the current monsoon total?**
> Because that leaks. Our first version of `rain_monsoon` used the whole June–September total,
> so an observation taken in August carried September's rainfall — rain that had not fallen
> yet. The season is now treated as complete only from October onwards. This is the kind of
> bug that quietly inflates a score, so it is worth stating that we found and fixed it.

**Q: Does rainfall actually help, or did you just add it because it sounds right?**
> We tested it rather than assuming. `experiments/ab_rainfall.py` trains the identical model
> with and without the five rainfall features on the same split: test R² rises from **0.576 to
> 0.632** and test RMSE falls from **3.365 m to 3.136 m**. That is the honest way to claim a
> feature matters.

**Q: Why NASA POWER and not IMD or ERA5?**
> IMD's gridded product needs a registered or paid download. We tried ERA5 through Open-Meteo
> first, but its free tier rate-limits on (locations × days) and issued multi-minute cooldowns
> part-way through 180 taluks × 29 years. NASA POWER is free, needs no key, and returns all
> 105 cells for a whole year in about two seconds. We cross-checked the two at Kolar for 2020:
> POWER 1139 mm vs ERA5 1104 mm, a 3% difference.

**Q: How do you know the rainfall data is right?**
> It reproduces Karnataka's geography without being told it. The driest taluks come out as
> Basavana Bagevadi, Bilgi and Indi at ~565 mm/year — the north interior dry belt. The wettest
> are Mangaluru, Belthangadi and Bantval at ~3,603 mm — the coastal Western Ghats. The monsoon
> accounts for 73% of annual rainfall. A dataset that gets a six-fold west-to-east gradient
> right in the correct direction is not mis-georeferenced.

**Q: How did you split the data?**
> Chronologically by observation date: train 1996 to May 2017 (79,218 rows), validation to
> November 2020 (16,975), test November 2020 to August 2024 (16,976). Never a random split —
> with lag features a random split puts a row's own neighbours in training and leaks the future.

**Q: Which model won, and what are the numbers?**
> XGBoost, selected on validation RMSE. Validation RMSE 3.913 m, R² 0.695. On the held-out
> test period **RMSE 3.136 m, MAE 1.986 m, R² 0.632**.

**Q: Is R² 0.632 good? Papers report 0.90.**
> It depends entirely on the split. Alkon et al. 2024 — reference [3] in our survey, using the
> same CGWB data — reports R² 0.4 to 0.6. The 0.85–0.90 studies test at known stations with
> monthly or daily data and short horizons, not a future-period holdout. The fair test is
> whether we beat a baseline that predicts "same as last reading": that baseline scores
> RMSE 3.838 and R² 0.449 on the same test period, and we beat it on both.

**Q: Why these three algorithms?**
> Random Forest and XGBoost handle non-linear relationships on tabular data and give feature
> importance; SVR is a different model family, useful as a contrast (it scored worst, R² 0.308
> on validation). A persistence baseline is included because a model that cannot beat "same as
> last time" is not worth deploying.

**Q: How did you handle missing feature values?**
> 6,656 values were imputed with the **training-set** median. Using the full dataset's median
> would leak test information into training.

**Q: How do you get a trend?**
> The Mann-Kendall test with Sen's slope per station — non-parametric, robust to outliers and
> irregular sampling. Of 2,042 stations with enough record, **312 show a significant decline,
> 460 a significant recovery, and 1,270 no significant trend** at p < 0.05.

**Q: 312 + 460 + 1,270 = 2,042 — but do the categories really cover everything?**
> Yes, and we had to fix our own arithmetic to be sure. An earlier count came to 2,027 because
> 15 stations have a Sen's slope of exactly zero and fell through every branch. The categories
> are now exhaustive.

**Q: More recovery than decline — is that wrong?**
> It is what the data says, and the official record agrees. The CGWB Karnataka Groundwater
> Year Book 2021–22 reports about 80% of monitored wells rising against the decadal mean in
> January 2022. But rising levels are not the same as sustainability: CGWB's own assessment
> shows recharge **falling** (18.16 to 17.74 BCM) while extraction **rose** (10.63 to 11.22
> BCM), and over a quarter of Karnataka's units remain critical or over-exploited.

---

## MODULE 2: Depletion Risk Mapping
### NITIN (R23EJ088) + VARSHITH (R23EJ100) + CHANDRASHEKAR (R23EQ029)

### Files
```
src/module2_risk.py     AHP weights, risk index, Jenks classification, validation
src/config.py           AHP matrix, risk classes, CGWB mapping
dashboard.py            Streamlit dashboard
notebooks/make_figures.py   all report and presentation figures
outputs/module2_*.csv   taluk indicators and the risk map
```

### Q&A

**Q: What unit do you assess, and why?**
> **Taluks — 177 of them.** This matters: CGWB itself assesses groundwater at taluk level, so
> assessing taluks makes validation a one-to-one comparison instead of a comparison against a
> district-level summary of taluk categories. 176 of our 177 taluks matched a CGWB category
> (99%). It also gives roughly six times the spatial resolution of our earlier district view.

**Q: Did the taluk names just match automatically?**
> No, and this is where we caught a real error. Name spellings differ between the CGWB
> extraction file and the India-WRIS export, so `TALUK_ALIASES` maps them by hand. Automated
> fuzzy matching proposed **Parasgad → Pavagada**, which is wrong — they are in different
> districts. Parasgad is in Belagavi and is now called **Saundatti**. Every alias was checked
> against its district rather than trusted on string similarity.

**Q: What is AHP?**
> The Analytic Hierarchy Process (Saaty). Indicators are compared in pairs on a 1–9 scale; the
> normalised principal eigenvector gives the weights. It is accepted only if the consistency
> ratio is below 0.10 — ours is **0.0542**.

**Q: What are your indicators and weights?**
> Five, all measured — none assumed:
>
> | Indicator | Weight | What it measures |
> |---|---|---|
> | decline_rate | 0.5028 | Mann-Kendall/Sen's slope, m/year |
> | current_depth | 0.2602 | Mean recent depth to water, m |
> | variability | 0.1344 | Coefficient of variation of the level |
> | rainfall_dependence | 0.0678 | Correlation of monsoon rain with post-monsoon recovery |
> | seasonal_recovery | 0.0348 | Pre-monsoon minus post-monsoon depth, m |

**Q: The design listed rainfall dependence and LULC change. What happened to them?**
> `rainfall_dependence` is now real and measured, from the NASA POWER data: per taluk, the
> correlation between the monsoon total and that monsoon's actual recovery (May depth minus
> November depth). A taluk whose recovery tracks the rain closely is exposed in a weak year.
> **LULC change is still deferred to Phase 2** — it needs land-cover rasters we have not
> integrated. It is listed in `DEFERRED_INDICATORS`, not silently dropped. In the Week 4 code
> both of these were being filled with `np.random.uniform()` — random numbers carrying 10% of
> the weight — which we removed.

**Q: Why Jenks natural breaks?**
> It chooses class boundaries that minimise variance within classes and maximise it between
> them, so the four risk classes follow natural groupings in the index rather than arbitrary
> cut-offs. Our breaks are 0.101 / 0.189 / 0.244 / 0.449 / 0.627, giving 47 Low, 95 Moderate,
> 32 High and 3 Very High taluks.

**Q: How do you validate?**
> Against CGWB's own categories, three ways, all at taluk level. Exact four-class agreement is
> **23.9%** with kappa 0.001. Binary agreement — our High/Very High against CGWB
> critical/over-exploited — is **77.3%**, precision 0.66, recall 0.45 (TP 23, FP 12, FN 28,
> TN 113). Spearman rank correlation with the CGWB category is **0.276**.

**Q: 23.9% and kappa near zero sounds like failure.**
> It is the wrong measure here, and we report it anyway rather than hide it. Our classes come
> from Jenks breaks and are *relative* to the 177 taluks assessed; CGWB categories are
> *absolute* thresholds on the stage of extraction, and most taluks are "safe". The two
> distributions cannot align by construction, and kappa is known to collapse under this kind of
> class imbalance. Binary agreement and rank correlation test what actually matters — whether
> we put the right taluks at the top.

**Q: Which taluks are highest risk?**
> Gudibanda, Malur and Srinivaspur — all in **Kolar** — then Hoskote in Bengaluru Rural.
> **8 of our top 25 are Kolar taluks**, and CGWB records 189% stage of extraction in Kolar, the
> worst in the state. That is a strong face-validity check: the model was never shown the
> extraction figures.

**Q: Why not just use the stage of extraction as an indicator? It would score better.**
> It would, and that is exactly why we did not. The extraction stage is what we validate
> against. Feeding it in as an input would make the validation circular and the 77.3% would
> mean nothing.

**Q: Recall is only 0.45 — you miss 28 stressed taluks. Is that a bug?**
> No, and we checked rather than tuning it away. The 28 we miss have **shallow (5.3 m mean) and
> flat** water tables despite 122% mean extraction; the 23 we catch are **deep (11.7 m) and
> declining**. That is real hard-rock hydrogeology: CGWB's monitored shallow wells refill
> seasonally while the borewells causing the damage draw from a deeper aquifer. **A water-level
> index cannot see stress occurring below the wells it monitors.** So our index complements
> CGWB's extraction accounting rather than replacing it — and closing that gap with deep-well
> or extraction data is a concrete Phase-2 objective.

---

## COMMON QUESTIONS

**Q: What problem are you solving?**
> Karnataka's groundwater is monitored but not forecast. CGWB publishes levels four times a
> year and an extraction category once a year, both describing the past. 62 of 227 taluks
> (27.3%) are already critical or over-exploited. We predict the next quarter's level per
> station and rank taluks by depletion risk so planners can act before wells fail.

**Q: How do the two modules connect?**
> Module 1 trains the predictor and writes a Mann-Kendall/Sen's-slope trend per station.
> `create_taluk_indicators()` aggregates that to taluks and joins current depth, variability,
> seasonal recovery and rainfall dependence. Module 2 weights those five by AHP, classifies
> with Jenks, and validates against CGWB. One command, `python -m src.main`, runs the whole
> chain in under 30 seconds.

**Q: What is the hardest bug you found?**
> A bug that produced no error. The "predicted decline rate" was the slope of a recursive
> four-quarter forecast, and recursive forecasting reverts to the training mean — 76% of
> station forecasts moved toward the overall average, and the correlation between the last
> observed depth and the "trend" was −0.665. So the indicator carrying half the weight was
> measuring how far the last reading sat from average, not depletion. The symptom was
> Chitradurga, an over-exploited district, ranking as the *safest*. We replaced it with the
> Mann-Kendall/Sen's slope trend that the design had specified all along.

**Q: What is left for Phase 2?**
> Kriging interpolation for a continuous risk surface, SHAP explanations, direct multi-horizon
> forecasting instead of recursive, the LULC indicator once land-cover rasters are integrated,
> deep-aquifer or extraction data to address the recall limitation above, and a
> spatio-temporal model (ConvLSTM or GCN-LSTM) for the spatial-relationship gap.

**Q: How do we know the numbers are real?**
> Every figure and table is regenerated by `python -m src.main` and
> `python notebooks/make_figures.py` from the CSVs in `data/raw/`. Nothing is typed by hand.
> The decks are built by `presentation/build_review_deck.py`, which reads the same JSON and
> CSV outputs, and the dashboard reads them too — so no artefact can drift from the code.
> `python -m pytest tests/` runs 13 checks over the cleaning, splitting, AHP and validation.

**Q: What would you do differently?**
> Validate the data before building on it. Weeks 4–5 reported metrics that came from
> `_synthetic_data()` with invented `LOC_xxx` locations while the real CGWB files sat unused in
> `data/raw/`, and nothing failed loudly enough to notice. Five silent bugs came out of that
> review; all are written up in `docs/debugging_log.md` section 2.
