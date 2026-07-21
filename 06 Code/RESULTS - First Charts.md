# 🛰️ RESULTS — First Light, July 20, 2026

![[iss_maneuvers.png]]

## What you're looking at (plain English)

That's the **International Space Station's altitude over the last 4 months**, drawn from free
public data, by code that ran on this computer tonight.

- The **blue line drifting down** = air drag slowly pulling the ISS toward Earth (yes, there's
  a tiny bit of air even at 425 km).
- Each **sharp jump up** = astronauts fired the engines to push it back up (a **reboost** — a
  real maneuver).
- Each **red dashed line** = the moment OUR detector caught it. Automatically. All 3 of them:
  - 2026-04-16 · 2026-06-10 · 2026-07-04

## Why this matters

**This is the company's core claim, proven at v0.1 scale:** *detect when a satellite moves on
purpose, using only free public data.* Tonight it found every ISS burn in a 4-month window with
zero misses on this object, from 426 data records, at a cost of $0.

Built the same day the founder first registered for the data. Day 1.

## Facts (for pitches and the Moriba call)
- Data: Space-Track **GP_HISTORY** (OMM-era API — modern format, not legacy TLE)
- 426 records · 120 days · object: ISS (NORAD 25544)
- Detector v0.1: altitude-jump threshold (0.25 km) with 12-hr burn grouping
- Code: `06 Code/maneuver_chart.py` — ~100 lines of Python

---

# Round 2 (same night) — a Starlink and a GEO bird

![[starlink_maneuvers.png]]
![[goes18_maneuvers.png]]

## 🪦 STARLINK-2083 — we caught a satellite DYING

The script auto-picked an active Starlink… and it happened to be one in its **final descent**.
400 km → 288 km in four months, steady and controlled — SpaceX is deliberately walking this
2021-era satellite down to burn up in the atmosphere (that's how responsible disposal works).
At this rate it has weeks left. **First night with the data and we're watching a satellite's
funeral in real time.** (Great story for the Kelso/Moriba conversations.)

Detector said **0 maneuvers** — technically "wrong," but honestly: v0.1 only looks for
**upward** jumps (chemical-burn style). A slow electric-thruster descent is invisible to it.
→ **Blind spot #1 found:** we need to watch *down* and *gradual*, not just *up* and *sudden*.

## 📡 GOES-18 — the detector got confused (also valuable!)

28 "maneuvers" in 120 days is too many for a GEO weather satellite. What's really there: some
REAL station-keeping burns mixed with **measurement noise** — at 35,786 km, the catalog's
altitude estimate wobbles by ±0.5 km on its own, and our simple threshold can't tell wobble
from burn.
→ **Blind spot #2 found:** at GEO, a dumb threshold drowns in noise. Separating real burns
from noise is *exactly* the ML problem — and exactly what [[Guide - SPLID Detector|SPLID]]
trains us to solve (its labels even include propulsion type!).

## The honest v0.1 scorecard
| Target | Result | Lesson |
|---|---|---|
| ISS (LEO, chemical burns) | ✅ 3/3, clean | pipeline works end-to-end |
| Starlink (LEO, electric, descending) | ⚠️ blind to it | detect down + gradual too |
| GOES-18 (GEO, tiny burns) | ⚠️ noise-drunk | need statistics/ML, not thresholds |

**This is the perfect launch pad:** one clean win + two precisely-named blind spots = the
exact to-do list for v0.3. That's not failure, that's a roadmap discovered in one evening.

---

# Round 3 (same night, 7:33–8:00 sprint) — blind spot #1 PATCHED

![[starlink_deorbit_detected.png]]

**Detector v0.2.1** now watches for *sustained descent*, not just upward kicks — and it
correctly flags STARLINK-2083's entire death-spiral (red zone, starting Mar 30): **112 km
lost, currently -1.6 km/day and accelerating.** Rough estimate: reentry within ~2 months,
likely sooner (air thickens as it falls, so the fall speeds up).

Code: `deorbit_check.py`. Remaining blind spot for v0.3: GEO noise (the ML/SPLID job).

**Also:** the MIT SPLID devkit is cloned (`06 Code/splid-devkit/` — it even includes the
winning solutions + evaluation code), and the public dataset download was kicked off.
Friday's build session starts warm.
