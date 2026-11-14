"""
build_internship_deck.py - the five per-student Internship Phase-1 decks.

    python presentation/build_internship_deck.py

The 14 November review runs two tracks with two separate 50-mark sheets, so each
student carries two decks. build_review_deck.py makes the Project one; this makes
the Internship one, following the official "Internship Presentation" template
(8 slides, slide for slide) and reusing that script's layout helpers so the two
decks look like one pair.

Self-assessment cells (the 1-5 baseline/now ratings) are left blank on purpose:
they are the student's own judgement, and slide 5 is where an examiner asks about
them. Fill them in by hand or in PowerPoint before printing.

Output: presentation/decks/Phase1_Internship_<NAME>.pptx
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "presentation"))

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

import build_review_deck as D   # layout helpers, palette, SDG 6 logo, live metrics

sys.path.insert(0, str(BASE / "scripts"))
import student_personal as P      # section, links, self-ratings

NAVY, AMBER, WHITE, GREY, DARK = D.NAVY, D.AMBER, D.WHITE, D.GREY, D.DARK
SW, SH = D.SW, D.SH
OUT = D.OUT
GUIDE = "Ms Indhuja Balakrishnan"
LEAD = "Dr. M. Shobha Rani"
BLANK = "____"

# ---------------------------------------------------------------- per student
S = {
"NITIN G A": dict(
    srn="R23EJ088", module="Module 2 - Depletion Risk Mapping",
    sub="AHP weighting and the composite risk index",
    files="src/module2_risk.py, src/config.py",
    contrib=[
        "Week 4 - built the AHP pairwise matrix on Saaty's 1-9 scale and the eigenvector "
        "routine that turns it into the five indicator weights.",
        "Week 6 - implemented the consistency check; CR = 0.0542, below the 0.10 AHP requires.",
        "Week 8 - implemented compute_risk_index(): normalisation, direction handling and "
        "the weighted sum over 177 taluks.",
        "Week 10 - removed two indicators that were np.random.uniform() placeholders and "
        "declared LULC change as deferred rather than dropping it.",
        "Week 12 - added weight renormalisation so a missing indicator rescales the rest "
        "instead of silently shrinking the index."],
    tech="Technical growth\nLinear algebra I could use, not just recite: the AHP "
         "eigenvector, the consistency ratio, and why a 5x5 matrix makes the O(n^3) cost "
         "irrelevant. Data modelling through the taluk join.",
    prof="Professional growth\nTelling the team bad news early. The placeholder defect "
         "changed numbers that were already in a submitted report, and saying so "
         "immediately cost less than letting an examiner find it.",
    chall="Challenge and response\nTwo of my five indicators were random numbers carrying "
          "10% of the AHP weight. Nothing failed and the map looked plausible. I replaced "
          "rainfall dependence with a measured quantity and wrote TC27 so it cannot return.",
    next_=["Add the deferred LULC-change indicator once land-cover rasters are integrated "
           "(Week 19).",
           "Re-derive the AHP weights with a second expert judgement and report the "
           "sensitivity of the ranking.",
           "Placement preparation: linear algebra and ML fundamentals, with this project "
           "as the worked example."]),
"R KOUSHIK": dict(
    srn="R23EJ096", module="Module 1 - Groundwater Level Prediction",
    sub="Model training, selection and rainfall integration",
    files="src/pipeline.py, src/rainfall.py",
    contrib=[
        "Week 4 - built the chronological train/validation/test split and established why "
        "a random split leaks the future through the lag features.",
        "Week 8 - trained and compared Random Forest, XGBoost and SVR against a persistence "
        "baseline; XGBoost selected on validation RMSE.",
        "Week 10 - integrated 29 years of NASA POWER daily rainfall after ERA5/Open-Meteo "
        "rate-limited, and built the five rainfall features.",
        "Week 10 - found and fixed a leak in rain_monsoon, which was using the in-progress "
        "season, and proved rainfall's value by A/B test (test R2 0.576 -> 0.632).",
        "Week 12 - wrote the regression tests that pin the split, the leak and the feature "
        "count."],
    tech="Technical growth\nModel selection on a held-out future period rather than a "
         "random fold; feature engineering with lag/rolling windows; writing an experiment "
         "that could have disproved my own claim.",
    prof="Professional growth\nReporting that earlier results came from synthetic data, "
         "and that three submitted documents were therefore wrong. Fixing the mechanism "
         "rather than the numbers.",
    chall="Challenge and response\nI nearly reported a higher R2 produced by a leak. "
          "Building the A/B harness exposed that rain_monsoon carried rain that had not "
          "fallen yet. The honest number, 0.632, is the one in every document.",
    next_=["Direct multi-horizon forecasting to replace recursive forecasting, which "
           "mean-reverts (Week 18).",
           "SHAP explanations on the selected XGBoost model so a planner sees why, not just "
           "what (Week 17).",
           "Placement preparation: DSA practice plus being able to defend a model choice "
           "end to end."]),
"S VARSHITH SAI": dict(
    srn="R23EJ100", module="Module 2 - Depletion Risk Mapping",
    sub="Jenks classification and validation against CGWB",
    files="src/module2_risk.py (classification, validate_against_cgwb)",
    contrib=[
        "Week 6 - implemented Jenks natural-breaks classification so the four risk classes "
        "follow groupings in the data, not arbitrary cut-offs.",
        "Week 8 - built validate_against_cgwb(): four-class agreement, Cohen's kappa, "
        "binary agreement with a confusion matrix, and Spearman rank without SciPy.",
        "Week 10 - established why four-class agreement is the wrong headline measure and "
        "why binary agreement and rank correlation are the fair tests.",
        "Week 12 - diagnosed the 0.45 recall as a hydrogeological limit, not a bug, by "
        "comparing the missed and caught taluks on depth, trend and extraction.",
        "Week 12 - added TC28 to pin the CGWB reference data (227 taluks, 62 stressed)."],
    tech="Technical growth\nStatistics I implemented rather than imported: Jenks natural "
         "breaks, Spearman with tie handling, and what Cohen's kappa does under class "
         "imbalance.",
    prof="Professional growth\nChoosing the measure before seeing the result, and arguing "
         "to keep the weak number in the report when it would have been easy to show only "
         "the strong one.",
    chall="Challenge and response\n23.9% agreement and kappa 0.001 looked like failure. "
          "Instead of tuning the breaks until the number improved, I showed why the measure "
          "cannot align by construction and reported all three measures.",
    next_=["Address the 0.45 recall with deep-well or piezometer data - shallow monitored "
           "wells cannot see deep-aquifer stress (Week 18).",
           "Re-validate against the next CGWB assessment when it is published.",
           "Placement preparation: statistics and ML evaluation questions, with the "
           "confusion matrix from this project as the example."]),
"BHIMISETTY KARTHIK": dict(
    srn="R23EJ168", module="Module 1 - Groundwater Level Prediction",
    sub="Cleaning, feature engineering and trend statistics",
    files="src/data_processor.py",
    contrib=[
        "Week 4 - merged the two CGWB exports and built the cleaning rules, separating 76 "
        "out-of-range readings from 165 records missing a level, date or district.",
        "Week 6 - wrote canonical_district() and the alias tables that reduced 33 district "
        "labels to the 28 real districts.",
        "Week 8 - implemented mann_kendall_sens_slope() from first principles, tie "
        "correction included, over 2,042 stations.",
        "Week 10 - verified every taluk alias by district rather than string similarity, "
        "catching a fuzzy match that proposed Parasgad to Pavagada.",
        "Week 12 - added TC15, TC18 and TC22 so the district count, that wrong alias and "
        "the exhaustive trend categories are all pinned."],
    tech="Technical growth\npandas at scale (123,632 rows), and statistics implemented "
         "from first principles rather than called - Mann-Kendall with Sen's slope, "
         "including why the median makes it robust.",
    prof="Professional growth\nChecking a join's match rate as a result in its own right, "
         "and preferring an explicit alias table I can defend over a similarity score I "
         "cannot.",
    chall="Challenge and response\nThe district join returned all-NaN. Three overlapping "
          "causes - renamed districts, a 13-character truncation and case. An explicit "
          "alias table fixed it and later caught the Parasgad/Pavagada error.",
    next_=["Extend the alias verification to the remaining unmatched taluk (176 of 177 "
           "matched today).",
           "Add data-quality assertions after every merge so a silent join failure cannot "
           "happen again.",
           "Placement preparation: SQL and data-handling rounds, using this cleaning work "
           "as the story."]),
"G M CHANDRASHEKAR": dict(
    srn="R23EQ029", module="Module 2 - Depletion Risk Mapping",
    sub="Dashboard, figures and delivery",
    files="dashboard.py, notebooks/make_figures.py",
    contrib=[
        "Week 8 - built the Streamlit dashboard so it reads models/ and outputs/ at run "
        "time and therefore cannot drift from the code.",
        "Week 10 - produced all 12 report and presentation figures from a single script, "
        "each with a colour legend and the value printed on every bar or point.",
        "Week 10 - added the plotly-version shim so the risk map works on both the pinned "
        "5.24 and the newer scatter_map API an examiner might have.",
        "Week 12 - cross-checked the rainfall grid against Karnataka's geography: 565 mm "
        "in the north interior against 3,603 mm on the coast, monsoon 73% of annual.",
        "Week 14 - rebuilt every figure and deck from the final pipeline run so nothing "
        "shown is a survivor of an older one."],
    tech="Technical growth\nStreamlit and Plotly, and dependency management as a real "
         "skill - pinning a version and writing a shim because an examiner's machine is "
         "not our machine.",
    prof="Professional growth\nTreating a reviewer's comment as a standing rule, not a "
         "task: every chart since the guide's feedback carries a legend and prints its "
         "values.",
    chall="Challenge and response\nThe dashboard kept disagreeing with the reports because "
          "metrics were typed into the source. I rewrote it to read pipeline output at run "
          "time, which removes the possibility rather than the symptom.",
    next_=["Add the kriging risk surface to the dashboard as a continuous layer (Week 17).",
           "Publish the dashboard so the guide and examiner can open it without a local "
           "install.",
           "Placement preparation: front-end and visualisation rounds, with a live demo "
           "rather than screenshots."]),
}

STACK = [
    ["Layer", "Technology", "Used for"],
    ["Language / data", "Python 3.11, pandas, NumPy", "123,391 cleaned CGWB records"],
    ["Machine learning", "scikit-learn, XGBoost", "Selected model: test R² 0.632"],
    ["Data sources", "India-WRIS (CGWB), NASA POWER", "Observations + 29 yr rainfall"],
    ["Visualisation", "Matplotlib, Plotly", "12 figures, interactive risk map"],
    ["Delivery", "Streamlit", "Dashboard reading outputs/ live"],
    ["Testing / tooling", "pytest, Git", "29 tests, all passing"],
]

FUNDAMENTAL_NOTES = {
    "Data structures and algorithms":
        "Trend statistics and the risk index implemented, not imported",
    "Operating systems":
        "Shell workflow, caching, exit codes and why silent failure is worse",
    "DBMS": "Keyed tables, join match rate treated as a first-class result",
    "Computer networks": "HTTP data acquisition, rate limits as a design constraint",
    "Assigned tech stack":
        "Python data and ML stack applied end to end on real public data",
}


def fundamentals(name: str):
    rows = [["Area", "Baseline (1-5)", "Now (1-5)", "What I did to improve"]]
    for area in P.AREAS:
        rows.append([area, *P.rating(name, area), FUNDAMENTAL_NOTES[area]])
    return rows

TOOLS = [
    ["Tool", "Used for", "Evidence"],
    ["Git", "History and change review", "Commits name the defect, not the file"],
    ["pytest", "Regression testing", "29 tests; 16 tied to specific defects"],
    ["Streamlit / Plotly", "Delivery and the risk map", "Live dashboard demo"],
    ["NASA POWER API", "Rainfall acquisition", "29 years, 105 grid cells, cached"],
    ["python-docx / pptx", "Report and deck generation", "Built from pipeline output"],
]


def deck(name: str) -> Path:
    d = S[name]; srn = d["srn"]
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH

    def content(title):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        D.textbox(s, Inches(0.55), Inches(0.30), Inches(12.2), Inches(0.7),
                  title, size=27, bold=True, color=NAVY)
        bar = s.shapes.add_shape(1, Inches(0.55), Inches(1.02), Inches(12.2), Pt(3.2))
        bar.fill.solid(); bar.fill.fore_color.rgb = AMBER; bar.line.fill.background()
        bar.shadow.inherit = False
        D.textbox(s, Inches(0.55), Inches(6.95), Inches(9), Inches(0.35),
                  f"RIO Internship Presentation  |  {name}  |  {srn}", size=10, color=GREY)
        return s

    def head(s, x, y, w, text, size=14):
        D.textbox(s, x + Inches(0.22), y + Inches(0.14), w - Inches(0.44), Inches(0.4),
                  text, size=size, bold=True, color=NAVY)

    # ---------- 1. title
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
    bg.shadow.inherit = False
    accent = s.shapes.add_shape(1, Inches(0.8), Inches(1.9), Pt(7), Inches(2.6))
    accent.fill.solid(); accent.fill.fore_color.rgb = AMBER
    accent.line.fill.background(); accent.shadow.inherit = False
    D.textbox(s, Inches(1.15), Inches(1.85), Inches(8.6), Inches(0.8),
              "Internship Presentation", size=38, bold=True, color=WHITE)
    D.textbox(s, Inches(1.15), Inches(2.72), Inches(8.8), Inches(1.1),
              f"{d['module']}  |  REVA University\n{d['sub']}", size=19, color=AMBER)
    D.textbox(s, Inches(1.15), Inches(4.00), Inches(9.0), Inches(1.6),
              f"{name}  |  {srn}  |  {P.program_short(name)}\n"
              f"Faculty Guide: {GUIDE}\n"
              "REVA Internship Opportunities (RIO)  |  14 November 2026",
              size=14, color=WHITE, spacing=1.5)
    D.title_branding(s)

    # ---------- 2. organisation and team
    s = content("Organisation and Team")
    p1 = D.panel(s, Inches(0.55), Inches(1.35), Inches(5.95), Inches(2.5))
    head(s, Inches(0.55), Inches(1.35), Inches(5.95), "The RIO Center")
    D.textbox(s, Inches(0.80), Inches(1.85), Inches(5.5), Inches(1.9),
              "REVA University, School of CSE - Center for Artificial Intelligence and "
              "Machine Learning (CAIML). RIO places students inside the university's own "
              "research centers, so the internship and the major project run together.\n"
              f"Center lead: {LEAD}. Applied ML on public-sector data; our customer for "
              "this work is state and district water administration.", size=12.5)
    D.panel(s, Inches(6.80), Inches(1.35), Inches(5.95), Inches(2.5))
    head(s, Inches(6.80), Inches(1.35), Inches(5.95), "My team")
    D.textbox(s, Inches(7.05), Inches(1.85), Inches(5.5), Inches(1.9),
              f"Five students on one system, problem statement "
              f"CAIML_Shobha_Rani_4_PS_160. I report to {GUIDE}.\n"
              f"My module: {d['module']} - {d['sub']}.\n"
              f"Files I own: {d['files']}.", size=12.5)
    D.panel(s, Inches(0.55), Inches(4.05), Inches(12.2), Inches(2.6))
    head(s, Inches(0.55), Inches(4.05), Inches(12.2), "How the team works")
    D.textbox(s, Inches(0.80), Inches(4.55), Inches(11.7), Inches(2.0),
              "Alternate-week rhythm set by the RIO schedule: a project deliverable one "
              "week, an internship deliverable the next, each reviewed before the next "
              "begins. Two module groups that integrate at every checkpoint. One shared "
              "debugging log, so a defect found by one person is visible to all five, and "
              "every fixed defect becomes a test.\n\n"
              "One real example: when the pipeline was found to have been running on "
              "synthetic data, the response was not only to fix the numbers. We removed the "
              "fallback, added src/provenance.py so no report can be generated from "
              "synthetic metadata, and wrote 16 regression tests - one per defect we had "
              "actually hit. The test suite went from 13 to 29.", size=12.5)

    # ---------- 3. module and problem statement
    s = content("Assigned Module and Problem Statement")
    D.panel(s, Inches(0.55), Inches(1.35), Inches(5.6), Inches(5.3))
    head(s, Inches(0.55), Inches(1.35), Inches(5.6), "Problem and users")
    D.textbox(s, Inches(0.80), Inches(1.85), Inches(5.1), Inches(4.6),
              "The problem is timing. CGWB's assessment tells an official a taluk is in "
              "trouble years after the fact, when the cheap interventions are gone.\n\n"
              "Users: district and taluk water authorities, Atal Bhujal Yojana and "
              "watershed planners, CGWB regional staff.\n\n"
              f"My module - {d['module']} - {d['sub']}.\n\n"
              "Measurable success, defined before the result was known: beat a persistence "
              f"baseline on a held-out future period (test R² {D.test['r2']:.3f} against "
              f"{D.test['baseline_r2']:.3f}) and place the taluks CGWB independently calls "
              "stressed at the top of the ranking (77.3% binary agreement).", size=12.5)
    img = D.W2 / "Fig1_Architecture.png"
    if img.exists():
        D.add_image(s, img, Inches(6.45), Inches(1.45), Inches(6.3), Inches(4.6))
    D.textbox(s, Inches(6.45), Inches(6.15), Inches(6.3), Inches(0.4),
              "Where my module sits in the larger system (Week 4 architecture).",
              size=11, italic=True, color=GREY, align=PP_ALIGN.CENTER)

    # ---------- 4. tech stack and contribution
    s = content("Tech Stack and My Contribution")
    D.add_table(s, Inches(0.55), Inches(1.35), Inches(6.1), Inches(3.4), STACK,
                col_w=[1.5, 2.1, 2.5], font=10, header_font=10.5)
    D.panel(s, Inches(6.95), Inches(1.35), Inches(5.8), Inches(5.3))
    head(s, Inches(6.95), Inches(1.35), Inches(5.8), "What I built or tested")
    D.textbox(s, Inches(7.20), Inches(1.85), Inches(5.3), Inches(4.6),
              "\n".join("•  " + c for c in d["contrib"]), size=11.5, spacing=1.25)

    # ---------- 5. fundamentals
    s = content("Fundamentals: Baseline vs Now")
    D.add_table(s, Inches(0.55), Inches(1.35), Inches(12.2), Inches(3.6),
                fundamentals(name),
                col_w=[2.6, 1.1, 1.0, 5.0], font=11, header_font=11)
    D.textbox(s, Inches(0.55), Inches(5.45), Inches(12.2), Inches(1.0),
              "The two rating columns are my own self-assessment against the Week-1 "
              "self-check - a judgement, not a measured quantity. The final column is "
              "evidence: every entry traces to code in the repository. "
              + ("Coding-platform evidence and the aptitude log are"
                 if P.has(name, "platform") else "The aptitude and coding-practice log is")
              + " attached separately (Week 5 deliverable).",
              size=12, italic=True, color=GREY)

    # ---------- 6. workplace practices and tools
    s = content("Workplace Practices and Industry Tools")
    D.panel(s, Inches(0.55), Inches(1.35), Inches(5.9), Inches(5.3))
    head(s, Inches(0.55), Inches(1.35), Inches(5.9), "Coding and documentation standards")
    D.textbox(s, Inches(0.80), Inches(1.85), Inches(5.4), Inches(4.6),
              "One responsibility per module; config isolated; names say what a thing is "
              "(canonical_district, rain_anomaly_12m). Docstrings state what a function "
              "refuses to do. Errors are loud - a missing data file raises rather than "
              "falling back. No number in any report, slide or dashboard is typed: all are "
              "read from pipeline output at build time. Every defect gets a regression test "
              "and a root-cause line in docs/debugging_log.md.", size=12)
    D.add_table(s, Inches(6.75), Inches(1.35), Inches(6.0), Inches(5.3), TOOLS,
                col_w=[1.5, 2.2, 2.3], font=11, header_font=11.5)

    # ---------- 7. reflection
    s = content("Reflection and Key Learnings")
    for i, text in enumerate([d["tech"], d["prof"], d["chall"]]):
        x = Inches(0.55 + i * 4.15)
        D.panel(s, x, Inches(1.35), Inches(3.9), Inches(5.3))
        title, body = text.split("\n", 1)
        head(s, x, Inches(1.35), Inches(3.9), title, size=13.5)
        D.textbox(s, x + Inches(0.22), Inches(1.90), Inches(3.45), Inches(4.5),
                  body, size=12)

    # ---------- 8. what next and thank you
    s = content("What Next and Thank You")
    D.panel(s, Inches(0.55), Inches(1.35), Inches(12.2), Inches(2.0))
    head(s, Inches(0.55), Inches(1.35), Inches(12.2), "Next steps")
    D.textbox(s, Inches(0.80), Inches(1.85), Inches(11.7), Inches(1.4),
              "\n".join("•  " + n for n in d["next_"]), size=12.5, spacing=1.25)
    D.textbox(s, Inches(0.55), Inches(4.00), Inches(12.2), Inches(0.8),
              "Thank you. Questions?", size=32, bold=True, color=NAVY,
              align=PP_ALIGN.CENTER)
    D.textbox(s, Inches(0.55), Inches(5.00), Inches(12.2), Inches(1.2),
              f"{name}  |  {srn}\n"
              f"{P.field(name, 'email', 26)}   |   "
              f"{P.field(name, 'linkedin', 26)}   |   "
              f"{P.field(name, 'github', 26)}\n"
              f"Guide: {GUIDE}  |  Center lead: {LEAD}",
              size=13, color=GREY, align=PP_ALIGN.CENTER, spacing=1.4)

    path = OUT / f"Phase1_Internship_{name.replace(' ', '_')}.pptx"
    prs.save(path)
    return path


if __name__ == "__main__":
    for nm in S:
        p = deck(nm)
        print(f"  wrote {p.relative_to(BASE)}  ({p.stat().st_size // 1024} KB)")
    print(f"\n{len(S)} internship decks written to {OUT}")
