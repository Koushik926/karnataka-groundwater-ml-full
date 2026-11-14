"""
build_evaluation_sheets.py - pre-fill the four official evaluation sheets per student.

    python scripts/build_evaluation_sheets.py

The circular of 04.11.2026 requires each student to bring printed Guide and Examiner
evaluation sheets for BOTH tracks - four sheets each, twenty for the team. This script
does not recreate those forms: it opens the university's own .docx files and types the
identification fields into them, so what prints is the official sheet.

Filled: Guide Name, Date (14.11.2026), Project Title, Program and Section, SRN,
Student Name.
Left blank, because they are not ours to write: Designation, Time, and every mark
column (a-e and Total).

Writes: Phase1_Reports/Evaluation_Sheets/<NAME>/*.docx
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import student_personal as P
PROJ = ROOT.parent
OUTDIR = PROJ / "Phase1_Reports" / "Evaluation_Sheets"

SRC = Path.home() / "Downloads" / \
    "Fw__Phase-1_Review_of_RIO_Internship_and_Major_Projects_templates"
FORMS = {
    "GuideEvaluation-Project-2026.docx": "Project — Guide",
    "ExaminerEvaluation-Project-2026.docx": "Project — Examiner",
    "GuideEvaluation-Internship-2026.docx": "Internship — Guide",
    "ExaminerEvaluation-Internship-2026.docx": "Internship — Examiner",
}

GUIDE = "Ms Indhuja Balakrishnan"
REVIEW_DATE = "14.11.2026"
TITLE = ("Spatio-Temporal Prediction and Risk Mapping of Groundwater Depletion in "
         "Karnataka Using Machine Learning  (CAIML_Shobha_Rani_4_PS_160)")

STUDENTS = [
    ("NITIN G A", "R23EJ088"),
    ("R KOUSHIK", "R23EJ096"),
    ("S VARSHITH SAI", "R23EJ100"),
    ("BHIMISETTY KARTHIK", "R23EJ168"),
    ("G M CHANDRASHEKAR", "R23EQ029"),
]


def set_cell(cell, text, size=None):
    """Write text into a table cell, keeping the cell's existing run formatting."""
    para = cell.paragraphs[0]
    if para.runs:
        para.runs[0].text = text
        for r in para.runs[1:]:
            r.text = ""
        if size:
            para.runs[0].font.size = size
    else:
        para.add_run(text)


def fill(src: Path, dst: Path, name: str, srn: str) -> None:
    doc = Document(str(src))

    # --- the "Guide Name: / Designation: / Date: / Time:" block lives in a text box,
    #     so reach it through the raw element tree rather than doc.paragraphs.
    for t in doc.element.body.iter(qn("w:t")):
        txt = t.text or ""
        if txt.strip().endswith("Name:") and GUIDE not in txt:
            t.text = txt + " " + GUIDE
        elif txt.strip() == "Date:":
            t.text = txt + " " + REVIEW_DATE

    # --- "Project Title:" paragraph
    for p in doc.paragraphs:
        if p.text.strip().startswith("Project Title:") and TITLE not in p.text:
            if p.runs:
                p.runs[-1].text = p.runs[-1].text + " " + TITLE
            else:
                p.add_run(" " + TITLE)
            break

    # --- the student row: Program and Section | SRN | Student Name | a..e | Total
    for tbl in doc.tables:
        hdr = [c.text.strip().lower() for c in tbl.rows[0].cells]
        if "srn" in hdr and "student name" in hdr and len(tbl.rows) > 1:
            row = tbl.rows[1]
            set_cell(row.cells[hdr.index("program and section")],
                     P.program_short(name))
            set_cell(row.cells[hdr.index("srn")], srn)
            set_cell(row.cells[hdr.index("student name")], name)
            break

    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dst))


if __name__ == "__main__":
    missing = [f for f in FORMS if not (SRC / f).exists()]
    if missing:
        raise SystemExit(
            f"Official forms not found in {SRC}\nMissing: {missing}\n"
            "Download the review e-mail attachments first - this script fills the "
            "university's own sheets rather than recreating them.")

    n = 0
    for name, srn in STUDENTS:
        folder = OUTDIR / name.replace(" ", "_")
        for form, label in FORMS.items():
            out = folder / f"{Path(form).stem}_{name.replace(' ', '_')}.docx"
            fill(SRC / form, out, name, srn)
            n += 1
        print(f"  {name:<20} 4 sheets -> {folder.relative_to(PROJ)}")
    print(f"\n{n} evaluation sheets written. Marks columns, Designation and Time are "
          f"left blank for the guide and examiner.")
