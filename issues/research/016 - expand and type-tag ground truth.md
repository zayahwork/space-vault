---
status: open
type: AFK
owner: Randy (research)
blocked-by: []
---
# Expand the ground-truth set and tag maneuver types

**Goal:** the referee dataset gets bigger and smarter: more documented events, every row tagged by maneuver type, so the verifier comparison (issue 015, tech lane) can say WHICH kinds of burns each observable catches.

**Done when:** `ground_truth.csv` reaches 30+ rows with LEO coverage grown to 15+ documented events (Starlink/OneWeb deorbits, reboosts, relocations from press, filings, McDowell GCAT, Space-Track reentry records); every row carries a `maneuver_type` column (NS-stationkeeping / EW-stationkeeping / relocation / reboost / deorbit / anomaly-quiet); every row still marked verified/assumed with double-sourced rows flagged; and `RESULTS - Ground Truth.md` gains a per-type summary table (events per type, caught/missed where scoreable).

**Notes:** the Galaxy 15 finding (a quiet-anomaly type that no jump-detector can catch) is exactly why the type column matters — count how many documented events are "quiet" types and say what fraction of the insurer story depends on quiet.py. WebSearch works; WebFetch doesn't — use Python urllib. Contact no one.
