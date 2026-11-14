# What R KOUSHIK carries tomorrow

**R23EJ096 | B.Tech CSIT — VII Sem, Sec B**  
**Saturday 14 November 2026, 1:30-3:30 PM** — be there by 1:20 PM. Mandatory, no rescheduling.  
Guide: Ms Indhuja Balakrishnan | Center lead: Dr. M. Shobha Rani

Two separate evaluations that afternoon — Internship and Major Project — separate coordinators, separate 50-mark sheets.

## 1. Print and bring — six items

- [ ] Project report — `Phase1_Report_R_KOUSHIK.pdf` (34 pages)
- [ ] Internship report — `Internship_Report_R_KOUSHIK.pdf` (13 pages)
- [ ] Guide sheet, Project — `Evaluation_Sheets/R_KOUSHIK/GuideEvaluation-Project-2026_R_KOUSHIK.docx`
- [ ] Examiner sheet, Project — `Evaluation_Sheets/R_KOUSHIK/ExaminerEvaluation-Project-2026_R_KOUSHIK.docx`
- [ ] Guide sheet, Internship — `Evaluation_Sheets/R_KOUSHIK/GuideEvaluation-Internship-2026_R_KOUSHIK.docx`
- [ ] Examiner sheet, Internship — `Evaluation_Sheets/R_KOUSHIK/ExaminerEvaluation-Internship-2026_R_KOUSHIK.docx`

Reports print from the PDF. The four evaluation sheets print from **Word / WPS / Pages**, not a converted PDF, so the REVA letterhead survives. Mark columns, Designation and Time stay blank — the guide and examiner fill them in the room.

## 2. On the laptop (and a pen drive)

- [ ] `presentation/decks/Phase1_Review_R_KOUSHIK.pptx` — project, 14 slides
- [ ] `presentation/decks/Phase1_Internship_R_KOUSHIK.pptx` — internship, 8 slides
- [ ] Both report PDFs, in case a printed copy goes missing
- [ ] Laptop charged, charger packed, dashboard launched once today

Both title slides carry the **SDG 6** logo, as the circular requires.

## 3. Before you leave home

- [ ] Sign and date the declaration on **both** reports — they are separate
- [ ] Internship 5.3 Reflection — read the draft, correct anything untrue of you, put it in your own words
- [ ] Internship 2.1 — check your own ratings against your Week-1 self-check
- [ ] Internship 5.1 — the mock-interview score is the one blank left; fill it or write "not held"
- [ ] Check your name and SRN on both title pages

## 4. Your module

**Module 1 - Groundwater Level Prediction (model training and rainfall)**

Files you own: `src/pipeline.py (training and selection), src/rainfall.py (NASA POWER)`

Open these before you walk in. The first question is almost always *which part is yours* — answer with a file path, not a topic.

## 5. Three questions to expect

**Q1. Why is the split chronological rather than random?**

The features include lagged groundwater levels, so a random split puts a station's future on both sides of the split and the model scores well by memorising. Chronological split means every test quarter is strictly after every training quarter. The scores dropped when I fixed this, which is the point.

**Q2. Why XGBoost over Random Forest, SVR or the LSTM?**

Selected on validation RMSE, not preference. Test RMSE 3.136 m and R2 0.632 against a persistence baseline of 3.838 m / 0.449 - so the model beats 'next quarter equals this quarter' by 18% RMSE, which is the comparison that matters. The LSTM is a benchmark, not the deliverable.

**Q3. Does rainfall actually help, or did you just add it?**

I tested it. Adding the five NASA POWER rainfall features and keeping everything else fixed is the only difference between the two runs, so the change in validation RMSE is attributable to rainfall alone. Median imputation is fitted on the training split only, so no test statistic leaks backwards.

## 6. Numbers to know cold

| | |
|---|---|
| Test RMSE / R2 | 3.136 m / 0.632, against a persistence baseline of 3.838 m / 0.449 |
| Risk units assessed | 177 taluks, 176 matched to CGWB |
| Agreement with CGWB | 77.3% binary (precision 0.66, recall 0.45); Spearman 0.276 |
| AHP consistency ratio | 0.0542 (must be under 0.10) |
| Honest completion | 70% - the Phase-1 target |
| Tests | 29 of 29 passing |

The two weak numbers, with the answer ready rather than avoided: four-class agreement is **23.9%** (relative Jenks classes against absolute CGWB thresholds — they cannot align by construction) and recall is **0.45** (the 28 taluks we miss are shallow and flat despite extraction over 100% — deep-aquifer stress a shallow-well index cannot see). Saying this first is stronger than being asked.

## 7. If they ask to see it running

```
cd Week4_Task4_Core_Implementation
python3 -m venv .venv                              # ONCE, before you leave
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run dashboard.py     # the demo
.venv/bin/python -m pytest tests/                  # 29 passed, under 10 s
.venv/bin/python -m src.main                       # whole pipeline, ~30 s
```

Bare `python3` is missing xgboost and pytest on this machine, so the venv is not optional. Full fallbacks in `DEMO_RUNBOOK.md`.

Run all three tonight. A command that fails in the room costs more than a missing slide.
