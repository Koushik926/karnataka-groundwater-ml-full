"""
student_personal.py - the personal fields no script can derive.

One place for everything that is a fact about a person rather than a fact about
the project: section, contact links, coding-platform evidence, certification,
self-ratings. Every document builder imports from here, so a detail typed once
appears correctly on both reports, both decks and the four evaluation sheets.

To update: edit the dict, then re-run
    python scripts/build_phase1_reports.py
    python scripts/build_internship_reports.py
    python scripts/build_evaluation_sheets.py
    python presentation/build_review_deck.py
    python presentation/build_internship_deck.py

An empty string prints a ruled line to be completed in pen. That is the correct
value for anything not yet true - do not put a plausible placeholder in a
document that is signed as the student's own work.

SELF-RATINGS (1-5, baseline from the Week-1 self-check -> now). These were set
from what each person demonstrably built during Weeks 1-7, at the team's request.
They are a judgement, not a measurement: read your own row before you sign it and
change any number that does not match your Week-1 self-check.
"""
from __future__ import annotations

RULED = ""   # prints a ruled line

# Order of the five areas in internship report 2.1 and deck slide 5.
AREAS = ["Data structures and algorithms", "Operating systems", "DBMS",
         "Computer networks", "Assigned tech stack"]

PERSONAL: dict[str, dict] = {
 "NITIN G A": dict(
    mock_improve='Explain the AHP consistency ratio before quoting the weights, so the weighting is seen to be checked rather than asserted; and be able to state the placeholder-indicator defect, how it was caught and what now prevents it.',
    section="B", branch="CSIT",                       # blank = the document omits the line entirely
    # baseline -> now
    ratings={"Data structures and algorithms": (2, 4),
             "Operating systems": (2, 3),
             "DBMS": (2, 3),
             "Computer networks": (2, 3),
             "Assigned tech stack": (2, 4)},
    # rows of the 1.3 technology-stack table this student worked in directly
    stack_strong={"Data handling", "Machine learning"}),

 "R KOUSHIK": dict(
    mock_improve='State the persistence baseline before the model result, so the comparison lands first; and explain the chronological split and the rainfall A/B test as the reason the scores can be trusted, rather than opening with R2.',
    section="B", branch="CSIT",
    ratings={"Data structures and algorithms": (3, 4),
             "Operating systems": (2, 3),
             "DBMS": (3, 4),
             "Computer networks": (2, 4),
             "Assigned tech stack": (2, 4)},
    stack_strong={"Machine learning", "Data sources", "Testing"}),

 "S VARSHITH SAI": dict(
    mock_improve='Lead with why relative Jenks classes cannot align with absolute CGWB thresholds before quoting 23.9%; and give the 0.45 recall as a hydrogeological limit with the depth figures, not as a weakness to be excused.',
    section="B", branch="CSIT",
    ratings={"Data structures and algorithms": (3, 4),
             "Operating systems": (2, 3),
             "DBMS": (3, 4),
             "Computer networks": (2, 3),
             "Assigned tech stack": (2, 4)},
    stack_strong={"Data handling", "Testing"}),

 "BHIMISETTY KARTHIK": dict(
    mock_improve='Give the two cleaning rules separately - 76 out of range and 165 missing - instead of the single total of 241; and explain the 33-to-28 district canonicalisation from the alias table rather than in general terms.',
    section="C", branch="CSIT",
    ratings={"Data structures and algorithms": (3, 4),
             "Operating systems": (2, 3),
             "DBMS": (3, 4),
             "Computer networks": (2, 3),
             "Assigned tech stack": (2, 4)},
    stack_strong={"Language / data", "Data handling"}),

 "G M CHANDRASHEKAR": dict(
    mock_improve='Demonstrate the dashboard reading outputs/ live rather than describing it; and be ready to trace any number on screen back to the file that produced it.',
    section="A", branch="ISE",
    ratings={"Data structures and algorithms": (3, 3),
             "Operating systems": (3, 4),
             "DBMS": (3, 4),
             "Computer networks": (2, 4),
             "Assigned tech stack": (2, 4)},
    stack_strong={"Visualisation", "Delivery", "Version control / tooling"}),
}

# Programme names behind the section codes the students gave (CSIT B, CSIT-C,
# ISE A). Not every member is in the same programme, so the title page, the
# "Program and Section" row and the evaluation sheets all read this.
BRANCH = {
    "CSIT": dict(long="Computer Science and Information Technology",
                 short="CSIT",
                 school="School of Computer Science and Engineering"),
    "ISE":  dict(long="Information Science and Engineering",
                 short="ISE",
                 school="School of Computer Science and Engineering"),
    "CSE":  dict(long="Computer Science and Engineering",
                 short="CSE",
                 school="School of Computer Science and Engineering"),
}

# ---------------------------------------------------------------- contact data
# Contact details live in student_personal_local.py, which is NOT in git: the
# repository is public and four of these people are not its owner, so their
# e-mail, LinkedIn and resume links are theirs to publish rather than mine.
# Without that file every contact field is empty - field() then prints a ruled
# line and has() reports False, so the documents still build, with the personal
# fields left blank. Contact keys are deliberately absent from PERSONAL above.
try:
    from student_personal_local import CONTACT
except ImportError:                                 # fresh clone
    CONTACT = {}

for _name, _d in PERSONAL.items():
    for _k in ("email", "linkedin", "github", "resume", "platform"):
        _d.setdefault(_k, CONTACT.get(_name, {}).get(_k, RULED))

# ---------------------------------------------------------------- Week 7
# RIO Schedule & Assessment Rubric, Part A row SL 7 (12 Oct 2026): "Stakeholder /
# Mentor Requirement Review & Mock Technical Interview". The date below is that
# scheduled date, cited as such. The mock-interview SCORE is deliberately left
# ruled: it comes off the signed feedback sheet, and an examiner may ask to see it.
WEEK7_DATE = "12 October 2026 (RIO schedule, SL 7)"
MOCK1_TOPICS = ("Core fundamentals (DSA, OS, DBMS, CN) and the assigned tech stack, "
                "plus a walk-through of my module")
# The Week-7 round was assessed qualitatively, not scored out of a total. These are
# the points actually recorded at the session; no number is invented to fill the cell.
MOCK1_SCORE = (
    "Assessed qualitatively, not scored out of a total. Points recorded: present the "
    "literature as a comparison table rather than bullets; state the research gap and say "
    "which module addresses it; show the system architecture and both module diagrams; put "
    "a legend and the data value on every chart; never show a bare number without its "
    "source.")
CAPSTONE_MOCK = "Scheduled — Week 15 (7 December 2026)"

# Default level for each row of the 1.3 technology-stack table; a row named in a
# student's stack_strong set is lifted to the second form.
STACK_LEVEL_DEFAULT = {
    "Language / data":            ("basic", "confident"),
    "Data handling":              ("basic", "working"),
    "Machine learning":           ("none", "working"),
    "Deep learning (benchmark)":  ("none", "aware"),
    "Data sources":               ("none", "working"),
    "Visualisation":              ("basic", "working"),
    "Delivery":                   ("none", "working"),
    "Testing":                    ("none", "working"),
    "Documentation":              ("none", "working"),
    "Version control / tooling":  ("basic", "working"),
}


def rating(name: str, area: str) -> tuple[str, str]:
    """('3', '4') for the two rating columns, or two ruled lines if unset."""
    r = PERSONAL[name]["ratings"].get(area)
    return (str(r[0]), str(r[1])) if r else ("______", "______")


def stack_level(name: str, layer: str) -> str:
    """'basic -> confident' for the 1.3 'My level at start -> now' column."""
    lo, hi = STACK_LEVEL_DEFAULT.get(layer, ("none", "working"))
    if layer in PERSONAL[name]["stack_strong"]:
        hi = "confident"
    return f"{lo} → {hi}"


def field(name: str, key: str, width: int = 24) -> str:
    """A personal field, or a ruled line of the given width if it is not set."""
    v = PERSONAL[name].get(key, RULED)
    return v if v else "_" * width


def _branch(name: str) -> dict:
    return BRANCH[PERSONAL[name].get("branch", "CSE")]


def program(name: str) -> str:
    """'B.Tech, Computer Science and Information Technology — Semester VII, Section B'"""
    b = _branch(name)
    sec = PERSONAL[name].get("section", RULED)
    sec = f"Section {sec}" if sec else "Section " + "_" * 6
    return f"B.Tech, {b['long']} — Semester VII, {sec}"


def program_short(name: str) -> str:
    """'B.Tech CSIT — VII Sem, Sec B' for the evaluation sheets and deck footers."""
    b = _branch(name)
    sec = PERSONAL[name].get("section", RULED)
    tail = f", Sec {sec}" if sec else ""
    return f"B.Tech {b['short']} — VII Sem{tail}"


def school(name: str) -> str:
    return _branch(name)["school"]


def has(name: str, key: str) -> bool:
    """True when a personal field is set. A field that is not set is omitted from
    the document altogether rather than printed as a blank to fill in."""
    return bool(PERSONAL[name].get(key))
