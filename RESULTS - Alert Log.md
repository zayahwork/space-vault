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

## 2026-07-22/1400Z

- **intelsat**: 1 over the bar of 44 scored (0 more among deorbiting hardware, 0 data-quality) — top: 27380 at 48.4 km, 1.0x its bar
- **oneweb**: 3 over the bar of 651 scored (0 more among deorbiting hardware, 0 data-quality) — top: 48767 at 116.9 km, 2.1x its bar
- **ses**: 1 over the bar of 68 scored (0 more among deorbiting hardware, 0 data-quality) — top: 36581 at 17.7 km, 1.1x its bar
- **starlink**: 205 over the bar of 10781 scored (32 more among deorbiting hardware, 67 data-quality) — top: 69652 at 477.5 km, 10.9x its bar

## 2026-07-22/2000Z

- **intelsat**: 2 over the bar of 44 scored (0 more among deorbiting hardware, 0 data-quality) — top: 27513 at 75.4 km, 1.6x its bar
- **oneweb**: 13 over the bar of 651 scored (0 more among deorbiting hardware, 0 data-quality) — top: 54647 at 21.9 km, 4.5x its bar
- **ses**: 1 over the bar of 68 scored (0 more among deorbiting hardware, 0 data-quality) — top: 53960 at 12.4 km, 1.4x its bar
- **starlink**: 142 over the bar of 10836 scored (7 more among deorbiting hardware, 63 data-quality) — top: 66372 at 478.1 km, 8.6x its bar

## 2026-07-23/0200Z

- **intelsat**: 🔇 quiet — all 44 objects inside the stored bar
- **oneweb**: 9 over the bar of 651 scored (0 more among deorbiting hardware, 0 data-quality) — top: 51631 at 17.7 km, 3.6x its bar
- **ses**: 1 over the bar of 68 scored (0 more among deorbiting hardware, 0 data-quality) — top: 60086 at 34.3 km, 1.9x its bar
- **starlink**: 151 over the bar of 10836 scored (19 more among deorbiting hardware, 49 data-quality) — top: 69380 at 280.4 km, 12.4x its bar

---

> [!note] 2026-07-23 (issue 020) — one-command daily run landed
> `python detect.py --all` now scores all four fleets in alert mode (stored bars,
> persistence applied), prints one combined block, and appends it here — a failure in
> one fleet is reported in its line and the others still score. **The scheduled task
> should switch from `daily_alert.py` to `python detect.py --all`** (founder's machine
> config — not changed from here). Until it does, `daily_alert.py` keeps working and the
> two dedupe against the same snapshot headings, so nothing is ever double-logged.
>
> Same change fixed why this log went silent after 2026-07-22/1400Z: SES's re-learned
> baseline stores its mixed-fleet floor as a list (`[1.0, 2.0]`), which crashed the
> scheduled scorer on every snapshot since. `load_baselines` now reads a list floor back
> as per-object regime floors; the two missed snapshots above were backfilled 2026-07-23.
