"""
build_carry_sheets.py - one "what I carry tomorrow" sheet per student.

Each sheet is personal: it names that student's own six printed items by exact
filename, their module, the questions they are most likely to be asked about
the code they wrote, and the answers in their own evidence. Written as .md for
the phone and .docx -> .pdf for printing.

    python scripts/build_carry_sheets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import student_personal as P  # noqa: E402

OUT = ROOT.parent / "Phase1_Reports" / "Carry_Tomorrow"

REVIEW = "Saturday 14 November 2026, 1:30-3:30 PM"
GUIDE = "Ms Indhuja Balakrishnan"
LEAD = "Dr. M. Shobha Rani"

STUDENTS = [
    ("NITIN G A", "R23EJ088"),
    ("R KOUSHIK", "R23EJ096"),
    ("S VARSHITH SAI", "R23EJ100"),
    ("BHIMISETTY KARTHIK", "R23EJ168"),
    ("G M CHANDRASHEKAR", "R23EQ029"),
]

MODULE = {
    "NITIN G A": "Module 2 - Depletion Risk Mapping (AHP weighting and the risk index)",
    "R KOUSHIK": "Module 1 - Groundwater Level Prediction (model training and rainfall)",
    "S VARSHITH SAI": "Module 2 - Depletion Risk Mapping (Jenks classification and validation)",
    "BHIMISETTY KARTHIK": "Module 1 - Groundwater Level Prediction (cleaning, features, trends)",
    "G M CHANDRASHEKAR": "Module 2 - Depletion Risk Mapping (dashboard and figures)",
}

FILES = {
    "NITIN G A": "src/module2_risk.py (AHP weighting, risk index), src/config.py (AHP matrix)",
    "R KOUSHIK": "src/pipeline.py (training and selection), src/rainfall.py (NASA POWER)",
    "S VARSHITH SAI": "src/module2_risk.py (Jenks classification, CGWB validation)",
    "BHIMISETTY KARTHIK": "src/data_processor.py (cleaning, features, Mann-Kendall / Sen's slope)",
    "G M CHANDRASHEKAR": "dashboard.py, notebooks/make_figures.py",
}

# The three questions each person is most likely to be asked about their own
# code, with the answer in the evidence they actually produced.
QA = {
 "NITIN G A": [
   ("Why AHP and not just equal weights, or weights from a regression?",
    "Because there is no ground-truth risk label to regress on. AHP makes the judgement "
    "explicit and testable: five indicators compared pairwise on Saaty's 1-9 scale, weights "
    "taken as the principal eigenvector, and the consistency ratio reported. Ours is 0.0542, "
    "under the 0.10 threshold, so the judgements are not self-contradictory. Equal weights "
    "would be a judgement too, just an unstated one."),
   ("How do you know the weights are not arbitrary?",
    "I ran the index with three normalisation schemes - min-max, percentile-clipped and rank - "
    "and the top-risk taluks stayed largely the same, so the ranking is not an artefact of one "
    "scaling choice. The CR is the second check, on the matrix itself."),
   ("What went wrong in your module and how did you find it?",
    "Two of my five indicators were np.random.uniform() placeholders left over from the design "
    "stage, carrying 10% of the weight. I found it because the risk map did not change when I "
    "re-ran the pipeline on corrected data. Both are now real CGWB fields, and there is a "
    "regression test that fails if any indicator column is constant or random."),
 ],
 "R KOUSHIK": [
   ("Why is the split chronological rather than random?",
    "The features include lagged groundwater levels, so a random split puts a station's future "
    "on both sides of the split and the model scores well by memorising. Chronological split "
    "means every test quarter is strictly after every training quarter. The scores dropped when "
    "I fixed this, which is the point."),
   ("Why XGBoost over Random Forest, SVR or the LSTM?",
    "Selected on validation RMSE, not preference. Test RMSE 3.136 m and R2 0.632 against a "
    "persistence baseline of 3.838 m / 0.449 - so the model beats 'next quarter equals this "
    "quarter' by 18% RMSE, which is the comparison that matters. The LSTM is a benchmark, not "
    "the deliverable."),
   ("Does rainfall actually help, or did you just add it?",
    "I tested it. Adding the five NASA POWER rainfall features and keeping everything else "
    "fixed is the only difference between the two runs, so the change in validation RMSE is "
    "attributable to rainfall alone. Median imputation is fitted on the training split only, "
    "so no test statistic leaks backwards."),
 ],
 "S VARSHITH SAI": [
   ("Four-class agreement with CGWB is 23.9% and kappa 0.001. Is the model wrong?",
    "No - the two scales are not comparable by construction. Jenks gives four classes relative "
    "to Karnataka's own distribution; CGWB's categories are absolute national thresholds on "
    "extraction percentage. A relative quartile can never align with an absolute cut-off. The "
    "honest comparison is binary high-risk vs not, which is 77.3%. I report both rather than "
    "the flattering one."),
   ("Why Jenks instead of quartiles or fixed cut-offs?",
    "Jenks minimises within-class variance, so the breaks fall at real gaps in the data instead "
    "of at arbitrary round numbers. With fixed cut-offs the class sizes depend on the scaling "
    "choice rather than the groundwater."),
   ("Recall is only 0.45. What are you missing?",
    "28 taluks that CGWB calls stressed and we do not. They are shallow and flat in the well "
    "record despite extraction over 100% - deep-aquifer stress that a shallow-well index cannot "
    "observe. That is a stated limitation of the data, not a tuning problem, and tuning the "
    "thresholds to hide it would be dishonest."),
 ],
 "BHIMISETTY KARTHIK": [
   ("How did you clean 123,632 records down to 123,391?",
    "241 removed, and the two rules are separate: 76 readings out of physical range (level "
    "below 0 m or above 100 m) and 165 records missing a level, a date or a district. An "
    "earlier version of our deck attributed all 241 to the range rule - that was wrong and is "
    "corrected."),
   ("You report 28 districts but the file has 33 labels. Why?",
    "Karnataka renamed districts during the record period and the exports mix spellings - "
    "Mysore and Mysuru, Bangalore and Bengaluru. canonical_district() resolves them. Before "
    "that fix the EDA drew the same district as two separate bars and the district join "
    "returned all-NaN."),
   ("How do you detect a trend, and what did you find?",
    "Mann-Kendall with the tie correction, plus Sen's slope for magnitude, both implemented "
    "from first principles rather than called from a library so the tie handling is visible. "
    "Of 2,042 stations: 312 declining, 460 recovering, 1,270 no significant trend."),
 ],
 "G M CHANDRASHEKAR": [
   ("Can the dashboard disagree with the report?",
    "No, and that is deliberate. It reads models/ and outputs/ at run time, so a pipeline "
    "re-run changes both together. The previous version had metrics typed into the source and "
    "drifted from the code after every run - that is the defect this design removes."),
   ("Why do your charts carry data labels and a colour legend?",
    "Because our guide asked for exactly that after the October review, and because colour "
    "alone is not readable for everyone. Every chart states what each colour means and prints "
    "the value on the point or bar."),
   ("Show us a number on the dashboard and where it comes from.",
    "Any of them - each traces to a file in outputs/. There is a provenance guard, "
    "src/provenance.py, that refuses to build a document or a figure from synthetic metadata, "
    "so a number on screen cannot have come from generated data."),
 ],
}

NUMBERS = [
    ("Test RMSE / R2", "3.136 m / 0.632, against a persistence baseline of 3.838 m / 0.449"),
    ("Risk units assessed", "177 taluks, 176 matched to CGWB"),
    ("Agreement with CGWB", "77.3% binary (precision 0.66, recall 0.45); Spearman 0.276"),
    ("AHP consistency ratio", "0.0542 (must be under 0.10)"),
    ("Honest completion", "70% - the Phase-1 target"),
    ("Tests", "29 of 29 passing"),
]


# ------------------------------------------------------------------ docx bits
def h(doc, text, size=13):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)


def para(doc, text, size=10.5, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(size); r.bold = bold; r.italic = italic
    p.paragraph_format.space_after = Pt(3)
    return p


def tick(doc, text, size=10.5):
    p = doc.add_paragraph()
    r = p.add_run("[  ]  " + text); r.font.size = Pt(size)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.4)


def build_docx(name: str, srn: str) -> Path:
    safe = name.replace(" ", "_")
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(1.6); s.left_margin = s.right_margin = Cm(1.8)

    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run(f"WHAT {name} CARRIES TOMORROW"); r.bold = True; r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run(f"{srn}  |  {P.program_short(name)}  |  {REVIEW}\n"
                    f"Phase-1 Review, RIO  |  Guide: {GUIDE}  |  Center lead: {LEAD}")
    r.font.size = Pt(10.5)
    para(doc, "Be there by 1:20 PM. Attendance is mandatory and there is no rescheduling. "
              "Two separate evaluations run that afternoon - Internship and Major Project - "
              "with separate coordinators and separate 50-mark sheets.", italic=True)

    h(doc, "1. Print and bring - six items, all yours alone")
    for item in [
        f"Project report, hard copy - Phase1_Report_{safe}.pdf  (34 pages)",
        f"Internship report, hard copy - Internship_Report_{safe}.pdf  (13 pages)",
        f"Guide evaluation sheet, Project - Evaluation_Sheets/{safe}/GuideEvaluation-Project-2026_{safe}.docx",
        f"Examiner evaluation sheet, Project - Evaluation_Sheets/{safe}/ExaminerEvaluation-Project-2026_{safe}.docx",
        f"Guide evaluation sheet, Internship - Evaluation_Sheets/{safe}/GuideEvaluation-Internship-2026_{safe}.docx",
        f"Examiner evaluation sheet, Internship - Evaluation_Sheets/{safe}/ExaminerEvaluation-Internship-2026_{safe}.docx",
    ]:
        tick(doc, item)
    para(doc, "Print the two reports from the PDF. Print the four evaluation sheets from "
              "Word, WPS or Pages - not from a converted PDF - so the REVA letterhead and the "
              "official layout stay exactly as issued. The mark columns, Designation and Time "
              "are blank on purpose: the guide and the examiner fill those in the room.",
         italic=True)

    h(doc, "2. On the laptop, and on a pen drive as backup")
    tick(doc, f"Project deck - presentation/decks/Phase1_Review_{safe}.pptx  (14 slides)")
    tick(doc, f"Internship deck - presentation/decks/Phase1_Internship_{safe}.pptx  (8 slides)")
    tick(doc, "Both reports as PDF, in case a printed copy goes missing")
    tick(doc, "Laptop charged, charger packed, dashboard already launched once today")
    para(doc, "Both title slides carry the SDG 6 logo, which the circular requires.",
         italic=True)

    h(doc, "3. Before you leave home")
    tick(doc, "Sign and date the declaration page on BOTH reports - they are separate declarations")
    tick(doc, "Internship report 5.3, Reflection - read the draft, correct anything untrue of "
              "you, put it in your own words before signing")
    tick(doc, "Internship report 2.1 - check your own baseline and 'now' ratings against your "
              "Week-1 self-check and change any number you disagree with")
    tick(doc, "Internship report 5.1 - the mock-interview score cell is the one blank left; "
              "fill it from the signed sheet, or write 'not held'")
    tick(doc, "Check your name and SRN on the title page of both reports")

    h(doc, "4. Your module - what you will be asked first")
    para(doc, MODULE[name], bold=True)
    para(doc, "Files you own: " + FILES[name])
    para(doc, "Open these files before you walk in. The first question is almost always "
              "'which part is yours', and the answer should be a file path, not a topic.",
         italic=True)

    h(doc, "5. Three questions you should expect, and your answers")
    for i, (q, a) in enumerate(QA[name], 1):
        para(doc, f"Q{i}.  {q}", bold=True)
        para(doc, a)

    h(doc, "6. Numbers to know cold - the whole team quotes these")
    for k, v in NUMBERS:
        para(doc, f"{k}:  {v}")
    para(doc, "And the two weak numbers, with the answer ready rather than avoided: "
              "four-class agreement is 23.9% (relative Jenks classes against absolute CGWB "
              "thresholds - they cannot align by construction), and recall is 0.45 (the 28 "
              "taluks we miss are shallow and flat in the well record despite extraction over "
              "100% - deep-aquifer stress a shallow-well index cannot see). Saying this first "
              "is stronger than being asked.", italic=True)

    h(doc, "7. If they ask to see it running")
    for cmd, what in [
        ("cd Week4_Task4_Core_Implementation", ""),
        ("python3 -m venv .venv", "ONCE, before you leave home"),
        (".venv/bin/python -m pip install -r requirements.txt", "takes under a minute"),
        (".venv/bin/python -m streamlit run dashboard.py", "map, forecasts, validation"),
        (".venv/bin/python -m pytest tests/", "29 passed, under 10 s"),
        (".venv/bin/python -m src.main", "the whole pipeline, about 30 seconds"),
    ]:
        p = doc.add_paragraph()
        r = p.add_run(cmd); r.font.name = "Consolas"; r.font.size = Pt(10)
        if what:
            r2 = p.add_run(f"     # {what}"); r2.font.size = Pt(9.5); r2.italic = True
        p.paragraph_format.space_after = Pt(1)
    para(doc, "Set the venv up and run all three BEFORE you leave. A command that fails in "
              "the room costs more than a slide that is missing. If it breaks anyway, "
              "DEMO_RUNBOOK.md has the fallback for each error.", italic=True)

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"CARRY_{safe}.docx"
    doc.save(str(out))
    return out


# ------------------------------------------------------------------ markdown
def build_md(name: str, srn: str) -> Path:
    safe = name.replace(" ", "_")
    L = [f"# What {name} carries tomorrow", "",
         f"**{srn} | {P.program_short(name)}**  ",
         f"**{REVIEW}** — be there by 1:20 PM. Mandatory, no rescheduling.  ",
         f"Guide: {GUIDE} | Center lead: {LEAD}", "",
         "Two separate evaluations that afternoon — Internship and Major Project — "
         "separate coordinators, separate 50-mark sheets.", "",
         "## 1. Print and bring — six items", ""]
    L += [f"- [ ] Project report — `Phase1_Report_{safe}.pdf` (34 pages)",
          f"- [ ] Internship report — `Internship_Report_{safe}.pdf` (13 pages)",
          f"- [ ] Guide sheet, Project — `Evaluation_Sheets/{safe}/GuideEvaluation-Project-2026_{safe}.docx`",
          f"- [ ] Examiner sheet, Project — `Evaluation_Sheets/{safe}/ExaminerEvaluation-Project-2026_{safe}.docx`",
          f"- [ ] Guide sheet, Internship — `Evaluation_Sheets/{safe}/GuideEvaluation-Internship-2026_{safe}.docx`",
          f"- [ ] Examiner sheet, Internship — `Evaluation_Sheets/{safe}/ExaminerEvaluation-Internship-2026_{safe}.docx`",
          "",
          "Reports print from the PDF. The four evaluation sheets print from **Word / WPS / "
          "Pages**, not a converted PDF, so the REVA letterhead survives. Mark columns, "
          "Designation and Time stay blank — the guide and examiner fill them in the room.",
          "", "## 2. On the laptop (and a pen drive)", "",
          f"- [ ] `presentation/decks/Phase1_Review_{safe}.pptx` — project, 14 slides",
          f"- [ ] `presentation/decks/Phase1_Internship_{safe}.pptx` — internship, 8 slides",
          "- [ ] Both report PDFs, in case a printed copy goes missing",
          "- [ ] Laptop charged, charger packed, dashboard launched once today", "",
          "Both title slides carry the **SDG 6** logo, as the circular requires.", "",
          "## 3. Before you leave home", "",
          "- [ ] Sign and date the declaration on **both** reports — they are separate",
          "- [ ] Internship 5.3 Reflection — read the draft, correct anything untrue of you, "
          "put it in your own words",
          "- [ ] Internship 2.1 — check your own ratings against your Week-1 self-check",
          "- [ ] Internship 5.1 — the mock-interview score is the one blank left; fill it or "
          "write \"not held\"",
          "- [ ] Check your name and SRN on both title pages", "",
          "## 4. Your module", "",
          f"**{MODULE[name]}**", "",
          f"Files you own: `{FILES[name]}`", "",
          "Open these before you walk in. The first question is almost always *which part is "
          "yours* — answer with a file path, not a topic.", "",
          "## 5. Three questions to expect", ""]
    for i, (q, a) in enumerate(QA[name], 1):
        L += [f"**Q{i}. {q}**", "", a, ""]
    L += ["## 6. Numbers to know cold", "", "| | |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in NUMBERS]
    L += ["", "The two weak numbers, with the answer ready rather than avoided: four-class "
          "agreement is **23.9%** (relative Jenks classes against absolute CGWB thresholds — "
          "they cannot align by construction) and recall is **0.45** (the 28 taluks we miss "
          "are shallow and flat despite extraction over 100% — deep-aquifer stress a "
          "shallow-well index cannot see). Saying this first is stronger than being asked.",
          "", "## 7. If they ask to see it running", "", "```",
          "cd Week4_Task4_Core_Implementation",
          "python3 -m venv .venv                              # ONCE, before you leave",
          ".venv/bin/python -m pip install -r requirements.txt",
          ".venv/bin/python -m streamlit run dashboard.py     # the demo",
          ".venv/bin/python -m pytest tests/                  # 29 passed, under 10 s",
          ".venv/bin/python -m src.main                       # whole pipeline, ~30 s",
          "```", "",
          "Bare `python3` is missing xgboost and pytest on this machine, so the venv "
          "is not optional. Full fallbacks in `DEMO_RUNBOOK.md`.", "",
          "Run all three tonight. A command that fails in the room costs more than a missing "
          "slide.", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"CARRY_{safe}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


if __name__ == "__main__":
    for name, srn in STUDENTS:
        d = build_docx(name, srn)
        m = build_md(name, srn)
        print(f"  {name:20s} -> {d.name}  +  {m.name}")
    print(f"\n{len(STUDENTS)} carry sheets written to {OUT}")
