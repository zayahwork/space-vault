---
status: written by a scheduled task - do not hand-edit entries, add notes below them
code: "06 Code/daily_alert.py (scheduled: Maneuver Alert, every 6h)"
---

# 🚨 Alert Log — every snapshot, judged against a fixed bar

Each entry below is one archive snapshot scored in **alert mode**: objects are flagged
only if their operator-vs-catalog gap exceeds a bar **learned from past snapshots and
held fixed** (see `baselines_<group>.json` for provenance). That means **zero is a real
answer** — a quiet line is the detector saying "nothing happened", not saying nothing.

*Jargon: "gap" = how far the operator's own orbit (SupGP) sits from the public catalog
(GP), in km. "bar" = the 99th-percentile gap for objects of the same catalog age and
regime, from the baseline file. "quiet" = nothing over the bar.*

## 2026-07-22/0200Z

- **intelsat**: 2 over the bar of 44 scored (0 more among deorbiting hardware, 0 data-quality) — top: 27513 at 20.7 km, 1.1x its bar
- **oneweb**: 7 over the bar of 651 scored (0 more among deorbiting hardware, 0 data-quality) — top: 54679 at 31.4 km, 5.9x its bar
- **ses**: 1 over the bar of 68 scored (0 more among deorbiting hardware, 0 data-quality) — top: 36581 at 17.7 km, 1.0x its bar
- **starlink**: 71 over the bar of 10781 scored (13 more among deorbiting hardware, 29 data-quality) — top: 69687 at 406.7 km, 9.3x its bar

## 2026-07-22/0750Z

- **intelsat**: 1 over the bar of 44 scored (0 more among deorbiting hardware, 0 data-quality) — top: 27380 at 48.4 km, 1.0x its bar
- **oneweb**: 7 over the bar of 651 scored (0 more among deorbiting hardware, 0 data-quality) — top: 54679 at 26.3 km, 5.0x its bar
- **ses**: 1 over the bar of 68 scored (0 more among deorbiting hardware, 0 data-quality) — top: 36581 at 17.7 km, 1.1x its bar
- **starlink**: 112 over the bar of 10781 scored (10 more among deorbiting hardware, 47 data-quality) — top: 67865 at 492.2 km, 11.2x its bar

## 2026-07-22/0800Z

- **intelsat**: 1 over the bar of 44 scored (0 more among deorbiting hardware, 0 data-quality) — top: 27380 at 48.4 km, 1.0x its bar
- **oneweb**: 7 over the bar of 651 scored (0 more among deorbiting hardware, 0 data-quality) — top: 54679 at 26.3 km, 5.0x its bar
- **ses**: 1 over the bar of 68 scored (0 more among deorbiting hardware, 0 data-quality) — top: 36581 at 17.7 km, 1.1x its bar
- **starlink**: 111 over the bar of 10781 scored (10 more among deorbiting hardware, 47 data-quality) — top: 67865 at 492.2 km, 11.2x its bar
