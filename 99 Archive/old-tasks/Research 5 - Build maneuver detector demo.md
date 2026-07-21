---
title: "Research 5 — Build the $0 maneuver-detector demo (on SPLID)"
tags: [task, research, ssa]
status: open
priority: high
contexts: [research]
projects:
  - "[[SSA Week - Day 5]]"
scheduled: 2026-07-24T12:15
timeEstimate: 240
due: 2026-07-24
---

Use **MIT ARCLab SPLID** — a public, *labeled* maneuver/pattern-of-life dataset — so you don't hand-label anything.
- Devkit: `github.com/ARCLab-MIT/splid-devkit` · docs: `splid-devkit.readthedocs.io`
- Labels = time-stamped PoL **nodes** `{time, EW/NS, node type, propulsion}` → this is change-point detection + segment classification at 2-hr cadence. Home turf.
- Sequence: run devkit baseline → study/reproduce 2024 winner (`DavidBaldsiefen/splid-challenge`) → your own ML pass → **transfer to live data**.
- ⚠️ **Live data = OMM, not TLE.** Catalog crossed 100,000 on Jul 11; new objects have NO TLE format. Query Space-Track `GP_HISTORY` as **JSON/OMM** (python `sgp4` supports OMM + Alpha-5). Never write a fixed-width TLE parser in 2026.
- Demo = your detector flagging a *real* maneuver on a real GEO sat from free data, with a benchmark score behind it.

Full build spec: [[DEEP_RESEARCH_2026-07-20]] §3.
