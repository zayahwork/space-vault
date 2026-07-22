---
date: 2026-07-22
status: first result the detector did not grade itself
code: "06 Code/verify.py"
snapshot: 2026-07-22 0200Z
---

# 🔬 RESULTS — checked against the catalog's own history

> [!success] The headline
> The top suspects move **11.3x more** than satellites the detector called ordinary, and
> **72%** of them clear a bar that only **11%** of ordinary satellites clear.
> **The detector is tracking real movement.** This is the first number here that
> `detect.py` did not produce about itself.

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
