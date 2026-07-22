---
status: open
type: AFK
owner: Randy (research)
priority: 1
blocked-by: []
---
# Pre-build the quiet detector's exam (before it wakes up Jul 29)

**Goal:** when `quiet.py` produces its first verdicts (~Jul 29, the day before the broker meeting), they land as a GRADED result — "caught X of Y known-dead satellites, Z false alarms on known-healthy ones" — not raw output. This also produces the company's first measurable false-positive rate: documented non-events don't exist for maneuvers, but they DO for "went quiet" (known-active, station-kept satellites are documented non-events).

**Done when:**
- A per-satellite **operational-status table** exists (`06 Code/quiet_exam.csv` + a note in `03 Reference/`) for the Intelsat, SES, and OneWeb fleets: status (active-stationkept / dead / abandoned / degraded / relocated), source (McDowell geotab status codes, operator fleet pages, ITU/FCC filings), and verified/assumed per row.
- Every one of the **44 objects with ≥3 spikes on record** has a **pre-registered expected verdict** written down BEFORE Jul 29: what quiet.py should say about it if it's working, based on documented status.
- A short scoring recipe: on Jul 29, compare quiet.py's verdicts to the table and report catch rate on known-dead + false-alarm rate on known-healthy, in one table.

**Notes:** this outranks 022 (operator disclosure map) — 022's findings partially fall out of this work anyway; finish this first. The known failure mode to watch for (from `_test_quiet.py`): "healthy satellite declared dead" — that's the worst output to hand a broker unscored, which is why the exam exists. Contact no one; WebSearch yes, WebFetch no (Python urllib).
