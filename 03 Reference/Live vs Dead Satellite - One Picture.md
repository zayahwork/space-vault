---
title: The live-vs-dead satellite picture (broker one-glancer)
type: reference
status: done 2026-07-23 night
issue: research/027
depends_on: "[[Abandoned GEO - can we build a catch-rate population]]"
figure: "06 Code/output/live_dead_inclination.png"
data: "06 Code/output/live_dead_inclination_2026-07-23.csv"
---

# 🛰️ What a dead satellite looks like next to a live one

One figure for the Jul 30 broker meeting, answering the question issue 025 predicted:
*"show me what a dead satellite looks like in your data."*

![live vs dead](../06%20Code/output/live_dead_inclination.png)

## What the picture shows

**Orbit tilt (inclination) over 60 days, 2026-05-24 → 2026-07-23**, for two Intelsat
satellites — deliberately the same operator, so the only difference is alive vs dead:

| object | NORAD | McDowell class | inclination over the window |
|---|---|---|---|
| **INTELSAT 10-02** (alive, station-kept at 1°W) | 28358 | `GEO/S` | 0.004° – 0.059°, held flat |
| **INTELSAT 601** (abandoned 1990s bird) | 21765 | `GEO/ID` | 13.365° – 13.423°, still rising |

The plain-English story on the figure itself: a live GEO satellite burns fuel
(north–south station-keeping) to pin its orbit plane flat near 0°. When the operator
stops — end of life, failure, abandonment — lunar/solar gravity tips the plane over at
roughly **0.85°/year**, up to a ~15° ceiling and back, over a ~53-year cycle. INTELSAT 601
has been dead long enough to sit at 13.4°. The separation is ~200× — visible from across
the room, which is the point.

## Why this framing is honest (and its limits)

- This is **the catalog-side signature of long-dead**, not our detector's output. Our
  quiet detector works on a different, earlier signal (operator ephemeris cadence);
  inclination takes months–years to visibly drift after death. Chart says "dead looks
  unmistakably different"; it does NOT say "we detect death this way." Don't let a broker
  conflate the two — the honest sequencing is: cadence goes quiet in days (our signal),
  the plane falls over in years (everyone's signal).
- Both classifications come from McDowell's `geotab` (`GEO/S` vs `GEO/ID`), not from us —
  the referee is independent.

## Reproduction

`python "06 Code/live_dead_inclination_chart.py"` — pulls Space-Track `GP_HISTORY` via
`groundtruth/gt_sources.py` (cached in `groundtruth/cache/`), asserts the claim before
drawing (live max < 0.5°, dead min > 10°, ≥20 epochs each), writes the CSV then the PNG.
Window is pinned to the dates above so the figure is reproducible.

## Evidence marks

| claim | mark |
|---|---|
| inclination series for both objects, 60 d | **verified** (Space-Track GP_HISTORY, pulled 2026-07-23; 185 + 141 epochs) |
| INTELSAT 10-02 = `GEO/S`, INTELSAT 601 = `GEO/ID` | **verified** (McDowell geotab, cached copy) |
| ~0.85°/yr tip rate, ~15° ceiling, ~53-yr cycle | **assumed** (standard GEO perturbation result; consistent with issue 025's measured +0.109°/60 d on the abandoned sample) |
