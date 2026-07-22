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
> **Still not proven, and one measure is now discredited.** Running the GEO verifier on LEO
> as a negative control showed the *longitude drift* column returns the same ~63–70× on every
> fleet from 475 km to GEO — it is reflecting the detector's own selection axis, not
> independent physics. **Inclination is the column that varies (1.21×–15×) and the one to
> quote.** Best independent evidence in the set: **OneWeb inclination, 11.5×, 70% vs 13%**,
> agreeing with the altitude verifier's separate 80%-vs-10% on the same fleet. GEO itself is
> still n=4.

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

### Run across all four fleets — LEO included, as a negative control

| fleet | regime | n | **inclination** (independent) | **longitude drift** (weak) |
|---|---|---|---|---|
| starlink | LEO | 15 | 1.56×, **6/15 (40%)** | 63.8×, 15/15 (100%) |
| oneweb | LEO | 10 | **11.50×, 7/10 (70%)** | 69.9×, 10/10 (100%) |
| intelsat | GEO | 4 | 1.21×, **0/4 (0%)** → *no signal* | 2.24×, 2/4 (50%) |
| ses | mixed | 4 | 15.00×, 1/4 (25%) | 63.0×, 4/4 (100%) |

> [!danger] The negative control paid off: **the drift column is near-circular**
> Running the GEO verifier on LEO fleets was meant as a sanity check. Instead it exposed the
> drift measure. It returns **63.8× / 69.9× / 63.0×** — essentially the same dramatic number
> — in 475 km of thick air *and* in the geostationary belt, with 100% of suspects over the
> bar in all three. **A measure that cannot tell those two places apart is not describing
> them.** It is reflecting the detector's own selection axis (along-track ≈ mean motion) back
> at us.
>
> Inclination over the same four fleets gives **1.56× / 11.50× / 15.00× / 1.21×**, and ranges
> from 70% of suspects over the bar down to 0%. **It varies.** That is what an observable
> carrying independent information looks like, and it is the column to quote.
>
> Practical upshot: **stop quoting the 63× numbers.** They are the least informative thing in
> this table despite being the largest.

> [!warning] A second correction — the controls' bar-clearing rate is arithmetic, not evidence
> Every run above shows controls at **exactly 2/15**. That is not a coincidence and not a
> measurement: the bar *is* the controls' 90th percentile, so with 15 controls exactly 2 sit
> above it, always, whatever the data says. `verify.py` already flagged this ("← 10% by
> construction"); `verify_geo.py` now prints it too.
>
> So the "clears the bar N× as often" figure is the suspects' own fraction rescaled by a
> constant — **not a second independent reading**, which is how I described it when I first
> committed this. Requiring both statistics is still right, because they fail differently
> (median moves with a bulk shift, bar-clearing with the tail — Intelsat's inclination had a
> 1.21× median with *nothing* in the tail). But two views of the same two samples is not
> corroboration.

**What changed and what didn't.** SES — the fleet the altitude verifier called a flat miss —
separates on both observables. Intelsat separates on drift only, and its inclination result
is *negative*: suspects cleared the controls' bar **less** often than the controls did. The
strongest independent evidence in the whole table is **OneWeb's inclination: 11.50×, 70% vs
13%** — and it agrees with the altitude verifier's independent 80%-vs-10% on the same fleet.

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
> [!danger] ⚖️ DISPUTED 2026-07-22 — Tim's mechanism vs Randy's ground truth (CTO ruling inside)
> Independently of the work above, Randy scored 14 documented GEO maneuvers
> ([[RESULTS - Ground Truth]]) and reports the opposite mechanism: **N–S station-keeping DOES
> move fitted altitude** (0.84–3.00 km on documented events, 2–7× the measured noise floor),
> and **longitude drift is arithmetically the same quantity as altitude** (1 km ≈ 0.0128°/day)
> — which *converges* with Tim's own negative control killing the drift column from a
> different direction. On Randy's data the altitude verifier's real GEO failure is the
> **±3-day timing window** against a catalog that can lag up to 10 days — wrong *when*, not
> wrong *what*. Under that reading the SES no-signal result has no confirmed explanation yet.
>
> **CTO ruling:** where they agree is settled — the drift column is dead, retired everywhere,
> two independent executions. Where they disagree, measured events outrank mechanism, but
> n=14 events vs n=4 suspects is not a settled fight either way. The ground-truth set is the
> referee: **issue 015 scores BOTH verifiers against the 14 documented maneuvers** — altitude
> with a lag-aware window, and inclination — and whichever catches more documented events
> wins. Until 015 reports: quote neither the SES "separation" nor the retraction as fact.
> SES is an open miss with two candidate explanations, and that sentence is the only
> external-safe one.
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
| "we *detect verified maneuvers* at GEO" | ⛔ DISPUTED pending issue 015 (see ruling above). External-safe sentence: "GEO corroboration is early and under active validation against 14 documented maneuvers." Do not quote SES separation or the retraction as fact |
| "the maneuvers we flag show up in an independent observable" | ✅ strongest at **OneWeb: inclination 11.5x, 70% vs 13%**, matching the altitude verifier's separate 80%-vs-10% |
| any claim resting on the **63x drift** figures | ❌ do not use — same number at every altitude, near-circular with the detector |

## Reproduce it

```bash
cd "C:\Space\06 Code"
python detect.py --group oneweb            # or intelsat / ses
python verify.py --group oneweb --top 10   # suspects vs matched controls
python detect.py --group ses --mode alert  # fixed bar, zero is an answer
python verify_geo.py --group intelsat      # GEO-shaped: inclination + longitude drift
python verify_geo.py --group oneweb        # LEO negative control - exposed the drift issue
python _test_verify_geo.py                 # 21 cases
```
