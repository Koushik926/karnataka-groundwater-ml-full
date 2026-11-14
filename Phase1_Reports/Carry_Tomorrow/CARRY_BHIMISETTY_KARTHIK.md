# What BHIMISETTY KARTHIK carries tomorrow

**R23EJ168 | B.Tech CSIT — VII Sem, Sec C**  
**Saturday 14 November 2026, 1:30-3:30 PM** — be there by 1:20 PM. Mandatory, no rescheduling.  
Guide: Ms Indhuja Balakrishnan | Center lead: Dr. M. Shobha Rani

Two separate evaluations that afternoon — Internship and Major Project — separate coordinators, separate 50-mark sheets.

## 1. Print and bring — six items

- [ ] Project report — `Phase1_Report_BHIMISETTY_KARTHIK.pdf` (34 pages)
- [ ] Internship report — `Internship_Report_BHIMISETTY_KARTHIK.pdf` (13 pages)
- [ ] Guide sheet, Project — `Evaluation_Sheets/BHIMISETTY_KARTHIK/GuideEvaluation-Project-2026_BHIMISETTY_KARTHIK.docx`
- [ ] Examiner sheet, Project — `Evaluation_Sheets/BHIMISETTY_KARTHIK/ExaminerEvaluation-Project-2026_BHIMISETTY_KARTHIK.docx`
- [ ] Guide sheet, Internship — `Evaluation_Sheets/BHIMISETTY_KARTHIK/GuideEvaluation-Internship-2026_BHIMISETTY_KARTHIK.docx`
- [ ] Examiner sheet, Internship — `Evaluation_Sheets/BHIMISETTY_KARTHIK/ExaminerEvaluation-Internship-2026_BHIMISETTY_KARTHIK.docx`

Reports print from the PDF. The four evaluation sheets print from **Word / WPS / Pages**, not a converted PDF, so the REVA letterhead survives. Mark columns, Designation and Time stay blank — the guide and examiner fill them in the room.

## 2. On the laptop (and a pen drive)

- [ ] `presentation/decks/Phase1_Review_BHIMISETTY_KARTHIK.pptx` — project, 14 slides
- [ ] `presentation/decks/Phase1_Internship_BHIMISETTY_KARTHIK.pptx` — internship, 8 slides
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

**Module 1 - Groundwater Level Prediction (cleaning, features, trends)**

Files you own: `src/data_processor.py (cleaning, features, Mann-Kendall / Sen's slope)`

Open these before you walk in. The first question is almost always *which part is yours* — answer with a file path, not a topic.

## 5. Three questions to expect

**Q1. How did you clean 123,632 records down to 123,391?**

241 removed, and the two rules are separate: 76 readings out of physical range (level below 0 m or above 100 m) and 165 records missing a level, a date or a district. An earlier version of our deck attributed all 241 to the range rule - that was wrong and is corrected.

**Q2. You report 28 districts but the file has 33 labels. Why?**

Karnataka renamed districts during the record period and the exports mix spellings - Mysore and Mysuru, Bangalore and Bengaluru. canonical_district() resolves them. Before that fix the EDA drew the same district as two separate bars and the district join returned all-NaN.

**Q3. How do you detect a trend, and what did you find?**

Mann-Kendall with the tie correction, plus Sen's slope for magnitude, both implemented from first principles rather than called from a library so the tie handling is visible. Of 2,042 stations: 312 declining, 460 recovering, 1,270 no significant trend.

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
