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
> The number that goes in front of people is now **96% of top-75 suspects clear a bar only
> ~11% of matched controls clear** (both snapshots, issue 003). ⬆️ **This replaces 68–72%**,
> which was measured minutes after the snapshot when the forward half of the window held no
> data yet; re-scored aged, the same suspects give 96% and controls stay at 11%. Practical
> rule: a same-day LEO verify under-reports — re-run ~12h later before quoting. The old
> **11.3× multiple stays RETIRED** (rates, not multiples). Separation sags with n as a ranked
> list should: 96% at 75, 52–63% at 300, control rate 10% throughout.
>
> GEO is no longer the "altitude-blind" story — the referee (015) refuted that; the fix was
> the timing window and it now ships (018, −3/+14d at GEO). SES's live miss is formally
> **unexplained**, back on the open list (card 025). OneWeb verified the method isn't a
> Starlink fluke. `quiet.py` is built and correctly refusing until ~Jul 29. The 6-hourly
> Maneuver Alert task is running itself.

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

## -> CTO report (tim, 2026-07-23 night)

**(a) Completed:** Issue 020 — `python detect.py --all` (one-command daily run). All four
fleets, alert mode, persistence, one block to stdout + appended to the Alert Log; per-fleet
failure isolation; `_test_all.py` (12 cases, fakes only). Its FIRST real run caught a real
outage: the scheduled `daily_alert.py` had been crashing on every snapshot since
2026-07-22/1400Z, because SES's re-learned mixed-fleet baseline stores `min_km` as a list
(`[1.0, 2.0]`) and the scorer forwarded it as a scalar. Fixed in `load_baselines` (list →
None → per-object regime floors, exactly what the learn run applied), regression in
`_test_alert.py`, and the two missed snapshots (22/2000Z, 23/0200Z) backfilled. Whole tech
suite green (10 files).

**(b) Recommended next move:** tell the founder to switch the scheduled task to
`python detect.py --all` — today proved the current task fails silently and takes the whole
ledger with it; `--all` degrades per fleet instead. After that, my queue disagreement:
**033 (unseen-data holdout) over 002 and 027.** 002's remaining substance is really 025
(SES suspect selection), which is archive-gated until ~Jul 29 like everything else GEO; 027
is a CTO convenience tool. 033 is the number the ~Jul 30 broker meeting and every diligence
call will lean on, the archive is accruing genuinely-unseen data every 6h RIGHT NOW, and
the cutoff protocol should be written before the demo week starts, not during it.

**(c) Blocked on:** nothing for 020. Fleet-wide: 005/006/025 all gated on archive depth
(~Jul 29); 021 gated on card 016's maneuver_type column.

## -> CTO report (tim, 2026-07-23, second night pass)

**(a) Completed:** Issue 033 — the unseen-data holdout. `06 Code/holdout.py` +
`_test_holdout.py` (26 cases). Cutoff 2026-07-23 00:00Z, enforced not asserted: the script
refuses if the stored bars' provenance contains a post-cutoff snapshot, refuses to
improvise if no strictly-after snapshot exists, and prints the zero-overlap statement
every run. First run on the first unseen snapshot (07-23/0200Z): **at matched forward
reach the unseen day reproduces the tuned floor exactly — 76% vs 11%** (tuned side
76%/93% at the same reach, controls pinned both sides). The settled unseen number is
PROVISIONAL by physics: GP_HISTORY materializes ~6–12 h late, so 5.8 h after the snapshot
the fetched history held 0.00 d of forward reach — the run measures reach from the data
itself and says when to re-run. Ground-truth side: the 16 rows that chose the −3/+14 d
window are frozen tuning-side forever; the 3 rows added later (issue 026) are the event
holdout and go **3/3 caught** — the first non-circular window evidence we have. Side-by-side
table + weekly reuse instructions in `RESULTS - Checked Against History.md`.

**(b) Recommended next move:** two things, in order. (1) **Tomorrow, before anything else
in my lane: re-run `python holdout.py` once 07-23/0200Z has ≥0.5 d of published reach** —
that turns the provisional 76% into the settled holdout figure, and it's the number the
~Jul 30 broker meeting should carry (ten minutes of work, most of it a fetch). (2) A queue
decision I'd like ruled on: **card 002 should be closed or rewritten, not built as
written.** Its longitude-drift scoring was declared dead by both sides in the referee
(015), its verification half shipped in 018, and its live-SES-signal half IS card 025,
archive-gated to ~Jul 29. As written it now asks for known-dead work. That leaves 027
(Cognee) as my only unblocked card — I'll take it next unless the CTO restocks with
something that matters more for demo week.

**(c) Blocked on:** nothing for 033. Settled holdout figure gated ~12 h on GP_HISTORY
publication lag (self-clearing). 005/006/025 archive-gated ~Jul 29; 021 gated on 016.
