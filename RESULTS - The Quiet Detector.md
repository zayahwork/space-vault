---
date: 2026-07-22
status: alert mode live; cadence built + now tested, one false-positive bug fixed, waiting on archive
code: "06 Code/detect.py --mode alert, 06 Code/quiet.py"
---

# 🔇 RESULTS — the detector can now say "nothing happened"

> [!success] What changed today
> 1. **Persistence went live** (second catalog snapshot banked at 0750Z): of 488 candidates,
>    **298 survived a second independent look, 190 are unconfirmed, 221 cleared.** ~39% of
>    yesterday's list didn't repeat.
> 2. **Alert mode exists.** `detect.py --mode alert` judges today against a bar learned from
>    *past* snapshots and held fixed — so **zero is now a possible answer.** Today: 122 over
>    the bar.
> 3. **Cadence machinery built** (`quiet.py`) — the "satellite stopped maneuvering" insurer
>    signal. It runs, and it **refuses**: 0.24 days of archive, needs 7. Unblocks itself
>    ~2026-07-29.

> [!bug] 🐞 Found and fixed 2026-07-22 — cadence would have false-flagged healthy satellites
> `quiet.py` had **no tests**. Writing them (`_test_quiet.py`, 15 cases) turned up a real
> defect in `judge()`, and it landed on exactly the wrong population.
>
> The typical spike-to-spike interval was taken straight from the median of observed spikes,
> with no floor. An object flagged on three **consecutive 6-hourly snapshots** — which is what
> a PERSISTENT SUSPECT looks like — got a "typical rhythm" of **0.25 days**. The next ordinary
> overnight sampling gap of **0.70 days** is 2.8× that, so the satellite was reported as
> **WENT QUIET**: healthy hardware declared a possible loss of control.
>
> ```
> before: judge(spikes 6h apart, silent 0.7d) -> {'status': 'WENT QUIET', 'typical_days': 0.25}
> after : judge(same)                          -> 'on rhythm'
>         judge(genuine 5d rhythm, silent 15d) -> 'WENT QUIET'   (real signal still fires)
> ```
>
> Fix: floor the typical interval at **1.0 day** (`MIN_TYPICAL_DAYS`) — a rhythm cannot be
> measured finer than we sample, and station-keeping cadence is measured in days. A burst of
> spikes inside one day describes *our archiving cadence*, not the satellite's behaviour.
>
> **Why it mattered even though cadence is blocked:** the 7-day gate was hiding it, not
> preventing it. **44 objects already have ≥3 spikes on record**, so this would have fired the
> moment the gate opened ~Jul 29 — as a wave of false "your satellite has failed" alerts, on
> the persistent suspects, which are the objects the product exists to watch.

## The problem (from [[Plan - The Quiet Detector]])

Every threshold so far was a percentile of *today's crowd* — which always returns the top 5%,
even on a day nothing moved. Fine for ranking. Wrong for alerting, and structurally unable to
see the insurer signal: a satellite that **stops** station-keeping drops *off* a ranked list
instead of onto it.

## Part 1 — alert mode (live now)

`--learn-baseline` learns each cohort's normal band (age bin × regime) from **every scoreable
snapshot**, and writes `baselines.json` with provenance stamped inside — which snapshots, what
percentile, when. `--mode alert` then flags only what exceeds that stored bar.

- Learned at the **99th percentile** from 2 snapshots (0200Z, 0750Z)
- Today: **122 objects** over a bar set *before* today
- A quiet day returns **zero and says so plainly** (tested: quiet-day-flags-zero is in
  `_test_detect.py`, plus: a cohort with no stored bar **refuses to invent one** rather than
  silently falling back to ranking)
- Rank mode unchanged — they answer different questions

> [!warning] The bar is two snapshots old
> A bar learned from one day only knows one day's weather. The tool prints this warning
> itself. **Re-learn weekly** as the archive grows: `python detect.py --learn-baseline --pct 99`.

## Part 2 — cadence (`quiet.py`, built, refusing honestly)

Tracks each object's **own rhythm**: spikes over its stored bar, the typical interval between
them, and how long it's been silent. "Went quiet" = silence > 2.5× the object's own typical
interval, with ≥3 spikes on record before any judgement.

Current output, verbatim intent:

```
archive span 0.24 days — a rhythm claim needs 7.
'this object went quiet' and 'we only just started watching' look identical,
and we will not pretend otherwise. Unblocks itself ~2026-07-29.
```

Same pattern as the persistence refusal — the machinery is done and finds its own data as the
archiver banks ~4 scoreable snapshots/day.

## What can and cannot be claimed (for the pricing page)

| claim | status |
|---|---|
| "we can tell you nothing happened today" | ✅ live (`--mode alert`) |
| "we can tell you which satellites moved beyond their normal" | ✅ live, bar auditable in `baselines.json` |
| "we can tell you a satellite in your book stopped station-keeping" | 🕒 **built, not yet claimable** — needs ~1 week of archive, self-unblocks |

## Reproduce it

```bash
cd "C:\Space\06 Code"
python detect.py --learn-baseline --pct 99   # re-learn as archive grows
python detect.py --mode alert                # zero is a possible answer
python quiet.py                              # cadence; refuses until ~Jul 29
python _test_detect.py                       # 9 cases - persistence logic
python _test_quiet.py                        # 15 cases - cadence logic
```

> [!warning] Test-count correction (2026-07-22)
> This block previously claimed `_test_detect.py` was **"12 cases, incl. alert mode."** It is
> **9 cases, and none of them touch alert mode** — they are all persistence. Counted, not
> assumed. Alert mode is still exercised only by running it, so the stored-bar path
> (`stored_cuts`, `learn_baselines`) remains untested code carrying a published claim.
