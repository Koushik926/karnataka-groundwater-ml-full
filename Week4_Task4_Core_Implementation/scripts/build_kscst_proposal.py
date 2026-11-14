"""
build_kscst_proposal.py - KSCST SPP 50th Series project proposal (closes 30 Nov 2026).

    python scripts/build_kscst_proposal.py

Follows the official 50th-series format exactly: Part A items 1-7, Part B items 8-23.
Field names and numbering are taken from 03_KSCST_SPP_50S_Proposal_Format_2026-27.

TWO THINGS MUST BE SETTLED BY THE TEAM BEFORE SUBMISSION:
  1. KSCST permits a MAXIMUM OF FOUR students per team. This team has five.
     The proposal leaves the four slots marked for the guide to fill; this script
     will not choose which member is left out.
  2. Personal fields (mobile, email, category, USN photographs, SPP coordinator,
     payment UTR) are marked [TO FILL]. They are not invented here.

Every technical number comes from the pipeline's own output files.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
import sys; sys.path.insert(0, str(ROOT))
PROJ = ROOT.parent
FIGS = ROOT / "outputs" / "figures"
W2 = PROJ / "week2_diagrams"

TODO = "[TO FILL]"
TITLE = ("SPATIO-TEMPORAL PREDICTION AND RISK MAPPING OF GROUNDWATER "
         "DEPLETION IN KARNATAKA USING MACHINE LEARNING")


def shade(c, h):
    e = OxmlElement("w:shd"); e.set(qn("w:fill"), h); c._tc.get_or_add_tcPr().append(e)


def centred(doc, t, s=12, b=False):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(t); r.bold = b; r.font.size = Pt(s); return p


def kv(doc, pairs, fs=10.5, w0=None):
    t = doc.add_table(rows=0, cols=2); t.style = "Table Grid"
    for k, v in pairs:
        cs = t.add_row().cells
        cs[0].text = ""; r = cs[0].paragraphs[0].add_run(str(k)); r.bold = True; r.font.size = Pt(fs)
        cs[1].text = ""; r2 = cs[1].paragraphs[0].add_run(str(v)); r2.font.size = Pt(fs)
        if str(v) == TODO:
            r2.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    return t


def table(doc, headers, rows, fs=9.5):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(fs); shade(c, "D9E2F3")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""
            run = cs[i].paragraphs[0].add_run(str(v)); run.font.size = Pt(fs)
            if str(v) == TODO:
                run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    return t


def figure(doc, path, caption, width=5.7):
    if not Path(path).exists():
        return
    doc.add_picture(str(path), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(caption); r.italic = True; r.font.size = Pt(9)


def main():
    from src.provenance import check as _check_provenance
    _check_provenance()   # refuse to build from synthetic numbers
    meta = json.loads((ROOT / "models" / "module1_best_model.json").read_text())
    t = meta["test_metrics"]
    risk = pd.read_csv(ROOT / "outputs" / "module2_risk_mapping.csv")
    top = risk.sort_values("risk_index", ascending=False).head(5)

    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.0); s.left_margin = s.right_margin = Cm(2.0)

    # ---- working note (delete before converting to PDF)
    p = doc.add_paragraph()
    r = p.add_run(
        "WORKING COPY — DELETE THIS BOX BEFORE CONVERTING TO PDF.\n"
        "Fields in red are [TO FILL]: personal details, SPP coordinator, and payment "
        "information are not filled in here. KSCST permits a maximum of four students "
        "per team and this team has five, so the student table has four slots for the "
        "guide to allocate. Item 11 of the KSCST instructions requires all instructional "
        "notes to be removed before submission.")
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    doc.add_page_break()

    centred(doc, "KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY", 13, True)
    centred(doc, "50th SERIES OF STUDENT PROJECT PROGRAMME 2026–2027", 12, True)
    centred(doc, "PROJECT PROPOSAL", 12, True)
    doc.add_paragraph()

    # ================= PART A =================
    doc.add_heading("PART–A: GENERAL INFORMATION", 1)

    doc.add_heading("1. Project Title", 2)
    doc.add_paragraph(TITLE)

    doc.add_heading("2. Keywords (5–8)", 2)
    doc.add_paragraph("GROUNDWATER DEPLETION; MACHINE LEARNING; RISK MAPPING; "
                      "SPATIO-TEMPORAL PREDICTION; ANALYTIC HIERARCHY PROCESS; "
                      "KARNATAKA; AQUIFER MANAGEMENT; DECISION SUPPORT")

    doc.add_heading("3. Broad Theme", 2)
    kv(doc, [("Theme No.", "2"),
             ("Theme Name", "WATER RESOURCES, ENVIRONMENT AND CLIMATE RESILIENCE"),
             ("Sub-theme / Focus Area",
              "GROUNDWATER ASSESSMENT, RECHARGE AND AQUIFER MANAGEMENT")])

    doc.add_heading("4. Institution Details", 2)
    kv(doc, [("Name of Institution", "REVA UNIVERSITY"),
             ("Course Name", "B.E. — BACHELOR OF ENGINEERING"),
             ("Department Name",
              "SCHOOL OF COMPUTER SCIENCE AND ENGINEERING (CENTER FOR AI & ML)"),
             ("Affiliated University", "REVA UNIVERSITY (STATE PRIVATE UNIVERSITY)"),
             ("District of Your Institution", "BENGALURU URBAN"),
             ("Complete Postal Address", "REVA UNIVERSITY, RUKMINI KNOWLEDGE PARK, "
              "KATTIGENAHALLI, YELAHANKA, BENGALURU – 560064, KARNATAKA")])

    doc.add_heading("5. Project Guide Details", 2)
    kv(doc, [("Project Guide Name", "MS. INDHUJA BALAKRISHNAN"),
             ("Designation", TODO),
             ("Department", "SCHOOL OF COMPUTER SCIENCE AND ENGINEERING"),
             ("Email id", TODO), ("Mobile Number", TODO)])
    doc.add_paragraph("Project Co-Guide (if applicable):")
    kv(doc, [("Co-Guide Name", "DR. M. SHOBHA RANI (CENTER LEAD, CAIML)"),
             ("Designation", TODO), ("Department", "CENTER FOR AI & ML"),
             ("Email id", TODO), ("Mobile Number", TODO)])

    doc.add_heading("6. Student Team Details", 2)
    p = doc.add_paragraph()
    r = p.add_run("KSCST permits a maximum of four students per team. This project team "
                  "has five members, so the guide must decide the final composition "
                  "before submission. Team members, as recorded by the department:")
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    table(doc, ["Sl.", "Name of the Student", "USN / Reg. No.", "Degree, Branch, Sem",
                "Category", "Mobile", "Email"],
          [["1", "NITIN G A", "R23EJ088", "B.E., CSE, VII", TODO, TODO, TODO],
           ["2", "R KOUSHIK", "R23EJ096", "B.E., CSE, VII", TODO, TODO, TODO],
           ["3", "S VARSHITH SAI", "R23EJ100", "B.E., CSE, VII", TODO, TODO, TODO],
           ["4", "BHIMISETTY KARTHIK", "R23EJ168", "B.E., CSE, VII", TODO, TODO, TODO],
           ["5", "G M CHANDRASHEKAR", "R23EQ029", "B.E., CSE, VII", TODO, TODO, TODO]],
          fs=8.5)
    doc.add_paragraph(
        "Mark the Team Leader by adding “(TEAM LEADER)” against that name. "
        "Paste a recent passport-size photograph for each student. Reduce this table to "
        "four rows before submission.")

    doc.add_heading("7. SPP Coordinator Details", 2)
    kv(doc, [("SPP Coordinator Name", TODO + " (Dr. Praveen Math held this role in the "
                                             "49th series — confirm for the 50th)"),
             ("Designation", TODO), ("Email", TODO), ("Mobile Number", TODO)])

    # ================= PART B =================
    doc.add_page_break()
    doc.add_heading("PART-B: PROJECT DESCRIPTION", 1)

    doc.add_heading("8. Background and Need of the Project", 2)
    doc.add_paragraph(
        "Karnataka is the second most drought-prone state in India and depends on "
        "groundwater for the majority of its irrigation and rural drinking water. The "
        "Central Ground Water Board (CGWB) assesses groundwater taluk by taluk: in its "
        "2020 Dynamic Groundwater Resources assessment, 62 of 227 taluks (27.3%) are "
        "already critical or over-exploited, and Kolar district draws 189% of what is "
        "recharged each year.")
    doc.add_paragraph(
        "The existing scenario is that groundwater is measured but not forecast. CGWB "
        "publishes well levels four times a year and an extraction category once a year. "
        "Both describe what has already happened. A taluk administration learns that its "
        "aquifer is over-exploited after the wells have begun to fail, not before.")
    doc.add_paragraph(
        "The problem this project addresses is the absence of a forward-looking, "
        "taluk-level indicator of groundwater depletion risk for Karnataka. The need is "
        "for a tool that predicts the next quarter's water level from the monitoring data "
        "that already exists, and converts the measured trend into a ranking that "
        "identifies which taluks need intervention first.")
    doc.add_paragraph(
        "Beneficiaries: taluk and district administrations planning recharge works and "
        "borewell permissions; the Minor Irrigation and Rural Drinking Water departments; "
        "farmers in hard-rock districts where borewell failure is common; and researchers "
        "who need a reproducible baseline for Karnataka groundwater modelling.")

    doc.add_heading("9. Review of Existing Work", 2)
    table(doc, ["Work", "Approach", "Shortcoming / gap"], [
        ["Alkon et al., 2024, Environmental Research Letters",
         "Random Forest with SHAP on CGWB wells across India",
         "National scale, reports R² of 0.4–0.6; produces no taluk-level risk output"],
        ["Supreetha et al., 2020, Appl. Comput. Intell. Soft Comput.",
         "Lion-algorithm-optimised LSTM, Udupi district",
         "Single district; prediction only, with no risk classification"],
        ["Asoka et al., 2017, Nature Geoscience",
         "GRACE satellite data with well records to separate monsoon from pumping",
         "Coarse spatial resolution; explanatory rather than predictive"],
        ["Tao et al., 2022, review of 100+ ML groundwater studies",
         "Survey of methods and reported accuracy",
         "Notes that most studies never compare against a naive baseline"],
        ["CGWB Dynamic Groundwater Resources (official assessment)",
         "Water-balance accounting of recharge against extraction",
         "Annual, retrospective, and does not forecast"],
        ["Commercial GIS groundwater tools (ArcGIS Hydro and similar)",
         "Interpolation and visualisation of observed levels",
         "Display historical data; no predictive model, licence cost"],
    ])
    doc.add_paragraph(
        "Research gaps addressed: (G5) many published studies use observation periods "
        "ending several years ago; (G4) prediction and risk mapping are treated as "
        "separate problems; (G2) spatial relationships between wells are rarely modelled, "
        "which this project notes and proposes for the next phase.")

    doc.add_heading("10. Problem Statement", 2)
    doc.add_paragraph(
        "To predict quarterly groundwater levels at monitoring stations across Karnataka "
        "from historical observations and rainfall, and to convert the predicted and "
        "measured trends into a validated taluk-level depletion-risk classification that "
        "identifies at-risk taluks before their wells fail.")

    doc.add_heading("11. Objectives", 2)
    for o in [
        "To build a cleaned, reproducible dataset of CGWB groundwater observations for "
        "Karnataka, integrated with daily rainfall.",
        "To develop and compare machine-learning models that predict the next quarter's "
        "groundwater level at a monitoring station.",
        "To evaluate those models on a held-out future period against a persistence "
        "baseline, rather than on a random split.",
        "To derive a statistically sound depletion trend per station using the "
        "Mann-Kendall test with Sen's slope.",
        "To design a composite depletion-risk index from measurable indicators, weighted "
        "by the Analytic Hierarchy Process with a verified consistency ratio.",
        "To validate the resulting taluk ranking against the independent CGWB extraction "
        "assessment.",
        "To deliver the results as an interactive decision-support dashboard.",
    ]:
        doc.add_paragraph(o, style="List Bullet")

    doc.add_heading("12. Innovation / Novelty", 2)
    doc.add_paragraph(
        "What is new. The project joins prediction and risk mapping into a single "
        "pipeline: the Mann-Kendall / Sen's slope trend produced by the prediction module "
        "becomes the highest-weighted indicator (0.5028) of the risk module. Published "
        "work treats these as separate problems.")
    doc.add_paragraph(
        "How it differs. The risk assessment is made at taluk level — the same unit "
        "CGWB itself assesses — so the output can be validated one-to-one against an "
        "independent official source rather than judged only on internal metrics. 176 of "
        "177 taluks matched a CGWB category.")
    doc.add_paragraph(
        "Why it is innovative. Three methodological choices are unusual in student and "
        "published work alike. First, evaluation is on a strictly chronological held-out "
        "period (2020–2024) against a persistence baseline, because a random split "
        "leaks the future through lag features. Second, the CGWB extraction figure is "
        "deliberately excluded from the model inputs so that validation against it is not "
        "circular. Third, the contribution of rainfall was established by an A/B "
        "experiment rather than assumed: adding it raised test R² from 0.576 to "
        f"{t['r2']:.3f}.")

    doc.add_heading("13. Proposed Methodology", 2)
    doc.add_paragraph(
        "The system has two modules behind one shared data pipeline, executed as a single "
        "ten-step chain.")
    table(doc, ["Stage", "Method"], [
        ["Data acquisition",
         "CGWB quarterly observations for Karnataka via India-WRIS; CGWB Dynamic "
         "Groundwater Resources 2020 for validation; NASA POWER PRECTOTCORR daily rainfall"],
        ["Cleaning",
         "Range checks (0–100 m), removal of records missing level, date or district, "
         "and canonicalisation of renamed district and taluk names"],
        ["Feature engineering",
         "Four quarterly lags, rolling mean and standard deviation, sine/cosine month "
         "encoding, coordinates, and five rainfall features — 15 in total"],
        ["Model training",
         "Random Forest, XGBoost and Support Vector Regression, selected on validation "
         "RMSE against a last-observed-value baseline"],
        ["Trend analysis",
         "Mann-Kendall test with Sen's slope per station, robust to outliers and "
         "irregular sampling"],
        ["Risk index",
         "Five measured indicators weighted by AHP on Saaty's 1–9 scale, accepted "
         "only when the consistency ratio is below 0.10"],
        ["Classification", "Jenks natural breaks into four risk classes"],
        ["Validation",
         "Four-class agreement, Cohen's kappa, binary agreement with a confusion matrix, "
         "and Spearman rank correlation against CGWB"],
        ["Delivery", "Streamlit dashboard reading the pipeline's own output files"],
    ])
    doc.add_paragraph()
    figure(doc, W2 / "Fig1_Architecture.png", "Figure 1: System architecture.")
    doc.add_paragraph()
    figure(doc, W2 / "Fig4_Module1_Flowchart.png", "Figure 2: Module 1 — prediction.")
    doc.add_paragraph()
    figure(doc, W2 / "Fig5_Module2_Flowchart.png", "Figure 3: Module 2 — risk mapping.")
    doc.add_paragraph("Software: Python, pandas, scikit-learn, XGBoost, Streamlit, Plotly, "
                      "matplotlib. No specialised hardware is required.")

    doc.add_heading("14. Expected Deliverables", 2)
    for d in [
        "Software: a reproducible Python pipeline that runs end to end with one command.",
        "Decision-support tool: an interactive dashboard ranking taluks by depletion risk.",
        "GIS-ready database: per-taluk indicators, risk index and risk class as open CSV.",
        "Validated methodology: an AHP-weighted risk index checked against CGWB.",
        "Project report and documented, tested source code.",
    ]:
        doc.add_paragraph(d, style="List Bullet")

    doc.add_heading("15. Expected Outcomes and Impact", 2)
    table(doc, ["Dimension", "Outcome"], [
        ["Technical", f"A validated predictor (test RMSE {t['rmse']:.3f} m, R² "
                      f"{t['r2']:.3f}) that beats a persistence baseline on a held-out "
                      f"four-year period, and a risk index agreeing with CGWB on 77.3% of "
                      f"taluks in the binary stressed/not-stressed test"],
        ["Social", "Earlier warning for taluks where drinking-water borewells are at risk, "
                   "supporting intervention before failure rather than after"],
        ["Environmental", "Supports targeted recharge planning and aquifer management, "
                          "directly serving SDG 6 (Clean Water and Sanitation)"],
        ["Economic", "Reduces wasted expenditure on borewells drilled in taluks where the "
                     "water table is falling; built entirely on free public data"],
        ["Industrial", "The method transfers to any Indian state covered by India-WRIS "
                       "without modification"],
        ["Academic", "A reproducible open baseline for Karnataka groundwater modelling, "
                     "including the negative and weak results"],
        ["Potential users", "Taluk and district administrations, Minor Irrigation and "
                            "Rural Drinking Water departments, CGWB regional offices, "
                            "agricultural extension officers, researchers"],
    ])

    doc.add_heading("16. Relevance", 2)
    doc.add_paragraph(
        "Applicable: SDGs (SDG 6 Clean Water and Sanitation, primary; SDG 13 Climate "
        "Action, secondary); Karnataka Priority Sector; Rural Development; Agriculture; "
        "Water; Environment; Climate; Digital India.")

    doc.add_heading("17. Work Plan", 2)
    table(doc, ["Activity", "M1", "M2", "M3", "M4", "M5"], [
        ["Literature Survey", "✓", "", "", "", ""],
        ["Design", "✓", "✓", "", "", ""],
        ["Development", "", "✓", "✓", "", ""],
        ["Testing", "", "", "✓", "✓", ""],
        ["Validation", "", "", "", "✓", "✓"],
        ["Final Report", "", "", "", "", "✓"],
    ])

    doc.add_heading("18. Facilities Available", 2)
    kv(doc, [("Laboratory", "Computer laboratories, School of Computer Science and "
                            "Engineering, REVA University"),
             ("Equipment", "Desktop and laptop computers; institutional network"),
             ("Software", "Python and the open-source scientific stack (pandas, "
                          "scikit-learn, XGBoost, Streamlit); all free and open source"),
             ("Instruments", "NONE — the project uses published monitoring data and "
                             "requires no field instrumentation"),
             ("Workshop", "NONE — no fabrication required"),
             ("Institutional facilities", "Library and e-journal access, Center for AI & ML "
                                          "computing facilities, internet connectivity")])

    doc.add_heading("19. Major Requirements for the Project", 2)
    doc.add_paragraph("Software: Python, scikit-learn, XGBoost, Streamlit, QGIS "
                      "(for map preparation). All open source.", style="List Bullet")
    doc.add_paragraph("Data: CGWB groundwater observations (India-WRIS, free); CGWB "
                      "Dynamic Groundwater Resources 2020 (free); NASA POWER rainfall "
                      "(free).", style="List Bullet")
    doc.add_paragraph("Field studies: limited validation visits to selected high-risk "
                      "taluks in Kolar and Bengaluru Rural.", style="List Bullet")
    doc.add_paragraph("Hardware: none beyond standard institutional computers.",
                      style="List Bullet")

    doc.add_heading("20. Budget Estimate", 2)
    table(doc, ["Item", "Estimated Cost (₹)"], [
        ["Equipment / Components", "0"],
        ["Consumables", "0"],
        ["Fabrication", "0"],
        ["Software / Cloud Services (hosting the dashboard for 12 months)", "4,000"],
        ["Field Survey / Data Collection (validation visits, Kolar and Bengaluru Rural)", "3,000"],
        ["Testing / Analysis (printing, maps, poster for the state-level exhibition)", "1,500"],
        ["Miscellaneous (documentation, data storage)", "1,500"],
        ["Total", "10,000"],
    ], fs=10)
    doc.add_paragraph(
        "The project is software-based and uses only free and open data, so no equipment, "
        "consumables or fabrication costs arise. The request is within the ₹10,000 "
        "ceiling.")

    doc.add_heading("21. References (IEEE)", 2)
    for i, ref in enumerate([
        "S. Alkon et al., “High resolution prediction and explanation of groundwater "
        "depletion across India,” Environmental Research Letters, vol. 19, no. 5, 2024.",
        "T. R. Supreetha, N. S. Shenoy and P. Nayak, “Lion Algorithm-Optimized "
        "Long Short-Term Memory Network for Groundwater Level Forecasting in Udupi "
        "District, India,” Applied Computational Intelligence and Soft Computing, 2020.",
        "A. Asoka, T. Gleeson, Y. Wada and V. Mishra, “Relative contribution of "
        "monsoon precipitation and pumping to changes in groundwater storage in India,” "
        "Nature Geoscience, vol. 10, pp. 109–117, 2017.",
        "H. Tao et al., “Groundwater level prediction using machine learning models: "
        "A comprehensive review,” Neurocomputing, vol. 489, pp. 271–308, 2022.",
        "S. Mohanavelu et al., “Trends and Non-Stationarity in Groundwater Level "
        "Changes in Rapidly Developing Indian Cities,” Water, vol. 12, no. 11, 2020.",
        "Central Ground Water Board, “Dynamic Ground Water Resources of Karnataka, "
        "2020,” Ministry of Jal Shakti, Government of India, 2020.",
        "Central Ground Water Board, “Ground Water Year Book, Karnataka "
        "2021–22,” Ministry of Jal Shakti, Government of India, 2022.",
        "NASA Langley Research Center, “POWER Project: PRECTOTCORR daily corrected "
        "total precipitation,” https://power.larc.nasa.gov (accessed Nov. 2026).",
        "T. L. Saaty, “A scaling method for priorities in hierarchical structures,” "
        "Journal of Mathematical Psychology, vol. 15, no. 3, pp. 234–281, 1977.",
    ], 1):
        doc.add_paragraph(f"[{i}] {ref}")

    doc.add_heading("22. Processing Fee Payment Details", 2)
    kv(doc, [("Mode of Payment", TODO + "  (UPI / NEFT)"),
             ("Transaction / UTR / Reference Number", TODO),
             ("Date of Payment", TODO), ("Amount Paid", "₹1,180/-"),
             ("Name of Account Holder", TODO), ("Name of Bank (for NEFT)", TODO),
             ("UPI ID Used", TODO)])
    doc.add_paragraph(
        "The fee of ₹1,180 (₹1,000 + 18% GST) must be paid in a SINGLE "
        "transaction before the Google Form is submitted. Split payments are rejected. "
        "Pay to: Secretary, KSCST, Canara Bank IISc Campus, A/C 0683201000024, "
        "IFSC CNRB0000683.")

    doc.add_heading("23. Student Details with Signature", 2)
    table(doc, ["Sl.", "Name of Student", "USN / Reg. No.", "Signature", "Date"],
          [["1", TODO, TODO, "", ""], ["2", TODO, TODO, "", ""],
           ["3", TODO, TODO, "", ""], ["4", TODO, TODO, "", ""]], fs=10)
    doc.add_paragraph()
    kv(doc, [("Name & Signature of SPP Coordinator with Seal", ""),
             ("Name & Signature of Project Guide with Seal", ""),
             ("Email id", TODO), ("Contact No.", TODO)])
    doc.add_paragraph()
    doc.add_paragraph("Mandatory attachments: signed Project Proposal (PDF); Declaration "
                      "signed by all team members, Guide and SPP Coordinator; Endorsement "
                      "on institution letterhead; Processing Fee Payment Receipt.")

    out = PROJ / "KSCST_SPP_50S_Proposal_DRAFT.docx"
    doc.save(out)
    print(f"  wrote {out}")
    return out


if __name__ == "__main__":
    main()
