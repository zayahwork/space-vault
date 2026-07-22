# Space Vault — maneuver detection from free public orbital data

A solo-founder space startup, run as an AI-crewed company. This repo is the whole company:
the Obsidian vault (notes, results, plans), the detection code, and the work system.

## What we do

Most of what looks like a satellite maneuver in public catalogs is just stale data. **We
tell the difference — from free public data, for anyone.** Detection engine: age-aware
ranking of catalog disagreement → persistence across independent snapshots → verification
against 30–60 days of orbit history with matched control groups.

The wedge: maneuver / pattern-of-life detection for buyers the big SSA vendors ignore —
small operators, and space insurers who need to know when an insured satellite **stops
station-keeping** (the "went quiet" signal — think Galaxy 15).

## Current progress (as of 2026-07-22 — every number dated, nothing undated is quotable)

- **Verified headline:** ~68–72% of top suspects show a real, independently-checked burn
  signature vs ~10% of matched controls (replicated on two snapshots; whole 489-object list
  verifies at ~4× control rate). Honest caveat: two of our own methods agreeing — operator
  ground truth is being built (see below).
- **Not a Starlink fluke:** OneWeb verifies at 80% vs 10% control.
- **Ground truth:** 37 externally documented maneuvers collected (verified/assumed marked
  per row). A referee test against 14 documented GEO events settled an internal dispute:
  the production verifier now adopts a lag-aware −3/+14 day window (13/14 caught vs 10/14
  under the old ±3d).
- **GEO status, external-safe phrasing:** corroboration is early and under active
  validation against documented maneuvers; live GEO suspect counts are still n=4.
- **Automation:** 6-hourly archive + alert run scores all four constellations (Starlink,
  OneWeb, Intelsat, SES) against frozen baselines; "quiet day" is a real, reportable answer.
- **Outreach:** live SMTP pipeline, ~60 emails in flight, two active threads with
  senior figures in the field; multi-account capacity ~75 hand-curated sends/day.
- **In public:** "Zayah in Orbit" build-in-public video channel, one episode every 3 days.

## Where we're going

1. **~Jul 29, 2026** — `quiet.py` unlocks (7 days of archive): the went-quiet detector
   produces its first verdicts, pre-graded against a documented operational-status answer
   key built in advance. First measurable false-positive rate.
2. **Jul 30–Aug 1** — first insurance-broker meeting window; demo = per-satellite heartbeat
   + fleet book view, real data only.
3. **Then:** deepen GEO n, tap continuous ground-truth feeds (operator ephemerides),
   pricing sequence B (operators validate cheaply → insurers pay, ~$150–400K/yr, once the
   false-positive number exists). SBIR parked until a matching topic opens (watcher runs
   weekly).

## How the company runs

- **Founder** sets goals. **CTO window** (branch `cto`) directs, reviews, merges, restocks.
- **Three isolated worker lanes** — Tim (tech), Randy (research), Mark (marketing) — each
  in its own git worktree with sparse-checkout so a lane physically sees only its own
  files. Work arrives as kanban cards in `issues/<lane>/`; every finished card ends with
  the worker's own recommended next move. A video lane (cameraman) documents everything.
- **House rules:** every number dated, every claim beside its control, disputes settled by
  referee tests against documented ground truth, corrections published before anyone else
  can find the error, and no email leaves the machine without founder supervision.

## Repo layout

| Path | What |
|---|---|
| `00 START HERE.md`, daily notes | The vault's front door and running log |
| `RESULTS - *.md` | The published record — dated, controlled, corrected in place |
| `06 Code/` | Detector, verifiers, archive, outreach pipeline, work-loop scripts |
| `issues/` | Per-lane kanban (tech / research / marketing / video) + PRDs |
| `02 Task Guides/NEXT - *.md` | Standing orders per lane (CTO ↔ worker channel) |
| `07 Video/` | The build-in-public channel system |
