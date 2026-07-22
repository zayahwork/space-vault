---
title: The quiet detector's exam — pre-registered before Jul 29
type: reference
status: pre-registered 2026-07-22 night, BEFORE quiet.py has produced any cadence verdict
data: "06 Code/quiet_exam.csv (812 rows; 55 in the exam set)"
scores: "06 Code/quiet.py --group starlink|oneweb"
issue: research/024
---

# 📝 The quiet detector's exam — written down before the answers exist

`quiet.py` unlocks ~Jul 29, the day before the broker meeting. This file exists so that when
it does, its first verdicts land as a **graded result** — "caught X of Y known-dead, Z false
alarms on known-healthy" — not a page of raw output nobody can challenge. Everything here was
pre-registered **before** any cadence verdict existed. That is the entire point, and it is why
the file is dated and committed now.

## What "the exam set" actually is — measured, not assumed

The issue said *"the 44 objects with ≥3 spikes."* I ran `quiet.py` against the live archive
and enumerated them from its own code path (`object_histories` → `judge`), so the set is
exactly what the tool will grade:

> **55 objects have ≥3 spikes on record — 49 Starlink, 6 OneWeb. Zero Intelsat, zero SES.**

It is 55, not 44, because the archive grew from 4 to 5 scoreable snapshots since
[[RESULTS - The Quiet Detector]] was written. It will keep drifting up until Jul 29; **re-run
the enumeration on the day** (`quiet.py` prints the count) and treat any object new to the set
as ungraded — its verdict was not pre-registered here.

**Why no GEO objects are in it, and why that matters:** a spike is a look where the object sat
over its station-keeping bar. GEO operators refresh SupGP slowly, so no Intelsat or SES object
has accumulated 3 independent looks in a 5-snapshot archive. The gradeable population is
LEO-only for now. This also means my first attempt at this exam — a GEO-belt status table —
intersected the actual spike population at **zero objects**. Corrected.

## The status of every object in the exam set — and the finding that inverts the issue

Looked up all 55 in McDowell's `currentcat` (stamp `Updated 2026 Jul 17 2054:56`):

> **All 55 are documented Active** — Active flag `A`, ExpandedStatus `In Earth orbit`.
> **Not one is documented dead or abandoned.**

| exam set | n | documented status | pre-registered verdict |
|---|---|---|---|
| Starlink | 49 | all Active (`A`) | **`on rhythm`** |
| OneWeb | 6 | all Active (`A`) | **`on rhythm`** |
| **total** | **55** | **55 healthy, 0 dead** | **all `on rhythm`** |

> [!danger] The exam can measure a false-alarm rate. It cannot measure a catch rate.
> There is no known-dead object in the gradeable population, so there is no catch-rate
> denominator. This is not a gap in the data-gathering — it is **structural**, for two
> compounding reasons:
>
> 1. **`MIN_SPIKES = 3` requires evidence of station-keeping.** An object that was already
>    dead when the archive began never spikes, never reaches 3, and reports `no rhythm yet`
>    forever. `WENT QUIET` is reachable **only** by a satellite that was healthy *during* our
>    window and stopped *during* our window — rare by construction, which is the whole product
>    thesis.
> 2. **Operators stop publishing SupGP for satellites they abandon.** The signal vanishes
>    exactly when the interesting thing happens — the same blind spot recorded in
>    [[RESULTS - Ground Truth]].
>
> **Nobody should describe a catch rate in the Jul 30 meeting.** What this exam *can* deliver
> is the thing the company has never had: **a false-alarm rate measured on 55 documented
> non-events.**

## The pre-registered verdicts

`quiet.py` emits exactly three verdicts: `no rhythm yet`, `on rhythm`, `WENT QUIET`.

**Every one of the 55 exam objects is pre-registered `on rhythm`.** Written down now, before
the gate opens. The failure to watch for is any of them coming back **`WENT QUIET`** — that is
a healthy satellite declared a possible loss of control, the precise defect `_test_quiet.py`
found and fixed (a burst of spikes inside one day yielding a 0.25-day "rhythm", so the next
overnight gap read as 2.8× and tripped the alarm). The fix — flooring the typical interval at
1.0 day — is in. **This exam is what confirms it on real data rather than synthetic cases.**

The full per-object list with its expected verdict is `06 Code/quiet_exam.csv`,
`in_exam_set == yes`. All 55 currently sit at 3 or 4 spikes (42 at three, 13 at four).

## The scoring recipe — run this on Jul 29

```bash
cd "C:\Space\06 Code"
python detect.py --learn-baseline --pct 99     # re-learn; the bar will be ~a week old
python quiet.py --group starlink
python quiet.py --group oneweb
```

Join each `WENT QUIET`/`on rhythm`/`no rhythm yet` verdict to `quiet_exam.csv` on NORAD, keep
`in_exam_set == yes`, and fill in exactly this table:

| measure | formula | pre-registered expectation |
|---|---|---|
| **False-alarm rate** | `WENT QUIET` among the 55 documented-Active objects ÷ 55 | **0%.** Anything above ~5% blocks the "we spot a failing satellite" claim |
| **Catch rate** | `WENT QUIET` among documented-dead objects with ≥3 spikes ÷ that denominator | **denominator = 0** → report as *not measurable*, **never as 0%** |
| **Gate coverage** | objects still reaching ≥3 spikes on Jul 29 ÷ objects tracked | report it; it bounds everything above |

**Report every number with its denominator.** "0 of 4" and "0 of 55" are different claims and
only the denominator separates them.

### What good and bad look like

- **Good:** all (or nearly all) 55 report `on rhythm`, zero report `WENT QUIET`. That is a
  **measured false-alarm rate on 55 documented non-events** — the first real one this company
  has, and genuinely quotable to a broker.
- **Bad, the one to watch:** any of the 55 reporting `WENT QUIET`. Regression on the
  `_test_quiet.py` bug; do not show the broker unscored output if this happens.
- **Not bad despite appearances:** no catch rate. Expected, explained above, and it must be
  *stated*, not quietly omitted.

## Honesty notes

- **Every row in `quiet_exam.csv` is marked `verified` or `assumed`** (72 verified, 740
  assumed) and carries the GCAT catalog and stamp it was read from.
- **The exam set's status is `assumed`, deliberately.** All 55 are LEO, classified by
  `currentcat`'s **Active flag**, whose meaning GCAT does not document in a page I could find.
  I validated it empirically instead — against the GEO orbit types whose meaning *is*
  documented, the flag `A` dominates station-kept `GEO/S` (387 of 471) and `P` dominates
  abandoned `GEO/ID` (617 of 917). Strong enough to corroborate status, not strong enough to
  call verified. So: `A` → active (assumed), `P` → abandoned (assumed).
- **GCAT is not fully independent of us.** McDowell derives from the same public catalog our
  detector reads. He applies independent curation, which is why it is usable as documented
  status — but it is not an operator statement and must not be described to a buyer as one.
- **OneWeb is now examinable** — last iteration recorded it as un-gradeable because `geotab` is
  GEO-only. `currentcat` covers all regimes (654 OneWeb in-orbit, 652 Active), which is how
  6 OneWeb objects enter the exam set.
- **Departure from the issue wording, recorded:** the "44" was a Starlink figure and no
  documented *operator* status exists for Starlink; GCAT's catalog status is what stands in.
  The exam pre-registers a verdict for every spike-history object keyed by NORAD, which is the
  gradeable population regardless of its exact size on the day.
