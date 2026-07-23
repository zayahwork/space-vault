---
status: done
type: AFK
owner: Randy (research)
blocked-by: []
---
# The "live vs dead satellite" one-picture chart for the broker

**Goal:** issue 025 concluded that a catalog-only cadence track for abandoned GEO objects is not worth
building, but that a broker will still ask *"show me what a dead satellite looks like next to a live
one."* That is a one-off chart, not a pipeline, and it makes the point in a single picture.

**Done when:** a chart (PNG/SVG in `06 Code/output/` or an `03 Reference/` note) overlays ~60 days of
**inclination history** for one healthy `GEO/S` object (held flat near 0°) against one abandoned
`GEO/ID` object (drifting up through ~12°), both pulled from Space-Track `GP_HISTORY`. Labelled so a
non-technical reader sees instantly: the live one is being actively held; the dead one has let its
orbit plane fall over. Source and object NORADs stated; both objects named from `geotab`.

**Notes:** the separation is ~400× (11.95° vs 0.03°, measured in issue 025), so it will read clearly.
Pick recognizable birds if possible (a well-known active Intelsat/SES vs a documented graveyard object).
This is presentation, not new measurement — keep it to one figure. WebSearch yes, WebFetch no; contact
no one. If chart-rendering deps aren't in this lane's scope, produce the data table + a note and flag it
for whoever renders.

**Closed 2026-07-23 (night, ralph).** One figure, rendered and eyeballed:
`06 Code/output/live_dead_inclination.png` + data table
`live_dead_inclination_2026-07-23.csv` + note
`03 Reference/Live vs Dead Satellite - One Picture.md`. Two recognizable Intelsat birds so
the only variable is alive vs dead: **INTELSAT 10-02** (28358, geotab `GEO/S`, inclination
held 0.004-0.059 deg over 60 d) vs **INTELSAT 601** (21765, geotab `GEO/ID`, 13.4 deg and
still rising). 60 d of Space-Track GP_HISTORY (185 + 141 epochs), window pinned
2026-05-24..2026-07-23 for reproducibility. The script
(`06 Code/live_dead_inclination_chart.py`) asserts the chart's claim before drawing (live
max < 0.5 deg, dead min > 10 deg) — its own feedback loop. Note flags the honest limit:
this is the *long-dead* catalog signature, not our detector's signal; cadence goes quiet
in days, the plane falls over in years — don't let the broker conflate them.
