---
date: 2026-07-22
owner: Randy (research)
status: assigned
---

> [!warning] 🚪 Workspace rule (standing)
> Work ONLY in your folder, on your own branch. Never touch master, other branches, or other
> lanes' files. Missing facts arrive in THIS note — if something is missing, say BLOCKED and
> state exactly what you need.

# 📚 NEXT — research (Randy)

> [!todo] ⚡ CTO ruling after your consult (2026-07-22 evening) — your proposal won
> **Card 024 is your #1: pre-build the quiet detector's exam** (operational-status table +
> pre-registered verdicts for the 44 spike-history objects) so Jul 29's first run lands
> graded, the day before the broker meeting. 022 (disclosure map) moves to second — its
> findings partially fall out of 024 anyway. Finish 016's type tags if any remain, then 024.

> [!info] Why this lane exists right now
> Our headline number (**~68–72% of top suspects vs ~10% of controls**) is two of our own
> methods agreeing. That survives "how do you know?" — it does not survive *"did any of them
> actually, provably maneuver?"* You own closing that gap. Every claim you log states which
> of **"I verified this"** or **"I'd assume so"** applies. Every time.

## 1. Main mission — issue 004: the ground-truth maneuver set

Full spec on the card (`issues/004 - ground-truth maneuver set.md`). Short version: collect
15–20 externally documented real maneuvers (operator announcements, FCC/ITU relocation
filings, Space-Track decay messages, McDowell's GCAT, AMOS papers) across our four
constellations, then score our detector against them: what did we catch, what did we miss,
what did we flag that nobody documents. Output: `06 Code/ground_truth.csv` +
`RESULTS - Ground Truth.md`.

First target: **GEO events** (Intelsat/SES relocations and station-keeping anomalies) —
they're the best-documented maneuvers in public record AND they're the broker's market.

## 2. Second job — GEO prior art for Tim

While mining filings you'll trip over how others detect GEO maneuvers from element sets
(longitude-drift methods are published). Anything useful goes in a short note linked from
issue 002 — source cited, "verified vs assumed" stated. Don't build; Tim builds.

## Practical notes

- WebSearch works in these sessions; WebFetch does not — pull pages with Python urllib.
- No LinkedIn, ever (standing company rule). Papers, filings, operator pages, X.
- Small field. If a source is a person we might email one day, log them in the outreach
  target list notes rather than contacting anyone. Mark owns all sending.

## -> CTO report (2026-07-22 night, ralph)

**(a) Completed: issue 019** - the `rcat` mislabel in `06 Code/groundtruth/gt_sources.py`.
`gcat_phases()` docstring corrected (`rcat` = suborbital rocket catalog, NOT reentries;
reentries are `satcat` Status `R` with a `DDate`), `gcat_updated()` default flipped
`rcat` -> `satcat`, plus the CLI `updated` fallback which hardcoded `rcat` separately.
Verified live: `python gt_sources.py updated` now returns the `satcat.tsv` stamp
(`2026 Jul 17 2011:55`, matching issue 026's pull). Note: the "outside my sparse checkout"
blocker on the card was stale - the files were merely `skip-worktree` in this worktree, so I
materialized the one file and fixed it in-lane; no cross-lane reach happened.

**(b) Recommended next move: issue 025 (abandoned-GEO catalog study), and I'd rank it above
022.** Reasoning: 024's structural finding is that the Jul 29 exam has NO catch-rate
denominator - we can only measure false alarms. 025 is the only card that attacks that gap,
and it's pure measurement on snapshots we already archive (`gp_active` from 2026-07-22/0200Z
onward). The sooner it starts, the more snapshots accumulate before anyone asks "what does a
dead satellite look like in your data?" - which a broker will ask on Jul 30. 022 (disclosure
map) is real but is a reading job with no time-sensitivity; its findings also partially fall
out of 025's source work. One caution for 025: it needs several days of archived snapshots
for gap/cadence stats to mean anything, so an early pass should frame results as preliminary
and name the date after which the numbers stabilize.

**(c) Blocked on:** nothing. (Housekeeping, not a blocker: five GCAT reentry promotions from
issue 026 stay parked until McDowell's `satcat.tsv` updates past `Jul 17 2011:55` - worth a
re-check whenever a night shift has spare minutes.)
