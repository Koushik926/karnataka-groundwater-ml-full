"""
action_briefs.py - turn the risk ranking into something a taluk officer can act on.

A ranking says which taluks are worst. It does not say what to do about them, and
that is the gap between a student project and an instrument an administration can
use. This module joins three things we already have:

    our measured trend      (is the water table falling, and how fast)
    our rainfall dependence (does recovery track the monsoon)
    CGWB's own water balance(how much is drawn against how much is extractable)

and produces, per taluk, a quantified deficit and a recommended intervention class
with the government programme that funds it.

The recommendation is a transparent rule, not a model. An officer can read the rule,
disagree with it, and see exactly which number drove the answer - which is what a
decision-support tool needs to allow.

Units: CGWB publishes in hectare-metres (ham). 1 ham = 10,000 cubic metres.
The state totals reconcile with CGWB's published 18.16 BCM annual recharge.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
HAM_TO_M3 = 10_000.0
# Jal Jeevan Mission service-level norm, used only to express a volume in
# human terms. Stated wherever it is used so the assumption is visible.
JJM_LPCD = 55.0
M3_PER_PERSON_YEAR = JJM_LPCD * 365 / 1000.0          # 20.075 m3

# Intervention classes. Each names the real programme that funds that kind of work.
INTERVENTIONS = {
    "recharge": dict(
        action="Supply-side recharge: check dams, percolation tanks and recharge "
               "shafts sited on the monsoon drainage lines",
        why="The water table is falling and recovery tracks the monsoon closely, so "
            "captured runoff reaches the aquifer.",
        scheme="MGNREGA water-conservation works; Atal Bhujal Yojana incentive "
               "component; Jal Shakti Abhiyan (Catch the Rain)"),
    "demand": dict(
        action="Demand-side regulation: notify the taluk under the Karnataka Ground "
               "Water Act, meter agricultural borewells, and shift cropping to the "
               "micro-irrigation package",
        why="The water table is falling but recovery does not track rainfall, so more "
            "recharge alone will not close the gap - extraction has to come down.",
        scheme="Karnataka Ground Water (Regulation and Control of Development and "
               "Management) Act, 2011; Pradhan Mantri Krishi Sinchayee Yojana "
               "(per-drop-more-crop)"),
    "investigate": dict(
        action="Deep-aquifer investigation: install piezometers below the shallow "
               "monitored zone and meter existing deep borewells",
        why="CGWB records over-extraction but the monitored shallow water table is "
            "flat, which means the stress is in a deeper aquifer we cannot see.",
        scheme="CGWB aquifer mapping (NAQUIM); Atal Bhujal Yojana monitoring component"),
    "watch": dict(
        action="Early warning: keep the taluk on the quarterly watch list and review "
               "borewell permissions against the trend",
        why="Extraction is within the recharge budget today, but our measured trend "
            "shows the water table falling.",
        scheme="Routine CGWB/State Ground Water Directorate monitoring"),
    "stable": dict(
        action="No intervention indicated. Maintain routine monitoring.",
        why="Extraction is within budget and the water table is stable or recovering.",
        scheme="Routine monitoring"),
}


def _norm(s):
    return str(s).strip().upper().replace("-", " ").replace(".", "")


def load_water_balance() -> pd.DataFrame:
    """Per-taluk water balance from the CGWB 2020 assessment, in ham."""
    p = ROOT / "data" / "raw" / "karnataka_gw_extraction_2020.csv"
    e = pd.read_csv(p)
    e.columns = [c.strip() for c in e.columns]
    cols = {
        "recharge": "Total annual groundwater recharge",
        "extractable": "Annual Extractable Groundwater Resource",
        "extraction": "Total Annual Extraction",
        "future": "Net GW availability for future",
        "stage": "Stage of GW extraction (%)",
    }
    out = pd.DataFrame({"Taluk": e["Taluk"].map(_norm),
                        "District": e["Name of District"].map(_norm)})
    for k, c in cols.items():
        out[k] = pd.to_numeric(e[c], errors="coerce")
    out["deficit"] = out["extraction"] - out["extractable"]
    logger.info("Water balance for %d taluks; state recharge %.2f BCM",
                len(out), out["recharge"].sum() * HAM_TO_M3 / 1e9)
    return out


def recommend(row) -> str:
    """Which intervention class this taluk falls into. A readable rule, by design."""
    over = row["deficit"] > 0
    falling = row["sl"] > 0.02           # Sen's slope, m/yr, depth increasing
    stable = abs(row["sl"]) <= 0.02
    monsoon_fed = row["rdep"] > 0.20     # recovery correlates with monsoon rainfall

    if over and falling and monsoon_fed:
        return "recharge"
    if over and falling and not monsoon_fed:
        return "demand"
    if over and stable:
        return "investigate"
    if over:                              # over-extracted and recovering
        return "investigate"
    if falling:
        return "watch"
    return "stable"


def build(risk_csv: Path | None = None) -> pd.DataFrame:
    """Join our risk output to CGWB's water balance and recommend an action."""
    risk_csv = risk_csv or ROOT / "outputs" / "module2_risk_mapping.csv"
    r = pd.read_csv(risk_csv)
    r["_t"], r["_d"] = r["Taluk"].map(_norm), r["District"].map(_norm)

    wb = load_water_balance().rename(columns={"Taluk": "_t", "District": "_d"})
    m = r.merge(wb.drop(columns=["_d"]), on="_t", how="left")

    m = m.rename(columns={"decline_rate": "sl", "rainfall_dependence": "rdep"})
    m["intervention"] = m.apply(
        lambda x: recommend(x) if pd.notna(x["deficit"]) else "stable", axis=1)
    m["action"] = m["intervention"].map(lambda k: INTERVENTIONS[k]["action"])
    m["rationale"] = m["intervention"].map(lambda k: INTERVENTIONS[k]["why"])
    m["funding_route"] = m["intervention"].map(lambda k: INTERVENTIONS[k]["scheme"])

    m["deficit_m3"] = m["deficit"].clip(lower=0) * HAM_TO_M3
    m["people_equiv"] = m["deficit_m3"] / M3_PER_PERSON_YEAR

    out = ROOT / "outputs" / "taluk_action_briefs.csv"
    keep = ["Taluk", "District", "risk_label", "risk_index", "sl", "rdep",
            "current_depth", "stage", "recharge", "extractable", "extraction",
            "deficit", "deficit_m3", "people_equiv", "intervention", "action",
            "rationale", "funding_route"]
    m[[c for c in keep if c in m.columns]].to_csv(out, index=False)
    logger.info("Action briefs -> %s", out)
    return m


def state_summary(m: pd.DataFrame, wb: pd.DataFrame) -> dict:
    """Headline figures, computed from CGWB's own published numbers."""
    over = wb[wb["deficit"] > 0]
    total_def_m3 = float(over["deficit"].sum() * HAM_TO_M3)
    return {
        "taluks_assessed_cgwb": int(len(wb)),
        "taluks_overdrawn": int(len(over)),
        "overdraft_m3": total_def_m3,
        "overdraft_bcm": total_def_m3 / 1e9,
        "people_equiv": total_def_m3 / M3_PER_PERSON_YEAR,
        "state_recharge_bcm": float(wb["recharge"].sum() * HAM_TO_M3 / 1e9),
        "state_extraction_bcm": float(wb["extraction"].sum() * HAM_TO_M3 / 1e9),
        "counts": m["intervention"].value_counts().to_dict(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    wb = load_water_balance()
    m = build()
    s = state_summary(m, wb)
    print(f"\nKarnataka, CGWB 2020 assessment")
    print(f"  recharge            {s['state_recharge_bcm']:.2f} BCM")
    print(f"  extraction          {s['state_extraction_bcm']:.2f} BCM")
    print(f"  taluks overdrawn    {s['taluks_overdrawn']} of {s['taluks_assessed_cgwb']}")
    print(f"  annual overdraft    {s['overdraft_bcm']:.3f} BCM "
          f"({s['overdraft_m3']:,.0f} m3)")
    print(f"  = annual domestic supply for {s['people_equiv']/1e6:.1f} million people "
          f"at the JJM norm of {JJM_LPCD:.0f} lpcd")
    print(f"\nrecommended interventions across our {len(m)} ranked taluks:")
    for k, v in sorted(s["counts"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:12s} {v:3d}   {INTERVENTIONS[k]['action'][:60]}...")
