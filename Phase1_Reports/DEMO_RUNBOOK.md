# "Can you run it here?" — the runbook

All three commands were run end to end on 14 November 2026 and work. The risk
is not the code; it is the laptop you present from.

---

## The one-time setup (do this BEFORE you leave)

Everything below needs a virtual environment. The system Python on Koushik's Mac
is missing xgboost, pytest and torch, so `python -m src.main` fails with
`ModuleNotFoundError` if you forget this step.

```
cd Week4_Task4_Core_Implementation
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Takes well under a minute. Then always run through `.venv/bin/python`, never
through bare `python3`.

**Do this on whichever laptop you present from, today, before 1:30.**
If a teammate's laptop is not set up, present from one that is — the examiner
cares that it runs, not whose machine it runs on.

---

## The three commands, fastest first

### 1. Tests — 8 seconds, show this first

```
.venv/bin/python -m pytest tests/ -q
```

Expect: `29 passed` in under 10 seconds — about 4 s once warm, 8 s on a cold start.

This is the safest thing to run. It is short, it cannot half-work, and it backs
the testing slide directly.

### 2. Dashboard — instant, this is the real demo

```
.venv/bin/python -m streamlit run dashboard.py
```

Opens on <http://localhost:8501>. Three views: the taluk risk map, per-station
forecasts, and the CGWB validation.

**Have it already running in a browser tab before you walk in.** Launching it
live costs 10–15 seconds of silence and can pop a firewall prompt.

If asked where a number on screen comes from: it is read from `outputs/` at run
time, so it is whatever the last pipeline run produced. Nothing on that page is
typed in.

### 3. Full pipeline — about 30 seconds

```
.venv/bin/python -m src.main
```

Measured at **29.7 s** on an M-series Mac. It rebuilds everything from the raw
CGWB export and reprints the metrics at the end, so it proves the numbers in
your report are reproducible rather than asserted.

Verified on this run: test RMSE **3.136**, R² **0.632**, **177** taluks,
**176** matched to CGWB. Exactly the figures in the report.

Only offer this if you have the time for it. 30 seconds of a scrolling log is a
long silence if you are not narrating it.

---

## What to say while each runs

- **Tests:** "29 tests — functional, boundary and negative for both modules, one
  end-to-end integration test, and 16 regression tests each tied to a defect we
  actually fixed."
- **Dashboard:** "It reads `models/` and `outputs/` at run time, so it cannot
  drift from the code. The old version had the metrics typed into the source and
  went stale after every run — that is the defect this design removes."
- **Pipeline:** "This is rebuilding everything from the raw CGWB export. The
  numbers it prints at the end are the numbers in my report."

---

## If something breaks

| What you see | What it means | Say this, then move on |
|---|---|---|
| `ModuleNotFoundError: xgboost` | You ran system `python3`, not the venv | "I'm on the wrong interpreter" — re-run with `.venv/bin/python` |
| `streamlit: command not found` | Same cause | Use `.venv/bin/python -m streamlit run dashboard.py` |
| Port 8501 in use | A dashboard is already running | Add `--server.port 8502` |
| Dashboard map blank | Plotly version mismatch | The version shim handles 5.24 and 7.x; refresh once |
| A test fails | Something genuinely changed | Do not argue with it. "That's a real failure, I'll take the trace and fix it" is a better answer than a guess |

**If the laptop refuses entirely:** the reports contain the evidence. Section 3.5
has the dashboard screenshots, section 4.1 has the full 29-test table with the
actual results, and section 4.4 has the CGWB validation. Hand over the printed
report and talk from it. A demo that fails and is handled calmly costs less than
a demo that is faked.

---

## Never do these

- Do not run `pip install` in front of an examiner.
- Do not open the code and edit it to make something work.
- Do not claim a number the run did not just print. If the screen disagrees with
  your report, say so and investigate after — that is the whole point of the
  provenance guard.
