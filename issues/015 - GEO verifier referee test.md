---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Referee test — score both GEO verifiers against the 14 documented maneuvers

**Goal:** settle the Tim-vs-Randy dispute with data: does the altitude verifier (with a lag-aware timing window) or the inclination verifier catch more of the 14 externally documented GEO maneuvers in `06 Code/ground_truth.csv`?

**Done when:** a table lands in `RESULTS - Beyond Starlink.md` (replacing the DISPUTED callout) scoring, for each of the 14 documented GEO events: (a) altitude verifier with the original ±3-day window, (b) altitude verifier with a window widened to cover the measured catalog lag (up to ±10 days), (c) inclination verifier — caught / missed for each. Plus one honest paragraph: which explanation of the SES miss survived (altitude-blindness, timing window, both, or neither), and what the external-safe GEO sentence now is. If the events' GP_HISTORY doesn't reach back far enough for some rows, say so per row instead of dropping them silently.

**Notes:** the ground-truth set is the referee precisely because neither author built it for this fight — but note only 7 of its rows survived Randy's own double-sourcing (`RESULTS - Ground Truth.md`); weight verified rows above assumed ones. Both sides already agree the longitude-drift column is dead — it stays retired regardless of outcome. This card outranks 003 (larger-n hardening): verification correctness underpins every number we quote.
