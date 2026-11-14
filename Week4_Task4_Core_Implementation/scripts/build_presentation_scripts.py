"""
build_presentation_scripts.py - a speaking script per student, slide by slide.

    python scripts/build_presentation_scripts.py

Each of the five presents the same 14-slide project deck to a different examiner,
so the narration is shared where the slide is shared and personal where it is not:
slide 7 or 8 goes deep for the presenter's own module and stays brief on the other,
slide 13 is their own contribution, and slide 14 is their own hardest problem.

Reads the per-student data from build_phase1_reports.py and the per-student viva
questions from build_carry_sheets.py, so a script cannot describe work a person
did not do.

Writes: Phase1_Reports/Presentation_Scripts/SCRIPT_<NAME>.{md,docx}
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT.parent / "Phase1_Reports" / "Presentation_Scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R = _load("_rep", ROOT / "scripts" / "build_phase1_reports.py")
C = _load("_carry", ROOT / "scripts" / "build_carry_sheets.py")

GUIDE = "Ms Indhuja Balakrishnan"
TITLE = ("Spatio-Temporal Prediction and Risk Mapping of Groundwater Depletion "
         "in Karnataka Using Machine Learning")

# ---------------------------------------------------------------- shared lines
# Narration for the slides every one of the five presents the same way.
SHARED = {
 1: ("25 s", "Title", [
   "Good afternoon. I am {name}, SRN {srn}, and this is my Phase-1 review for the "
   "major project on spatio-temporal prediction and risk mapping of groundwater "
   "depletion in Karnataka using machine learning.",
   "It is a team of five under problem statement PS_160, guided by " + GUIDE + ". "
   "My module is {module_short}.",
   "The project aligns to UN Sustainable Development Goal 6, clean water and sanitation, "
   "which is the logo on the slide.",
 ], "If the examiner starts asking immediately, go straight to slide 13 and come back."),

 2: ("50 s", "Problem Statement and Literature Gaps", [
   "The problem is a timing problem, not a measurement problem. Karnataka is the second "
   "most groundwater-stressed state in India. The Central Ground Water Board's 2020 "
   "assessment puts 62 of 227 assessed taluks in the critical or over-exploited "
   "category - that is 27.3 percent.",
   "Recharge fell from 18.16 to 17.74 billion cubic metres while extraction rose from "
   "10.63 to 11.22. But that assessment reaches an official years after the fact, by "
   "which time the cheap interventions are gone.",
   "Our users are district and taluk water authorities, Atal Bhujal Yojana planners, and "
   "CGWB's own regional staff.",
   "The success metric was fixed before we saw any result: beat a persistence baseline on "
   "a held-out future period, and put the taluks CGWB independently calls stressed at the "
   "top of our ranking.",
 ], "Say 'fixed before we saw any result' deliberately - it answers a question before it is asked."),

 3: ("40 s", "Literature Survey", [
   "We surveyed 20 papers from 2017 to 2026. Three matter most.",
   "Alkon and colleagues, 2024, use the same CGWB well data with a Random Forest and "
   "report R-squared between 0.4 and 0.6. That sets the realistic bar for this data.",
   "Supreetha, 2020, shows an LSTM works on Karnataka wells, but on a single district and "
   "for prediction only, with no risk map.",
   "Tao and colleagues, 2022, reviewed over a hundred machine-learning groundwater "
   "studies: tree ensembles are competitive with deep learning on tabular well data, and "
   "most studies never test against a naive baseline. We do.",
 ], "The full 20-paper table is in the report at section 1.2 if they ask to see it."),

 4: ("30 s", "Requirements", [
   "Ten requirements. The four that drive everything: predict the next quarter's level at "
   "each station; beat a persistence baseline on a held-out period; rank taluks by risk "
   "from measured indicators only; and validate that ranking against an independent "
   "official source.",
   "Eight of the ten are met. One is Phase-2, the continuous risk surface. Every "
   "requirement traces to a design element and a source file in section 2.5 of the report.",
 ], "If asked which are unmet: R8, the kriging surface - say it plainly."),

 5: ("40 s", "System Design", [
   "Two modules behind one shared data pipeline.",
   "The pipeline loads the CGWB quarterly observations, cleans them, canonicalises "
   "district and taluk names, attaches NASA POWER rainfall and builds a 15-feature table.",
   "Module 1 predicts the next quarter's depth per station and derives a Mann-Kendall and "
   "Sen's-slope trend for each one. Module 2 aggregates those trends to taluks, combines "
   "them with four more measured indicators under AHP weights, classifies with Jenks "
   "natural breaks and validates against CGWB.",
   "The modules talk through files in outputs and models, not shared memory. That is why "
   "the dashboard and every report read the same numbers and cannot disagree with the code.",
 ], "The last sentence is the strongest thing on this slide. Do not rush it."),

 6: ("30 s", "Detailed Design: Flowchart, UML and DFD", [
   "These are the design artefacts: the module flowcharts, the data flow diagrams at "
   "level 0 and level 1, the UML use case, class and sequence diagrams, and the "
   "entity-relationship model.",
   "The one to look at is the sequence diagram: main dot py calls the data processor, then "
   "run_module1, which writes the station forecast file, then builds the taluk indicators "
   "and calls run_module2. Section 4.4 of my report says exactly which values are passed "
   "between the two modules and which are recomputed from the same shared function.",
 ], "If asked how a diagram maps to code, name the file - that is the expected answer."),

 9: ("35 s", "Implementation Progress", [
   "Three checkpoints. Week 8, about 30 percent: the shared pipeline on real CGWB data and "
   "Module 1 training. Week 10, about 55 percent: Module 2 with AHP, Jenks and CGWB "
   "validation, rainfall integrated, and seven silent defects fixed. Week 14, about 70 "
   "percent: the two modules integrated, the 29-test suite, and the dashboard.",
   "We state 70 percent, not higher, because four planned components have not been "
   "started - the kriging surface, SHAP, the land-use indicator and the spatio-temporal "
   "model.",
 ], "70 percent is the Phase-1 target. Claiming more invites a question you cannot win."),

 10: ("45 s", "Key Features and Demo", [
   "The delivered interface is a Streamlit dashboard. It reads the models and outputs "
   "folders at run time, so what you see on screen is the most recent pipeline run - no "
   "number on it can have been typed in.",
   "It has three views: the taluk risk map, the per-station forecast, and the CGWB "
   "validation view.",
   "I can show it running now if you would like.",
 ], "Have it already running in a browser tab. Do not launch it live in front of them."),

 11: ("40 s", "Testing", [
   "29 tests, 29 passing, nothing failing. Functional, boundary and negative cases for "
   "both modules, one end-to-end integration test, and 16 regression tests, each tied to a "
   "specific defect we fixed, so a fixed bug cannot come back unnoticed.",
   "Two worth naming. TC26 is a negative test that fails if CGWB's extraction figure ever "
   "becomes a model input - that is what keeps the validation from being circular. TC18 "
   "checks that the taluk Parasgad maps to Saundatti in Belagavi and never to Pavagada in "
   "Tumakuru, which is what an automated fuzzy matcher proposed.",
   "Six of the sixteen regression tests failed when first written, against the real API "
   "rather than the one we assumed, and were corrected before being counted as passing.",
 ], "Admitting the six failures is a strength. It shows the tests were real."),

 12: ("50 s", "Debugging and Integration", [
   "Every defect on this slide produced no error message. That is why they survived into "
   "our Week 4 and Week 5 reports.",
   "The worst one: the pipeline looked for a features dot csv that is never created, and "
   "silently fell back to synthetic data. Test R-squared was minus 0.098 while 123,391 "
   "real records sat unused in the same folder. Nothing crashed.",
   "We found it by checking the output against reality instead of checking that the code "
   "ran - a negative R-squared is worse than predicting the mean, so something had to be "
   "wrong. The fallback now raises, and a provenance guard blocks any report being built "
   "from synthetic metadata.",
   "On integration, the modules are coupled two ways: by order - main dot py runs Module 1 "
   "first and stops if it produced no trends - and by a shared function, station_trends in "
   "data_processor, which both rely on. The district path takes Module 1's trends as an "
   "argument; the taluk path recomputes the same slopes from the same cleaned data. Two "
   "bugs there - run_module2 was called with no arguments so it scored invented locations, "
   "and the station-to-taluk join silently matched almost nothing. 176 of 177 taluks match "
   "now.",
 ], "This is the slide that earns marks. Tell it as a story, not a list."),
}

# ---------------------------------------------------------------- module blocks
M1_DEEP = ("75 s", [
  "This is my module. 15 features per observation: four lagged levels, a rolling mean and "
  "standard deviation computed per station, month as sine and cosine so December and "
  "January are adjacent, latitude and longitude, and five rainfall features.",
  "The split is chronological, not random. The features include lagged levels, so a random "
  "split puts a station's future on both sides and the model scores well by memorising. "
  "Our scores fell when we fixed that, which is the point.",
  "We trained Random Forest, XGBoost and SVR on that split against a persistence baseline "
  "- the baseline just repeats the last observed level. XGBoost was selected on validation "
  "RMSE. The test split was touched once, after selection.",
  "Result: test RMSE 3.136 metres, R-squared 0.632, against a baseline of 3.838 metres and "
  "0.449. That is an 18 percent reduction in RMSE over what a planner would otherwise "
  "assume.",
  "Rainfall was tested, not assumed. Identical model, identical split, with and without "
  "the five rainfall features: R-squared 0.576 to 0.632. Running that test is how we found "
  "a leak - the monsoon feature was summing the in-progress season, so an August reading "
  "carried September's rain.",
  "Trends come from Mann-Kendall with the tie correction and Sen's slope, both written "
  "from first principles. Of 2,042 stations: 312 declining, 460 recovering, 1,270 with no "
  "significant trend.",
])
M1_BRIEF = ("30 s", [
  "Module 1, built by Koushik and Karthik, predicts the next quarter's level at each "
  "station. XGBoost, selected on validation RMSE against Random Forest, SVR and a "
  "persistence baseline, on a chronological split.",
  "Test RMSE 3.136 metres and R-squared 0.632, against a baseline of 3.838 and 0.449.",
  "What my module consumes from it is the Mann-Kendall and Sen's-slope trend per station.",
])
M2_DEEP = ("75 s", [
  "This is my module. Risk is assessed per taluk - 177 of them - because CGWB assesses "
  "taluks, so our ranking validates one to one against their table instead of against a "
  "district summary. It also gives about six times the resolution.",
  "Five measured indicators are combined. The weights come from AHP: a five by five "
  "pairwise comparison matrix on Saaty's 1 to 9 scale, and the weights are the principal "
  "eigenvector of that matrix.",
  "We use AHP because there is no ground-truth risk label to regress on. The judgement has "
  "to be made either way - AHP makes it explicit and checkable. The consistency ratio is "
  "0.0542, below the 0.10 the method requires.",
  "Classification is Jenks natural breaks, which minimises within-class variance, so the "
  "boundaries fall at real gaps in the data instead of at round numbers.",
  "The decline indicator is the measured Sen's slope, not the model's own forecast. "
  "Recursive forecasts drift to the training mean - 76 percent did - and that inverted the "
  "ranking, putting over-exploited Chitradurga at lowest risk.",
  "Validation against CGWB 2020: 77.3 percent binary agreement, precision 0.66, recall "
  "0.45, Spearman 0.276. Eight of our top 25 are Kolar taluks, and CGWB records 189 "
  "percent extraction in Kolar - the worst in the state. The model never saw that figure.",
])
M2_BRIEF = ("30 s", [
  "Module 2, built by Nitin, Varshith and Chandrashekar, turns my trends into a taluk "
  "risk ranking. Five measured indicators weighted by AHP, consistency ratio 0.0542, "
  "classified with Jenks natural breaks.",
  "Validated against CGWB's 2020 assessment: 77.3 percent binary agreement over 177 "
  "taluks, and 8 of the top 25 are Kolar taluks, where CGWB records 189 percent "
  "extraction.",
])

MODULE_SHORT = {
    "Module 1 - Groundwater Level Prediction": "Module 1, groundwater level prediction",
    "Module 2 - Depletion Risk Mapping": "Module 2, depletion risk mapping",
}

NUMBERS = [
    ("Test RMSE / R2", "3.136 m / 0.632, baseline 3.838 m / 0.449"),
    ("Taluks assessed", "177, of which 176 matched to CGWB"),
    ("Agreement with CGWB", "77.3% binary; precision 0.66, recall 0.45"),
    ("AHP consistency ratio", "0.0542 (must be under 0.10)"),
    ("Tests", "29 of 29 passing"),
    ("Honest completion", "70%"),
]


def script_for(stu: dict) -> list:
    """The ordered slide-by-slide script for one student."""
    name, srn = stu["name"], stu["srn"]
    mine_is_1 = stu["module"].startswith("Module 1")
    ctx = dict(name=name, srn=srn,
               module_short=MODULE_SHORT.get(stu["module"], stu["module"]))

    rows = []
    for n in (1, 2, 3, 4, 5, 6):
        t, title, lines, note = SHARED[n]
        rows.append((n, title, t, [l.format(**ctx) for l in lines], note))

    d7, l7 = M1_DEEP if mine_is_1 else M1_BRIEF
    rows.append((7, "Module 1 - Groundwater Level Prediction", d7, l7,
                 "Your module - go slow here." if mine_is_1
                 else "Not your module. Keep it short and hand the detail to the numbers."))
    d8, l8 = M2_DEEP if not mine_is_1 else M2_BRIEF
    rows.append((8, "Module 2 - Depletion Risk Mapping", d8, l8,
                 "Your module - go slow here." if not mine_is_1
                 else "Not your module. Keep it short and hand the detail to the numbers."))

    for n in (9, 10, 11, 12):
        t, title, lines, note = SHARED[n]
        rows.append((n, title, t, [l.format(**ctx) for l in lines], note))

    # ---- 13: entirely personal
    mine = [f"My module is {ctx['module_short']}, and the files I own are "
            f"{stu['files']}."]
    mine += [d for d in stu["did"]]
    mine += ["The Phase-2 table on the right has six items. The first is the honest one: "
             "deep-well or piezometer data, because our 0.45 recall is a data limitation, "
             "not a modelling one."]
    rows.append((13, "My Contribution and Phase-2 Plan", "70 s", mine,
                 "Answer 'which part is yours' with a file path, not a topic."))

    # ---- 14: personal hardest problem
    rows.append((14, "Learnings and Thank You", "60 s",
                 [stu["challenge"],
                  "Thank you. I am happy to take questions."],
                 "Finish on the sentence beginning 'What I would do differently'. "
                 "It is the strongest note to end on."))
    return rows


# ------------------------------------------------------------------ docx
def h(doc, text, size=13, color=(0x1F, 0x38, 0x64)):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(*color)
    p.paragraph_format.space_before = Pt(11); p.paragraph_format.space_after = Pt(3)


def para(doc, text, size=10.5, italic=False, bold=False, indent=0.0):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(size); r.italic = italic; r.bold = bold
    p.paragraph_format.space_after = Pt(3)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    return p


def build(stu: dict) -> tuple[Path, Path]:
    name, srn = stu["name"], stu["srn"]
    safe = name.replace(" ", "_")
    rows = script_for(stu)
    total = sum(int(t.split()[0]) for _, _, t, _, _ in rows)

    # ---------------- docx
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(1.6); s.left_margin = s.right_margin = Cm(1.8)

    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run(f"PRESENTATION SCRIPT - {name}")
    r.bold = True; r.font.size = Pt(16); r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run(f"{srn}  |  {stu['module']}  |  deck: Phase1_Review_{safe}.pptx "
                f"(14 slides)").font.size = Pt(10.5)
    para(doc, f"Roughly {total // 60} minutes {total % 60} seconds of speaking. Say it in "
              f"your own words - these are the points to hit and the order to hit them in, "
              f"not lines to memorise. Everything here is true of the work; do not add "
              f"anything that is not.", italic=True)

    h(doc, "Before you walk in")
    for b in ["Deck open in presentation mode, and the dashboard already running in a "
              "browser tab - do not launch it live.",
              "Both reports printed and signed, and the four evaluation sheets.",
              "Know the six numbers at the end of this script without looking."]:
        para(doc, "[  ]  " + b, indent=0.3)

    for n, title, time, lines, note in rows:
        h(doc, f"Slide {n} - {title}   ({time})")
        for line in lines:
            para(doc, line, indent=0.3)
        if note:
            para(doc, "Note: " + note, italic=True, size=9.5, indent=0.3)

    h(doc, "If you are cut short")
    para(doc, "Keep slides 1, 2, 5, then your own module slide (7 or 8), then 12 and 13. "
              "Those six carry the problem, the design, your work and the honesty. Drop "
              "3, 4, 6, 9, 10, 11 first.")

    h(doc, "Three questions you will be asked")
    for i, (q, a) in enumerate(C.QA[name], 1):
        para(doc, f"Q{i}.  {q}", bold=True)
        para(doc, a, indent=0.3)

    h(doc, "Six numbers to know without looking")
    for k, val in NUMBERS:
        para(doc, f"{k}:  {val}", indent=0.3)
    para(doc, "And the two weak ones, said before you are asked: four-class agreement is "
              "23.9% because relative Jenks classes cannot align with absolute CGWB "
              "thresholds by construction; recall is 0.45 because the 28 taluks we miss "
              "are shallow and flat despite 122% extraction - deep-aquifer stress a "
              "shallow-well index cannot see.", italic=True)

    h(doc, "Never say these", color=(0x99, 0x33, 0x00))
    para(doc, "RMSE 3.63, R-squared 0.40, or 68% accuracy. Those came from the synthetic "
              "fallback we fixed and are not real results. The real ones are RMSE 3.136, "
              "R-squared 0.632 and 77.3% binary agreement.")

    OUT.mkdir(parents=True, exist_ok=True)
    dpath = OUT / f"SCRIPT_{safe}.docx"
    doc.save(str(dpath))

    # ---------------- markdown, for the phone
    L = [f"# Presentation script - {name}", "",
         f"**{srn} | {stu['module']}**  ",
         f"Deck: `Phase1_Review_{safe}.pptx` (14 slides)  ",
         f"About **{total // 60} min {total % 60} s** of speaking.", "",
         "Say it in your own words. These are the points to hit and the order to hit them "
         "in, not lines to memorise.", "",
         "## Before you walk in", "",
         "- [ ] Deck open in presentation mode; dashboard already running in a browser tab",
         "- [ ] Both reports printed and signed, plus the four evaluation sheets",
         "- [ ] The six numbers at the bottom, known without looking", ""]
    for n, title, time, lines, note in rows:
        L += [f"## Slide {n} — {title}  *({time})*", ""]
        L += [f"> {l}" + "\n" for l in lines]
        if note:
            L += [f"*Note: {note}*", ""]
    L += ["## If you are cut short", "",
          "Keep slides **1, 2, 5, your own module slide (7 or 8), 12 and 13**. Those six "
          "carry the problem, the design, your work and the honesty. Drop 3, 4, 6, 9, 10, "
          "11 first.", "",
          "## Three questions you will be asked", ""]
    for i, (q, a) in enumerate(C.QA[name], 1):
        L += [f"**Q{i}. {q}**", "", a, ""]
    L += ["## Six numbers to know without looking", "", "| | |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in NUMBERS]
    L += ["", "The two weak ones, said **before** you are asked: four-class agreement is "
          "**23.9%** because relative Jenks classes cannot align with absolute CGWB "
          "thresholds by construction; recall is **0.45** because the 28 taluks we miss are "
          "shallow and flat despite 122% extraction — deep-aquifer stress a shallow-well "
          "index cannot see.", "",
          "## Never say these", "",
          "RMSE 3.63, R² 0.40, 68% accuracy. Those came from the synthetic fallback we "
          "fixed. The real ones are **RMSE 3.136**, **R² 0.632**, **77.3%**.", ""]
    mpath = OUT / f"SCRIPT_{safe}.md"
    mpath.write_text("\n".join(L), encoding="utf-8")
    return dpath, mpath


if __name__ == "__main__":
    for stu in R.STUDENTS:
        d, m = build(stu)
        print(f"  {stu['name']:20s} -> {d.name}  +  {m.name}")
    print(f"\n{len(R.STUDENTS)} presentation scripts written to {OUT}")
