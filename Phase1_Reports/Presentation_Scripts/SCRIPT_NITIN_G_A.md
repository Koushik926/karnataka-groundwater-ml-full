# Presentation script - NITIN G A

**R23EJ088 | Module 2 - Depletion Risk Mapping**  
Deck: `Phase1_Review_NITIN_G_A.pptx` (14 slides)  
About **10 min 20 s** of speaking.

Say it in your own words. These are the points to hit and the order to hit them in, not lines to memorise.

## Before you walk in

- [ ] Deck open in presentation mode; dashboard already running in a browser tab
- [ ] Both reports printed and signed, plus the four evaluation sheets
- [ ] The six numbers at the bottom, known without looking

## Slide 1 — Title  *(25 s)*

> Good afternoon. I am NITIN G A, SRN R23EJ088, and this is my Phase-1 review for the major project on spatio-temporal prediction and risk mapping of groundwater depletion in Karnataka using machine learning.

> It is a team of five under problem statement PS_160, guided by Ms Indhuja Balakrishnan. My module is Module 2, depletion risk mapping.

> The project aligns to UN Sustainable Development Goal 6, clean water and sanitation, which is the logo on the slide.

*Note: If the examiner starts asking immediately, go straight to slide 13 and come back.*

## Slide 2 — Problem Statement and Literature Gaps  *(50 s)*

> The problem is a timing problem, not a measurement problem. Karnataka is the second most groundwater-stressed state in India. The Central Ground Water Board's 2020 assessment puts 62 of 227 assessed taluks in the critical or over-exploited category - that is 27.3 percent.

> Recharge fell from 18.16 to 17.74 billion cubic metres while extraction rose from 10.63 to 11.22. But that assessment reaches an official years after the fact, by which time the cheap interventions are gone.

> Our users are district and taluk water authorities, Atal Bhujal Yojana planners, and CGWB's own regional staff.

> The success metric was fixed before we saw any result: beat a persistence baseline on a held-out future period, and put the taluks CGWB independently calls stressed at the top of our ranking.

*Note: Say 'fixed before we saw any result' deliberately - it answers a question before it is asked.*

## Slide 3 — Literature Survey  *(40 s)*

> We surveyed 20 papers from 2017 to 2026. Three matter most.

> Alkon and colleagues, 2024, use the same CGWB well data with a Random Forest and report R-squared between 0.4 and 0.6. That sets the realistic bar for this data.

> Supreetha, 2020, shows an LSTM works on Karnataka wells, but on a single district and for prediction only, with no risk map.

> Tao and colleagues, 2022, reviewed over a hundred machine-learning groundwater studies: tree ensembles are competitive with deep learning on tabular well data, and most studies never test against a naive baseline. We do.

*Note: The full 20-paper table is in the report at section 1.2 if they ask to see it.*

## Slide 4 — Requirements  *(30 s)*

> Ten requirements. The four that drive everything: predict the next quarter's level at each station; beat a persistence baseline on a held-out period; rank taluks by risk from measured indicators only; and validate that ranking against an independent official source.

> Eight of the ten are met. One is Phase-2, the continuous risk surface. Every requirement traces to a design element and a source file in section 2.5 of the report.

*Note: If asked which are unmet: R8, the kriging surface - say it plainly.*

## Slide 5 — System Design  *(40 s)*

> Two modules behind one shared data pipeline.

> The pipeline loads the CGWB quarterly observations, cleans them, canonicalises district and taluk names, attaches NASA POWER rainfall and builds a 15-feature table.

> Module 1 predicts the next quarter's depth per station and derives a Mann-Kendall and Sen's-slope trend for each one. Module 2 aggregates those trends to taluks, combines them with four more measured indicators under AHP weights, classifies with Jenks natural breaks and validates against CGWB.

> The modules talk through files in outputs and models, not shared memory. That is why the dashboard and every report read the same numbers and cannot disagree with the code.

*Note: The last sentence is the strongest thing on this slide. Do not rush it.*

## Slide 6 — Detailed Design: Flowchart, UML and DFD  *(30 s)*

> These are the design artefacts: the module flowcharts, the data flow diagrams at level 0 and level 1, the UML use case, class and sequence diagrams, and the entity-relationship model.

> The one to look at is the sequence diagram: main dot py calls the data processor, then run_module1, which writes the station forecast file, then builds the taluk indicators and calls run_module2. Section 4.4 of my report says exactly which values are passed between the two modules and which are recomputed from the same shared function.

*Note: If asked how a diagram maps to code, name the file - that is the expected answer.*

## Slide 7 — Module 1 - Groundwater Level Prediction  *(30 s)*

> Module 1, built by Koushik and Karthik, predicts the next quarter's level at each station. XGBoost, selected on validation RMSE against Random Forest, SVR and a persistence baseline, on a chronological split.

> Test RMSE 3.136 metres and R-squared 0.632, against a baseline of 3.838 and 0.449.

> What my module consumes from it is the Mann-Kendall and Sen's-slope trend per station.

*Note: Not your module. Keep it short and hand the detail to the numbers.*

## Slide 8 — Module 2 - Depletion Risk Mapping  *(75 s)*

> This is my module. Risk is assessed per taluk - 177 of them - because CGWB assesses taluks, so our ranking validates one to one against their table instead of against a district summary. It also gives about six times the resolution.

> Five measured indicators are combined. The weights come from AHP: a five by five pairwise comparison matrix on Saaty's 1 to 9 scale, and the weights are the principal eigenvector of that matrix.

> We use AHP because there is no ground-truth risk label to regress on. The judgement has to be made either way - AHP makes it explicit and checkable. The consistency ratio is 0.0542, below the 0.10 the method requires.

> Classification is Jenks natural breaks, which minimises within-class variance, so the boundaries fall at real gaps in the data instead of at round numbers.

> The decline indicator is the measured Sen's slope, not the model's own forecast. Recursive forecasts drift to the training mean - 76 percent did - and that inverted the ranking, putting over-exploited Chitradurga at lowest risk.

> Validation against CGWB 2020: 77.3 percent binary agreement, precision 0.66, recall 0.45, Spearman 0.276. Eight of our top 25 are Kolar taluks, and CGWB records 189 percent extraction in Kolar - the worst in the state. The model never saw that figure.

*Note: Your module - go slow here.*

## Slide 9 — Implementation Progress  *(35 s)*

> Three checkpoints. Week 8, about 30 percent: the shared pipeline on real CGWB data and Module 1 training. Week 10, about 55 percent: Module 2 with AHP, Jenks and CGWB validation, rainfall integrated, and seven silent defects fixed. Week 14, about 70 percent: the two modules integrated, the 29-test suite, and the dashboard.

> We state 70 percent, not higher, because four planned components have not been started - the kriging surface, SHAP, the land-use indicator and the spatio-temporal model.

*Note: 70 percent is the Phase-1 target. Claiming more invites a question you cannot win.*

## Slide 10 — Key Features and Demo  *(45 s)*

> The delivered interface is a Streamlit dashboard. It reads the models and outputs folders at run time, so what you see on screen is the most recent pipeline run - no number on it can have been typed in.

> It has three views: the taluk risk map, the per-station forecast, and the CGWB validation view.

> I can show it running now if you would like.

*Note: Have it already running in a browser tab. Do not launch it live in front of them.*

## Slide 11 — Testing  *(40 s)*

> 29 tests, 29 passing, nothing failing. Functional, boundary and negative cases for both modules, one end-to-end integration test, and 16 regression tests, each tied to a specific defect we fixed, so a fixed bug cannot come back unnoticed.

> Two worth naming. TC26 is a negative test that fails if CGWB's extraction figure ever becomes a model input - that is what keeps the validation from being circular. TC18 checks that the taluk Parasgad maps to Saundatti in Belagavi and never to Pavagada in Tumakuru, which is what an automated fuzzy matcher proposed.

> Six of the sixteen regression tests failed when first written, against the real API rather than the one we assumed, and were corrected before being counted as passing.

*Note: Admitting the six failures is a strength. It shows the tests were real.*

## Slide 12 — Debugging and Integration  *(50 s)*

> Every defect on this slide produced no error message. That is why they survived into our Week 4 and Week 5 reports.

> The worst one: the pipeline looked for a features dot csv that is never created, and silently fell back to synthetic data. Test R-squared was minus 0.098 while 123,391 real records sat unused in the same folder. Nothing crashed.

> We found it by checking the output against reality instead of checking that the code ran - a negative R-squared is worse than predicting the mean, so something had to be wrong. The fallback now raises, and a provenance guard blocks any report being built from synthetic metadata.

> On integration, the modules are coupled two ways: by order - main dot py runs Module 1 first and stops if it produced no trends - and by a shared function, station_trends in data_processor, which both rely on. The district path takes Module 1's trends as an argument; the taluk path recomputes the same slopes from the same cleaned data. Two bugs there - run_module2 was called with no arguments so it scored invented locations, and the station-to-taluk join silently matched almost nothing. 176 of 177 taluks match now.

*Note: This is the slide that earns marks. Tell it as a story, not a list.*

## Slide 13 — My Contribution and Phase-2 Plan  *(70 s)*

> My module is Module 2, depletion risk mapping, and the files I own are src/module2_risk.py (AHP weighting, risk index), src/config.py (AHP matrix).

> Built the AHP pairwise-comparison matrix on Saaty's 1-9 scale and the eigenvector routine that turns it into the five indicator weights.

> Implemented the consistency check and verified CR = 0.0542, below the 0.10 threshold AHP requires.

> Implemented compute_risk_index(): per-indicator normalisation, direction handling (recovery is protective, decline is risk) and the weighted sum.

> Removed the two indicators that were being filled with np.random.uniform() and documented LULC change as deferred to Phase 2.

> The Phase-2 table on the right has six items. The first is the honest one: deep-well or piezometer data, because our 0.45 recall is a data limitation, not a modelling one.

*Note: Answer 'which part is yours' with a file path, not a topic.*

## Slide 14 — Learnings and Thank You  *(60 s)*

> The hardest problem was discovering that two of my five indicators were np.random.uniform() placeholders left from the design stage, carrying 10% of the AHP weight between them. Nothing failed; the risk index still looked plausible. I replaced rainfall_dependence with a measured quantity - the correlation between each taluk's monsoon total and its actual post-monsoon recovery - and declared LULC change as deferred in DEFERRED_INDICATORS rather than dropping it quietly. I also added weight renormalisation so a missing indicator rescales the remaining weights instead of silently shrinking the index. What I would do differently: never commit a placeholder that returns a valid-looking number.

> Thank you. I am happy to take questions.

*Note: Finish on the sentence beginning 'What I would do differently'. It is the strongest note to end on.*

## If you are cut short

Keep slides **1, 2, 5, your own module slide (7 or 8), 12 and 13**. Those six carry the problem, the design, your work and the honesty. Drop 3, 4, 6, 9, 10, 11 first.

## Three questions you will be asked

**Q1. Why AHP and not just equal weights, or weights from a regression?**

Because there is no ground-truth risk label to regress on. AHP makes the judgement explicit and testable: five indicators compared pairwise on Saaty's 1-9 scale, weights taken as the principal eigenvector, and the consistency ratio reported. Ours is 0.0542, under the 0.10 threshold, so the judgements are not self-contradictory. Equal weights would be a judgement too, just an unstated one.

**Q2. How do you know the weights are not arbitrary?**

I ran the index with three normalisation schemes - min-max, percentile-clipped and rank - and the top-risk taluks stayed largely the same, so the ranking is not an artefact of one scaling choice. The CR is the second check, on the matrix itself.

**Q3. What went wrong in your module and how did you find it?**

Two of my five indicators were np.random.uniform() placeholders left over from the design stage, carrying 10% of the weight. I found it because the risk map did not change when I re-ran the pipeline on corrected data. Both are now real CGWB fields, and there is a regression test that fails if any indicator column is constant or random.

## Six numbers to know without looking

| | |
|---|---|
| Test RMSE / R2 | 3.136 m / 0.632, baseline 3.838 m / 0.449 |
| Taluks assessed | 177, of which 176 matched to CGWB |
| Agreement with CGWB | 77.3% binary; precision 0.66, recall 0.45 |
| AHP consistency ratio | 0.0542 (must be under 0.10) |
| Tests | 29 of 29 passing |
| Honest completion | 70% |

The two weak ones, said **before** you are asked: four-class agreement is **23.9%** because relative Jenks classes cannot align with absolute CGWB thresholds by construction; recall is **0.45** because the 28 taluks we miss are shallow and flat despite 122% extraction — deep-aquifer stress a shallow-well index cannot see.

## Never say these

RMSE 3.63, R² 0.40, 68% accuracy. Those came from the synthetic fallback we fixed. The real ones are **RMSE 3.136**, **R² 0.632**, **77.3%**.
