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

## 1. Warm-up — issue 001 (tests for detect.py core math)

`06 Code/tests/test_detect.py` per the card. Every RESULTS number rides on this math and it
has zero automated coverage. Small, closed-ended, do it first.

## 2. Main build this week — issue 002 (GEO-aware verifier)

The founder meets a GEO insurance broker ~Jul 30. Right now we are half-blind exactly in her
market. Longitude drift + inclination, not altitude — full spec on the card. Target: a real
SES answer (signal with numbers, or miss explained with numbers) by **Jul 29**. Either
outcome updates `RESULTS - Beyond Starlink.md`.

## 3. When blocked or done — issue 003 (larger-n hardening)

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
