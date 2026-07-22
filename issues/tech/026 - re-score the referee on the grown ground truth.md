---
status: done
type: AFK
owner: Tim (tech)
blocked-by: []
closed: 2026-07-22
closed-by: tim
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

---

## ✅ Closed 2026-07-22 — re-scored on 17 rows; headline number held where it matters

`referee_geo.py` re-run on the current CSV (17 scoreable, up from 14). New scoreboard:

| measurement | all 17 | double-sourced 6 |
|---|---|---|
| altitude ±3d | 13/17 | 2/6 |
| **altitude −3/+14d** | **16/17** | **5/6** |
| inclination −3/+14d | 9/17 | 3/6 |

- **The double-sourced 5/6 did not move** — that is the number quoted externally, and it is
  the point of this card: the all-scoreable rate rose 13/14 → 16/17 purely on the three new
  **single-sourced** rows, the weak tier. RESULTS now leads with 5/6 and flags the 16/17 as
  leaning on weak evidence, so the headline can't drift upward on the cheapest rows.
- **All three new rows are east-west station-keeping and all three are caught on altitude at
  ±3d** (Intelsat 1002 42×, Astra 3B 43×, AMC 11 7×; lag <1 day). E-W burns move fitted
  altitude 15–21 km — a third strike against the altitude-blindness hypothesis 015 already
  refuted, this time on the *other* GEO burn type.
- Updated: `RESULTS - Beyond Starlink.md` (table extended to 17, scoreboard, external-safe
  sentence, test count 53→55). 015's closed record keeps its 14-row numbers with a pointer
  to this re-score. Run saved to `output/referee_026.json`.
- Whole suite green (referee 55, window 36). No code changed — data-only re-run, as filed.
