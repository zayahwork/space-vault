---
title: The quiet detector's exam — pre-registered before Jul 29
type: reference
status: pre-registered 2026-07-22 night, BEFORE quiet.py has produced any verdict
data: "06 Code/quiet_exam.csv (140 rows, 67 in the exam set)"
scores: "06 Code/quiet.py --group intelsat|ses"
issue: research/024
---

# 📝 The quiet detector's exam — written down before the answers exist

`quiet.py` unlocks ~Jul 29, the day before the broker meeting. This file exists so that when
it does, its output lands as a **graded result** rather than a page of raw verdicts nobody can
argue with. Everything here was written **before** any verdict existed — that is the whole
point, and it is why the file is dated and committed now.

> [!danger] The headline, and it is not what the issue expected
> **This exam can measure a false-alarm rate. It cannot measure a catch rate.**
> Of the 67 objects with documented status that we actually track, **66 are documented
> healthy and exactly 1 is documented dead.** There is no catch-rate denominator. Worse,
> the one dead object *structurally cannot* be caught — see "The catch-rate problem" below.
> **Nobody should walk into the Jul 30 meeting describing a catch rate.** What we can
> honestly claim is the thing we have never had: **a measured false-alarm rate.**

---

## Where the status comes from

McDowell's GCAT `geotab.tsv` (stamp `Updated 2026 Jul 17 2058:25`) classifies every GEO-belt
object by its orbit type. That classification is made **independently of our detector** and is
the closest thing to documented per-satellite operational status that exists publicly.

| GCAT `OType` | what it means | our `status` | evidence |
|---|---|---|---|
| `GEO/S` | station-kept in longitude *and* inclination | **active-stationkept** | verified |
| `GEO/ID` | inclined drift — abandoned, nobody is flying it | **abandoned** | verified |
| `GEO/I` | inclination let go, longitude still held | degraded | assumed |
| `GEO/D` | drifting at low inclination | relocated-or-disposing | assumed |
| `VHEO` | super-synchronous disposal orbit | abandoned | assumed |

`GEO/S` and `GEO/ID` are marked **verified** because they are unambiguous states with a clear
expected behaviour. The middle categories are marked **assumed** — a `GEO/D` object might be
mid-relocation (healthy, manoeuvring hard) or freshly disposed (dead). They are deliberately
**excluded from the exam set** rather than guessed at.

**Fleet coverage, measured not assumed:**

| fleet | we track | documented status | in exam set |
|---|---|---|---|
| Intelsat | 44 | 37 | **34** |
| SES | 68 | 34 | **33** |
| OneWeb | 651 | **0** | **0** |
| **total** | | | **67** |

**OneWeb has zero documented per-satellite status.** `geotab` is GEO-only and no public
per-satellite health source for OneWeb was found. OneWeb cannot be examined this way at all —
that gap is real and is not closed by this work.

---

## The pre-registered verdicts

`quiet.py` emits exactly three verdicts: **`no rhythm yet`** (fewer than 3 spikes on record),
**`on rhythm`**, and **`WENT QUIET`**. Written down now, before the run:

| status | n in exam | **expected verdict** | a different answer means |
|---|---|---|---|
| **active-stationkept** | **66** | **`on rhythm`** | `WENT QUIET` = **FALSE ALARM** — the exact bug `_test_quiet.py` was written to catch |
| **abandoned** | **1** | **`no rhythm yet`** | see below — *not* `WENT QUIET` |

### The catch-rate problem — the thing worth knowing before Jul 29, not after

`judge()` requires **`MIN_SPIKES = 3`** before it will call anything. A spike is a look where
the object sat over its stored bar — i.e. **evidence of station-keeping**. So:

> An object that was already abandoned when our archive began **never spikes**, therefore never
> reaches 3 spikes, therefore reports **`no rhythm yet`** forever. It can never be reported as
> `WENT QUIET`.

`WENT QUIET` is reachable **only** by a satellite that was station-keeping *during* our archive
and then stopped *during* our archive. That is a rare event by construction — it is the entire
product thesis that it is rare. With an archive that starts 2026-07-22, the catch population is
**expected to be zero**, and a zero there is **not** a failure of the detector.

There is a second, compounding reason: **operators stop publishing SupGP ephemeris for
satellites they have abandoned.** That is why only 1 of 65 documented-abandoned GEO objects
appears in our tracked fleets at all. The signal disappears exactly when the interesting thing
happens — the same structural blind spot recorded in [[RESULTS - Ground Truth]].

**Pre-registered prediction:** on Jul 29, the abandoned row (Intelsat IS-11, NORAD 32253,
`GEO/ID`) reports `no rhythm yet`. If it reports `WENT QUIET`, that is *surprising* and worth
investigating — it would mean the object is still spiking, which would contradict GCAT's
classification of it as abandoned.

---

## The scoring recipe — run this on Jul 29

```bash
cd "C:\Space\06 Code"
python detect.py --learn-baseline --pct 99      # re-learn; the bar will be a week old
python quiet.py --group intelsat
python quiet.py --group ses
```

Join each verdict to `quiet_exam.csv` on NORAD, keep rows where `in_exam_set == yes`, and fill
in exactly this table:

| measure | formula | pre-registered expectation |
|---|---|---|
| **False-alarm rate** | `WENT QUIET` among **active-stationkept** ÷ active-stationkept objects that reached ≥3 spikes | **0%.** Anything above ~5% should block the claim |
| **Catch rate** | `WENT QUIET` among **abandoned** ÷ abandoned objects that reached ≥3 spikes | **denominator expected to be 0** — report as *not measurable*, never as 0% |
| **Gate coverage** | objects reaching ≥3 spikes ÷ 67 | unknown; report it — it bounds everything above |

**Report all three numbers including the denominators.** A false-alarm rate of "0 of 4" is a
very different statement from "0 of 66", and only the denominator distinguishes them.

### What a good result actually looks like

- **Good:** most of the 66 healthy objects clear the ≥3-spike gate and report `on rhythm`;
  zero report `WENT QUIET`. That is a **measured false-alarm rate on 66 documented non-events**
  — the first real one this company has had, and a genuinely quotable number.
- **Bad, and the one to watch for:** any healthy object reporting `WENT QUIET`. This is the
  precise failure `_test_quiet.py` found and fixed before the gate opened (a burst of spikes
  inside one day producing a 0.25-day "rhythm"). The fix is in; this exam is what confirms it
  on real data rather than on synthetic cases.
- **Not bad, despite appearances:** a catch rate of nothing. Expected, explained above, and it
  must be *stated* rather than quietly omitted.

---

## Honesty notes

- **Every row in `quiet_exam.csv` is marked `verified` or `assumed`** (131 / 9), and carries
  the GCAT stamp it was read from.
- **GCAT's classification is not fully independent of us.** McDowell derives orbit type from
  the same public catalog our detector reads. He applies independent judgement and curation,
  which is why this is usable as documented status — but it is not an operator statement, and
  it should not be described to a buyer as one.
- **The issue asked for pre-registered verdicts for "the 44 objects with ≥3 spikes."** That 44
  is a **Starlink** figure from [[RESULTS - The Quiet Detector]], and **no documented
  per-satellite status exists for Starlink** — so those 44 cannot be graded. This exam instead
  pre-registers a verdict for **every object where documented status exists**, keyed by NORAD,
  so whichever objects clear the gate on Jul 29 already have an expectation on record. That is
  a change from the issue's wording, made deliberately and recorded here.
- **The exam set is 67, not 140.** The other 73 documented objects are real but we do not track
  them, so they cannot be scored. They stay in the CSV with `in_exam_set = no` in case fleet
  coverage grows.
