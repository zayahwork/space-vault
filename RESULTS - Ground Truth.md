---
date: 2026-07-22
status: first independent scoring of the detector against documented reality; expanded to 37 typed events the same night
code: "06 Code/ground_truth.csv"
sources: McDowell GCAT · Space-Track SATCAT + GP_HISTORY · Northrop/Intelsat PRs · S4S · SpaceX FCC filings
supersedes: the GEO hypothesis in [[RESULTS - Beyond Starlink]]
---

# 🎯 RESULTS — the detector vs. 37 documented maneuvers

> [!info] Updated the night of 2026-07-22
> The set grew from 24 to **37 events** and every row now carries a `maneuver_type` tag —
> see [[#The per-type view — what each observable can and cannot catch]]. The scoring
> numbers below (33% / 73% / the noise floor) are **unchanged**: all ten new rows are
> reentries that predate our archive, so they add evidence, not score. Verified rows went
> **7 → 17** because ten new decays are corroborated by both Space-Track and McDowell's
> GCAT. Text below this box still says "24" where it describes the original stress test.

> [!quote] The honest summary — read this before any other number on this page
> We assembled 24 documented events and then stress-tested every row, demanding a **second
> source independent of the first**. Only **7 of 24 survived**; the other 17 are marked
> *assumed*. Of the 15 scoreable maneuvers we catch 11 — but that 73% is flattered by its
> evidence. **On the 6 events with two independent sources, we catch 2 — 33%.** The gap is a
> selection effect, and it is the most important thing on this page: the events that earn two
> independent sources are *anomalies* — breakups, failures, servicer dockings — which is
> precisely the class our altitude-step method handles worst; the events we catch reliably are
> graveyard disposals and routine station-keeping, which no operator ever announces, so they
> can only ever be self-sourced. **We are best at what nobody documents and worst at what
> everybody documents.** And on false positives this set says almost nothing: it contains one
> true negative, our two live undocumented flags are unresolvable in principle, and the 205
> Starlink objects flagged on 2026-07-22 have no public documentation of any kind. The ~1%
> false-alarm rate implied by our bar is a **calibration artifact** — we set the bar at the
> 99th percentile of a null distribution — **not a measurement**. Ground truth tells you about
> events that happened; measuring a false-positive rate needs documented *non*-events, which
> essentially do not exist in public sources. **So: a real but modest detection result on hard
> cases, a strong one on easy cases, and no measured false-positive rate at all.**

> [!success] The one-line version — true, but read the summary above first
> Against **14 scoreable GEO maneuvers, the method catches 10 (71%)** — and the four it drops
> are not random. **Two are catalog *lateness*, not blindness** (the signal is real, it just
> arrives 5–10 days after the event). **Two are servicer dockings, where the target satellite
> doesn't move at all.** Widen one timing window and 71% becomes 86%.
>
> ⚠️ **Caveat that outranks this box:** most of those 10 catches are events we dated from the
> catalog ourselves. Restricted to double-sourced events, the rate is **2 of 6**. Use 71% for
> engineering decisions about where to spend effort; **never use it with a buyer.**

> [!danger] The one-line version we'd rather not write
> **Our detector can currently be scored on 12 hours of data, not two days.** The public
> catalog half of the archive only starts at the 2026-07-22 **0200Z** snapshot. Everything
> from July 21 is operator-side only and cannot be scored at all. Of 24 ground-truth
> events, exactly **three** fall inside the window the live detector can see.

Everything before today was the detector checking its own homework: our suspects, scored
against our own controls, using our own data. This is the first time it has been graded
against **events other people documented, dated, and published** — press releases,
Space Force breakup confirmations, regulator-facing filings, and an independent catalog
curated by an astronomer who has been doing it since 1985.

---

## What "ground truth" means here, and what it cost

24 events in `06 Code/ground_truth.csv`. **Every row is marked `verified` or `assumed`,
after a stress test on 2026-07-22 that demanded a second independent source per row:**

| mark | meaning | count |
|---|---|---|
| **verified** | **two mutually independent sources** attest the event and its date | **7** |
| **assumed** | one source, or a source that derives from the data we measure | **17** |

**What "independent" means here:** neither source derives from the other. Trade coverage
restating a press release is *not* a second source. A company announcement plus a government
tracking record *is*. This rule cost us 8 rows that were marked verified on the first pass.

**The 8 downgrades, and why** — each one is a small lesson:

| row | why it fell |
|---|---|
| Intelsat 901 graveyard raise | Northrop's release is the only document; every trade story derives from it, **and we supplied the date ourselves** |
| AMC 18 (null object) | McDowell's classification derives from the same public catalog we measure — not independent of us |
| 5 × Starlink reentries | Space-Track is authoritative but alone: **McDowell's `satcat.tsv` was last updated 2026-07-17 20:11 UTC, before all five decays** |
| STARLINK-37977 orbit-raise | SpaceX's FCC filings describe orbit-raising generically, never per-satellite. The classification is our inference |

> [!note] A downgrade is not a doubt
> The five Starlink reentries are almost certainly real — Space-Track's decay record is the
> authoritative US government source. They fell to *assumed* on a **procedural** rule, not
> because anyone disputes them. **Re-check `satcat.tsv` and they should promote.**
> That's the difference between "we don't believe it" and "we can't yet corroborate it."
>
> ⚠️ **Correction (issue 018):** earlier notes told the next shift to re-check `rcat.tsv`.
> That is wrong — GCAT's `rcat` is the **Suborbital Rocket (Exoatmospheric) Catalog**
> ("objects whose apogee was 80 km or more"), per GCAT's own catalog index. A Starlink
> payload would never appear in it whether it had reentered or not, so the original
> "not in rcat" reasoning proved nothing. **`satcat.tsv` — Status `R` with a `DDate` — is
> the correct source.** Same conclusion, sound reasoning.

**Two things the stress test actually corrected:**
- **Intelsat 29e's date moved from 2019-04-09 to 2019-04-07** — Intelsat's own release puts
  the propellant leak "late on April 7". Verdict unchanged (still caught, now with a +2 day
  lag instead of 0).
- **I had misread McDowell's catalog.** Its rows are *phases*, not objects — `DDate` is the
  end of a phase and `Status` is the event that ended it. My first pass read first-phase rows
  and would have reported Galaxy 15 as "decayed 2006" (it was *renamed* in 2006). Corrected
  before it reached the CSV. This is also how S33153 resolved: launched as **Protostar 1**,
  renamed October 2009, now Intelsat 25.
- **Two dockings gained hour-level corroboration:** GCAT independently records MEV-1 docking
  at *2020 Feb 25 07:15* and MEV-2 at *2021 Apr 12 17:34* — the latter matching Northrop's
  "1:34 pm EDT" exactly.

*Jargon: "the catalog" = the public US government orbit list (GP). "GP_HISTORY" = the same
list, but every past version, going back years. "SupGP" = the operator's own published
orbit for its own satellite — better, but only for satellites the operator still cares about.*

**An honest note on circularity.** For some events I could only get the *date* by reading
it out of the catalog's own history. That is the same data our verifier uses, so those rows
cannot independently validate the verifier — they can only test whether it agrees with
itself. **All 7 surviving verified rows are dated by an outside source** — a press release, a Space
Force statement, a NASA debris bulletin, a USGS space-weather study, or McDowell's phase
catalog. Every row whose date we had to read out of the catalog is now marked *assumed*,
which is exactly where the circularity risk lives.

---

## The scoreboard

### GEO — 14 scoreable events, 10 caught

| verdict | n | what they are |
|---|---|---|
| ✅ **caught** | **10** | graveyard disposals (5), failures with drift onset (2), routine N–S station-keeping (3) |
| ⏱️ **missed on timing** | 2 | Intelsat 33e breakup, Galaxy 15 — signal is real but +10 and +5 days late |
| ❌ **missed outright** | 2 | MEV-2 docking, Intelsat 1002 being docked |
| — excluded | 1 | MEV-1's own orbit-raising contaminated the window; not a fair test |
| — true negative | 1 | AMC 18, abandoned: 1,604 orbit updates, no burns, correctly silent |

### The same scoreboard, split by how well-evidenced each event is

This is the split that matters, and it is not flattering:

| evidence tier | events | caught | rate |
|---|---|---|---|
| **two independent sources** | 6 | **2** | **33%** |
| single-source / self-dated | 9 | 9 | 100% |
| **all scoreable** | 15 | 11 | 73% |

The 100% row should make you suspicious, not pleased — those are the events we dated from the
catalog ourselves, so a catalog-based detector agreeing with them is close to tautological.
**The 33% is the number to quote to anyone who matters.** The four verified misses are two
servicer dockings (target doesn't move), one breakup and one command-loss (both real signals,
both arriving late).

**The bar this is scored against is measured, not chosen.** I took four satellites McDowell
classifies as abandoned — they drift, they never fire an engine — and measured how much the
catalog's altitude wobbles on its own. Across **2,128 measurements in 132 windows**, the
biggest wobble ever seen was **0.42 km**. That's the bar. Anything above it is not the
catalog being noisy.

| GEO altitude noise floor (abandoned objects, 2026) | km |
|---|---|
| median | 0.083 |
| 99th percentile | 0.304 |
| **largest ever observed** | **0.419** ← the bar used |

Against that bar the catches aren't marginal — they're enormous: the Intelsat 901 graveyard
raise is **732× the bar**, AMC 11's is **638×**. Even the weakest true positive (a routine
station-keeping nudge) is 2× clear.

### LEO — 8 events at stress-test time, 1 scoreable *(now 18 — the ten added rows are all pre-archive reentries, so still 1 scoreable)*

| verdict | n | why |
|---|---|---|
| ✅ caught | 1 | STARLINK-37977, mid orbit-raise, flagged at 9.3× its bar |
| 🔍 flagged but undocumented | 2 | STARLINK-36738 and ONEWEB-0685 — no public source can confirm *or* deny |
| 🚫 **not scoreable** | **5** | five Starlink reentries, all invisible to us — see below |

---

## The per-type view — what each observable can and cannot catch

Every row now carries a `maneuver_type` tag so the verifier comparison (tech lane, issue
015) can say WHICH kinds of burns each observable sees. Counts computed from the CSV,
not by hand:

| maneuver_type | events | verified | caught | missed | timing-miss | not scoreable / other |
|---|---|---|---|---|---|---|
| **deorbit** (graveyard + reentry) | 19 | 10 | 4 | 0 | 0 | 15 reentries pre-date the archive |
| **NS-stationkeeping** | 3 | 0 | 3 | 0 | 0 | — |
| **anomaly-sudden** (breakup, leak, fragmentation) | 3 | 3 | 2 | 0 | 1 | — |
| **docking** (servicer + target) | 3 | 3 | 0 | 2 | 0 | 1 excluded (MEV-1 transit) |
| **anomaly-quiet** (Galaxy 15, AMC 18) | 2 | 1 | 0 | 0 | 1 | 1 true negative |
| **relocation** | 1 | 0 | 1 | 0 | 0 | — |
| **reboost** | 1 | 0 | 1 | 0 | 0 | — |
| **unknown** (our flags, unconfirmable) | 2 | 0 | — | — | — | 2 flagged-undocumented |
| **EW-stationkeeping** | 3 | 0 | 3 | 0 | 0 | signature-inferred, not documented |
| **total** | **37** | **17** | 14 | 2 | 2 | |

**What the table says, plainly:**

- **The step detector's wins concentrate in exactly two types: deliberate altitude
  changes (deorbit, reboost, relocation) and N–S station-keeping.** 9 of its 11 catches
  are those. That's a coherent product claim: *we see satellites that move on purpose.*
- **The quiet fraction is half the dataset.** 2 rows are tagged `anomaly-quiet`, but the
  15 unscoreable reentries fail for the *same underlying reason* — the signal is an
  absence (the operator stops publishing; the expected correction never comes). **17 of
  37 documented events (46%) can only ever be covered by `quiet.py`-class logic, not by
  any jump detector.** That is the measured size of the bet the insurer story places on
  the Jul 29 unlock.
- **Docking is 0-for-2 and structurally so** — the target doesn't move. If servicing
  missions matter to a buyer, that needs a different observable (relative-motion, not
  altitude), and we should say so rather than promise it.
- **EW-stationkeeping now has three examples — but they are inferred, not documented**
  (issue 018, 2026-07-22 night). The signature is unmistakable and self-checking: a
  **pair of opposite-sign longitude-drift corrections about a day apart** — one burn to
  start the drift, one to stop it — with **inclination held at noise** (0.0010–0.0051°,
  all under the measured 0.0058° null). N–S burns move inclination by ~0.045°; these do
  not, which is what makes them east–west.

  | satellite | dates | drift change | Δinc | Δalt |
  |---|---|---|---|---|
  | Intelsat 1002 | 2025-02-23 / 02-28 | +0.2321 → −0.2668 °/day | 0.0010° | 20.77 km (49× bar) |
  | Astra 3B | 2025-09-07 / 09-08 | +0.1785 → −0.1974 °/day | 0.0021° | 15.36 km (37× bar) |
  | AMC 11 | 2025-06-10 / 06-11 | −0.0386 → +0.0339 °/day | 0.0051° | 3.01 km (7× bar) |

  **All three are caught, comfortably.** Two things follow. First, **the altitude step
  detector is not blind to east–west burns either** — which further narrows what the
  original "wrong observable at GEO" story could ever have explained. Second, **AMC 11
  now carries both burn types**, and **Intelsat 1002 carries an EW burn our method catches
  and a docking it missed** — both are clean controlled comparisons for the tech lane's
  verifier work.

  The honest limit stands: **no operator publishes per-maneuver EW data, so a *documented*
  east–west burn remains unobtainable.** These rows are marked `assumed` on exactly the
  same footing as the N–S rows, and the verifier comparison should treat them as
  signature-labelled, not ground truth.

**Where the ten new rows came from, and the honest independence caveat.** Space-Track's
SATCAT decay records (8 Starlink decays 2026-07-02..07-14, both OneWeb decays) each
corroborated against McDowell's GCAT `satcat.tsv` reentry phases — three match to the
minute with a reentry location. That satisfies our two-source rule as previously applied
(it's exactly the promotion path the note above prescribes for the July 17–21 rows). The
caveat worth keeping in view: GCAT's reentry dating draws on the same government tracking
network Space-Track publishes, so this is the *weakest* form of independence in the set —
independent curation and estimation (McDowell's `?`-flagged times are his own), not an
independent sensor.

**Re-check performed 2026-07-22 night (issue 018), second pass:** the five July 17–21
Starlink reentries were re-queried by streaming `satcat.tsv` fresh from planet4589.org —
**19,010,777 bytes, file stamp `Updated 2026 Jul 17 2011:55`, byte-identical to the
earlier pull.** All five remain Status `O` with no decay date, so **0 of 5 promoted and
all five stay `assumed`**, now with the re-check date recorded in their `source_2`.

The blocker is simply that **GCAT has not published an update since July 17** — this is
data lag on his side, not disagreement, and nothing we can do from here. Re-check is
cheap (one stream, one filter); next shift should just run it again. The `source_2` note
in each row now cites `satcat.tsv` rather than the earlier, incorrect `rcat.tsv`.

**A OneWeb fact worth its own line:** Space-Track records **exactly two OneWeb decays
ever** (ONEWEB-0251 and -0265, both 2022, both early on-orbit failures). OneWeb does not
actively deorbit — dead OneWebs are abandoned in place and decay over months to years.
So the OneWeb ground-truth gap isn't a documentation gap, it's physical: **for OneWeb,
"went quiet" is the only failure signature that will ever exist.** Another point for
`quiet.py`.

---

## Three findings that change what we do next

### 1. The GEO explanation in [[RESULTS - Beyond Starlink]] is wrong. I'm retracting it.

That doc said SES showed no signal because *"the verifier watches altitude, and GEO
station-keeping is east–west and north–south burns that barely change altitude — a
GEO-shaped verifier (longitude drift, inclination) is the fix."*

Ground truth says otherwise, on two counts:

- **N–S station-keeping is NOT invisible in altitude.** AMC 11's three routine
  station-keeping events produced altitude steps of **3.00, 1.23 and 0.84 km — 2× to 7×
  the bar**. All three would be caught. The premise was wrong.
- **"Switch to longitude drift" would gain us literally nothing.** Drift rate and altitude
  are the *same number*: `1 km of altitude = 0.0128°/day of drift`. I checked this against
  the real IS-901 burn — measured 0.01269, theory 0.01284, agreeing to 1.2%. Rebuilding the
  verifier around longitude drift would be a rename, not a fix.

So **SES's "no signal" has some other cause**, and we no longer have an explanation for it.
That's worse news than having a wrong one, but it's true. It goes back on the open list.

### 2. The real GEO failure mode is *catalog lateness*, and it's a one-line fix

`verify.py` only counts a step if it lands within **±3 days** of the event
(`WINDOW_DAYS = 3.0`). The catalog does not cooperate:

| event | documented | catalog shows the step | lag | size when it lands |
|---|---|---|---|---|
| Intelsat 33e breakup | 2024-10-19 | 2024-10-29 | **+10 d** | 29.87 km (71× bar) |
| Galaxy 15 command loss | 2010-04-05 | 2010-04-10 | **+5 d** | 2.15 km (5× bar) |

Both signals are strong. Both are thrown away by the window. **Widening it to ±14 days
takes GEO from 10/14 (71%) to 12/14 (86%)** with no other change. That is the single
highest-value edit in the codebase right now, and it's one constant.

The catch worth saying out loud to a buyer: it also means **we cannot promise same-day
detection at GEO**. The catalog itself is up to ten days behind. Any product claim has to
be "we see it within two weeks," not "we see it today."

### 3. Galaxy 15 — our flagship story — is the one we'd have missed

Galaxy 15 is *the* "satellite went quiet" event: the 2010 zombiesat that kept broadcasting
while ignoring commands. It is the exact scenario in our pitch. Our detector's altitude
signal for it is **2.15 km, arriving five days late.**

Because nothing dramatic happened to the orbit. The satellite didn't move — **it stopped
moving.** The regular rhythm of small corrections simply ceased. You cannot see that by
looking for a big step; you can only see it by noticing an expected step *didn't happen*.

**That is `quiet.py`'s premise, and this is the first hard evidence that it's the right
one** — and that the step-based verifier will never carry the "went quiet" claim on its own.
Good news for the Jul 29 unlock. Bad news for anyone hoping the existing verifier covers it.

**Where a genuinely independent second channel does exist: inclination.** Unlike drift
rate, inclination is not a restatement of altitude. Measured on the same abandoned objects,
its noise floor is **0.0058°** — and AMC 11's N–S station-keeping burns move it by
**0.0435–0.0471°, a 7.5–8.1× separation.** That's a real, unused signal sitting in data we
already download.

---

## The uncomfortable one: five reentries we structurally cannot see

Five Starlink satellites reentered on July 17–21 — authoritative, dated, Space-Track decay
records. We caught none. Not because the detector is badly tuned, but because of this:

```
STARLINK-2128 (47404), decayed 2026-07-21
  present in operator data ......... 07-21 0851Z, 0852Z, 1400Z, 2025Z, 2157Z
  gone ............................. 07-22 0200Z onward
  first snapshot we can score ...... 07-22 0200Z
```

**The operator stopped publishing the satellite's orbit before our first scoreable
snapshot.** Our whole method is *operator's orbit vs. public catalog*. When a satellite
dies, gets abandoned, or finishes deorbiting, the operator stops publishing — so the gap
doesn't grow large, it **stops existing**.

That's a structural blind spot worth understanding clearly: **the signal disappears exactly
when the interesting thing happens.** A disappearance is still information — arguably the
strongest information available — but it is a different detector than the one we have. It
is also, again, `quiet.py`'s territory.

---

## The population cross-check — the one number that isn't ours

SpaceX tells the FCC how many collision-avoidance maneuvers the constellation performed:
**207,152 between December 2025 and May 2026**. That's aggregate — no per-satellite dates,
which is why per-object LEO ground truth basically doesn't exist. But it lets us sanity-check
our *rate*:

| | |
|---|---|
| SpaceX-implied maneuver rate | ~0.11 per satellite per day → **~2.8% in any 6-hour window** |
| our flag rate, 2026-07-22 1400Z | 205 of 10,781 → **1.9%** |

Same order of magnitude, and on the conservative side. **Caveat, stated plainly:** our alert
bar is set at the 99th percentile, so ~1% would be flagged by construction even on a dead-quiet
day. Read strictly, our *excess* over that is ~0.9% against an expected 2.8%. So this is a
consistency check that we're not wildly over-flagging — **not** proof we catch most maneuvers.

---

## What this changes in what we claim

| claim | before today | after ground truth |
|---|---|---|
| "we detect GEO maneuvers" | ❌ unproven | ⚠️ **11 of 15 documented events — but only 2 of 6 that carry two independent sources. Quote 33%, not 73%** |
| "we have a known false-positive rate" | implied | ❌ **never measured. The ~1% is how we set the bar, not a result** |
| "we detect them same-day" | implied | ❌ **no — the catalog itself is up to 10 days late** |
| "we detect 'went quiet'" | implied by the pitch | ⚠️ **not with the step verifier. Galaxy 15 proves it. Needs `quiet.py`** |
| "the GEO gap is an altitude-vs-longitude problem" | stated in [[RESULTS - Beyond Starlink]] | ❌ **retracted — drift and altitude are the same number** |
| "we monitor LEO reentries" | implied by the deorbit bucket | ❌ **operator data vanishes first; we cannot see the end of life** |

## Next three moves, in order

1. **Change `WINDOW_DAYS` from 3.0 to 14.0 in `verify.py`.** 71% → 86% on documented GEO
   events. One constant. (Tech lane.)
2. **Add inclination as a second verify channel** — independent of altitude, 7.5× separation,
   free from data we already pull.
3. **Re-open the SES question.** Its stated explanation is now falsified and we don't have a
   replacement.

## Reproduce it

```bash
cd "C:\Space\06 Code"
python -c "import csv;[print(r) for r in csv.DictReader(open('ground_truth.csv'))]"
python detect.py --group starlink --mode alert --csv     # 2026-07-22 flags
```

Ground truth pulled from McDowell's GCAT `geotab.tsv` (GEO classification and drift rates),
Space-Track `satcat` (decay records) and `gp_history` (burn dating), plus the press releases
and Space Force statements cited per-row in the CSV's `source` column.
