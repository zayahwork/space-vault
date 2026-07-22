---
date: 2026-07-21
status: working prototype, unverified against real maneuver records
code: "06 Code/detect.py"
---

# 🛰️ RESULTS — telling a maneuver apart from a stale catalog

> [!success] The headline
> Ranking Starlink on raw SupGP-vs-catalog disagreement surfaces **3,555 objects**.
> Ranking with catalog age taken into account surfaces **541** — of which **17** are
> physically impossible (RMS jumps of thousands of km) and are gated out as data-quality
> flags, leaving **524 real maneuver candidates**.
> **85% of the naive list was just old data, not movement.**

## The problem this fixes

[[RESULTS - First Charts]] proved the disagreement between operator orbits (SupGP) and the
public catalog is real and large — median **3.72 km**, 90th percentile **16.6 km**, **6.0%**
of Starlink over 25 km. But a big disagreement has two completely different causes:

| | What happened | What it looks like |
|---|---|---|
| **Maneuvered** | The object burned. The operator knows. The catalog hasn't caught up. | Big gap, **fresh** catalog entry |
| **Stale** | Nobody burned anything. The catalog entry is simply old, and any orbit drifts. | Big gap, **old** catalog entry |

Treat those as the same thing and the "maneuver detector" is mostly an **age detector wearing
a hat**. This is the single most likely way we'd have fooled ourselves.

## The method (deliberately assumption-light)

1. RMS position difference between SupGP and GP over 6 hours — Kelso's own comparison.
2. **GP age** — how old the public catalog's element set was at the moment of capture.
3. Bin the whole population by age. Measure what a *normal* gap looks like inside each bin.
4. Flag an object only if it's extreme **for its own age bin**.

Step 4 is the whole idea. We never say *"20 km is a lot."* We say *"20 km is a lot for an
element set that's 8 hours old, because its same-age neighbours sit at 2.3 km."*

**No drag model. No physics assumption. Nothing tuned.** The baseline is measured off the same
population on the same day, so it can't be wrong about the atmosphere — it can only be wrong
about the population, which is checkable.

## What came out (starlink, 2026-07-21 21:57Z, 10,780 comparable objects)

| catalog age | objects | normal gap (median) | flagged above |
|---|---|---|---|
| 3–6 h | 299 | 6.13 km | 13.01 km |
| 6–12 h | 4,796 | 2.29 km | 13.81 km |
| 12–24 h | 5,022 | 3.52 km | 22.33 km |
| 24–48 h | 618 | 7.23 km | 78.76 km |
| 48–96 h | 45 | 14.06 km | 58.68 km |

```
MANEUVER SUSPECTS    524  of 10,780  (4.9%)
DATA QUALITY FLAG     17  ← gap ≥ 500 km, physically impossible; likely decay or bad TLE
big gap but stale  3,014  ← would have been false positives on gap alone
agrees             7,225
```

> [!warning] Hard plausibility gate (added 2026-07-21)
> `detect.py` now applies a **hard 500 km gate** before the age-aware statistics. No
> station-keeping burn moves an object hundreds of km RMS over 6 hours, so any larger gap
> means the two element sets describe wholly different orbits — a decaying/reentering object
> or a bad TLE, not a maneuver. The worst two (**8,412 km** and **5,337 km**) that used to sit
> at the top of the candidate list are now bucketed as **data-quality flags**, never shown as
> detections. They're also excluded from the per-age-bin baseline so a handful of nonsense
> orbits can't distort the thresholds the honest candidates are judged against. Tune with
> `--max-km`.

![[detect_starlink_2026-07-21_2157Z.png]]

Note how the normal gap **climbs with age** — 2.29 km at 6–12 h, 7.23 km at 24–48 h. That
climb is exactly the effect that a naive detector would have reported as thousands of
maneuvers.

## ⚠️ What this is NOT (read before telling anyone)

- **These are candidates, not detections.** Nothing here has been checked against an actual
  maneuver record. Tim owns that check — see [[01 TASKS]].
- **The top suspects are suspicious in the wrong way.** The largest gaps are 5,337 km and
  8,412 km RMS. No station-keeping burn does that. Those are far more likely to be decaying
  objects, or bad element sets, than maneuvers. Until they're explained, the *top* of the
  list is the *least* trustworthy part of it.
- **The 24–48 h band's threshold (78.76 km) is higher than the 48–96 h band's (58.68 km).**
  A threshold that isn't monotonic in age is a small-sample artifact — 618 and 45 objects.
  Real, but not yet load-bearing.
- **Public GP data is smoothed around maneuvers by design** ([[Kelso Reading - Digest]] §2).
  That biases what we can see, and saying so out loud is a credibility asset.

## Why this matters commercially

The pitch was never *"we detect maneuvers"* — everyone claims that. It's:

> **Most of what looks like a maneuver is just old data. We can tell the difference, from
> free public data, for anyone.**

That's a claim with a number attached, and the number is 85%.

## Reproduce it

```bash
cd "C:\Space\06 Code"
python detect.py --group starlink --chart --csv
python detect.py --group oneweb --chart
```
