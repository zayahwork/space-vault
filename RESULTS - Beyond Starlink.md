---
date: 2026-07-22
status: OneWeb clean; GEO referee ruled (issue 015) — altitude + lag-aware −3/+14d window catches 16/17 documented maneuvers (5/6 double-sourced — quote the 5/6); SES miss still unexplained; live GEO suspects still n=4
code: "06 Code/detect.py --group oneweb|intelsat|ses, 06 Code/verify.py (LEO), 06 Code/verify_geo.py (GEO), 06 Code/referee_geo.py (issue 015)"
snapshot: 2026-07-22 0800Z
---

# 🌍 RESULTS — the detector leaves Starlink

> [!success] The one-line version
> **OneWeb: the method works, full stop** — suspects show 80% independent-movement
> confirmation vs a 10% control base rate.
>
> **GEO: the referee has ruled (issue 015, re-scored 026).** Against the 17 externally
> documented GEO maneuvers, the **altitude verifier with a lag-aware −3/+14 day window
> catches 16 of 17** — but quote the **5 of 6 double-sourced**, since the three rows that
> lifted it above 13/14 are all single-sourced. The inclination channel catches 9 of 17 and
> never beats altitude at any window width. The verifier's GEO failure was its **±3-day timing window** against a
> catalog that lags up to ~11 days — wrong *when*, not wrong *what*. The earlier "altitude is
> blind to GEO burns by construction" claim in this note was mine, it is refuted, and it is
> struck below.
>
> **What that does *not* settle: the SES miss.** All seven documented SES events behave
> correctly under the verifier exactly as shipped, so neither candidate explanation accounts
> for SES's live no-signal. It goes back on the open list, unexplained.
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

The 80%-vs-10% is comparable to Starlink's own top tier. (Starlink's headline was re-measured
to **96%** once its snapshots aged past the catalog-lag window — see
[[RESULTS - Checked Against History]]; OneWeb's 80% is an early-observability number too and
would likely rise the same way if re-run aged. The like-for-like comparison is early-vs-early:
OneWeb 80%, Starlink 76% at zero forward reach.) Different operator, different orbit shell,
different maneuver style — same signal. This is the "it's a method, not a Starlink quirk"
evidence.

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

> [!danger] Revisited twice on 2026-07-22 — final reading: **neither explanation survives, and
> the SES miss is still unexplained**
> First revision: `verify_geo.py` re-ran the fleet on inclination + drift and SES appeared to
> separate on both — read at the time as "the altitude verifier looked at the wrong axis."
> The referee test (issue 015, callout further down) killed that reading. But it does not
> hand the win to the other candidate either, and the reason is specific to SES:
>
> **Every documented SES event is caught by the altitude verifier exactly as shipped**, at
> ±3 days, with the catalog step arriving +0.3 to +2.4 days late — AMC-9's fragmentation
> (9.2× its bar), AMC-9's graveyard raise (8.3×), AMC 11's graveyard raise (678×) and all
> three of AMC 11's routine N–S station-keeping burns (2.0×, 3.3×, 6.0×). And AMC 18, SES's
> abandoned bird, stays correctly silent. On SES's own documented record the ±3-day window
> was never the constraint, so **the timing window cannot be why SES's live suspects showed
> no signal** — even though it is genuinely the verifier's biggest defect elsewhere.
>
> So of the four options the CTO ruling named — altitude-blindness, timing window, both,
> neither — the answer for SES is **neither**. That is worse than having an explanation, and
> it is where the evidence points. What it does do is move the suspicion: the verifier
> handles SES's documented maneuvers correctly, which makes `detect.py`'s **GEO suspect
> selection** the next thing to test, not `verify.py`. That is a hypothesis with no
> measurement behind it yet — do not quote it as a finding.
>
> The SES drift "separation" is dead (negative control), and the inclination one is n=4 and
> unconfirmed.

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

1. ~~**The verifier watches altitude.**~~ **Refuted by the referee, 2026-07-22** (callout
   below). The claim was that GEO burns barely change altitude, so the step the altitude
   verifier looks for is close to invisible. Documented events say otherwise: N–S burns move
   fitted altitude 0.8–3.0 km at 2.0–6.0× their own noise bar, and altitude catches more
   documented maneuvers than inclination at every window width. The real fault was the
   **±3-day window** against a catalog that lags up to ~11 days.
> [!success] ⚖️ RESOLVED 2026-07-22 — the referee has ruled (issue 015): **Randy's timing
> explanation survived; my altitude-blindness mechanism did not**
> `referee_geo.py` scored every documented GEO event in `ground_truth.csv` on both channels
> at four window shapes, with the same step-finding rule the shipped verifiers use — asserted
> identical to `verify.biggest_step_km` and `verify_geo.biggest_step` by `_test_referee.py`,
> 55 cases, so this scores the verifiers we actually ship rather than a rewrite of them.
>
> Each event is judged against its **own era- and cadence-matched bar**: the largest step
> abandoned GEO drifters (GCAT `GEO/ID`, no engine) tracked at a comparable catalog rate
> ever produced over the same ±120 days. That matching is not bookkeeping, it decides rows —
> a first pass with one global bar got 1.51 km, and the entire excess was two sparsely
> tracked 1960s objects; the well-tracked drifters reproduce Randy's ~0.42 km bar from an
> independent sample. Era matters more still: in 2010 comparably-tracked drifters threw
> 0.78–2.20 km steps on their own.
>
> **The lag-aware window is asymmetric (−3/+14d), and that is load-bearing.** Catalog
> lateness runs one way — an orbit determination can be published days after a burn, never
> days before it. A symmetric ±14d window does not model lateness, it just takes the biggest
> thing in four weeks of history: run that way, MEV-2 and Intelsat 1002 both "catch" on
> inclination steps landing **12.3 days *before* the docking**, at 5.2× and 5.0× the bar.
> Randy's recommended edit as literally written — `WINDOW_DAYS = 3.0 → 14.0` — would
> introduce exactly that. The fix is a one-sided window, not a wider one.
>
> All 17 scoreable events (2src = survived Randy's double-sourcing; steps in km / degrees,
> with how many times the row's own bar in brackets; ✅ over its bar, ✗ under;
> \* = verdict flips if the 99th-pct bar is used instead of the max). **Re-scored
> 2026-07-22 (issue 026)** — the research lane added three east-west station-keeping rows;
> they are the last three, all 1src:
>
> | event | date | src | alt ±3d | alt −3/+14d | inc ±3d | inc −3/+14d |
> |---|---|---|---|---|---|---|
> | Galaxy 15 (loss of command) | 2010-04-05 | 2src | 0.033 ✗ | 2.154 (1.0×) ✗\* | 0.0045 ✗ | 0.0101 ✗ |
> | AMC-9 (fragmentation) | 2017-06-17 | 2src | 12.98 (9.2×) ✅ | 12.98 ✅ | 0.0158 ✗\* | 0.0158 ✗ |
> | Intelsat 29e (prop failure) | 2019-04-07 | 2src | 35.69 (104×) ✅ | 61.64 ✅ | 0.0116 (1.2×) ✅ | 0.0143 ✅ |
> | MEV-2 (docking) | 2021-04-12 | 2src | 0.085 ✗ | 0.584 (1.1×) ✅ | 0.0139 (1.8×) ✅ | 0.0139 ✅ |
> | Intelsat 1002 (docked-by) | 2021-04-12 | 2src | 0.052 ✗ | 0.981 (1.8×) ✅ | 0.0021 ✗ | 0.0024 ✗ |
> | Intelsat 33e (breakup) | 2024-10-19 | 2src | 0.076 ✗ | **29.87 (74×) ✅** | 0.0020 ✗ | 0.0313 (1.5×) ✅ |
> | AMC-9 (graveyard) | 2017-11-13 | 1src | 11.36 (8.3×) ✅ | 11.36 ✅ | 0.0077 ✗ | 0.0077 ✗ |
> | Intelsat 901 (stack reloc) | 2020-03-02 | 1src | 148.16 (154×) ✅ | 148.16 ✅ | 0.1111 (5.8×) ✅ | 0.1111 ✅ |
> | AMC 11 (N–S burn) | 2025-02-10 | 1src | 3.00 (6.0×) ✅ | 3.00 ✅ | 0.0471 (2.7×) ✅ | 0.0471 ✅ |
> | Intelsat 901 (graveyard) | 2025-03-31 | 1src | 97.82 (196×) ✅ | 307.60 ✅ | 0.0027 ✗ | 0.0080 ✗ |
> | AMC 11 (N–S burn) | 2025-08-08 | 1src | 0.836 (2.0×) ✅ | 0.933 ✅ | 0.0466 (5.2×) ✅ | 0.0466 ✅ |
> | AMC 11 (N–S burn) | 2025-10-21 | 1src | 1.227 (3.3×) ✅ | 1.550 ✅ | 0.0435 (4.8×) ✅ | 0.0435 ✅ |
> | AMC 11 (graveyard) | 2026-04-22 | 1src | 267.82 (678×) ✅ | 267.82 ✅ | 0.0135 (1.8×) ✅ | 0.0135 ✅ |
> | Intelsat 25 (graveyard) | 2026-05-04 | 1src | 112.45 (285×) ✅ | 112.45 ✅ | 0.0293 (4.0×) ✅ | 0.0293 ✅ |
> | Intelsat 1002 (E–W SK) | 2025-02-28 | 1src | 20.77 (42×) ✅ | 20.77 ✅ | 0.0021 ✗ | 0.0021 ✗ |
> | AMC 11 (E–W SK) | 2025-06-10 | 1src | 3.01 (7.0×) ✅ | 3.01 ✅ | 0.0021 ✗ | 0.0021 ✗ |
> | Astra 3B (E–W SK) | 2025-09-08 | 1src | 15.36 (43×) ✅ | 15.36 ✅ | 0.0021 ✗\* | 0.0021 ✗ |
>
> | measurement | all 17 | double-sourced 6 |
> |---|---|---|
> | (a) altitude, ±3d as shipped | 13/17 | 2/6 |
> | (b) altitude, lag-aware −3/+10d | 15/17 | 4/6 |
> | (b′) altitude, lag-aware −3/+14d | **16/17** | **5/6** |
> | (c) inclination, ±3d | 8/17 | 2/6 |
> | (d) inclination, −3/+14d (fairness control) | 9/17 | 3/6 |
>
> **Quote the double-sourced 5/6, not the all-scoreable 16/17.** The three new rows are all
> single-sourced and catalog-dated, the weak tier this write-up already warns is close to
> tautological — a catalog-based detector agreeing with catalog-dated events. They lifted
> the all-scoreable altitude rate from 13/14 to 16/17, but **the double-sourced column did
> not move** (still 5/6), and that is the honest external number. The all-scoreable rate
> going up on the strength of the weakest evidence is exactly the drift issue 026 was filed
> to prevent.
>
> **They are, however, a third strike against altitude-blindness.** East-west station-keeping
> is the *other* GEO burn my original claim said altitude could not see. Measured: it moves
> fitted altitude **15–21 km** (Intelsat 1002 42×, Astra 3B 43×) — even the small one, AMC 11,
> is 3 km at 7× — and all three are caught inside ±3 days, lag under a day. Nothing at GEO
> that actually fires an engine is invisible to the altitude verifier; the miss was never
> the observable.
>
> **±10 days is one day short.** Intelsat 33e's 29.87 km step lands at **+10.98 days** —
> `ground_truth.csv` rounds that lag to 10, and a ±10d window misses the best-evidenced
> late signal in the set by 24 hours. At −3/+14d it comes in at 74× its bar. The constant
> to ship is 14, which is what Randy's own write-up recommended; the CSV's rounded lag
> column is what made 10 look sufficient.
>
> No row lacked GP_HISTORY — all 17 scored on real catalog data back to 2010 (thinnest:
> Galaxy 15, 53 records over its ±25 days, 1.1/day). One row, AMC-9 2017-11-13, had no
> drifter tracked within 0.5–2× its own rate that season and is scored against a widened
> cadence match; it is marked `widened` in the run output and its verdict (8.3× the bar)
> does not depend on the relaxation. AMC 18, the documented **non**-maneuvering control,
> stayed silent in every column at every window — including ±14d, so widening did not break
> the one true negative we have (n=1; that is a check, not a false-positive rate). MEV-1 is
> excluded because its own orbit-raising transit (a 35,670 km "step") contaminates its
> window.
>
> **Galaxy 15 is not a catch, and this corrects Randy too.** `RESULTS - Ground Truth` scores
> its 2.15 km step at 5× the bar and counts it as caught-once-widened. That used a bar
> measured in the modern catalog. Against 2010-era drifters tracked at Galaxy 15's own rate,
> the noise floor is **1.68–2.20 km** — its "signal" is 1.0× the bar, inside the noise. It
> is missed at every window on both channels. That does not weaken the Galaxy 15 story, it
> relocates it: nothing burned, the *rhythm stopped*, and a step-finder cannot see an absence.
> That is `quiet.py`'s premise and this is the second independent piece of evidence for it.
>
> **What survived, honestly, and it is not my half.** The events the lag-aware window catches
> that ±3d missed had their catalog step land **+5.2, +5.6 and +11.0 days after** the
> documented date: measured lateness, exactly Randy's mechanism. And N–S station-keeping —
> the maneuver class my whole argument rested on — **does** move fitted altitude: AMC 11's
> three documented N–S burns show 0.84, 1.23 and 3.00 km at 2.0×, 3.3× and 6.0× their own
> bars, all three caught by the altitude verifier *as shipped*, inside ±3 days. I wrote that
> the dominant GEO maneuver was invisible to an altitude verifier "by construction, not by
> bad luck." The documented record says that is simply false, and `verify_geo.py`'s stated
> reason for existing goes with it. Inclination catches **fewer** events than altitude at
> every window width (8 vs 10 at ±3d, 9 vs 13 at −3/+14d) and never beats it on the
> double-sourced subset. It keeps exactly one distinction worth having: it is the only
> channel that sees the MEV-2 docking inside ±3 days, a plane change altitude needs five
> more days to notice. So inclination stays as a **secondary** channel on its own merits,
> not as the replacement I built it to be. The drift column stays retired — both of us
> killed it independently, from different directions.
2. **n=3 against n=3 controls.** A 90th-percentile bar drawn from 3 controls is barely a
   bar. The population is 44–68 objects, so 95th-percentile ranking can only ever produce
   a handful of suspects per snapshot.
3. **GEO operators refresh SupGP slower** — median 1 independent look over our 6h window,
   so persistence can't confirm anything at GEO yet. It will, as the archive grows.

All three get better automatically: the daily task ([[RESULTS - Alert Log]]) banks every
snapshot, and a week of GEO data supports a real n and a real rhythm.

## The lag-aware window is now what ships (issue 018, 2026-07-22)

The referee's winning configuration is no longer harness-only. `verify.py` and
`verify_geo.py` take the window from one table, keyed by regime, and it is **one-sided**:

| regime | window | basis |
|---|---|---|
| LEO | −3 / +3 d | unchanged — measured catalog update interval **median 0.27 d** (Starlink, n=2,701); the LEO catalog is not late |
| GEO | **−3 / +14 d** | documented GEO lag up to **+10.98 d** (Intelsat 33e); 14 d clears it |
| MEO · mixed | −3 / +14 d | ⚠️ **UNVALIDATED** — no MEO ground truth; borrowing GEO's window is a judgement, like the 1.0 km floor |

Each run now prints the fleet's own measured update interval, the window, and the basis
string, so the constant can be argued with from the output instead of the source.

> [!danger] The honest part: **this change moves no live number today, and cannot**
> A forward-looking window can only be evaluated in retrospect. The newest snapshot is
> **two hours old**, so of the +14 day reach, **0.08 days has been published**. Recomputing
> all 80 cached objects under the old ±3 d and the new −3/+14 d gives **identical steps on
> 80 of 80**. The runs say so themselves — every one printed
> `** PROVISIONAL: only 0.08 d of the +14 d forward reach has been published yet **`.
>
> The change is still correct and still worth shipping: on the 17 documented maneuvers it
> takes verification from 13/17 to 16/17 (2/6 → 5/6 double-sourced). It pays off when a
> snapshot has aged past the window, not on the day it is taken. **Anyone quoting a
> same-day GEO verification is quoting a window that has not happened yet.**

**SES moved — and it was not this change.** The live SES run now shows suspects at 21.8×
the controls' median step, 50% vs 13% over the bar, where the earlier run read *NO SIGNAL*
(0.8×, 1/3 vs 1/3). Since the two windows are provably identical on today's data, the
difference is the **archive and the suspect list**, not the window: this run had 4 suspects
against 15 controls, the earlier one 3 against 3. That is a change worth chasing, not a
result worth quoting — n=4, and the SES miss stays formally unexplained until it is
reproduced on a snapshot deep enough to score.

Intelsat, same run: 1.1× median, 50% vs 25%, n=2 suspects. Still an anecdote.

Regression covered by `06 Code/_test_verify_window.py`, 31 cases — including that LEO is
untouched, that the GEO window refuses a step landing before the event, and that a fresh
snapshot is reported provisional rather than silently under-reaching.

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
| "we *detect verified maneuvers* at GEO" | ⚠️ partial. External-safe sentence: **"Scored against 17 externally documented GEO maneuvers, our altitude method with a lag-aware window catches 5 of the 6 that carry two independent sources — and a documented non-maneuvering control stays silent."** Then the caveat, in the same breath: **detection is not same-day — the catalog itself runs up to 11 days late.** Do NOT say we verify *live* GEO suspects (still n=4, unproven), do not quote the SES "separation", and lead with the double-sourced 5/6 — the all-scoreable 16/17 leans on single-sourced rows |
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
python referee_geo.py                      # issue 015: both verifiers vs 14 documented maneuvers
python _test_referee.py                    # 55 cases, incl. step-math identity with shipped verifiers
```
