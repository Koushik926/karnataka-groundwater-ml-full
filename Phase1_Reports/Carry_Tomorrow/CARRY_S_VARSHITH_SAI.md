# What S VARSHITH SAI carries tomorrow

**R23EJ100 | B.Tech CSIT — VII Sem, Sec B**  
**Saturday 14 November 2026, 1:30-3:30 PM** — be there by 1:20 PM. Mandatory, no rescheduling.  
Guide: Ms Indhuja Balakrishnan | Center lead: Dr. M. Shobha Rani

Two separate evaluations that afternoon — Internship and Major Project — separate coordinators, separate 50-mark sheets.

## 1. Print and bring — six items

- [ ] Project report — `Phase1_Report_S_VARSHITH_SAI.pdf` (34 pages)
- [ ] Internship report — `Internship_Report_S_VARSHITH_SAI.pdf` (13 pages)
- [ ] Guide sheet, Project — `Evaluation_Sheets/S_VARSHITH_SAI/GuideEvaluation-Project-2026_S_VARSHITH_SAI.docx`
- [ ] Examiner sheet, Project — `Evaluation_Sheets/S_VARSHITH_SAI/ExaminerEvaluation-Project-2026_S_VARSHITH_SAI.docx`
- [ ] Guide sheet, Internship — `Evaluation_Sheets/S_VARSHITH_SAI/GuideEvaluation-Internship-2026_S_VARSHITH_SAI.docx`
- [ ] Examiner sheet, Internship — `Evaluation_Sheets/S_VARSHITH_SAI/ExaminerEvaluation-Internship-2026_S_VARSHITH_SAI.docx`

Reports print from the PDF. The four evaluation sheets print from **Word / WPS / Pages**, not a converted PDF, so the REVA letterhead survives. Mark columns, Designation and Time stay blank — the guide and examiner fill them in the room.

## 2. On the laptop (and a pen drive)

- [ ] `presentation/decks/Phase1_Review_S_VARSHITH_SAI.pptx` — project, 14 slides
- [ ] `presentation/decks/Phase1_Internship_S_VARSHITH_SAI.pptx` — internship, 8 slides
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

**Module 2 - Depletion Risk Mapping (Jenks classification and validation)**

Files you own: `src/module2_risk.py (Jenks classification, CGWB validation)`

Open these before you walk in. The first question is almost always *which part is yours* — answer with a file path, not a topic.

## 5. Three questions to expect

**Q1. Four-class agreement with CGWB is 23.9% and kappa 0.001. Is the model wrong?**

No - the two scales are not comparable by construction. Jenks gives four classes relative to Karnataka's own distribution; CGWB's categories are absolute national thresholds on extraction percentage. A relative quartile can never align with an absolute cut-off. The honest comparison is binary high-risk vs not, which is 77.3%. I report both rather than the flattering one.

**Q2. Why Jenks instead of quartiles or fixed cut-offs?**

Jenks minimises within-class variance, so the breaks fall at real gaps in the data instead of at arbitrary round numbers. With fixed cut-offs the class sizes depend on the scaling choice rather than the groundwater.

**Q3. Recall is only 0.45. What are you missing?**

28 taluks that CGWB calls stressed and we do not. They are shallow and flat in the well record despite extraction over 100% - deep-aquifer stress that a shallow-well index cannot observe. That is a stated limitation of the data, not a tuning problem, and tuning the thresholds to hide it would be dishonest.

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
