# What NITIN G A carries tomorrow

**R23EJ088 | B.Tech CSIT — VII Sem, Sec B**  
**Saturday 14 November 2026, 1:30-3:30 PM** — be there by 1:20 PM. Mandatory, no rescheduling.  
Guide: Ms Indhuja Balakrishnan | Center lead: Dr. M. Shobha Rani

Two separate evaluations that afternoon — Internship and Major Project — separate coordinators, separate 50-mark sheets.

## 1. Print and bring — six items

- [ ] Project report — `Phase1_Report_NITIN_G_A.pdf` (34 pages)
- [ ] Internship report — `Internship_Report_NITIN_G_A.pdf` (13 pages)
- [ ] Guide sheet, Project — `Evaluation_Sheets/NITIN_G_A/GuideEvaluation-Project-2026_NITIN_G_A.docx`
- [ ] Examiner sheet, Project — `Evaluation_Sheets/NITIN_G_A/ExaminerEvaluation-Project-2026_NITIN_G_A.docx`
- [ ] Guide sheet, Internship — `Evaluation_Sheets/NITIN_G_A/GuideEvaluation-Internship-2026_NITIN_G_A.docx`
- [ ] Examiner sheet, Internship — `Evaluation_Sheets/NITIN_G_A/ExaminerEvaluation-Internship-2026_NITIN_G_A.docx`

Reports print from the PDF. The four evaluation sheets print from **Word / WPS / Pages**, not a converted PDF, so the REVA letterhead survives. Mark columns, Designation and Time stay blank — the guide and examiner fill them in the room.

## 2. On the laptop (and a pen drive)

- [ ] `presentation/decks/Phase1_Review_NITIN_G_A.pptx` — project, 14 slides
- [ ] `presentation/decks/Phase1_Internship_NITIN_G_A.pptx` — internship, 8 slides
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

**Module 2 - Depletion Risk Mapping (AHP weighting and the risk index)**

Files you own: `src/module2_risk.py (AHP weighting, risk index), src/config.py (AHP matrix)`

Open these before you walk in. The first question is almost always *which part is yours* — answer with a file path, not a topic.

## 5. Three questions to expect

**Q1. Why AHP and not just equal weights, or weights from a regression?**

Because there is no ground-truth risk label to regress on. AHP makes the judgement explicit and testable: five indicators compared pairwise on Saaty's 1-9 scale, weights taken as the principal eigenvector, and the consistency ratio reported. Ours is 0.0542, under the 0.10 threshold, so the judgements are not self-contradictory. Equal weights would be a judgement too, just an unstated one.

**Q2. How do you know the weights are not arbitrary?**

I ran the index with three normalisation schemes - min-max, percentile-clipped and rank - and the top-risk taluks stayed largely the same, so the ranking is not an artefact of one scaling choice. The CR is the second check, on the matrix itself.

**Q3. What went wrong in your module and how did you find it?**

Two of my five indicators were np.random.uniform() placeholders left over from the design stage, carrying 10% of the weight. I found it because the risk map did not change when I re-ran the pipeline on corrected data. Both are now real CGWB fields, and there is a regression test that fails if any indicator column is constant or random.

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
