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

## ✅ Closed 2026-07-22 — Randy's timing explanation won; the table is live in `RESULTS - Beyond Starlink.md`

**Scoreboard** (each event judged against its own era- and cadence-matched null bar from abandoned GEO/ID drifters):

| measurement | all 14 | double-sourced 6 |
|---|---|---|
| altitude ±3d (as shipped) | 10/14 | 2/6 |
| **altitude ±10d (lag-aware)** | **12/14** | **4/6** |
| inclination ±3d | 8/14 | 2/6 |
| inclination ±10d | 8/14 | 2/6 |

- The two events ±10d rescues (MEV-2, Intelsat 1002) had their catalog step land **+5.6 / +5.2 days** after the event — measured lag, exactly Randy's mechanism. The altitude-blindness theory is refuted: N–S burns move fitted altitude 0.8–3.0 km and altitude beats inclination at every window width.
- Galaxy 15 and Intelsat 33e are missed by **every** column — both are "operator lost control" events with no burn to find; that's `quiet.py` territory, noted honestly in the RESULTS file.
- No row lacked GP_HISTORY (thinnest: Galaxy 15, 53 records). AMC 18 (documented non-maneuverer) stayed silent in all four columns; MEV-1 excluded (own transit contaminates its window). 3 verdicts flip between max-bar and 99th-pct bar; headline unaffected.
- Harness: `referee_geo.py` + `_test_referee.py` (45 cases, incl. asserting step-math identity with the shipped `verify.py`/`verify_geo.py`). DISPUTED callout replaced; contradicted claims struck per the standing rule.
- Follow-up filed: issue 018 (widen the shipped verifier's GEO window to ±10d).
