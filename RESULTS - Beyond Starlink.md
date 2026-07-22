---
date: 2026-07-22
status: method generalizes to OneWeb cleanly; GEO runs but is not yet verified
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

## SES (GEO, 68 objects) — the honest miss

- 3 suspects, 75% of the naive list was stale.
- Verify: **NO SIGNAL.** Suspects' median step 0.8x the controls', 1/3 vs 1/3 over the bar.
  The suspects look like everything else.

Better we say it first: **on today's data, SES detections are not corroborated.**

## Why GEO verification is weak by construction (not an excuse — a mechanism)

> [!danger] ⛔ RETRACTED 2026-07-22 — point 1 below is wrong
> Scored against 14 documented GEO maneuvers, **N–S station-keeping does move altitude**
> (0.84–3.00 km, 2–7× the measured noise floor), and **longitude drift is arithmetically
> the same quantity as altitude** (1 km = 0.0128°/day). The proposed "GEO-shaped verifier"
> would change nothing. The real failure is the ±3-day timing window vs. a catalog that
> lags up to 10 days. **SES's no-signal result now has no explanation.**
> → [[RESULTS - Ground Truth]]

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
