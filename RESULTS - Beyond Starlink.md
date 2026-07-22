---
date: 2026-07-22
status: OneWeb clean; GEO regime-aware + GEO-shaped verifier built; early corroboration at n=4, no operator ground truth
code: "06 Code/detect.py --group oneweb|intelsat|ses, 06 Code/verify.py (LEO), 06 Code/verify_geo.py (GEO)"
snapshot: 2026-07-22 0800Z
---

# 🌍 RESULTS — the detector leaves Starlink

> [!success] The one-line version
> **OneWeb: the method works, full stop** — suspects show 80% independent-movement
> confirmation vs a 10% control base rate.
>
> **GEO: the verifier was the problem, and it is now fixed.** The altitude-based verifier was
> blind to the dominant GEO maneuver by construction — north–south station-keeping is ~95% of
> the budget and changes *inclination*, not altitude. `verify_geo.py` watches inclination and
> longitude drift instead, and **SES, previously a flat miss, now separates from its controls
> on both**; Intelsat separates on drift.
>
> **Still not proven.** n=4 suspects per fleet, and the most dramatic column (drift) is the
> least independent of the detector, while the most independent one (Intelsat inclination)
> came back *negative*. Early corroboration, not a result.

Everything before today was one constellation. Same pipeline — detect (age-aware ranking),
persistence (independent looks), verify (Space-Track altitude history vs matched controls) —
run unchanged on three more, chosen because GEO is where the big insured birds live and
station-keeping there is the textbook rhythm.

## OneWeb (LEO, 651 objects) — generalizes cleanly

| stage | result |
|---|---|
| detect | 10 suspects at the 95th percentile of their age bins |
| persistence | **5 of 10 flagged in 2/2 independent looks** |
| verify vs controls | median step **0.129 km vs 0.003 km**; **80% over the controls' bar vs 10%** |

The 80%-vs-10% is a *stronger* separation than Starlink's own top-tier (68–72%). Different
operator, different orbit shell, different maneuver style — same signal. This is the
"it's a method, not a Starlink quirk" evidence.

## Intelsat (GEO, 44 objects) — promising, unproven

- 3 suspects, and the age filter earned its keep: **ranking on raw gap alone would have
  flagged 25 of 44 objects; age-awareness cut that to 3** (88% of the naive list was just
  an old catalog entry, which at GEO is most of them).
- Verify: **all 3 suspects over the controls' bar** (vs 1/3 controls), median step 16.3x
  the controls'. Right direction — but n=3 is an anecdote with a table around it.

## SES (~~GEO~~ **mixed GEO+MEO**, 68 objects) — the honest miss

> [!warning] Correction 2026-07-22 — SES is not a GEO fleet
> Measured, not assumed: **38 of the 68 sit at GEO (35,786 km) and 30 sit at 8,066 km** —
> that is O3b, SES's MEO constellation. Calling the whole fleet "GEO" and judging it with
> one set of constants put half the population under the other half's physics. This may be
> part of why SES shows no signal below; it is not a *sufficient* explanation, and the miss
> stands until something corroborates it.

- 3 suspects, 75% of the naive list was stale.
- Verify (**altitude**): **NO SIGNAL.** Suspects' median step 0.8x the controls', 1/3 vs 1/3
  over the bar. The suspects look like everything else.

Better we say it first: **on today's data, SES detections are not corroborated.**

> [!success] Revisited 2026-07-22 with a GEO-shaped verifier — the miss was the instrument
> `verify_geo.py` re-ran the same fleet on the observables GEO burns actually move, and SES
> separates from its controls on **both**. The altitude verifier was not finding nothing;
> it was looking at the wrong axis. Numbers in the section below.

## The detector now knows which physics it is in (issue 002, 2026-07-22)

Before today the same code, the same table and the same confident tone came out whatever
altitude it was pointed at. It ran on GEO — nothing crashed — but **two of its three filters
cannot fire up there**, and it never said so.

| | starlink (LEO) | intelsat (GEO) | ses (mixed) |
|---|---|---|---|
| median altitude | 475.2 km | 35,786.6 km | 35,786 / 8,066 km |
| km/day range | −55.44 … +24.18 | −0.077 … +0.160 | −0.085 … +0.192 |
| objects "on the way down" | 1,021 | **0** | **0** |
| median gap | 9.68 km | 7.44 km | 0.97 km |

**1. The decay split is inert above LEO, and now says so.** It needs an object to lose
0.4 km/day. Nothing at GEO comes within a factor of two, because there is no atmosphere to
lose it to. Printing `on the way down: 0` as though it had looked and found none is lying by
omission — the run now prints `DECAY SPLIT INERT here`, names the range the population
actually spans, and states that 0 means **not applicable**.

**2. The floor was a Starlink number wearing a lab coat.** `--min-km 5.0` is about *half*
Starlink's median gap but *five times* SES's — the same nominal number is ~10× more
restrictive relative to the population it judges, silently excluding most of a GEO fleet from
ever being flagged. Floors are now per regime: **LEO 5.0 · MEO 2.0 · GEO 1.0 km**.

**3. The floor is stamped per OBJECT, not per constellation** — because operators do not
respect the boundary. SES's two halves are now judged against 1.0 and 2.0 km respectively. A
fleet-wide scalar could only have been wrong for one half.

> [!danger] The GEO floor is a judgement, not a measurement
> 1.0 km sits above the sub-km noise and leaves normal station-keeping reachable, and that is
> the whole argument for it. It has **not** been validated against a real GEO maneuver record.
> Evidence it may still be wrong: every one of Intelsat's 44 objects clears it (median gap
> 7.44 km), so for that fleet the floor does no filtering at all — while for SES (median
> 0.97 km) it bites hard. Until there is ground truth, this is the least defensible constant
> in `detect.py`, and it should not be tuned to make output look better.

Baseline files now stamp `orbital_regime` and the floors actually applied
(`baselines_ses.json` records `[1.0, 2.0]` and `mixed`, because one scalar would be a lie
about how that bar was made). Starlink's numbers are **unchanged** — verified figure by
figure across the whole run.

Covered by `06 Code/_test_geo.py`, 22 cases.

## 🛰️ The GEO verifier — `verify_geo.py` (built 2026-07-22)

Point 1 below said the fix was "a GEO-shaped verifier (longitude drift, inclination)".
Built. The mechanism it exists for, stated plainly:

> **North–south station-keeping is ~95% of a GEO bird's station-keeping budget** (~45–50 m/s
> a year against ~2 m/s for east–west). N–S burns fight the Sun and Moon pulling the orbit
> plane over, and what they change is **inclination — not altitude.** The dominant GEO
> maneuver was invisible to an altitude-only verifier *by construction*, not by bad luck.

Same control-group discipline as `verify.py`: suspects against objects `detect.py` called
ordinary, drawn from the same catalog-age range, identical logic, bar set at the controls'
90th percentile. 60 days of GP_HISTORY, steps taken within ±3 days of the snapshot.

| | Intelsat | SES |
|---|---|---|
| **inclination** (N–S, the big burn) | median 1.21×, **0/4 over bar vs 13%** → *no signal* | median **15.0×**, 1/4 vs 2/15 → separation |
| **longitude drift** (E–W) | median **2.24×**, **2/4 (50%) vs 13%**, 3.75× | median **63.0×**, **4/4 (100%) vs 13%**, 7.50× |

**What changed and what didn't.** SES — the fleet the altitude verifier called a flat miss —
separates on both observables. Intelsat separates on drift only, and its inclination result
is *negative*: suspects cleared the controls' bar **less** often than the controls did.

> [!warning] The two observables are NOT equally independent — read before quoting
> `detect.py` ranks on RMS position difference over 6 h, which is dominated by **along-track**
> error — essentially a disagreement about mean motion. **Longitude drift is derived from
> mean motion.** So a big drift step and a big detector gap are partly two views of the same
> quantity, and that column will tend to agree with the detector *by construction*.
>
> **Inclination does not share that axis** — a plane change barely moves along-track position
> over six hours — so it is much closer to genuinely independent evidence.
>
> Which means the honest reading is uncomfortable: **the most dramatic number here (SES 63×
> on drift) is the weakest kind of evidence, and the most independent one (Intelsat
> inclination) came back negative.** When the two disagree, believe inclination.

> [!danger] n = 4
> Four suspects per fleet. A 95th-percentile ranking of 44–68 objects cannot produce more.
> Every ratio above is computed off single figures and is an anecdote with a table around it,
> whichever way it points. This does not become a result until the GEO archive is weeks deep.

A verdict now requires **both** readings to agree — median ratio ≥1.2 **and** bar-clearing
rate ≥1.5×. The first draft used `or`, which reported Intelsat's inclination as a separation
on the strength of a 1.21× median while suspects were clearing the bar 0% against the
controls' 13%. Reading the flattering half of two disagreeing numbers is how a detector
starts believing itself.

Covered by `06 Code/_test_verify_geo.py`, 21 cases — including the textbook cross-check that
a satellite 1 km above geostationary drifts west at **0.01284 °/day** (published value
0.0128), derived from `detect.py`'s own Kepler and the sidereal day.

## Why GEO verification was weak by construction (not an excuse — a mechanism)

1. ~~**The verifier watches altitude.**~~ **Fixed 2026-07-22** — see the GEO verifier above.
   GEO station-keeping is mostly east–west and north–south burns that barely change altitude,
   so the step the altitude verifier looks for is close to invisible. It was built for LEO
   reboosts.
2. **n=3 against n=3 controls.** A 90th-percentile bar drawn from 3 controls is barely a
   bar. The population is 44–68 objects, so 95th-percentile ranking can only ever produce
   a handful of suspects per snapshot.
3. **GEO operators refresh SupGP slower** — median 1 independent look over our 6h window,
   so persistence can't confirm anything at GEO yet. It will, as the archive grows.

All three get better automatically: the daily task ([[RESULTS - Alert Log]]) banks every
snapshot, and a week of GEO data supports a real n and a real rhythm.

## Alert mode now covers all four

Per-group baselines learned at the 99th percentile (`baselines_starlink.json`,
`_oneweb`, `_intelsat`, `_ses` — provenance stamped inside; the old single-group
`baselines.json` is gone). The scheduled **Maneuver Alert** task scores every new snapshot
for all four groups. Bars are 3 snapshots old — **re-learn weekly** as the archive grows.

## What to claim, commercially

| claim | status |
|---|---|
| "the method is constellation-agnostic in LEO" | ✅ OneWeb, 80% vs 10% |
| "we monitor GEO, where the insured value is" | ✅ runs daily, bar auditable |
| "we *detect verified maneuvers* at GEO" | ⚠️ partial — GEO-shaped verifier separates suspects from controls on both Intelsat and SES, but n=4 per fleet and the strongest column is the least independent. Say "early corroboration, n=4, not operator ground truth" |

## Reproduce it

```bash
cd "C:\Space\06 Code"
python detect.py --group oneweb            # or intelsat / ses
python verify.py --group oneweb --top 10   # suspects vs matched controls
python detect.py --group ses --mode alert  # fixed bar, zero is an answer
python verify_geo.py --group intelsat      # GEO-shaped: inclination + longitude drift
python _test_verify_geo.py                 # 21 cases
```
