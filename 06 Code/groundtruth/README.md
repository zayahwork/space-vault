# groundtruth/ — grading the detector against documented reality

Everything here exists to answer one question: **when a satellite really did manoeuvre, and
somebody else wrote it down, does our detector see it?**

Output lives in two places:
- `../ground_truth.csv` — 24 events, every row marked `verified` or `assumed`
- `../../RESULTS - Ground Truth.md` — the scoring and what it means

## Run it

```bash
cd "C:\Space\06 Code\groundtruth"
python gt_analyze.py all            # every number in the RESULTS doc
python gt_analyze.py noise-floor    # where the 0.42 km bar comes from
python gt_analyze.py score          # the caught/missed table
python gt_analyze.py lag            # are the misses absent, or just late?
python gt_analyze.py identity       # proves drift == altitude rescaled
```

Needs `../spacetrack_auth.json` (gitignored — never commit it). First run pulls from
Space-Track and planet4589.org into `cache/` and takes a few minutes; after that it's instant.

## The two rules that make this honest

**1. A source is only a second source if it doesn't derive from the first.** Trade press
restating a press release is not corroboration. A company announcement plus a government
tracking record is. Applying this dropped us from 15 verified rows to 7.

**2. Where we had to read the date out of the catalog, the row is `assumed`.** Our detector
reads the same catalog, so scoring against a date we took from it is close to circular. Those
rows are still useful — they just can't be quoted as validation.

The consequence, and the headline of the whole exercise: **on the 6 double-sourced events we
catch 2 (33%); across all 15 scoreable events we catch 11 (73%).** The gap is a selection
effect. Double-sourced events are anomalies — breakups, failures, dockings — which is exactly
what altitude-step detection handles worst. What we catch reliably (graveyard raises, routine
station-keeping) is never announced by anyone, so it can only ever be self-sourced.

## Traps already paid for — don't re-learn these

- **GCAT rows are phases, not objects.** `DDate` ends a phase; `Status` is the event that
  ended it (`N` = renamed, `DK` = docked, `R` = reentered, `E` = exploded). Reading the first
  row as "current" reports Galaxy 15 as decayed in 2006, when it was renamed. Use
  `gt_sources.gcat_phases()`, which returns all of them.
- **Longitude drift is not a second observable.** It's mean motion rescaled: 1 km of altitude
  = 0.0128°/day. Verified against a real burn to 1.2%. **Inclination is** genuinely
  independent — 7.5–8× separation on N-S station-keeping.
- **A missing GCAT match may just be data lag.** Check `gcat_updated()` before concluding
  McDowell disagrees. The five Starlink reentries in the CSV are `assumed` only because his
  `rcat.tsv` was last refreshed 2026-07-17 20:11 UTC, before they happened.
- **Space-Track decay records and operator ephemeris disagree by design.** When a satellite
  dies, the operator stops publishing SupGP — so our gap signal doesn't grow, it *vanishes*.

## Open follow-ups

- [ ] **Re-check `gcat_updated("rcat")` after ~2026-07-29.** If McDowell has caught up, the
      five Starlink reentries promote from `assumed` to `verified` for free.
- [ ] `WINDOW_DAYS` is 3.0 here to mirror `verify.py`. Prior art says that's too tight —
      Decoto & Loerch measured a mean 4-day lag, max 7. Re-run `score` at 14 and GEO goes
      71% → 86%. See `03 Reference/Prior Art - GEO Maneuver Detection.md`.
- [ ] No OneWeb ground truth exists at all — zero decay records in the window and no
      per-manoeuvre disclosure. That gap is currently unfixable from public sources.
