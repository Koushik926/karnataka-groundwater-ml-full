# Phase-1 Review — what each of the five of us carries

> **Each person now has their own sheet:** `Carry_Tomorrow/CARRY_<NAME>.pdf`
> (print or read on the phone — the `.md` is the same thing). It names your own
> six files, your module, and the three questions you personally will be asked.
> This page is the shared version; the personal one is the one to carry.

**Saturday 14 November 2026, 1:30–3:30 PM. Be there by 1:20. No rescheduling.**

The review is two separate evaluations with two separate coordinators and two
separate 50-mark sheets: **Internship** and **Major Project**. Every student
appears for the Major Project. Students not doing an outside internship appear
for both.

## Per student — six items

| # | Item | File | Print? |
|---|------|------|--------|
| 1 | Guide evaluation sheet — Project | `Evaluation_Sheets/<NAME>/GuideEvaluation-Project-2026_<NAME>.docx` | Yes, 1 copy |
| 2 | Examiner evaluation sheet — Project | `Evaluation_Sheets/<NAME>/ExaminerEvaluation-Project-2026_<NAME>.docx` | Yes, 1 copy |
| 3 | Guide evaluation sheet — Internship | `Evaluation_Sheets/<NAME>/GuideEvaluation-Internship-2026_<NAME>.docx` | Yes, 1 copy |
| 4 | Examiner evaluation sheet — Internship | `Evaluation_Sheets/<NAME>/ExaminerEvaluation-Internship-2026_<NAME>.docx` | Yes, 1 copy |
| 5 | Project report, hard copy | `Phase1_Report_<NAME>.pdf` (34 pages) | Yes |
| 6 | Internship report, hard copy | `Internship_Report_<NAME>.pdf` (13 pages) | Yes |

Plus, on the laptop, **two decks**:

- Project: `Week4_Task4_Core_Implementation/presentation/decks/Phase1_Review_<NAME>.pptx` (14 slides)
- Internship: `Week4_Task4_Core_Implementation/presentation/decks/Phase1_Internship_<NAME>.pptx` (8 slides)

Both title slides carry the **SDG 6** logo, as the circular requires.

## Print notes

- The **reports** print from the `.pdf` — already checked: no browser headers,
  no blank pages, figures intact.
- The **evaluation sheets** are the university's own `.docx` with our details
  typed in, so print them **from Word / WPS / Pages**, not from a converted PDF.
  That keeps the official layout and the REVA letterhead exactly as issued.
- Before printing, fill in the items in `FILL_IN_BY_HAND.txt` — about ten
  minutes each.

## Have the demo ready

If the examiner asks to see it running:

```
cd Week4_Task4_Core_Implementation
streamlit run dashboard.py        # map, station forecasts, CGWB validation
python -m pytest tests/           # 29 passed
python -m src.main                # whole pipeline, ~30 seconds
```

## The five numbers to know cold

| | |
|---|---|
| Test RMSE / R² | **3.136 m / 0.632** against a persistence baseline of 3.838 m / 0.449 |
| Risk units assessed | **177 taluks**, 176 matched to CGWB |
| Agreement with CGWB | **77.3%** binary (precision 0.66, recall 0.45); Spearman 0.276 |
| AHP consistency ratio | **0.0542** (must be < 0.10) |
| Honest completion | **70%** — the Phase-1 target |

And the two weak numbers, with the answer ready: four-class agreement is 23.9%
(relative Jenks classes vs absolute CGWB thresholds — cannot align by
construction), and recall is 0.45 (the 28 taluks we miss are shallow and flat
despite 122% extraction: deep-aquifer stress a shallow-well index cannot see).
