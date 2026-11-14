"""
provenance.py - refuse to build a document from numbers that are not real.

Every report, deck and brief in this project reads models/module1_best_model.json.
If that file was ever produced by a synthetic run, the documents would state
metrics no real run produced - which is the mistake that made the Week 4 and
Week 5 reports wrong. One call at the top of each builder prevents it.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REAL = "CGWB"


def check(model_json: Path | None = None) -> dict:
    """Return the model metadata, or raise if it did not come from real data."""
    path = model_json or ROOT / "models" / "module1_best_model.json"
    if not path.exists():
        raise RuntimeError(
            f"{path} is missing. Run `python -m src.main` before building documents."
        )
    meta = json.loads(path.read_text())
    src = str(meta.get("data_source", ""))
    if REAL not in src:
        raise RuntimeError(
            f"Refusing to build a document: {path.name} records data_source="
            f"{src!r}, which is not the real CGWB data. Re-run `python -m src.main`."
        )
    return meta
