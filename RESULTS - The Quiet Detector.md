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
> `quiet.py` had **no tests**. Writing them (`_test_quiet.py`, 14 cases) turned up a real
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
python _test_quiet.py                        # 14 cases - cadence logic
python _test_alert.py                        # 19 cases - alert mode's stored-bar path
python _test_learn.py                        # 15 cases - learning the bar from the archive
python _test_orbital.py                      # 24 cases - the orbital math underneath it all
```

> [!success] ✅ Orbital math tested (2026-07-22) — `_test_orbital.py`, 24 cases, **no bugs found**
> `altitude_km`, `descent_km_per_day`, `epoch_jd`, `capture_jd` and `rms_difference` sit
> beneath every figure in every RESULTS note, and nothing gates them — there is no "refuses
> until the archive grows" to hide a mistake behind. A flipped sign flows straight into the
> published numbers and looks exactly like a real result.
>
> These are the only functions here with **external ground truth**, so they are checked
> against physics rather than against themselves:
>
> | check | result |
> |---|---|
> | geostationary altitude (textbook 35,786 km) | **35,786.0 km** |
> | ISS mean motion (flies 400–430 km) | **415.6 km** |
> | Starlink mean motion (shell ~550 km) | **548.4 km** |
> | Kepler's third law, written via rad/s instead of period | agrees to **<1e-6 km** at 4 orbits |
> | TLE epoch 24001.5 → 2024-01-01 12:00 UTC | **JD 2460311.0** |
> | J2000 (2000-01-01 12:00 UTC), by definition | **JD 2451545.0 exactly** |
>
> Also pinned: the **sign convention the whole deorbit filter rides on** — positive
> `MEAN_MOTION_DOT` gives a *negative* drop (falling), negative gives positive (being
> raised), zero gives exactly zero. If that ever inverts, the detector separates precisely
> the wrong population and every regime-split number in these notes inverts with it. The
> OMM `n-dot/2` convention is confirmed applied as **2×, not 1×** — using the raw value would
> halve every descent and reclassify deorbiting hardware as station-keeping. The published
> **0.4 km/day** threshold sits at `MEAN_MOTION_DOT` **6.5232e-04**, asserted from both sides.
> `rms_difference` is 0 against itself, symmetric in its arguments (the guard on starting
> from the *later* of the two epochs), and grows with the size of the element change.
>
> **No defect found.** The math was already right.

> [!success] ✅ `learn_baselines` tested (2026-07-22) — `_test_learn.py`, 15 cases, **no bugs found**
> The last untested link in the alert-mode chain, and the highest-consequence one: it writes a
> plausible number into a file stamped with real provenance, and every later run trusts it.
> Nothing downstream can tell a poisoned bar from an honest one.
>
> The archive is faked so every expected percentile is checkable by hand (percentile set to 50
> — a median of a known list can be verified by eye; a 99th of 30 values cannot).
>
> Pinned: a 5,000 km nonsense orbit is excluded from the bar **and** from the band's `n`
> (leaking it would move the test median 15.5 → 16.0) · falling hardware learns a separate,
> much higher bar and leaves the station-keepers' untouched (15.5 vs 114.5) · a thin band
> (n=5) falls back to the whole regime instead of a percentile off five objects · bands are
> half-open, so an age of exactly 24.0 h lands in 24–48 · a **negative** catalog age — the
> time-travel bug `load_gp` exists to prevent — is dropped rather than folded into the lowest
> band · every scoreable snapshot pools in, and skipped or empty ones are not claimed as
> provenance · an empty archive exits loudly instead of writing a baseline full of nothing.
>
> **No defect found.** Worth stating plainly rather than dressing up: this one was already
> correct.

> [!warning] Test-count correction (2026-07-22)
> This block previously claimed `_test_detect.py` was **"12 cases, incl. alert mode."** It is
> **9 cases, and none of them touch alert mode** — they are all persistence. Counted, not
> assumed.

> [!success] ✅ Alert mode's stored-bar path is now tested (2026-07-22) — `_test_alert.py`, 19 cases
> The code carrying *"zero is a possible answer"* had no tests. It does now, and the headline
> claim is pinned by construction: **40 objects all sitting under a stored bar return zero
> flags**, while the *same population* in rank mode still has to hand somebody back. That
> contrast is the feature, and it is now a test rather than a sentence.
>
> Also pinned: the stored bar decides (not today's crowd) · `--min-km` still floors it · the
> 500 km plausibility gate runs first in alert mode too · an age band with **no** stored bar
> flags nothing rather than borrowing today's percentile · a baseline stamped for another
> constellation is refused, not applied · provenance survives the round trip.
>
> **One latent bug found and fixed.** `load_baselines` returned `cuts` with only the regimes
> present in the file. `classify()` reads `None` as *"rank mode"*, so a truncated or
> hand-edited baseline missing a regime would have **silently ranked that entire regime while
> the run still called itself alert mode** — the one failure here that leaves no trace in the
> output. `load_baselines` now guarantees a key per regime (`{}` = refuse loudly).
> Not live: `learn_baselines` always writes both regimes, so no shipped file was affected.
> An *empty* regime is different from a missing one and was already handled correctly —
> `baselines_oneweb.json` is genuinely shaped that way, since nothing up there is decaying.
>
> Alert mode re-run end-to-end after the change: **205 objects, unchanged.**
