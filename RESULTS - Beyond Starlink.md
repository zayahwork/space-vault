---
date: 2026-07-22
status: OneWeb clean; GEO now regime-aware (issue 002) but still unverified against real maneuver records
code: "06 Code/detect.py --group oneweb|intelsat|ses, 06 Code/verify.py --group ..."
snapshot: 2026-07-22 0800Z
---

# 🌍 RESULTS — the detector leaves Starlink

> [!success] The one-line version
> **OneWeb: the method works, full stop** — suspects show 80% independent-movement
> confirmation vs a 10% control base rate. **GEO: the pipeline runs and the age-filter does
> its best work there, but verification is data-starved** — Intelsat looks promising (3/3
> confirmed), SES shows no signal yet (n=3, and the verifier is half-blind at GEO). Nothing
> about GEO broke; nothing about GEO is proven either.

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
- Verify: **NO SIGNAL.** Suspects' median step 0.8x the controls', 1/3 vs 1/3 over the bar.
  The suspects look like everything else.

Better we say it first: **on today's data, SES detections are not corroborated.**

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

## Why GEO verification is weak by construction (not an excuse — a mechanism)

1. **The verifier watches altitude.** GEO station-keeping is mostly east–west and
   north–south burns that barely change altitude — the step the verifier looks for is
   close to invisible. It was built for LEO reboosts. A GEO-shaped verifier (longitude
   drift, inclination) is the fix, not more of this one.
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
| "we *detect verified maneuvers* at GEO" | ❌ not yet — say "in validation, ~1 week of data needed" |

## Reproduce it

```bash
cd "C:\Space\06 Code"
python detect.py --group oneweb            # or intelsat / ses
python verify.py --group oneweb --top 10   # suspects vs matched controls
python detect.py --group ses --mode alert  # fixed bar, zero is an answer
```
