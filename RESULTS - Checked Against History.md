---
date: 2026-07-22
status: first result the detector did not grade itself
code: "06 Code/verify.py"
snapshot: 2026-07-22 0200Z
---

# 🔬 RESULTS — checked against the catalog's own history

## 🧪 Unseen-data holdout (issue 033, 2026-07-23) — "did you tune on what you tested?"

The diligence question, answered in writing and enforced in code: `06 Code/holdout.py`
(tests: `_test_holdout.py`, 26 cases). **Cutoff 2026-07-23 00:00Z** — every detector
constant, the verify window table (issue 018), the observability correction (issue 003)
and the stored alert bars (learned 2026-07-22 19:16Z from snapshots ≤ 07-22/1400Z, checked
against provenance, not assumed) were fixed at or before it. A snapshot counts as unseen
only if captured **strictly after** the cutoff; the script refuses to run if the bars'
provenance contains a post-cutoff snapshot, and refuses to improvise if no unseen snapshot
exists yet.

**First run, on the first unseen snapshot (2026-07-23/0200Z), top-75, production code path**
(`detect.analyze` rank mode → `verify.select_groups` → controls' own 90th-pct bar):

| forward reach (matched) | tuned set (Jul 22) | **UNSEEN (post-cutoff)** |
|---|---|---|
| 0.00 d | 76% / 11% (0200Z) · 93% / 11% (0800Z) | **76% / 11%** (31/41 vs 8/75) |

- **At matched reach the unseen day reproduces the tuned floor exactly** — 76% of scoreable
  unseen suspects clear the bar vs 11% of matched controls, the same zero-reach value the
  published sweep recorded. The separation is not an artifact of tuning on July 22's data.
- **The settled holdout number is still pending, and must be** — the +3 d forward window
  needs published orbit determinations that don't exist yet. Measured from the fetched
  history itself (never the wall clock: GP_HISTORY materializes ~6–12 h late, so a fetch
  5.8 h after the snapshot contains **0.00 d** of forward reach), the run labels itself
  PROVISIONAL and says when to re-run. **Do not quote a settled holdout figure externally
  until a re-run at ≥0.5 d reach lands in this table.**
- **34 of the unseen top-75 are a fresh launch batch** (analyst-range NORADs 100012–100056,
  climbing at 280–490 km gaps, 2–3 history records each) — unscoreable yet, excluded from
  the denominator per the standing thin-history rule, not counted as misses.

**Ground-truth split (GEO −3/+14 d window):** the 16 rows that existed at issue 015 *chose*
the window and may never be quoted as evidence for it again (13/14 scoreable caught —
tuning-set performance, not validation). The three rows added afterward by issue 026 —
Astra 3B 2025-09-08, Intelsat 1002 2025-02-28, AMC 11 2025-06-10 — never touched any
tuning decision: **3/3 caught by the frozen window**. Small n and single-sourced tier, but
it is the first window evidence that is not circular. Future ground-truth rows land in the
holdout side automatically (frozen key list in `holdout.py`).

**Reusable weekly:** `python holdout.py --cutoff <new freeze instant>` — the archive grows
every 6 h, so genuinely unseen data accumulates daily. Run saved to
`06 Code/output/holdout_033.json`.

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

> [!danger] ⬆️ **THE HEADLINE MOVED — 68–72% was an UNDERESTIMATE. Re-measured: 96% vs 11%** (issue 003, 2026-07-22)
> The 68–72% figure was measured within minutes of the snapshot it scored. At that moment
> the **forward half of the ±3-day window contained no data** — the catalog had not yet
> published the orbit determinations that show the burns. Re-scored on the same two
> snapshots once they had aged, the same top-75 suspects give **96% vs 11%**.
>
> Measured, not argued — top 75 on 0200Z, sweeping how much of the forward window exists:
>
> | forward reach available | bar (km) | suspects over | controls over |
> |---|---|---|---|
> | 0.00 d ← *what the published run could see* | 0.151 | 57/75 (**76%**) | 8/75 (11%) |
> | 0.25 d | 0.151 | 70/75 (93%) | 8/75 (11%) |
> | 0.50 d | 0.156 | 72/75 (**96%**) | 8/75 (11%) |
> | 1.50 d / 3.00 d | 0.156 | 72/75 (96%) | 8/75 (11%) |
>
> At zero forward reach this reproduces **76%**, next to the published 72% — the mechanism
> checks out. The rate **plateaus by ~0.5 days** and does not climb further, so 96% is the
> settled value, not a number that keeps drifting up.
>
> **The controls stay pinned at 11% throughout.** That is what makes this a real correction
> and not general inflation: only the suspects moved.
>
> **What this costs us:** a same-day verification at LEO under-reports. Any figure quoted
> from a run fired immediately after a snapshot is a floor, not the result. Re-run ~12 hours
> later before quoting.

> [!success] The headline (re-measured 2026-07-22 at full observability)
> **96% of the top 75 suspects** clear a movement bar that only **11% of ordinary
> satellites** clear, on both snapshots. The separation survives to a much longer list —
> **52–63% at n=300 against a 10% control rate** (table below). **The detector is tracking
> real movement.** This is the first number here that `detect.py` did not produce about
> itself.
>
> ~~68–72% vs ~10%~~ — struck, not deleted: it was measured too early, see the callout above.

## 📏 Larger-n hardening under the production window (issue 003, 2026-07-22)

Measured **once**, by `06 Code/hardening.py`, under the window the live pipeline actually
runs (`verify.window_for_regime` — LEO −3/+3 d after issue 018) and with the groups chosen
by the same `verify.select_groups` the production path calls. So a bigger n is the same
measurement with more objects in it, not a different measurement.

| snapshot | n | bar (km) | median ratio | **SUSPECTS over bar** | CONTROLS over bar |
|---|---|---|---|---|---|
| 0200Z | 25 | 0.085 | 172× | **23/25 (92%)** | 3/25 (12%) |
| 0200Z | 75 | 0.156 | 32× | **72/75 (96%)** | 8/75 (11%) |
| 0200Z | 150 | 0.114 | 11× | **119/150 (79%)** | 15/150 (10%) |
| 0200Z | 300 | 0.153 | 5.4× | **155/300 (52%)** | 30/300 (10%) |
| 0800Z | 25 | 0.145 | 91× | **23/25 (92%)** | 3/25 (12%) |
| 0800Z | 75 | 0.149 | 79× | **72/75 (96%)** | 8/75 (11%) |
| 0800Z | 150 | 0.124 | 40× | **129/150 (86%)** | 15/150 (10%) |
| 0800Z | 300 | 0.140 | 9.0× | **188/300 (63%)** | 30/300 (10%) |

**It sags with n, exactly as a ranked list should.** 96% at the top 75, 79–86% at 150,
52–63% at 300. The list is ranked by how far each object sits above its own age-bin bar, so
objects at rank 250 barely cleared the flag threshold and a weaker signal down there is the
ranking working. If the detector were noise this column would be flat at ~10%.

**Even at n=300 the separation is 5–6× the control rate**, and the control rate holds at
10% at every n — which it must, since the bar is the controls' own 90th percentile. That
column is a sanity check, not a second measurement, and it is printed beside the suspects'
every time precisely so nobody reads the left column alone.

**The honest asymmetry between the two snapshots.** At n=300 the two snapshots disagree
more than at small n (52% vs 63%). Down-list ranks are where the two candidate lists differ
most, so that spread is the real uncertainty on any large-n claim — quote the range, not the
better half.

> [!note] Both rows are settled, not provisional
> The rates above plateau by ~0.5 days of forward reach and do not move after
> (checked at n=75 and n=300 on both snapshots). These are the aged values, not the
> too-early ones that produced the old 68–72%.

## 🔬 Hardened 2026-07-22 (CTO ask): does it hold at bigger samples? *(superseded by the table above — kept for history; measured before the observability correction)*

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
