# What G M CHANDRASHEKAR carries tomorrow

**R23EQ029 | B.Tech ISE — VII Sem, Sec A**  
**Saturday 14 November 2026, 1:30-3:30 PM** — be there by 1:20 PM. Mandatory, no rescheduling.  
Guide: Ms Indhuja Balakrishnan | Center lead: Dr. M. Shobha Rani

Two separate evaluations that afternoon — Internship and Major Project — separate coordinators, separate 50-mark sheets.

## 1. Print and bring — six items

- [ ] Project report — `Phase1_Report_G_M_CHANDRASHEKAR.pdf` (34 pages)
- [ ] Internship report — `Internship_Report_G_M_CHANDRASHEKAR.pdf` (13 pages)
- [ ] Guide sheet, Project — `Evaluation_Sheets/G_M_CHANDRASHEKAR/GuideEvaluation-Project-2026_G_M_CHANDRASHEKAR.docx`
- [ ] Examiner sheet, Project — `Evaluation_Sheets/G_M_CHANDRASHEKAR/ExaminerEvaluation-Project-2026_G_M_CHANDRASHEKAR.docx`
- [ ] Guide sheet, Internship — `Evaluation_Sheets/G_M_CHANDRASHEKAR/GuideEvaluation-Internship-2026_G_M_CHANDRASHEKAR.docx`
- [ ] Examiner sheet, Internship — `Evaluation_Sheets/G_M_CHANDRASHEKAR/ExaminerEvaluation-Internship-2026_G_M_CHANDRASHEKAR.docx`

Reports print from the PDF. The four evaluation sheets print from **Word / WPS / Pages**, not a converted PDF, so the REVA letterhead survives. Mark columns, Designation and Time stay blank — the guide and examiner fill them in the room.

## 2. On the laptop (and a pen drive)

- [ ] `presentation/decks/Phase1_Review_G_M_CHANDRASHEKAR.pptx` — project, 14 slides
- [ ] `presentation/decks/Phase1_Internship_G_M_CHANDRASHEKAR.pptx` — internship, 8 slides
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

**Module 2 - Depletion Risk Mapping (dashboard and figures)**

Files you own: `dashboard.py, notebooks/make_figures.py`

Open these before you walk in. The first question is almost always *which part is yours* — answer with a file path, not a topic.

## 5. Three questions to expect

**Q1. Can the dashboard disagree with the report?**

No, and that is deliberate. It reads models/ and outputs/ at run time, so a pipeline re-run changes both together. The previous version had metrics typed into the source and drifted from the code after every run - that is the defect this design removes.

**Q2. Why do your charts carry data labels and a colour legend?**

Because our guide asked for exactly that after the October review, and because colour alone is not readable for everyone. Every chart states what each colour means and prints the value on the point or bar.

**Q3. Show us a number on the dashboard and where it comes from.**

Any of them - each traces to a file in outputs/. There is a provenance guard, src/provenance.py, that refuses to build a document or a figure from synthetic metadata, so a number on screen cannot have come from generated data.

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
