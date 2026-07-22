---
date: 2026-07-22
status: first result the detector did not grade itself
code: "06 Code/verify.py"
snapshot: 2026-07-22 0200Z
---

# 🔬 RESULTS — checked against the catalog's own history

> [!note] Window change 2026-07-22 (issue 018) — **the Starlink headline did not move, and here is the proof**
> `verify.py` no longer hardcodes a ±3-day step window; it now takes a regime-aware,
> one-sided window (see [[RESULTS - Beyond Starlink]] for why). **LEO deliberately stays at
> ±3 days**, because the measured Starlink catalog update interval is a **median of 0.27
> days** (95th 0.98 d, n=2,701 intervals) — the LEO catalog is not late, so widening the
> window there would only feed the control bar more noise for no gain.
>
> So every number on this page is unchanged, by construction rather than by hope. Checked
> anyway: recomputing all 80 cached objects under the old ±3d and the new window gives
> **identical steps on 80 of 80**. Nothing on this page was re-baselined quietly.

> [!success] The headline (hardened 2026-07-22, two snapshots)
> **~two-thirds of the top suspects** clear a movement bar that only **~10% of ordinary
> satellites** clear — replicated on two independent snapshots (72% vs 11% at 0200Z,
> 68% vs 11% at 0800Z). The **entire flagged list**, all 489 objects, verifies at ~4x the
> control rate. **The detector is tracking real movement.** This is the first number here
> that `detect.py` did not produce about itself.

## 🔬 Hardened 2026-07-22 (CTO ask): does it hold at bigger samples?

| sample | median step, suspects vs controls | over the controls' bar |
|---|---|---|
| top 25 | 8.3x | 64% vs 12% |
| **top 75** | **11.3x** | **72% vs 11%** |
| top 200 | 9.2x | 68% vs 10% |
| top 400 (near the whole flagged list) | 5.4x | 41% vs 10% |

**It holds where it matters and declines exactly where it should.** The list is ranked;
rank 300–400 are objects that barely cleared the flag threshold, so a weaker signal down-list
is the ranking working, not the finding failing. If the detector were noise, that column would
be flat. Even the *bottom* of the list clears the bar 4x more often than controls.

## 🔬 Hardened again, same day: full list + a second, independent snapshot

The table above is all one snapshot (0200Z). The stronger test is whether the same structure
shows up on a *different* snapshot with a *different* candidate list. Re-ran everything on
0800Z — six hours later, freshly ranked, **every one of the 489 flagged objects checked**
(nothing sampled), with a control pool pushed to 600:

| sample (0800Z snapshot) | median step ratio | over the controls' bar |
|---|---|---|
| top 25 | 5.4x | 56% vs 12% |
| top 75 | 23.8x | 68% vs 11% |
| top 200 | 9.2x | 68% vs 10% |
| **all 489 flagged (the whole list)** | **4.8x** | **37% vs 10%** |

Same shape, second snapshot: strong at the top, declining down-list, never anywhere near 1x.

> [!warning] Which number to quote
> The **median ratio is volatile** — 11.3x at 0200Z became 23.8x at 0800Z for the same top-75
> cut. That's what medians of a heavy-tailed quantity do at n=75; neither number is "the"
> number. The **over-the-bar rate is stable** (72% → 68%) and is the one to stake credibility
> on. **Say it this way:** *"about two-thirds of our top candidates show independent movement
> in the catalog's own history, against a 10% base rate for matched controls — and the full
> flagged list, all ~490 objects, still verifies at nearly 4x the control rate."* Retire the
> bare "11.3x" from anything customer-facing; it was true once, on one day, at one cut.

Persistence cross-check (all 319 persistent vs all 222 single-look suspects): persistent ones
verify better — **46% vs 37%** over the bar, median step 0.110 vs 0.072 km. Both far above the
10% control base rate; the two filters agree in the right direction.

## Why this had to happen

Everything before this was self-graded. `detect.py` ranks satellites by how far the
operator's orbit sits from the public catalog *right now*, and nothing in it had ever been
compared against whether the satellite actually moved. A ranked guess with a good story is
still a guess.

`verify.py` checks with a **different method on differently-shaped data**: 30 days of
altitude history from Space-Track, looking for the step a burn leaves behind. That's the
v0.1/v0.2 chart detector that went 3/3 on ISS reboosts — it shares nothing with the
SupGP-vs-catalog comparison except the satellite.

> [!important] The control group is the whole point
> *"72% of our suspects show a burn"* means nothing alone — maybe 72% of **all** Starlinks
> show a burn in any given week, in which case we've detected nothing. So every run also
> pulls satellites `detect.py` called **ordinary**, matched on catalog age and regime, and
> runs identical logic on them. **The difference between the two groups is the finding.**
> The bar isn't ours either — it's set at the 90th percentile of the controls.

## Result — top suspects vs matched controls

| | suspects | controls |
|---|---|---|
| n | 75 | 75 |
| **median altitude step** near the snapshot | **0.306 km** | **0.027 km** |
| 90th percentile | 4.960 km | 0.131 km |
| **over the bar** (0.131 km) | **54 (72%)** | 8 (11%) |

- Suspects move **11.3x** more than controls
- They clear the bar **6.7x** as often
- Checked at n=25 first (8.3x / 5.3x) — **the signal got stronger with more data**, which
  is the right direction

## ⚠️ We published something wrong — and now we know

[[RESULTS - Maneuver vs Stale]] states in writing that the >500 km gaps are *"likely decay
or bad TLE, not a maneuver."* That was a guess, published. Checked against 30 days of
altitude history for all 29:

```
decaying, gate confirmed      5
NOT decaying                 24   <-- the published reason was wrong
no usable history             0
```

Only **17%** are actually falling out of the sky. The real breakdown of the 24:

| what they actually are | n | evidence |
|---|---|---|
| **freshly launched, climbing** | 16 | all 2026 launches, sitting at 325–460 km — below the ~475 km working shell, still raising orbit |
| **old satellites, flat history** | 8 | at working altitude, no altitude change at all — genuinely bad or mismatched element sets |

> [!note] The gate itself is still right, for the wrong reason
> Keeping these out of the candidate list was correct — none of them are station-keeping
> maneuvers. But we said *"decay"* and it's mostly *"a satellite that launched last week and
> is still climbing."* **Fix the sentence in [[RESULTS - Maneuver vs Stale]] before this goes
> to anyone.**

## ⚠️ What this does NOT prove

- **Not operator ground truth.** `GP_HISTORY` is the *public catalog's* history, so it shares
  the catalog side with `detect.py`. It's independent of the operator data, the age-binning,
  and the persistence logic — but two of our own methods agreeing is not proof a satellite
  burned. Real ground truth = operator maneuver logs, which aren't public for Starlink.
- **One snapshot, one day.** 2026-07-22 0200Z only.
- **The verifier is partly blind.** Starlink uses electric thrusters — slow, gradual pushes
  that don't leave a clean step. Some of the 28% that didn't clear the bar are probably real
  maneuvers this method can't see (blind spot #1, known since STARLINK-2083). That's a limit
  of the *verifier*, not of `detect.py`.

## Reproduce it

```bash
cd "C:\Space\06 Code"
python verify.py --flags          # the 29 data-quality flags
python verify.py --top 75         # suspects vs matched controls
```

Space-Track responses are cached in `06 Code/verify_cache/`, so re-runs are free and don't
hammer their API.
