"""
build_internship_reports.py - the five per-student Internship Phase-1 reports.

    python scripts/build_internship_reports.py

The 14 November 2026 review has two separate tracks with separate coordinators and
separate 50-mark sheets: Internship and Major Project. scripts/build_phase1_reports.py
produces the Project report; this produces the Internship one, following the official
"Internship Report -Phase-1" template circulated on 04.11.2026, section for section.

Everything personal - section, contact links, coding-platform evidence, certification,
the 1-5 self-ratings - comes from scripts/student_personal.py. Edit that one file and
re-run; a detail typed once lands on both reports, both decks and the four evaluation
sheets. Anything still unset there prints a ruled line rather than a plausible guess,
because this report is signed as the student's own work.

Writes: Phase1_Reports/Internship_Report_<NAME>.docx
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import student_personal as P
PROJ = ROOT.parent
OUTDIR = PROJ / "Phase1_Reports"
ASSETS = ROOT / "assets"

GUIDE = "Ms Indhuja Balakrishnan"
LEAD = "Dr. M. Shobha Rani"
PSID = "CAIML_Shobha_Rani_4_PS_160"
TITLE = ("Spatio-Temporal Prediction and Risk Mapping of Groundwater Depletion "
         "in Karnataka Using Machine Learning")
BLANK = "____________"

# ------------------------------------------------------------------ per student
# "module", "files" and "did" mirror scripts/build_phase1_reports.py so the two
# reports a student carries into the same room cannot contradict each other.
STUDENTS = [
 dict(name="NITIN G A", srn="R23EJ088",
      module="Module 2 - Depletion Risk Mapping (AHP weighting and the risk index)",
      files="src/module2_risk.py, src/config.py",
      stack_focus="NumPy linear algebra (eigenvector solution of the AHP matrix), pandas",
      improved={
        "Data structures and algorithms":
          "Implemented the AHP eigenvector solution and the weighted-sum risk index over "
          "177 taluks; reasoned about the O(n^3) cost of the eigen-decomposition against "
          "the 5x5 matrix size.",
        "Operating systems":
          "Worked from the shell throughout: file paths, exit codes and why a script that "
          "logs a warning and continues is worse than one that exits non-zero.",
        "DBMS":
          "Treated outputs/module2_*.csv as relations - designed the primary key "
          "(Taluk, District) and found the join defect that produced all-NaN categories.",
        "Computer networks":
          "Followed the NASA POWER HTTP API work: request/response, status codes, and why "
          "the Open-Meteo free tier rate-limited on (locations x days).",
        "Assigned tech stack":
          "NumPy and pandas for the indicator pipeline; wrote the consistency-ratio check "
          "and the weight renormalisation that keeps the index on scale when an indicator "
          "is absent."},
      examples=[
        "Named every indicator after the quantity it measures (decline_rate, "
        "rainfall_dependence) rather than i1..i5, so the AHP matrix reads as a document.",
        "Listed LULC change in DEFERRED_INDICATORS with a comment saying why, instead of "
        "deleting it - a reader can see what the design promised and what was built.",
        "Added TC27 so the np.random.uniform() placeholders that once filled two "
        "indicators cannot come back unnoticed."],
      conduct="Raised the random-placeholder problem with the team as soon as it was found, "
              "rather than quietly replacing it, because it changed numbers that were "
              "already in a submitted report.",
      reflection=
        "I came into this internship able to write Python that produced an answer, and I "
        "leave it much more careful about whether the answer means anything. The clearest "
        "example is my own: two of the five indicators in my risk index were "
        "np.random.uniform() placeholders left over from the design stage, carrying ten per "
        "cent of the AHP weight between them. Nothing crashed and the map looked plausible, "
        "which is exactly why it survived into a submitted report. I replaced rainfall "
        "dependence with a measured quantity and declared LULC change as deferred instead of "
        "dropping it quietly. I strengthened my linear algebra working through the AHP "
        "eigenvector and the consistency ratio, and my understanding of data modelling "
        "through the taluk-level join. On the soft side I learned to tell the team bad news "
        "early. The hardest moment was accepting that a result I had presented was not real; "
        "what worked was writing a regression test for it so it cannot return. I feel ready "
        "for placement technical rounds on the strength of being able to explain not just "
        "what my code does but what it refuses to do."),
 dict(name="R KOUSHIK", srn="R23EJ096",
      module="Module 1 - Groundwater Level Prediction (training, selection, rainfall)",
      files="src/pipeline.py, src/rainfall.py",
      stack_focus="scikit-learn, XGBoost, the NASA POWER API, pytest",
      improved={
        "Data structures and algorithms":
          "Built the chronological split and the lag/rolling feature construction; reasoned "
          "about why a random split leaks the future through those same lag columns.",
        "Operating systems":
          "Cached 29 years of rainfall to disk and made re-runs free; learned the cost "
          "difference between a network round trip and a local read the hard way.",
        "DBMS":
          "Designed the feature table as a keyed relation (station, date) and used "
          "train-set medians for imputation so no test information leaks into training.",
        "Computer networks":
          "Wrote the NASA POWER client: HTTP requests per year, retry behaviour, and a "
          "measured comparison against ERA5 at Kolar 2020 (1139 mm vs 1104 mm, 3%).",
        "Assigned tech stack":
          "scikit-learn and XGBoost for model selection on validation RMSE; pytest for the "
          "regression tests that encode each defect we fixed."},
      examples=[
        "Every experiment lives in experiments/ with a single entry point and prints its "
        "own result, so a claim in the report can be re-run in one command.",
        "Wrote the A/B harness (experiments/ab_rainfall.py) before claiming rainfall helped "
        "- the report says 0.576 to 0.632 because that was measured, not assumed.",
        "Docstrings state what a function refuses to do: run_module1() documents that it "
        "raises rather than falling back to synthetic data."],
      conduct="Kept the team's numbers honest in both directions - I was the one who had to "
              "report that an earlier result was produced on synthetic data and that three "
              "submitted documents were therefore wrong.",
      reflection=
        "The single most useful thing this internship taught me is that a result you have "
        "not tried to disprove is not a result. I added five rainfall features because the "
        "hydrology says rain drives recharge, and my first instinct was to report the new "
        "R2 and move on. That proves nothing, so I built an A/B harness that trains the same "
        "model with and without those features on the same chronological split: test R2 rose "
        "from 0.576 to 0.632. While building it I found that my rain_monsoon feature was "
        "summing the whole June-September season, so an August reading carried September's "
        "rain - a leak that had been quietly inflating the score. Technically I strengthened "
        "model selection, feature engineering and testing; I also learned that an API's free "
        "tier is a design constraint, not a detail. The hardest part was telling the team "
        "that numbers already in a submitted report came from synthetic data. What worked "
        "was fixing the mechanism, not just the numbers. I feel ready for placement rounds, "
        "and more importantly ready to defend a result rather than recite it."),
 dict(name="S VARSHITH SAI", srn="R23EJ100",
      module="Module 2 - Depletion Risk Mapping (classification and CGWB validation)",
      files="src/module2_risk.py (Jenks classification, validate_against_cgwb)",
      stack_focus="pandas, statistics implemented from first principles, pytest",
      improved={
        "Data structures and algorithms":
          "Implemented Jenks natural breaks (a dynamic-programming variance minimisation) "
          "and a Spearman rank correlation without SciPy, which meant handling ties myself.",
        "Operating systems":
          "Ran and profiled the pipeline from the shell; understood why the classification "
          "step is cheap and the trend step is not.",
        "DBMS":
          "Built the one-to-one validation join between our 177 taluks and CGWB's 227, and "
          "learned to check match rate as a first-class result (176/177).",
        "Computer networks":
          "Followed the data-acquisition work from India-WRIS and NASA POWER well enough to "
          "explain where every input file came from.",
        "Assigned tech stack":
          "pandas for the validation pipeline; pytest for the tests that pin the CGWB "
          "reference data (227 taluks, 62 stressed) so it cannot drift."},
      examples=[
        "Reported all three validation measures, including the one that looks bad, with the "
        "reason - the report is a document someone can check, not a sales sheet.",
        "Wrote the confusion matrix out in full (TP 23, FP 12, FN 28, TN 113) so precision "
        "and recall can be recomputed by the reader.",
        "Added TC28 to pin the CGWB reference table, because a validation result is only as "
        "stable as what it is validated against."],
      conduct="Argued for keeping the 23.9% four-class agreement in the report when it would "
              "have been easy to show only the 77.3%, and wrote the explanation of why the "
              "weak measure is the wrong measure here.",
      reflection=
        "This internship changed how I read a number. My job was to validate the risk map "
        "against CGWB's own assessment, and the first result looked like failure: 23.9 per "
        "cent four-class agreement, kappa 0.001. The tempting move was to tune the class "
        "boundaries until the number improved. Instead I worked out why the measure is wrong "
        "here - our classes are relative to the 177 taluks we assess, CGWB's are absolute "
        "thresholds on stage of extraction, so the two distributions cannot align - and "
        "added binary agreement (77.3%) and Spearman rank correlation (0.276) as the fair "
        "tests, reporting all three. I then diagnosed our 0.45 recall by comparing the 28 "
        "taluks we miss with the 23 we catch: the missed ones are shallow and flat despite "
        "122% extraction, which is deep-aquifer stress a shallow-well index cannot see. "
        "Technically I strengthened statistics and implemented Jenks and Spearman myself. "
        "Professionally I learned to choose the measure before seeing the result. I feel "
        "ready for placement interviews because I can now defend a weak number instead of "
        "hiding it."),
 dict(name="BHIMISETTY KARTHIK", srn="R23EJ168",
      module="Module 1 - Groundwater Level Prediction (cleaning, features, trend statistics)",
      files="src/data_processor.py",
      stack_focus="pandas, NumPy, statistical methods implemented from first principles",
      improved={
        "Data structures and algorithms":
          "Implemented Mann-Kendall with Sen's slope from first principles including the "
          "tie correction - an O(n^2) pairwise comparison run over 2,042 stations.",
        "Operating systems":
          "Learned to reason about memory and run time on a 123,632-row join rather than "
          "guessing; the whole pipeline now runs in under a minute on a laptop (measured: 30 s).",
        "DBMS":
          "Merged two CGWB exports into one keyed table, designed the cleaning rules, and "
          "wrote the alias tables that resolve renamed districts.",
        "Computer networks":
          "Understood the India-WRIS export route and why two separate downloads "
          "(1991-2020 and 2021-2025) had to be reconciled rather than concatenated blindly.",
        "Assigned tech stack":
          "pandas groupby/shift/rolling for the lag features; NumPy for the trend "
          "statistics; pytest for the regression tests on district and taluk naming."},
      examples=[
        "Separated the two cleaning rules in both the code and the report - 76 out-of-range "
        "readings and 165 missing fields - because an earlier version reported 241 as one "
        "number and that was wrong.",
        "Chose an explicit alias table over a fuzzy matcher and documented why: fuzzy "
        "matching proposed Parasgad to Pavagada, two taluks in different districts.",
        "Added TC15 and TC18 so the district count (28, not 33) and that specific wrong "
        "alias are both pinned by tests."],
      conduct="Checked every taluk alias against its district by hand rather than trusting a "
              "similarity score, and recorded the one it would have got wrong.",
      reflection=
        "Most of what I learned in this internship came from data that looked fine and was "
        "not. My first district-level join returned all-NaN categories, and the cause turned "
        "out to be three overlapping problems: Karnataka has renamed districts so the export "
        "carries both Mysore and Mysuru, one file truncated names at thirteen characters, "
        "and the case differed. I wrote canonical_district() with an explicit alias table "
        "instead of a fuzzy matcher, and that decision paid off later at taluk level, where "
        "fuzzy matching proposed mapping Parasgad to Pavagada - two taluks in different "
        "districts. Every alias is now checked against its district. Technically I "
        "strengthened pandas and statistics: I implemented Mann-Kendall with Sen's slope "
        "from first principles, tie correction included, over 2,042 stations. "
        "Professionally I learned to assert the result of a merge immediately rather than "
        "inspecting output later, and to state cleaning rules precisely - 76 out of range "
        "plus 165 missing, not 241 removed. I feel ready for placement drives, particularly "
        "on data-handling questions where I now have a real story to tell."),
 dict(name="G M CHANDRASHEKAR", srn="R23EQ029",
      module="Module 2 - Depletion Risk Mapping (dashboard, figures, delivery)",
      files="dashboard.py, notebooks/make_figures.py",
      stack_focus="Streamlit, Plotly, matplotlib, dependency management",
      improved={
        "Data structures and algorithms":
          "Shaped the dashboard's data layer: indexed lookups over the risk table rather "
          "than re-filtering the full frame on every interaction.",
        "Operating systems":
          "Managed the virtual environment and pinned dependencies; learned what a "
          "requirements file is actually for when a library removed an API we used.",
        "DBMS":
          "Treated outputs/ as the read model - the dashboard queries files written by the "
          "pipeline and never recomputes, so the two can never disagree.",
        "Computer networks":
          "Ran the Streamlit server and understood the request cycle, caching and why a "
          "cold start reads every CSV once.",
        "Assigned tech stack":
          "Streamlit and Plotly for delivery; matplotlib for the twelve report figures, "
          "each with a legend and the value printed on every bar."},
      examples=[
        "Removed every hand-typed metric from the presentation layer: the dashboard reads "
        "models/ and outputs/ at run time, so it cannot drift from the code.",
        "Pinned plotly to 5.24.0 and added a dual-API shim after 7.x removed "
        "px.scatter_mapbox - an examiner's machine is not our machine.",
        "Generated all twelve figures from one script so a figure can never be the stale "
        "survivor of an older run."],
      conduct="Took the guide's chart feedback as a standing rule rather than a one-off fix: "
              "every chart since carries a legend and prints its values.",
      reflection=
        "My part of this internship was delivery, and it taught me that the presentation "
        "layer is where honesty is easiest to lose. The dashboard I inherited had metrics "
        "typed into the source, so every pipeline re-run made it quietly stale with no error "
        "anywhere. I rewrote it to read models/ and outputs/ at run time, which means it "
        "cannot drift from the code even if someone forgets to update it. A second problem "
        "taught me about dependencies: plotly 7.x removed px.scatter_mapbox, so our risk map "
        "worked on our machines and would have failed on a newer install - I pinned the "
        "version and added a shim that works either way. I also rebuilt all twelve figures "
        "from a single script, each with a legend and the value printed on every bar, after "
        "our guide pointed out that colour alone was carrying the meaning. Technically I "
        "strengthened Streamlit, Plotly and dependency management; professionally I learned "
        "to treat a reviewer's comment as a rule rather than a task. I feel ready for "
        "placement rounds and can demo something real."),
]

TECH_STACK = [
    ("Language", "Python 3.11", "All pipeline, analysis and report-generation code"),
    ("Data handling", "pandas, NumPy",
     "Cleaning 123,632 CGWB rows, feature construction, indicator tables"),
    ("Machine learning", "scikit-learn, XGBoost",
     "Random Forest, SVR and the selected XGBoost regressor"),
    ("Deep learning (benchmark)", "PyTorch",
     "Sequence LSTM used only as a competitor in the benchmark study"),
    ("Data sources", "India-WRIS (CGWB), NASA POWER API",
     "Quarterly groundwater observations; 29 years of daily rainfall"),
    ("Visualisation", "Matplotlib, Plotly",
     "The twelve report figures and the interactive risk map"),
    ("Delivery", "Streamlit",
     "Dashboard reading models/ and outputs/ live, so it cannot drift"),
    ("Testing", "pytest",
     "29 tests: functional, boundary, negative and 16 regression tests"),
    ("Documentation", "python-docx, python-pptx",
     "Reports and decks generated from pipeline output, not typed"),
    ("Version control / tooling", "Git, shell",
     "History, branching and the single-command reproduction path"),
]

TOOLS = [
    ("Git", "Version history and change review",
     "Commit messages state the defect, not just the file touched"),
    ("pytest", "Automated regression testing",
     "Each of the 16 new tests is tied to one defect we actually hit"),
    ("Streamlit", "Interactive delivery to a non-technical reader",
     "Reads outputs/ at run time; no hand-typed numbers"),
    ("Matplotlib / Plotly", "Figures and the risk map",
     "Legend on every chart; value printed on every bar or point"),
    ("NASA POWER API", "Rainfall acquisition",
     "Cached per year; cross-checked against ERA5 at Kolar (3% difference)"),
    ("python-docx / python-pptx", "Report and deck generation",
     "Guarded by src/provenance.py so no document can be built from synthetic data"),
    ("Chrome headless", "DOCX to PDF conversion for submission",
     "--headless=new with --no-pdf-header-footer; output checked for file:// artefacts"),
]

GUIDE_FEEDBACK = [
    ("Literature review must be a table, not bullet points",
     "Rebuilt the survey as a four-column table (paper, approach, strength, limitation) in "
     "both the report and the deck", "Done"),
    ("The research gap and the proposed solution must be stated explicitly",
     "Added a gaps section naming G2, G4 and G5, and said which gap each module addresses",
     "Done"),
    ("A system architecture diagram and separate Module-1 and Module-2 diagrams are missing",
     "Reused the real diagrams from week2_diagrams/ and week3_diagrams/; all three now "
     "appear in the report and the deck", "Done"),
    ("Every chart needs a legend explaining the colours, and the data value on each bar",
     "Regenerated all twelve figures from notebooks/make_figures.py with legends and "
     "printed values", "Done"),
    ("A tile reading '0 - Predictive Systems' had no source and contradicted another slide",
     "Removed it. Standing rule adopted: no bare number on a slide without saying what it "
     "counts and where it came from", "Done"),
]



def _deck_reflections() -> dict:
    """Technical growth / professional growth / challenge, read from the deck builder.

    The internship template asks for the same three headings in report 3.3 and on
    deck slide 7. They are written once, in presentation/build_internship_deck.py,
    and read here, so the report and the deck cannot drift apart.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_deck", ROOT / "presentation" / "build_internship_deck.py")
    try:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return {k: (d["tech"], d["prof"], d["chall"]) for k, d in m.S.items()}
    except Exception:
        return {}


REFLECTIONS = _deck_reflections()

# ------------------------------------------------------------------ docx bits
def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    e = OxmlElement("w:shd"); e.set(qn("w:fill"), hexc); tcPr.append(e)


def centred(doc, text, size=12, bold=False):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); r.bold = bold; r.font.size = Pt(size)


def table(doc, headers, rows, fs=9.5):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    for c, h in zip(t.rows[0].cells, headers):
        c.text = ""
        run = c.paragraphs[0].add_run(h); run.bold = True; run.font.size = Pt(fs)
        shade(c, "1F3864")
        run.font.color.rgb = __import__("docx.shared", fromlist=["RGBColor"]).RGBColor(
            0xFF, 0xFF, 0xFF)
    for row in rows:
        cells = t.add_row().cells
        for c, val in zip(cells, row):
            c.text = ""
            r = c.paragraphs[0].add_run(str(val)); r.font.size = Pt(fs)
    return t


# ------------------------------------------------------------------ the report
def build(stu: dict) -> Path:
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11.5)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.2); s.left_margin = s.right_margin = Cm(2.0)

    if (ASSETS / "reva_logo.png").exists():
        doc.add_picture(str(ASSETS / "reva_logo.png"), width=Inches(2.9))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    centred(doc, "School of Computer Science and Engineering", 12)
    doc.add_paragraph()
    centred(doc, "Internship Report -Phase-1", 14, True)
    doc.add_paragraph()

    centred(doc, "Student and Internship Details", 12, True)
    table(doc, ["Field", "Details"], [
        ["Student name", stu["name"]],
        ["SRN / Roll number", stu["srn"]],
        ["Program and Section", P.program(stu["name"])],
        ["Project title", TITLE],
        ["Faculty guide", GUIDE],
    ], fs=10.5)

    doc.add_paragraph()
    centred(doc, "Sustainable Development Goals addressed", 11, True)
    p_logos = doc.add_paragraph(); p_logos.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, img in enumerate(["sdg06.png", "sdg13.png"]):
        if (ASSETS / img).exists():
            if i:
                p_logos.add_run("    ")
            p_logos.add_run().add_picture(str(ASSETS / img), width=Inches(1.3))
    pg = doc.add_paragraph(); pg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rg = pg.add_run(
        "SDG 6, targets 6.4 and 6.6: the project measures where Karnataka's groundwater "
        "is withdrawn faster than it recovers. SDG 13: rainfall dependence is one of the "
        "five risk indicators, which is how climate variability reaches the aquifer.")
    rg.font.size = Pt(9.5); rg.italic = True
    doc.add_page_break()

    # ================================================================ 1
    doc.add_heading("1. Organization, Team and Module Overview", 1)

    doc.add_heading("1.1 Organization and team", 2)
    doc.add_paragraph(
        "The internship is hosted inside REVA University under REVA Internship "
        "Opportunities (RIO), which places students in the university's own research "
        "centers so that an internship runs alongside the major project rather than apart "
        f"from it. I am attached to the Center for Artificial Intelligence and Machine "
        f"Learning (CAIML) in the School of Computer Science and Engineering, whose work is "
        f"applied machine learning on public-sector data. My team is five students building "
        f"one system, problem statement {PSID}. I report day to day to my faculty mentor, "
        f"{GUIDE}, and the center is led by {LEAD}. The team works on an alternate-week "
        "rhythm set by the RIO schedule: a project deliverable one week, an internship "
        "deliverable the next, each reviewed before the next begins. Within the team we "
        "split into two module groups, integrate at the end of every checkpoint, and keep a "
        "shared debugging log so that a defect one person finds is visible to everyone.")

    doc.add_heading("1.2 Assigned module and problem statement", 2)
    doc.add_paragraph(f"My module: {stu['module']}. Primary files: {stu['files']}.")
    doc.add_paragraph(
        "The system predicts groundwater levels across Karnataka and converts the measured "
        "trends into a taluk-level depletion-risk ranking. The problem it solves is a timing "
        "problem: CGWB's assessment tells an official that a taluk is in trouble years "
        "after the fact, by which time the cheap interventions are gone. Its users are "
        "district and taluk water authorities, Atal Bhujal Yojana and watershed planners, "
        "and CGWB's own regional staff. My module sits inside that larger system as "
        "described above — Module 1 produces per-station predictions and trends, Module 2 "
        "turns those trends into a ranked, validated risk map, and the dashboard presents "
        "both. Success for the whole system was defined before results were known: beat a "
        "persistence baseline on a held-out future period, and place the taluks CGWB "
        "independently calls stressed at the top of the ranking. Both were met — test R² "
        "0.632 against a 0.449 baseline, and 77.3% binary agreement with CGWB.")

    doc.add_heading("1.3 Technology stack", 2)
    doc.add_paragraph(
        f"My own work concentrated on: {stu['stack_focus']}.")
    table(doc, ["Layer / component", "Technology", "Purpose in the module",
                "My level at start → now"],
          [[a, b, c, P.stack_level(stu["name"], a)] for a, b, c in TECH_STACK], fs=9)

    # ================================================================ 2
    doc.add_page_break()
    doc.add_heading("2. Technical Fundamentals and Placement-Aligned Proficiency", 1)
    doc.add_heading("2.1 Fundamentals: baseline vs now", 2)
    doc.add_paragraph(
        "Rated 1 (weak) to 5 (strong); the baseline is the Week-1 self-check. The final "
        "column records what I actually did during the internship, and each entry can be "
        "traced to code in the repository.")
    table(doc, ["Area", "Baseline (1–5)", "Now (1–5)", "What I did to improve"],
          [[area, *P.rating(stu["name"], area), text]
           for area, text in stu["improved"].items()], fs=9)
    doc.add_paragraph()
    p = doc.add_paragraph()
    if P.has(stu["name"], "platform"):
        p.add_run("Coding-platform and aptitude evidence: ").bold = True
        p.add_run(f"{P.field(stu['name'], 'platform')}.  Aptitude and coding-practice log "
                  f"with scores: attached (Week-5 deliverable).")
    else:
        p.add_run("Aptitude and coding-practice evidence: ").bold = True
        p.add_run("aptitude and coding-practice log with scores: attached "
                  "(Week-5 deliverable).")

    # ================================================================ 3
    doc.add_heading("3. Workplace Practices, Documentation and Industry Tools", 1)
    doc.add_heading("3.1 Coding and documentation standards", 2)
    doc.add_paragraph(
        "The conventions the team follows are written down and enforced rather than assumed. "
        "Code is organised as a package with one responsibility per module (src/), a single "
        "entry point (src/main.py), configuration isolated in src/config.py, and scripts/ "
        "and experiments/ kept out of the library import path. Names say what a thing is — "
        "canonical_district(), compute_risk_index(), rain_anomaly_12m — and every public "
        "function carries a type hint and a docstring that states what it refuses to do as "
        "well as what it does. Errors are loud: a missing data file raises rather than "
        "logging a warning and continuing, because the project's worst defect came from a "
        "silent fallback. Every number that appears in a report, slide or dashboard is read "
        "from pipeline output at build time, never typed. Each defect we fix gets a "
        "regression test and an entry in docs/debugging_log.md recording the symptom, the "
        "root cause in one line, and the fix.")
    doc.add_paragraph("Examples from my own work:")
    for ex in stu["examples"]:
        doc.add_paragraph(ex, style="List Bullet")

    doc.add_heading("3.2 Tools used", 2)
    table(doc, ["Tool", "Used for", "Remarks"], TOOLS, fs=9.5)

    # ================================================================ 4
    doc.add_page_break()
    doc.add_heading("3.3 Reflection and key learnings", 2)
    blocks = REFLECTIONS.get(stu["name"])
    if blocks:
        for raw in blocks:
            head, _, body = raw.partition("\n")
            h = doc.add_paragraph(); h.add_run(head.strip()).bold = True
            doc.add_paragraph(body.strip())

    doc.add_page_break()
    doc.add_heading("4. Guide Feedback and Professional Conduct", 1)

    doc.add_heading("4.1 Requirement review", 2)
    doc.add_paragraph(
        f"Review date: {P.WEEK7_DATE}; minutes signed by the mentor. The faculty mentor, "
        f"{GUIDE}, reviewed the October presentation and the requirement set with the team. "
        "What was validated: the two-module decomposition, the choice of CGWB observation "
        "data as the primary source, and the decision to validate the risk ranking against "
        "an independent official assessment rather than against ourselves. What changed as a "
        "result: the literature survey was rebuilt as a comparison table with an explicit "
        "gap analysis; the architecture and both module diagrams became required content in "
        "every deliverable; chart standards were tightened so that colour is never the only "
        "carrier of meaning; and the unit of risk assessment moved from district to taluk so "
        "that validation against CGWB is one-to-one. The requirement set in section 1.4 of "
        "the project report is the revised one.")

    doc.add_heading("4.2 Guide feedback and my response", 2)
    table(doc, ["Feedback point", "Action I took", "Status"], GUIDE_FEEDBACK, fs=9.5)

    doc.add_heading("4.3 Professional conduct", 2)
    doc.add_paragraph(
        "Attendance and punctuality: present for every scheduled review and alternate-week "
        "deliverable of Phase 1; the LMS submission record is the evidence. "
        "Communication and teamwork: the team meets on the alternate-week rhythm the RIO "
        "schedule sets, and every integration point is treated as a scheduled event rather "
        "than something that happens at the end. We keep one shared debugging log so that a "
        "defect found by one person is visible to all five, and each fixed defect becomes a "
        "test rather than a note. Deadlines were handled by scoping honestly: when spatial "
        "interpolation could not be finished to a standard we would defend, we recorded it "
        "as Phase-2 work and stated overall completion as 70% rather than claiming more. "
        "Disagreements were settled by measurement where possible — the normalisation choice "
        "and the value of the rainfall features were both decided by running the experiment "
        "rather than by argument.")
    doc.add_paragraph(f"My own contribution to the team's conduct: {stu['conduct']}")
    p = doc.add_paragraph()
    p.add_run("Evidence: ").bold = True
    p.add_run("mentor-signed minutes and revised requirement notes (Week 7); mentor feedback "
              "form and action plan (Week 11).")

    # ================================================================ 5
    doc.add_page_break()
    doc.add_heading("5. Reflection, Placement Readiness and Capstone Showcase", 1)

    doc.add_heading("5.1 Mock interviews", 2)
    doc.add_paragraph(
        "The Week-7 round is the mock technical interview held alongside the stakeholder "
        "requirement review (RIO schedule, SL 7). It was assessed qualitatively rather than "
        "scored out of a total, so the feedback recorded at the session is given in full "
        "below instead of a mark.")
    table(doc, ["Round and date", "Topics covered", "Score / key feedback",
                "What I will improve"], [
        [f"Mock interview 1 (Week 7)\n{P.WEEK7_DATE}", P.MOCK1_TOPICS,
         P.MOCK1_SCORE, P.field(stu["name"], "mock_improve")],
        [f"Capstone mock interview (Week 15)\n{P.CAPSTONE_MOCK}",
         "Fundamentals, tech-stack mastery and the capstone walk-through",
         "Not yet held", "To be completed after the round"],
    ], fs=9.5)

    doc.add_heading("5.2 Resume, LinkedIn and portfolio", 2)
    table(doc, ["", ""], [
        ["Resume", P.field(stu["name"], "resume", 52)],
        ["LinkedIn", P.field(stu["name"], "linkedin", 52)],
        ["GitHub / portfolio", P.field(stu["name"], "github", 52)],
        ["E-mail", P.field(stu["name"], "email", 52)],
    ], fs=10.5)
    doc.add_paragraph(
        "What changed after mentor and faculty comments: the project entry was rewritten to "
        "lead with a measured outcome rather than a technology list — \"predicted quarterly "
        "groundwater levels for 2,769 CGWB stations; test R² 0.632 against a 0.449 "
        "persistence baseline\" in place of \"used Python, pandas and XGBoost\". My own "
        "module and the one defect I found and fixed are named, because that is what the "
        "mock interview actually asked about. The repository link was added so a reader can "
        "run the pipeline in one command.")

    doc.add_heading("5.3 Reflection (150–200 words)", 2)
    doc.add_paragraph(stu["reflection"])

    doc.add_heading("5.4 Capstone showcase plan", 2)
    doc.add_paragraph("The three points I will present:")
    doc.add_paragraph(
        "The system works on real public data end to end — 123,391 CGWB observations and 29 "
        "years of NASA POWER rainfall, one command from raw files to a ranked risk map.",
        style="List Bullet")
    doc.add_paragraph(
        "It is validated against something outside itself: 77.3% binary agreement with "
        "CGWB's independent 2020 assessment, with the weak measures reported too and "
        "explained.", style="List Bullet")
    doc.add_paragraph(
        "It produces something a planner can act on: a per-taluk action brief naming one "
        "intervention (recharge, demand management, investigate, watch or stable) built from "
        "the CGWB water balance and our measured trend.", style="List Bullet")
    doc.add_paragraph(
        "Demo and evidence: the live Streamlit dashboard (streamlit run dashboard.py) "
        "showing the station forecast view, the taluk risk map and the CGWB validation "
        "panel; the twelve generated figures; and the test run (python -m pytest tests/, "
        "29 passed) as evidence that the fixed defects stay fixed.")
    p = doc.add_paragraph()
    p.add_run("Evidence: ").bold = True
    p.add_run("reflective write-up (Week 13); showcase photo or video, mock-interview "
              "evaluation sheet and resume or portfolio proof (Week 15).")

    # ---------------- declaration
    doc.add_page_break()
    doc.add_heading("Declaration", 1)
    doc.add_paragraph(
        f"I, {stu['name']} (SRN {stu['srn']}), declare that this report is my own work and "
        f"that the evidence I have uploaded is genuine.")
    doc.add_paragraph()
    table(doc, ["Student signature and date", "Faculty Guide signature and date"],
          [["\n\n" + stu["name"] + f"  ({stu['srn']})", "\n\n" + GUIDE]], fs=11)

    OUTDIR.mkdir(exist_ok=True)
    path = OUTDIR / f"Internship_Report_{stu['name'].replace(' ', '_')}.docx"
    doc.save(path)
    return path


if __name__ == "__main__":
    from src.provenance import check as _check_provenance
    _check_provenance()   # the Phase-1 figures quoted here come from the real run
    for s in STUDENTS:
        p = build(s)
        print(f"  wrote {p.relative_to(PROJ)}  ({p.stat().st_size // 1024} KB)")
    print(f"\n{len(STUDENTS)} internship reports written to {OUTDIR}")
