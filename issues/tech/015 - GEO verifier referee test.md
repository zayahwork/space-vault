---
status: done
type: AFK
owner: Tim (tech)
blocked-by: []
closed: 2026-07-22
closed-by: tim
---
# Referee test — score both GEO verifiers against the 14 documented maneuvers

**Goal:** settle the Tim-vs-Randy dispute with data: does the altitude verifier (with a lag-aware timing window) or the inclination verifier catch more of the 14 externally documented GEO maneuvers in `06 Code/ground_truth.csv`?

**Done when:** a table lands in `RESULTS - Beyond Starlink.md` (replacing the DISPUTED callout) scoring, for each of the 14 documented GEO events: (a) altitude verifier with the original ±3-day window, (b) altitude verifier with a window widened to cover the measured catalog lag (up to ±10 days), (c) inclination verifier — caught / missed for each. Plus one honest paragraph: which explanation of the SES miss survived (altitude-blindness, timing window, both, or neither), and what the external-safe GEO sentence now is. If the events' GP_HISTORY doesn't reach back far enough for some rows, say so per row instead of dropping them silently.

**Notes:** the ground-truth set is the referee precisely because neither author built it for this fight — but note only 7 of its rows survived Randy's own double-sourcing (`RESULTS - Ground Truth.md`); weight verified rows above assumed ones. Both sides already agree the longitude-drift column is dead — it stays retired regardless of outcome. This card outranks 003 (larger-n hardening): verification correctness underpins every number we quote.

---

## ✅ Closed 2026-07-22 — Randy's timing explanation won; my altitude-blindness mechanism is refuted. Table live in `RESULTS - Beyond Starlink.md`

**Scoreboard** (each event judged against its own era- and cadence-matched null bar from abandoned GEO/ID drifters):

| measurement | all 14 | double-sourced 6 |
|---|---|---|
| altitude ±3d (as shipped) | 10/14 | 2/6 |
| altitude −3/+10d (lag-aware) | 12/14 | 4/6 |
| **altitude −3/+14d (lag-aware)** | **13/14** | **5/6** |
| inclination ±3d | 8/14 | 2/6 |
| inclination −3/+14d | 9/14 | 3/6 |

- **My mechanism was wrong.** I wrote that N–S station-keeping was invisible to an altitude verifier "by construction, not by bad luck." AMC 11's three documented N–S burns move fitted altitude 0.84/1.23/3.00 km at 2.0×/3.3×/6.0× their own bars, and the verifier catches all three **as shipped, inside ±3 days**. Altitude beats inclination at every window width. `verify_geo.py`'s stated reason for existing goes with it; it survives as a secondary channel because it uniquely catches MEV-2 inside ±3d, not as the replacement I built it to be.
- **Randy's timing mechanism is confirmed, with two corrections to his prescription.** (1) The window must be **asymmetric** — catalog lateness runs one way, and a symmetric ±14d credits MEV-2 and Intelsat 1002 with inclination steps landing **12.3 days *before*** the docking, at 5.2×/5.0× the bar. His literal `WINDOW_DAYS = 3.0 → 14.0` would introduce that. (2) **±10d is one day short**: Intelsat 33e's 29.87 km step lands at **+10.98d**; the CSV rounds that lag to 10. At −3/+14d it comes in at 74× bar.
- **Galaxy 15 is not a catch at any window, which corrects Randy too.** `RESULTS - Ground Truth` scores its 2.15 km step at 5× a modern-era bar. Against 2010-era drifters tracked at its own cadence the noise floor is **1.68–2.20 km** — the step is 1.0× the bar, inside the noise. Nothing burned; the rhythm stopped. Second independent piece of evidence for `quiet.py`. (Intelsat 33e, by contrast, *is* a real late signal and is caught at −3/+14d — the earlier "both are quiet.py territory" reading was wrong.)
- **SES: neither explanation survives.** All seven documented SES events are caught by the verifier exactly as shipped (+0.3 to +2.4d lag) and AMC 18 stays silent, so the ±3-day window was never SES's constraint. The live SES no-signal is still unexplained; suspicion moves to `detect.py`'s GEO suspect selection — untested hypothesis, not a finding.
- Per-row data quality: no row lacked GP_HISTORY (thinnest: Galaxy 15, 53 records / 1.1 per day). One row (AMC-9 2017-11-13) had no cadence-matched drifter that season and is scored against a widened match, marked `widened` in the output; its 8.3× verdict does not depend on it. AMC 18 silent in every column at every window incl. ±14d — widening did not break the one true negative (n=1: a check, not a false-positive rate). MEV-1 excluded (own transit contaminates its window). 6 verdicts flip between max-bar and 99th-pct bar, all listed in the run output; no headline depends on them.
- **The CSV has 7 double-sourced rows but only 6 are scoreable** — MEV-1 is one of the 7 and is excluded. Scored the 6.
- Harness: `referee_geo.py` + `_test_referee.py` (53 cases, incl. asserting step-math identity with the shipped `verify.py`/`verify_geo.py`, and that the lag-aware windows really are one-sided). DISPUTED callout replaced; contradicted claims struck per the standing rule.
- Follow-up: issue 018 — **filed twice, by two agents, under the same number**. Both specs corrected to −3/+14d asymmetric; Zayah to pick one and renumber or close the other.
