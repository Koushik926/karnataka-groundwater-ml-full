"""check_no_placeholders.py - refuse to ship a document that asks a human to fill it in.

    python scripts/check_no_placeholders.py        # exit 1 if anything is found

Run after every document build. A narrow word-list sweep missed
"[Add the specific parts you personally wrote before printing]" on deck slide 13,
so this matches the SHAPE of a placeholder - bracketed text containing an
instruction verb, or a run of underscores - rather than a list of known phrases.
"""
import glob, re, sys, zipfile
from pypdf import PdfReader
from pptx import Presentation

PAT = re.compile(
    # any bracketed run of prose carrying an instruction verb, at any length -
    # the first version capped each side at 120 characters and so walked past
    # "[Draft, assembled from what you actually did ... in your own words ...]"
    r"\[[^\]\n]{0,400}?\b(add|insert|your|fill|paste|enter|screenshot|rewrite|"
    r"draft|correct anything|tbd|todo|xx)\b[^\]\n]{0,400}?\]"
    r"|before printing|to be filled|fill in|fill after|paste here|insert here"
    r"|enter actual|enter your|add your|\bTODO\b|\bTBD\b|\[TO FILL\]"
    r"|lorem ipsum|_{4,}|xxxx", re.I)

def text_of(f):
    if f.endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
    if f.endswith(".pptx"):
        out = []
        for sl in Presentation(f).slides:
            for sh in sl.shapes:
                if sh.has_text_frame: out.append(sh.text_frame.text)
                if sh.has_table:
                    for r in sh.table.rows:
                        out.extend(c.text for c in r.cells)
        return "\n".join(out)
    if f.endswith(".docx"):
        z = zipfile.ZipFile(f)
        xml = "".join(z.read(n).decode("utf8", "ignore")
                      for n in z.namelist() if n.endswith(".xml"))
        return re.sub(r"<[^>]+>", " ", xml)
    return open(f, errors="ignore").read()

bad = 0
targets = (sorted(glob.glob("Phase1_Reports/**/*.pdf", recursive=True))
           + sorted(glob.glob("Phase1_Reports/**/*.docx", recursive=True))
           + sorted(glob.glob("Week4_Task4_Core_Implementation/presentation/decks/Phase1_*.pptx")))
for f in targets:
    try:
        hits = sorted(set(m.group(0).strip()[:70] for m in PAT.finditer(text_of(f))))
    except Exception as e:
        print("ERR", f, e); continue
    if hits:
        bad += len(hits)
        print(f"{f.split('/')[-1]:45s} {hits}")
print(f"\nscanned {len(targets)} files; placeholder hits: {bad}")
sys.exit(1 if bad else 0)
