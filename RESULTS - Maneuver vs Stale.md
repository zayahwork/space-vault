---
date: 2026-07-22
status: persistence RUNNING on real archive; still unverified against real maneuver records
code: "06 Code/detect.py"
---

# 🛰️ RESULTS — telling a maneuver apart from a stale catalog

> [!success] The headline (re-measured 2026-07-22 1400Z — all three filters now RUNNING)
> Ranking Starlink on raw disagreement with the catalog surfaces **6,948 objects**. Three
> filters explain almost all of it:
> 1. **Old data** — 92% of the naive list was just a stale catalog entry, not movement.
> 2. **Falling hardware** — 83% of what survived was satellites being deliberately deorbited.
>    They move every day, on purpose, and nobody pays to hear it.
> 3. **Didn't repeat** — a real maneuver still disagrees next time you look. **No longer
>    blocked: this ran across 4 snapshots / 3 independent looks.**
>
> What's left: **489 satellites holding station that moved when they shouldn't have** — and
> **400 of those were invisible** under the old ranking, crowded out by falling junk. Of those
> 489, **376 (77%) survived a second independent look**; 113 rest on a single look so far.

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

## 🕒 Second filter — temporal persistence (added 2026-07-22)

The age filter fixes *"old data looks like movement."* It does nothing about the other way to
fool ourselves: **one snapshot is one measurement.** Asking for the top 5% of 10,780 objects
hands you ~540 suspects *by construction*, whether or not anything moved. Some of those are
one-off garbage — a bad element set, a fit that went wrong once.

A real maneuver doesn't go away when you look again. The operator's orbit keeps disagreeing
with that catalog entry, through refresh after refresh, until the catalog catches up and the
gap collapses. Noise doesn't do that. So `detect.py` now checks the same object across several
snapshots and asks: **is it still flagged?**

> [!danger] The trap this had to dodge — fake corroboration
> CelesTrak republishes SupGP every ~30 min, but the underlying element sets only actually
> change **a few times a day**. Two of our six snapshots are byte-identical to the one before
> them (`0851Z`≡`0852Z`, `2025Z`≡`2157Z` — measured, not assumed). *"Flagged in 6 of 6
> snapshots"* would have been **the same two files compared six times**, dressed up as six
> pieces of evidence. That's a worse lie than the one the age filter fixed.
>
> So persistence counts **independent looks**, not snapshots. A snapshot only counts for an
> object if at least one of its two element sets (operator or catalog) actually changed epoch
> since the last counted look. Six snapshots → **four** independent looks.

New verdicts: **PERSISTENT SUSPECT** (flagged in ≥2 independent looks) · **unconfirmed**
(flagged only in the newest look — a fresh burn *or* a one-off; the next snapshot decides) ·
**cleared** (was flagged, normal now — catalog caught up, or it was noise).

> [!success] ✅ UNBLOCKED 2026-07-22 — persistence ran for real, on the real archive
> The archiver has now banked **three** catalogs (`0200Z`, `0750Z`, `1400Z`), so the check that
> was blocked below is **running against real data, no rehearsal, no time-travelled catalog**.
>
> **Scored across 4 snapshots spanning 12.0h** (`0200Z/0750Z/0800Z/1400Z`), which collapse to a
> **median of 3 independent looks** per object — the byte-identical republishes are being
> discarded exactly as designed.
>
> ```
> PERSISTENT SUSPECTS  376  of 10,781 (3.5%)  ← flagged in ≥2 independent looks
> unconfirmed          113  ← flagged only in the newest look; next snapshot decides
> cleared              344  ← was flagged, normal now (catalog caught up, or it was noise)
> ```
>
> **The filter is doing real work:** 344 candidates — **42% of the 833 ever flagged** — failed
> to repeat and were dropped. Under the old single-snapshot method every one of those would
> have been reported as a maneuver candidate. The top of the list is solid, though: the 15
> largest gaps are all **3/3 persisted** (one is 2/3), so the strongest candidates are the ones
> repeating most reliably — which is the direction you want that correlation to run.
>
> **What it must never do instead:** score the Jul-21 snapshots against the Jul-22 catalog.
> That's borrowing from the future — it gives catalog entries *negative* age, drops them in
> the wrong age bin, and manufactures perfect fake persistence (every snapshot scored against
> one identical catalog file). `load_gp` now refuses to borrow forwards, and a replay of an
> old snapshot no longer falls back to fetching today's catalog live. **That fallback was
> live in the code and would have silently produced exactly this error.**

The earlier rehearsal on a throwaway archive suggested 18% of the age-aware list would fail to
repeat. **On the real archive it is 42%** (344 of 833). The rehearsal understated it by more
than 2×, which is the expected direction — it used one time-travelled catalog, so objects were
being compared against an identical file and looked far more persistent than they are. Logic is
covered by `06 Code/_test_detect.py` — nine cases including the fake-corroboration trap, all
passing as of 2026-07-22.

### What today's run measured (starlink, 2026-07-22 1400Z, 10,781 comparable)

| catalog age | objects | normal gap (median) | flagged above |
|---|---|---|---|
| 12–24 h | 1,522 | 9.11 km | 49.74 km |
| 24–48 h | 7,941 | 7.95 km | 32.79 km |
| 48–96 h | 263 | 10.86 km | 58.43 km |
| 96+ h | 1 | 1.13 km | 36.56 km *(too few — used whole population)* |

Population split: **9,760 holding station** · **1,021 on the way down** (>0.4 km/day).

## 🪂 Third filter — separating "moved" from "falling" (added 2026-07-22)

**Plain version:** most of what the detector was excited about was satellites being thrown
away on purpose.

SpaceX retires dead Starlinks by slowly dropping them until they burn up. That takes months,
and the whole time the satellite is sinking — so the public catalog is *permanently* behind it.
Huge gap, every single day, forever. Not a maneuver. Just a satellite in the bin.

Measured on 2026-07-22:

| | share of population | share of the candidate list |
|---|---|---|
| falling faster than 0.4 km/day | **9.5%** | **79%** |

Those objects sit ~356 km up (the working satellites are ~475 km), they're 558 days old on
average, and they lose altitude **12x faster** than everything else. Median gap **19.7 km** vs
**4.0 km** for the rest.

> [!note] Why 0.4 km/day
> That's not a new number — it's the exact threshold `deorbit_check.py` already uses to call
> a satellite "in sustained descent." Reusing it deliberately, so the two tools can never
> drift into disagreeing about what "falling" means.

The fix is the same move as the age filter: **judge like against like.** A satellite on its way
down is only interesting if it's extreme compared to *other satellites on their way down*.

> [!warning] What this did NOT do — shorten the list
> The threshold is a percentile, so ~5% of each group gets flagged **no matter what happens up
> there**. Separating the groups doesn't cut the list, it **swaps who's on it**:
> - **448 of the 537** candidates were deorbiting hardware → now judged separately, only
>   **54** are unusual for their own kind
> - **400 station-keeping satellites** are now on the list that the old ranking **never showed
>   at all** — they were buried under falling junk
>
> Old list: 83% garbage, and it surfaced only 89 of the satellites we actually care about.
> New list: 489 station-keepers, 400 of them newly visible.
> *(Re-measured 2026-07-22 1400Z. The previous figures — 428/540/53/378/490 — were the 0200Z
> snapshot; same conclusion, and the sizes move a little snapshot to snapshot.)*

> [!danger] The open problem this exposes
> Because the cut is a percentile, **the detector can never say "quiet day."** It will hand you
> ~5% every time you run it, even if nothing in orbit moved at all. That's fine for ranking and
> wrong for alerting. Needs an absolute threshold before anyone gets an alert from this.

Sanity check: run on OneWeb (1,200 km, nothing decaying) and the falling group is **0 objects** —
the filter doesn't fire where it shouldn't.

> [!danger] ✅ CHECKED 2026-07-22 — and the reason below is WRONG
> The claim *"likely decay or bad TLE"* was checked against 30 days of altitude history
> ([[RESULTS - Checked Against History]]). Only **5 of 29** are actually decaying. The other
> 24 are **16 freshly-launched satellites still climbing** (2026 launches at 325–460 km) and
> **8 old satellites with flat histories** (genuinely bad element sets).
> **Keeping them out of the candidate list is still correct** — none are station-keeping
> maneuvers. But the stated reason is mostly wrong. Don't repeat the sentence below.

> [!warning] Hard plausibility gate (added 2026-07-21)
> `detect.py` now applies a **hard 500 km gate** before the age-aware statistics. No
> station-keeping burn moves an object hundreds of km RMS over 6 hours, so any larger gap
> means the two element sets describe wholly different orbits — a decaying/reentering object
> or a bad TLE, not a maneuver. The objects that used to sit at the top of the candidate list
> are now bucketed as **data-quality flags**, never shown as detections. They're also excluded
> from the per-age-bin baseline so a handful of nonsense orbits can't distort the thresholds
> the honest candidates are judged against. Tune with `--max-km`.
>
> **2026-07-22 count: 67 objects** (was 17 when this was written) — worst three 11,731 km,
> 8,608 km, 7,781 km. The gate is catching ~4× more than first published, so it is load-bearing,
> not a formality. See the CHECKED note above for why "decay or bad TLE" is the wrong reason.

![[detect_starlink_2026-07-21_2157Z.png]]

Note how the normal gap **climbs with age** — 2.29 km at 6–12 h, 7.23 km at 24–48 h. That
climb is exactly the effect that a naive detector would have reported as thousands of
maneuvers.

## ⚠️ What this is NOT (read before telling anyone)

- **These are candidates, not detections.** Nothing here has been checked against an actual
  maneuver record. That is still the single biggest unverified claim in this note. Tim owns
  that check — see [[01 TASKS]].
- **376 have now been seen twice; 113 have not.** ~~None of them have been seen twice yet.~~
  Superseded 2026-07-22 — persistence ran across 3 independent looks. The 376 PERSISTENT
  SUSPECTS rest on ≥2 independent measurements. The 113 unconfirmed still rest on one, and
  should be described that way to anyone outside the company.
- **12 hours is a short baseline.** Persistence currently spans `0200Z`→`1400Z` of a single
  day. "Repeated over 12 hours" is genuinely stronger than one look, but it is not "repeated
  over a week." Don't let it get quoted as the latter.
- **The top of the list is no longer the least trustworthy part** — that changed when the
  500 km gate went in. The largest surviving candidate is **491.7 km** (NORAD 60029, 62× its
  age-band norm, 3/3 persisted). The nonsense orbits are now bucketed separately and are
  bigger than previously published: worst three are **11,731 km**, **8,608 km**, **7,781 km**
  (69694, 69715, 69487) — not the 8,412/5,337 km quoted above.
- **The 24–48 h band's threshold (78.76 km) is higher than the 48–96 h band's (58.68 km).**
  A threshold that isn't monotonic in age is a small-sample artifact — 618 and 45 objects.
  Real, but not yet load-bearing.
- **Public GP data is smoothed around maneuvers by design** ([[Kelso Reading - Digest]] §2).
  That biases what we can see, and saying so out loud is a credibility asset.

## Why this matters commercially

The pitch was never *"we detect maneuvers"* — everyone claims that. It's:

> **Most of what looks like a maneuver is just old data. We can tell the difference, from
> free public data, for anyone.**

That's a claim with a number attached, and the number is **92%** (re-measured 2026-07-22;
it was published as 85%, then 89% — it has moved with each re-measurement, so quote it with
the date attached, not as a constant).

## Reproduce it

```bash
cd "C:\Space\06 Code"
python detect.py --group starlink --chart --csv   # persistence on by default (last 4 snapshots)
python detect.py --group oneweb --chart
python detect.py --history 1                      # single snapshot, old behaviour
python detect.py --snapshot 2026-07-21/2025Z      # replay a past snapshot
python _test_detect.py                            # persistence logic, 9 cases
```
