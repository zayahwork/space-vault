---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Re-score the referee — ground truth grew from 16 to 19 GEO rows

**Goal:** issue 015's headline (altitude −3/+14d catches **13/14**, inclination 9/14) was
measured against 14 scoreable GEO events. `ground_truth.csv` has since gained three
single-sourced rows — **Astra 3B 2025-09-08, Intelsat 1002 2025-02-28, AMC 11 2025-06-10** —
so the set is now **17 scoreable**. The published ratio no longer matches the file it claims
to be scored against.

**Done when:** `python referee_geo.py` is re-run on the current CSV and the scoreboard in
`RESULTS - Beyond Starlink.md` (and the 015 card) is updated to x/17, with the per-event
table extended to the three new rows. If the rate moves, say so plainly rather than keeping
the nicer number.

**Notes:**
- The **double-sourced denominator is unchanged at 6**, so the 5/6 figure — the one that
  matters for anything external — should be unaffected. Verify that rather than assuming it.
- All three new rows are `1src`, i.e. the weak tier the 015 write-up already warns is close
  to tautological (catalog-dated events scored by a catalog-based detector). Adding them
  will likely *inflate* the all-scoreable rate. Do not let the headline drift upward on the
  strength of rows that carry the least evidence — quote 5/6 first.
- `_test_referee.py` no longer hardcodes the count (changed under issue 018) precisely so a
  data change fails loudly in the doc, not silently in the suite.
- Cheap: `referee_cache/` already holds the null-object history; only the three new events
  need fetching.
