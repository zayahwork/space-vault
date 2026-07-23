---
date: 2026-07-22
branch: randy
status: all work committed; safe to clear context and resume from this file
---

# 🔁 Handoff — where Randy's lane stands

Read this first after a context reset. Everything below is committed on branch `randy`.
Nothing has been merged to master; that's Zayah's call.

## What got built today (4 deliverables)

| file | what it is |
|---|---|
| `06 Code/ground_truth.csv` | **24 documented manoeuvres**, 16 GEO / 8 LEO. Every row marked `verified` (7) or `assumed` (17) |
| `RESULTS - Ground Truth.md` | The scoring, and the honest summary at the top |
| `03 Reference/Prior Art - GEO Maneuver Detection.md` | **7 published methods, cited** — written as Tim's shortcut for the GEO verifier |
| `06 Code/groundtruth/` | Runnable scripts that regenerate every number. See its README |

## The three findings that matter

1. **On double-sourced events we catch 2 of 6 (33%), not 73%.** The higher number is
   flattered by events we dated from the catalog ourselves. The gap is a selection effect:
   well-documented events are anomalies (breakups, failures, dockings) — exactly what
   altitude-step detection handles worst. **Quote 33% to anyone who matters.**

2. **We have no measured false-positive rate,** and this set can't produce one. Ground truth
   records things that *happened*; an FP rate needs documented non-events, which don't exist
   publicly. The ~1% is how the bar was set, not a result.

3. **The GEO hypothesis in `RESULTS - Beyond Starlink` is retracted** (a warning callout sits
   at the point it was stated). Altitude is *not* blind to GEO station-keeping, and longitude
   drift is altitude rescaled. **Why SES shows no signal is an open question again.**

## What's queued, in priority order

- [ ] **`WINDOW_DAYS` 3.0 → 14.0 in `verify.py`.** One constant, takes GEO 71% → 86%. Three
      independent sources say 3 days is below the field's known floor (we measured +10 days on
      Intelsat 33e; Decoto & Loerch measured mean 4 / max 7; Kelecy carries a lag term).
      **Tech lane — not mine to edit.**
- [ ] **Add inclination as a second verify channel.** Genuinely independent of altitude,
      7.5–8× separation on N-S station-keeping, from data we already pull. Decoto's paper
      already specifies how (CrossTrack = out-of-plane, Radial+InTrack = in-plane).
- [ ] **Re-open the SES question.** Its stated explanation is falsified and unreplaced.
- [ ] **After ~2026-07-29: re-run `gt_sources.gcat_updated("rcat")`.** If McDowell has caught
      up, five Starlink reentries promote `assumed` → `verified` for free.

## Standing constraints I'm working under

- Own worktree, own branch (`randy`). Never switch, merge, or push. Never touch master.
- Other agents' worktrees and branches are off limits — missing facts come via Zayah.
- Contact no one. All outreach is Marketing's lane.
- Separate **VERIFIED** (with source) from **SPECULATION** (labelled) in everything.

## Live context that may go stale

- **The Heldreth (Gallagher, Seattle) coffee email needed to go out Jul 22–23** to land a slot
  after `quiet.py` unlocks ~Jul 29. Marketing's to send — check whether it did.
- **The detector's scoreable window is 12 hours, not 2 days.** The catalog half of the archive
  starts at the `2026-07-22 0200Z` snapshot. This grows on its own; re-check before quoting.
- The Jul 22 SBIR window (**DOW SBIR Specific Topic 26.BX Release 4, closes Aug 18**) was
  never checked on DSIP. Still open as far as I know.
