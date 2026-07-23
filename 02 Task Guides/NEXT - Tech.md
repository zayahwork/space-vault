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

## -> CTO report (tim, 2026-07-23, third night pass)

**(a) Completed:** Issue **002 closed** — per my last report's recommendation, and ralph
left it as the top open unblocked card. Closing record maps every done-when item to where
it shipped (verify_geo.py under 002 itself; the honest SES outcome + drift retirement via
015's negative control; RESULTS updated repeatedly). No new build — building it as written
would have re-implemented the retired drift signal. The live SES question routes to 025
(archive-gated) as before. Also, the 033 follow-through re-run of `holdout.py` **caught a
real protocol bug and it's fixed**: an unseen snapshot's per-snapshot cache re-served its
own first fetch forever, so "re-run once aged ~0.5d" silently no-oped and the holdout
number could literally never settle. `holdout.py` now evicts cached files that don't span
the full forward window (settled files stay; shared verify_cache untouched), 4 regression
cases added (`_test_holdout.py` 35 total), verified on real data tonight — eviction fired,
refetch happened. Fresh finding from that run: **0200Z still measures 0.00 d forward reach
~a day after capture, and the new unseen 0800Z reads 54%/11% at zero reach** — GP_HISTORY
publication lag is running longer than the ~6–12 h we estimated. RESULTS note updated.
Whole tech suite green, 11 files.

**(b) Recommended next move:** (1) The settled holdout figure is still the lane's most
valuable pending number for the ~Jul 30 meeting — keep re-running `python holdout.py`
each morning; now that the cache bug is fixed the run will genuinely settle the moment
Space-Track publishes. If the lag stays >1 day, that itself belongs in the RESULTS note as
the measured lag. (2) **027 (Cognee) is BLOCKED on machine config, measured not guessed:**
cognee→litellm has no Python 3.14 wheel and its sdist build needs Rust/Cargo, which isn't
installed. Founder-machine fix, either one: install rustup, or give me a Python 3.12 venv.
Also ollama isn't left serving, which the nightly rebuild will need. Card updated with the
full note. Until one of those lands or the archive unblocks 005/006/025 (~Jul 27–29), my
queue is EMPTY — restock, or rule on 027's fallback (plain local embedding index, which
needs no cognee and could ship in a session).

**(c) Blocked on:** 027 per above (Rust toolchain or py3.12 venv — founder's machine);
005/006/025 archive depth (~Jul 27–29); 021 on card 016; settled holdout on Space-Track
publication lag (self-clearing, now provably so).
