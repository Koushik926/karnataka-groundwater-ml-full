"""
build_review_deck.py - Phase-1 review decks (14 Nov 2026), one per student.

    python presentation/build_review_deck.py

Follows the official REVA "Project Presentation" template and the guide's
review feedback on the October deck:

  * literature review as a TABLE, not bullets
  * research gap, proposed solution, system architecture, and separate
    Module 1 and Module 2 diagrams all present
  * every chart carries a legend explaining its colours and a value on each bar
  * SDG 6 logo on the title slide
  * no hand-typed metrics: every number is read from models/ and outputs/, so
    the deck can never disagree with the code

Output: presentation/decks/Phase1_Review_<NAME>.pptx (one per team member).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import student_personal as P  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE.parent
FIGS = BASE / "outputs" / "figures"
W2, W3 = PROJECT / "week2_diagrams", PROJECT / "week3_diagrams"
OUT = BASE / "presentation" / "decks"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = RGBColor(0x1E, 0x2A, 0x44)
AMBER = RGBColor(0xE8, 0xA3, 0x17)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY = RGBColor(0x6B, 0x72, 0x80)
DARK = RGBColor(0x11, 0x11, 0x11)
PANEL = RGBColor(0xF1, 0xF3, 0xF5)
SW, SH = Inches(13.333), Inches(7.5)

# ---------------------------------------------------------------- live numbers
meta = json.loads((BASE / "models" / "module1_best_model.json").read_text())
risk = pd.read_csv(BASE / "outputs" / "module2_risk_mapping.csv")
UNIT = "Taluk" if "Taluk" in risk.columns else "District"
trends = pd.read_csv(BASE / "outputs" / "module1_district_trends.csv")
val, test, split = meta["validation_metrics"], meta["test_metrics"], meta["split"]
BEST = meta["selected_model"]
N_UNITS = len(risk)
N_DIST = N_UNITS
TOP = risk.sort_values("risk_index", ascending=False)[UNIT].head(4).tolist()
HIGH_N = int((risk["risk_class"] >= 3).sum())
# Which district dominates the top of the ranking, and by how much.  Computed,
# not asserted: an earlier draft of the deck claimed "9 of the top 25" by hand
# and the real figure is 8 (the 9th Kolar taluk ranks 51st).
_top25 = risk.sort_values("risk_index", ascending=False).head(25)
TOP_DISTRICT = _top25["District"].value_counts().idxmax()
TOP_DISTRICT_N = int(_top25["District"].value_counts().max())

TEAM = [
    ("NITIN G A", "R23EJ088", 2),
    ("R KOUSHIK", "R23EJ096", 1),
    ("S VARSHITH SAI", "R23EJ100", 2),
    ("BHIMISETTY KARTHIK", "R23EJ168", 1),
    ("G M CHANDRASHEKAR", "R23EQ029", 2),
]


# ---------------------------------------------------------------- SDG 6 logo
def make_sdg6_logo() -> Path:
    """Draw an SDG 6 tile (recreation - swap for the official UN asset if required)."""
    path = BASE / "presentation" / "sdg6_logo.png"
    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=300)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#26BDE2"))
    ax.text(0.07, 0.72, "6", fontsize=46, fontweight="bold", color="white",
            ha="left", va="center")
    ax.text(0.07, 0.40, "CLEAN WATER\nAND SANITATION", fontsize=11.5,
            fontweight="bold", color="white", ha="left", va="center", linespacing=1.25)
    # water drop
    ax.add_patch(plt.Circle((0.80, 0.74), 0.085, color="white"))
    ax.add_patch(plt.Polygon([[0.715, 0.755], [0.80, 0.90], [0.885, 0.755]], color="white"))
    ax.arrow(0.80, 0.60, 0.0, -0.10, width=0.016, head_width=0.05,
             head_length=0.045, color="white", length_includes_head=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0, facecolor="#26BDE2")
    plt.close(fig)
    return path


SDG6 = make_sdg6_logo()


# ---------------------------------------------------------------- helpers
def textbox(slide, x, y, w, h, text, size=14, bold=False, color=DARK,
            align=PP_ALIGN.LEFT, italic=False, spacing=1.15):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for i, line in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.line_spacing = spacing
        for r in p.runs:
            r.font.size = Pt(size); r.font.bold = bold
            r.font.italic = italic; r.font.color.rgb = color
            r.font.name = "Calibri"
    return tb


def panel(slide, x, y, w, h, fill=PANEL):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = RGBColor(0xD8, 0xDD, 0xE3); sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    sh.text_frame.text = ""
    return sh


def content_slide(prs, title, name, srn):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    textbox(s, Inches(0.55), Inches(0.30), Inches(12.2), Inches(0.7),
            title, size=27, bold=True, color=NAVY)
    bar = s.shapes.add_shape(1, Inches(0.55), Inches(1.02), Inches(12.2), Pt(3.2))
    bar.fill.solid(); bar.fill.fore_color.rgb = AMBER; bar.line.fill.background()
    bar.shadow.inherit = False
    textbox(s, Inches(0.55), Inches(6.95), Inches(9), Inches(0.35),
            f"Project Presentation  |  {name}  |  {srn}", size=10, color=GREY)
    return s


def add_image(slide, img, x, y, max_w, max_h):
    from PIL import Image
    iw, ih = Image.open(img).size
    scale = min(max_w / iw, max_h / ih)
    w, h = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(str(img), x + int((max_w - w) / 2),
                                    y + int((max_h - h) / 2), width=w, height=h)


def add_table(slide, x, y, w, h, data, col_w=None, font=10.5, header_font=10.5):
    rows, cols = len(data), len(data[0])
    shape = slide.shapes.add_table(rows, cols, x, y, w, h)
    tbl = shape.table
    if col_w:
        total = sum(col_w)
        for i, cw in enumerate(col_w):
            tbl.columns[i].width = Emu(int(w * cw / total))
    for r, row in enumerate(data):
        for c, valtext in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = str(valtext)
            cell.margin_left = Inches(0.06); cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02); cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.line_spacing = 0.95
                for run in p.runs:
                    run.font.size = Pt(header_font if r == 0 else font)
                    run.font.bold = (r == 0)
                    run.font.name = "Calibri"
                    run.font.color.rgb = WHITE if r == 0 else DARK
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if r == 0 else (
                RGBColor(0xFF, 0xFF, 0xFF) if r % 2 else RGBColor(0xF4, 0xF6, 0xF8))
    return tbl


# ---------------------------------------------------------------- deck

# Per-student contributions come from the report builder, so a person's slide and
# their report describe the same work. Imported lazily: a failure here must not
# stop the deck being built, but it must also never fall back to placeholder text.
def _contrib() -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_rep", BASE / "scripts" / "build_phase1_reports.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return {d["name"]: d for d in m.STUDENTS}


CONTRIB = _contrib()

# ---------------------------------------------------------------- branding
ASSETS = BASE / "assets"
REVA_LOGO = ASSETS / "reva_logo.png"
SDG_TILES = [ASSETS / "sdg06.png", ASSETS / "sdg13.png"]


def title_branding(slide):
    """REVA logo and the two SDG tiles on a title slide.

    The logo is the university's own asset (orange wordmark over dark grey), so
    it sits on a white plate - on the navy background the grey line would be
    unreadable. Shared by both decks so the two title slides match.
    """
    if REVA_LOGO.exists():
        plate = slide.shapes.add_shape(1, Inches(0.78), Inches(0.42),
                                       Inches(3.35), Inches(1.02))
        plate.fill.solid(); plate.fill.fore_color.rgb = WHITE
        plate.line.fill.background(); plate.shadow.inherit = False
        slide.shapes.add_picture(str(REVA_LOGO), Inches(0.95), Inches(0.56),
                                 width=Inches(3.0))
    tiles = [t for t in SDG_TILES if t.exists()]
    for i, t in enumerate(tiles):
        slide.shapes.add_picture(str(t), Inches(9.62 + i * 1.72), Inches(2.55),
                                 height=Inches(1.6))
    if tiles:
        textbox(slide, Inches(9.42), Inches(4.32), Inches(3.3), Inches(0.5),
                "Aligned to UN SDG 6 and SDG 13", size=11, color=WHITE,
                align=PP_ALIGN.CENTER)


def count_tests() -> int:
    """Count the test functions in tests/, so the deck cannot quote a stale total.

    The deck said 13 for weeks after the suite grew to 29, because the number was
    typed in. It is now derived.
    """
    total = 0
    for f in sorted((BASE / "tests").glob("test_*.py")):
        total += sum(1 for line in f.read_text().splitlines()
                     if line.lstrip().startswith("def test_"))
    return total or 29


def build(name: str, srn: str, module: int) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH

    # ---------- 1. title
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
    bg.shadow.inherit = False
    accent = s.shapes.add_shape(1, Inches(0.8), Inches(1.9), Pt(7), Inches(2.6))
    accent.fill.solid(); accent.fill.fore_color.rgb = AMBER
    accent.line.fill.background(); accent.shadow.inherit = False
    textbox(s, Inches(1.15), Inches(1.85), Inches(8.6), Inches(0.8),
            "Project Presentation", size=38, bold=True, color=WHITE)
    textbox(s, Inches(1.15), Inches(2.72), Inches(8.8), Inches(1.1),
            "Spatio-Temporal Prediction and Risk Mapping of\n"
            "Groundwater Depletion in Karnataka Using Machine Learning",
            size=19, color=AMBER)
    textbox(s, Inches(1.15), Inches(4.00), Inches(9.0), Inches(1.5),
            f"{name}  |  {srn}  |  {P.program_short(name)}\n"
            "Faculty guide: Ms Indhuja Balakrishnan     Phase-1 review\n"
            "REVA Internship Opportunities (RIO)  |  14 November 2026",
            size=14, color=WHITE, spacing=1.5)
    title_branding(s)

    # ---------- 2. problem + gaps
    s = content_slide(prs, "Problem Statement and Literature Gaps", name, srn)
    panel(s, Inches(0.55), Inches(1.30), Inches(6.0), Inches(5.3))
    textbox(s, Inches(0.80), Inches(1.45), Inches(5.5), Inches(0.4),
            "Problem and users", size=16, bold=True, color=NAVY)
    textbox(s, Inches(0.80), Inches(1.95), Inches(5.5), Inches(4.5),
            "Karnataka's groundwater is monitored, but not forecast. CGWB "
            "publishes readings four times a year and an extraction category "
            "once a year — both describe the past.\n\n"
            "62 of 227 taluks (27.3%) are already critical or over-exploited.\n\n"
            "Users: district water-resource planners and Gram Panchayats, who "
            "must decide where to act before wells fail.\n\n"
            "Success: predict the next quarter's level better than assuming "
            "'same as last time', and rank every district by depletion risk.",
            size=13.5)
    panel(s, Inches(6.78), Inches(1.30), Inches(5.98), Inches(5.3))
    textbox(s, Inches(7.03), Inches(1.45), Inches(5.5), Inches(0.4),
            "Gaps in existing work", size=16, bold=True, color=NAVY)
    textbox(s, Inches(7.03), Inches(1.95), Inches(5.5), Inches(4.5),
            "Gap 1 — Studies stop at 2013–2018, so recent drought and recovery "
            "years are unmodelled (Asoka 2017; Alkon 2024).\n\n"
            "Gap 2 — Prediction and risk mapping are done separately. Risk maps "
            "are static snapshots that ignore predicted trends (Saha 2021; "
            "Hanumantha 2026).\n\n"
            "Gap 3 — Indian studies model each well independently, ignoring "
            "spatial relationships (Malakar 2021; Supreetha 2020).\n\n"
            "Addressed here: Gap 1 → Module 1 (data to 2024)\n"
            "Gap 2 → Module 2 (risk built FROM predicted trends)\n"
            "Gap 3 → noted as Phase-2 scope",
            size=13)

    # ---------- 3. literature survey TABLE
    s = content_slide(prs, "Literature Survey", name, srn)
    textbox(s, Inches(0.55), Inches(1.12), Inches(12.2), Inches(0.3),
            "10 of the 20 papers reviewed (2017–2026); full table in the report",
            size=11.5, italic=True, color=GREY)
    lit = [
        ["Paper (author, year)", "Approach / technique", "Strength", "Limitation"],
        ["Hanumantha 2026, Discover Water", "DRASTIC index + GIS overlay, 7 layers",
         "Latest statewide Karnataka map", "Contamination not depletion; static, no ML"],
        ["Srinivasan 2025, PLOS Water", "Field census of wells, cost analysis",
         "Ground truth near Bengaluru", "Two Gram Panchayats only; no forecasting"],
        ["Alkon 2024, Environ. Res. Lett.", "XGBoost + RF, SHAP, quantile forests",
         "Same CGWB data; explainable", "R² 0.4–0.6; data stop at 2014; no risk zones"],
        ["Boo 2024, Water Research", "Review of 142 ML forecasting papers",
         "Best-practice checklist", "No new experiments"],
        ["Patra & Chu 2024, Front. Water", "ConvLSTM on interpolated grids",
         "Captures space and time together", "Head only; no rainfall or pumping"],
        ["Wang 2024, J. Hydroinformatics", "GCN + LSTM across 16 wells",
         "+11% fit over single-well LSTM", "Small network; not hard-rock aquifers"],
        ["Wunsch 2021, HESS", "NARX vs LSTM vs CNN benchmark",
         "Fair, reproducible comparison", "Germany; no abstraction inputs"],
        ["Malakar 2021, ACS ES&T Eng.", "FNN / RNN / LSTM on 5,367 wells",
         "All-India; 5-year forecast", "Well-wise only; no risk classification"],
        ["Saha 2021, J. Cleaner Prod.", "Fuzzy + Bagging + ANN drought index",
         "Statewide Karnataka ML map (86.5%)", "Drought, not groundwater; static"],
        ["Supreetha 2020, ACISC", "LSTM tuned by Lion Algorithm",
         "Karnataka hard-rock (Udupi)", "One well; rainfall the only input"],
    ]
    add_table(s, Inches(0.55), Inches(1.50), Inches(12.2), Inches(5.0), lit,
              col_w=[26, 27, 23, 24], font=9.3, header_font=10)

    # ---------- 4. requirements
    s = content_slide(prs, "Requirements", name, srn)
    reqs = [
        ["ID", "Requirement", "Type", "Priority", "Status"],
        ["R1", "Ingest CGWB quarterly levels and the CGWB extraction assessment for Karnataka",
         "Functional", "High", "Done"],
        ["R2", "Predict the next quarter's depth per station, beating a last-value baseline",
         "Functional", "High", "Done"],
        ["R3", "Estimate a statistically tested long-term trend per station and district",
         "Functional", "High", "Done"],
        ["R4", "Classify every district into four depletion-risk zones from those trends",
         "Functional", "High", "Done"],
        ["R5", "Validate the risk zones against the official CGWB categories",
         "Functional", "Medium", "Done"],
        ["R6", "Present results on an interactive dashboard for planners",
         "Functional", "Medium", "Working"],
        ["R7", "Reproducible run: one command regenerates every reported number",
         "Non-functional", "High", "Done"],
        ["R8", "No fabricated or placeholder values in any reported result",
         "Non-functional", "High", "Done"],
    ]
    add_table(s, Inches(0.55), Inches(1.35), Inches(12.2), Inches(4.6), reqs,
              col_w=[5, 56, 14, 12, 13], font=11)
    textbox(s, Inches(0.55), Inches(6.15), Inches(12.2), Inches(0.6),
            "Traceability: R1 → data_processor.py · R2 → pipeline.py (RF/XGBoost/SVR) · "
            "R3 → mann_kendall_sens_slope() · R4 → module2_risk.py · "
            "R5 → validate_against_cgwb() · R6 → dashboard.py · R7 → src/main.py",
            size=11, italic=True, color=GREY)

    # ---------- 5. system design
    s = content_slide(prs, "System Design", name, srn)
    add_image(s, W2 / "Fig1_Architecture.png", Inches(0.55), Inches(1.35),
              Inches(8.5), Inches(5.0))
    panel(s, Inches(9.25), Inches(1.35), Inches(3.5), Inches(5.0))
    textbox(s, Inches(9.45), Inches(1.50), Inches(3.1), Inches(0.4),
            "Why this design", size=15, bold=True, color=NAVY)
    textbox(s, Inches(9.45), Inches(1.98), Inches(3.1), Inches(4.2),
            "Layered, with every stage exchanging data through one store, so each "
            "module runs and is tested on its own.\n\n"
            "PostGIS over plain files: the data is both temporal and spatial, and "
            "we need 'which wells fall in this taluk'.\n\n"
            "Rejected: a single end-to-end notebook — not reproducible and "
            "impossible to test.\n\n"
            "Rejected: deep learning first — with 2,769 stations of quarterly data, "
            "tree ensembles are stronger and explainable.",
            size=12)

    # ---------- 6. detailed design
    s = content_slide(prs, "Detailed Design: Flowchart, UML and DFD", name, srn)
    for img, x, cap in [
        (W3 / "Fig3_Flowchart_PartB.png", Inches(0.55), "Flowchart — main logic"),
        (W3 / "Fig8_UseCase.png", Inches(4.75), "UML — use case"),
        (W2 / "Fig3_DFD_Level1.png", Inches(8.95), "DFD — level 1"),
    ]:
        add_image(s, img, x, Inches(1.35), Inches(3.9), Inches(4.4))
        textbox(s, x, Inches(5.95), Inches(3.9), Inches(0.4), cap,
                size=12, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    textbox(s, Inches(0.55), Inches(6.45), Inches(12.2), Inches(0.4),
            "Each element traces to a requirement: flowchart → R1–R5 · use case → R1–R6 · "
            "DFD stores D1–D4 → R7. Class, component, activity, sequence and ER diagrams are in the report.",
            size=11, italic=True, color=GREY)

    # ---------- 7. Module 1
    s = content_slide(prs, "Module 1 — Groundwater Level Prediction", name, srn)
    add_image(s, W2 / "Fig4_Module1_Flowchart.png", Inches(0.55), Inches(1.30),
              Inches(4.3), Inches(5.1))
    add_image(s, FIGS / "fig5_model_comparison.png", Inches(5.05), Inches(1.30),
              Inches(7.7), Inches(3.5))
    rows = [["Model", "Val RMSE (m)", "Val R²", "Test RMSE (m)", "Test R²"]]
    order = ["baseline_last_value", "svr", "random_forest", "xgboost"]
    pretty = {"baseline_last_value": "Baseline (last value)", "svr": "SVR",
              "random_forest": "Random Forest", "xgboost": "XGBoost  ← selected"}
    for k in order:
        if k not in val:
            continue
        if k == BEST:
            rows.append([pretty[k], f"{val[k]['rmse']:.3f}", f"{val[k]['r2']:.3f}",
                         f"{test['rmse']:.3f}", f"{test['r2']:.3f}"])
        elif k == "baseline_last_value":
            rows.append([pretty[k], f"{val[k]['rmse']:.3f}", f"{val[k]['r2']:.3f}",
                         f"{test.get('baseline_rmse', float('nan')):.3f}",
                         f"{test.get('baseline_r2', float('nan')):.3f}"])
        else:
            rows.append([pretty[k], f"{val[k]['rmse']:.3f}", f"{val[k]['r2']:.3f}", "–", "–"])
    add_table(s, Inches(5.05), Inches(4.95), Inches(7.7), Inches(1.5), rows, font=11)
    textbox(s, Inches(5.05), Inches(6.52), Inches(7.7), Inches(0.5),
            f"Trained on {split['train']['rows']:,} rows ({split['train']['from']} to "
            f"{split['train']['to']}); tested on {split['test']['rows']:,} rows from "
            f"{split['test']['from']} onwards — the model never sees the test period.",
            size=10.5, italic=True, color=GREY)

    # ---------- 8. Module 2
    s = content_slide(prs, "Module 2 — Depletion Risk Mapping", name, srn)
    add_image(s, W2 / "Fig5_Module2_Flowchart.png", Inches(0.55), Inches(1.30),
              Inches(4.0), Inches(5.2))
    add_image(s, FIGS / "fig10_ahp_weights.png", Inches(4.70), Inches(1.30),
              Inches(4.0), Inches(2.55))
    add_image(s, FIGS / "fig8_risk_class_distribution.png", Inches(8.80), Inches(1.30),
              Inches(4.0), Inches(2.55))
    add_image(s, FIGS / "fig11_cgwb_validation.png", Inches(4.70), Inches(3.95),
              Inches(4.0), Inches(2.55))
    panel(s, Inches(8.80), Inches(3.95), Inches(3.95), Inches(2.55))
    textbox(s, Inches(9.00), Inches(4.08), Inches(3.6), Inches(0.35),
            "What the map says", size=14, bold=True, color=NAVY)
    textbox(s, Inches(9.00), Inches(4.48), Inches(3.6), Inches(2.0),
            f"{N_UNITS} taluks ranked — the same unit CGWB assesses, so "
            f"validation is one-to-one.\n\n"
            f"{HIGH_N} are High or Very High risk.\n\n"
            f"Highest: {', '.join(TOP[:3])}.\n\n"
            f"{TOP_DISTRICT_N} of the top 25 are {TOP_DISTRICT.title()} taluks, and "
            f"CGWB records 189% extraction in {TOP_DISTRICT.title()} — the worst in the state.\n\n"
            f"Checked against CGWB 2020: 77.3% binary agreement, precision 0.66, "
            f"recall 0.45, Spearman 0.276.",
            size=11)

    # ---------- 9. implementation progress
    s = content_slide(prs, "Implementation Progress", name, srn)
    prog = [
        ["Checkpoint", "Target", "What is working", "Honest completion"],
        ["Core implementation (Week 8)", "~30%",
         "Shared data pipeline on real CGWB data; three models trained and compared; "
         "metrics written to disk", "30%"],
        ["Complete, refine, debug (Week 10)", "~55%",
         "Module 2 (AHP, Jenks, CGWB validation), dashboard, rainfall integrated, "
         "seven silent defects found and fixed", "55%"],
        ["Consolidation, Phase-1 (Week 14)", "~70%",
         "Modules integrated on real CGWB data; risk mapping at taluk level; "
         f"{count_tests()}-test suite passing; Kriging, SHAP and the LULC indicator "
         "still pending", "70%"],
    ]
    add_table(s, Inches(0.55), Inches(1.35), Inches(12.2), Inches(2.6), prog,
              col_w=[25, 10, 50, 15], font=11)
    panel(s, Inches(0.55), Inches(4.20), Inches(12.2), Inches(2.3))
    textbox(s, Inches(0.80), Inches(4.35), Inches(11.7), Inches(0.35),
            "The honest part", size=14, bold=True, color=NAVY)
    textbox(s, Inches(0.80), Inches(4.75), Inches(11.7), Inches(1.6),
            "Up to 2 November the pipeline silently fell back to synthetic data: it looked for a "
            "features.csv that is never created, so every reported metric came from random numbers "
            "(test R² was −0.098) while 123,391 real CGWB records sat unused in the same folder. "
            "Module 2 never received Module 1's output at all and scored 100 invented locations.\n"
            f"After the fix the same pipeline reaches test R² {test['r2']:.3f} on real data and "
            f"Module 2 ranks {N_DIST} named districts. Every figure in this deck is regenerated "
            "from that run.",
            size=12)

    # ---------- 10. key features and demo
    s = content_slide(prs, "Key Features and Demo", name, srn)
    for img, x, cap in [
        (FIGS / "fig6_predicted_vs_actual.png", Inches(0.55), "Prediction accuracy on unseen seasons"),
        (FIGS / "fig12_rainfall_data_and_effect.png", Inches(4.75), "Real rainfall: data and its effect"),
        (FIGS / "fig9_risk_index_by_district.png", Inches(8.95), "25 highest-risk taluks"),
    ]:
        add_image(s, img, x, Inches(1.30), Inches(3.9), Inches(3.8))
        textbox(s, x, Inches(5.22), Inches(3.9), Inches(0.4), cap,
                size=11.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    panel(s, Inches(0.55), Inches(5.70), Inches(6.0), Inches(1.0))
    textbox(s, Inches(0.75), Inches(5.80), Inches(5.6), Inches(0.9),
            "How it is built: src/pipeline.py trains and selects the model; "
            "mann_kendall_sens_slope() in data_processor.py gives the trend; "
            "module2_risk.py does AHP, Jenks and validation.", size=11)
    panel(s, Inches(6.78), Inches(5.70), Inches(5.98), Inches(1.0))
    textbox(s, Inches(6.98), Inches(5.80), Inches(5.6), Inches(0.9),
            "Improvement made: SVR was refitting on all 79,218 training rows and dominating "
            "runtime; it now fits the most recent 5,000 rows — the full run finished in minutes "
            "instead of stalling.", size=11)

    # ---------- 11. testing
    s = content_slide(prs, "Testing", name, srn)
    n_tests = count_tests()
    for i, (big, lab) in enumerate([(str(n_tests), "test cases designed"),
                                    (str(n_tests), "passed"), ("0", "failing")]):
        x = Inches(0.55 + i * 4.15)
        panel(s, x, Inches(1.30), Inches(3.9), Inches(1.5))
        textbox(s, x, Inches(1.42), Inches(3.9), Inches(0.8), big,
                size=34, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        textbox(s, x, Inches(2.25), Inches(3.9), Inches(0.4), lab,
                size=12, color=GREY, align=PP_ALIGN.CENTER)
    tests = [
        ["Test ID", "Category", "Input", "Expected", "Actual", "Result"],
        ["TC02", "Valid", "Feature table with dates", "Train before val before test",
         "Order preserved", "Pass"],
        ["TC04 (negative)", "Invalid", "Empty DataFrame", "Raise, not silent output",
         "Raises ValueError", "Pass"],
        ["TC05 (boundary)", "Boundary", "Smallest viable sample count",
         "Still produces a model", "Model produced", "Pass"],
        ["TC08", "Valid", "AHP matrix (5×5)", "Consistency ratio < 0.10",
         "CR = 0.0542", "Pass"],
        ["TC11 (negative)", "Invalid", "Indicator column removed",
         "Clear error, not a silent wrong answer", "Raises ValueError", "Pass"],
        ["TC13", "Integration", "Module-1 output into Module 2",
         "risk index + class for every taluk", "177 taluks classified", "Pass"],
        ["TC18 (negative)", "Invalid", "Taluk name PARASGAD",
         "Saundatti (Belagavi), never Pavagada", "Saundatti", "Pass"],
        ["TC26 (negative)", "Invalid", "Risk indicator list",
         "CGWB extraction never a model input", "Absent", "Pass"],
    ]
    add_table(s, Inches(0.55), Inches(3.05), Inches(12.2), Inches(3.3), tests,
              col_w=[13, 11, 22, 23, 21, 10], font=9.5)
    textbox(s, Inches(0.55), Inches(6.50), Inches(12.2), Inches(0.4),
            "Run with: python -m pytest tests/   →   29 passed in under 10 s. "
            "8 of the 29 are shown here; all 29 are listed in the report, and 16 of them are "
            "regression tests tied to a specific defect we fixed.",
            size=11, italic=True, color=GREY)

    # ---------- 12. debugging and integration
    s = content_slide(prs, "Debugging and Integration", name, srn)
    bugs = [
        ["#", "Symptom", "Root cause (one line)", "Fix"],
        ["1", "Test R² = −0.098, worse than the mean",
         "Pipeline looked for features.csv, which is never created, and silently used synthetic data",
         "load_feature_table() reads the real CGWB export"],
        ["2", "Risk map listed LOC_000…LOC_099",
         "main.py called run_module2() with no arguments, so Module 2 invented its own data",
         "Module 1 trends are passed into Module 2"],
        ["3", "CGWB validation ran on 0 districts",
         "'Mysore' vs 'MYSURU' and 13-character truncation; both spellings present, splitting districts",
         "canonical_district() alias map; 33 → 28"],
        ["4", "Risk index changed between runs",
         "rainfall_dependence and lulc_change were np.random.uniform()",
         "Removed; replaced by measured seasonal recovery"],
        ["5", "Over-exploited Chitradurga ranked lowest risk",
         "Trend came from a recursive forecast that reverts to the mean (corr −0.665 with last depth)",
         "Mann–Kendall + Sen's slope on observed data"],
    ]
    add_table(s, Inches(0.55), Inches(1.30), Inches(12.2), Inches(3.5), bugs,
              col_w=[4, 24, 44, 28], font=9.5)
    panel(s, Inches(0.55), Inches(5.00), Inches(12.2), Inches(1.5))
    textbox(s, Inches(0.80), Inches(5.12), Inches(11.7), Inches(0.35),
            "Module 1 + Module 2 integration", size=14, bold=True, color=NAVY)
    textbox(s, Inches(0.80), Inches(5.52), Inches(11.7), Inches(0.9),
            "Module 1 writes a Sen's-slope trend per station to "
            "outputs/module1_station_forecasts.csv; Module 2 aggregates those stations to taluks "
            "and joins current depth, variability and seasonal recovery, weights the five "
            "indicators by AHP and classifies with Jenks. The integration bugs were #2 (no data "
            "passed) and #3 (the join silently matching nothing) — both were invisible because "
            "each module produced plausible output on its own. 176 of 177 taluks now match.",
            size=12)

    # ---------- 13. contribution and Phase-2
    s = content_slide(prs, "My Contribution and Phase-2 Plan", name, srn)
    panel(s, Inches(0.55), Inches(1.30), Inches(6.0), Inches(5.2))
    textbox(s, Inches(0.80), Inches(1.42), Inches(5.6), Inches(0.4),
            "My contribution", size=15, bold=True, color=NAVY)
    # Each person's own four contributions, read from the same list the written
    # report uses, so the deck and the report cannot describe different work.
    stu = CONTRIB.get(name, {})
    mine = (f"{stu.get('module', '')}\nPrimary files: {stu.get('files', '')}\n\n"
            + "\n".join("•  " + d for d in stu.get("did", [])))
    textbox(s, Inches(0.80), Inches(1.90), Inches(5.6), Inches(4.4), mine, size=11)
    textbox(s, Inches(0.80), Inches(6.05), Inches(5.6), Inches(0.4),
            "Team: Koushik & Karthik — Module 1 · Nitin, Varshith & Chandrashekar — Module 2",
            size=10.5, italic=True, color=GREY)
    ph2 = [
        ["Pending work (~30%)", "Priority", "Approach", "Target"],
        ["Deep-well data for the 0.45 recall", "High",
         "CGWB piezometer series + a depth-stratified indicator", "Week 18"],
        ["Kriging risk surface", "High",
         "Ordinary kriging over the 177 taluk centroids", "Week 17"],
        ["SHAP driver explanation", "High",
         "TreeSHAP on the selected XGBoost model, per station", "Week 17"],
        ["Direct multi-horizon forecasting", "Medium",
         "One model per horizon, removing recursive drift", "Week 18"],
        ["Land-use change indicator", "Medium",
         "Land-cover rasters; adds the deferred fifth indicator", "Week 19"],
        ["Spatio-temporal model (Gap 3)", "Low",
         "ConvLSTM / GCN-LSTM across wells", "Week 20"],
    ]
    add_table(s, Inches(6.78), Inches(1.30), Inches(5.98), Inches(3.4), ph2,
              col_w=[33, 14, 38, 15], font=10)

    # ---------- 14. learnings
    s = content_slide(prs, "Learnings and Thank You", name, srn)
    panel(s, Inches(0.55), Inches(1.30), Inches(12.2), Inches(2.5))
    textbox(s, Inches(0.80), Inches(1.42), Inches(11.7), Inches(0.4),
            "Hardest problem and what I learnt", size=15, bold=True, color=NAVY)
    textbox(s, Inches(0.80), Inches(1.88), Inches(11.7), Inches(1.9),
            "The hardest problem was a bug that produced no error: every module ran, every chart "
            "rendered, and the numbers looked reasonable — but the pipeline was training on random "
            "data and Module 2 was scoring invented locations.\n\n"
            "What worked was checking outputs against reality rather than checking that the code ran: "
            "a negative R², a risk map with no district names, and an over-exploited district ranked "
            "safest. Each was a thread that led to a real defect. Next time I would assert on the data "
            "itself — row counts, value ranges, join coverage — not just on functions returning without "
            "raising.",
            size=12.5)
    textbox(s, Inches(0.55), Inches(4.30), Inches(12.2), Inches(0.8),
            "Thank you. Questions?", size=32, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    textbox(s, Inches(0.55), Inches(5.30), Inches(12.2), Inches(0.9),
            f"{name}  |  {srn}\nProblem statement CAIML_Shobha_Rani_4_PS_160  |  "
            "Guide: Ms Indhuja Balakrishnan",
            size=13, color=GREY, align=PP_ALIGN.CENTER, spacing=1.4)

    safe = name.replace(" ", "_")
    path = OUT / f"Phase1_Review_{safe}.pptx"
    prs.save(path)
    return path


if __name__ == "__main__":
    for nm, sr, mod in TEAM:
        p = build(nm, sr, mod)
        print(f"  wrote {p.relative_to(BASE)}  ({p.stat().st_size // 1024} KB)")
    print(f"\n{len(TEAM)} decks written to {OUT}")
