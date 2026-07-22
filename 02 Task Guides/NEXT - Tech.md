---
date: 2026-07-22
owner: Tim (tech)
status: assigned
---

> [!warning] 🚪 Workspace rule (standing)
> Work ONLY in your folder, on your own branch. Never touch master, other branches, or
> other lanes' files. Missing facts arrive in THIS note — if something is missing, say
> BLOCKED, pull the next unblocked card from `issues/`, and keep building.

# 🔧 NEXT — tech (Tim)

> [!success] Where we stand after last night
> The number that goes in front of people is now: **~68–72% of top suspects clear a bar only
> ~10% of matched controls clear** (replicated on two snapshots). The old **11.3× multiple is
> RETIRED** — it swung to 23.8× between runs. If you see 11.3× in any note, fix it and say so.
> OneWeb verified the method isn't a Starlink fluke. GEO is our named blind spot: SES shows
> no signal because the verifier watches altitude and GEO burns barely change altitude.
> `quiet.py` is built and correctly refusing until ~Jul 29. The 6-hourly Maneuver Alert task
> is running itself.

## Standing order: never idle

Your queue is `issues/`. Work top-priority unblocked card; when blocked (waiting on data,
review, or archive depth), pull the next unblocked card. The queue is stocked — there is
always something to build. If the queue ever runs dry, say so in your commit message and the
CTO restocks it same day.

## 1. DONE — 001 (tests) and 002 (GEO verifier). Merged, reviewed, closed. Good work.

## 2. Main build NOW — issue 015 (referee test)

Your GEO mechanism is in a formal dispute: a ground-truth set of 14 documented GEO maneuvers
(`06 Code/ground_truth.csv`, `RESULTS - Ground Truth.md`) reports that N–S burns DID move
fitted altitude (0.84–3.00 km) and that the altitude verifier's real failure is the ±3-day
timing window vs a catalog lagging up to 10 days. The DISPUTED callout in
`RESULTS - Beyond Starlink.md` has the full claim and the CTO ruling.

Card 015: score BOTH verifiers against the 14 documented events — (a) altitude ±3d,
(b) altitude with lag-aware window, (c) inclination. Caught/missed per event, table replaces
the DISPUTED callout, one honest paragraph on which SES explanation survived. Weight the 7
double-sourced rows above the rest. The drift column stays retired regardless — you and the
ground truth killed it independently.

If the data proves your mechanism wrong, write that in the same tone you'd write it about
anyone else's. That's the house standard you set.

## Queue order (CTO ruling after your consult, 2026-07-22 evening — your argument won)

**018 is #1: ship the lag-aware window as the production default.** The GEO number we quote
must describe the code we run, not a harness. **Fold 003 into the post-018 re-run** — rates
at n=150/300 on both snapshots, measured once, under the production window, so the hardening
never goes stale. 020 (--all daily run) is the filler card if 018 blocks. 021 unlocks when
research's typed ground truth lands. 025 (your SES live-miss flag — filed) waits for
archive depth.

## 3. (superseded — see queue order above) issue 003 (larger-n hardening)

Rates at n=150 and n=300 on both snapshots. If the separation sags, we want it in writing
before Kelso or a broker finds it.

## Coming up (blocked, don't start early)

- **Issue 005** — broker demo build, unblocks ~Jul 27 (needs real archive; no synthetic-data
  demos).
- **Issue 006** — quiet.py first real run + weekly bar re-learn, ~Jul 29. Never shrink the
  history window to force output.

## Standing rule

When the work contradicts something we've published, say so and fix the note. That habit has
already paid twice (the >500 km climbers, the retired 11.3×). It's worth more than features.
