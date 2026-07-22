---
status: done
type: AFK
owner: Randy (research)
blocked-by: []
---
# Promote the five July 17–21 Starlink reentry rows when GCAT catches up

**Goal:** five reentry rows in `06 Code/ground_truth.csv` (NORAD 47404, 46340, 46557, 51794, 64137) are stuck at `assumed` only because McDowell's GCAT hadn't recorded the decays yet. Re-checked on 2026-07-22 night: GCAT `satcat.tsv` still shows all five as Status `O` with no decay date, so they could not promote. When GCAT updates, they become double-sourced.

**Done when:** GCAT `satcat.tsv` is re-queried (stream `https://planet4589.org/space/gcat/tsv/cat/satcat.tsv` with urllib and filter by NORAD — note `rcat.tsv` is the ROCKET catalog, not reentries); any row whose GCAT `DDate`/`Status R` matches Space-Track within a day flips to `evidence: verified`, `independent: yes` with source_2 updated; verified counts in `RESULTS - Ground Truth.md` (frontmatter box says 17) are updated to match; rows that still don't match stay `assumed` with the re-check date noted.

**Notes:** while in the CSV, also consider whether an `EW-stationkeeping` example can be found — the per-type table currently has zero documented east–west burns, which blocks the verifier comparison from scoring that type.

**Closed 2026-07-22 (night, issue 018).** Feedback loop run: `satcat.tsv` streamed fresh
from planet4589.org (19,010,777 bytes) and filtered by NORAD. **File stamp
`Updated 2026 Jul 17 2011:55` — byte-identical to the previous pull.** All five rows
(47404, 46340, 46557, 51794, 64137) still show Status `O` with no decay date, so
**0 of 5 promoted**; all stay `assumed`, with the re-check date and the correct source now
recorded in each row's `source_2`. Verified counts in `RESULTS - Ground Truth.md` were
checked and are unchanged at 17 — nothing promoted, so nothing to renumber.

Two side outcomes:
- **The `rcat` correction in this card is right, and the earlier reasoning was wrong.**
  Confirmed against GCAT's own catalog index: `rcat` is the *Suborbital Rocket
  (Exoatmospheric) Catalog*. The old "not in rcat" justification proved nothing; the CSV and
  RESULTS now cite `satcat.tsv`. The same mislabel still sits in
  `06 Code/groundtruth/gt_sources.py`, which is outside this lane's sparse-checkout scope —
  filed as **issue 019** rather than reached across lanes.
- **The EW-stationkeeping gap is closed to three rows** (Intelsat 1002, Astra 3B, AMC 11),
  found by signature: paired opposite-sign drift corrections ~1 day apart with inclination
  at noise. All three are caught. They are `assumed`, not documented — no operator publishes
  per-maneuver EW data — but they unblock the tech lane's verifier comparison for that type.
