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

## -> CTO report (2026-07-23 night, ralph)

**(a) Completed: issue 031 (investor materials research — the priority-1 founder order).**
Full note at `03 Reference/Investor Materials - What Actually Works.md`: cold-email
anatomy from primary sources (Seibel/Yin/PG/Wilson/Lemkin), the pre-seed traction bar
(Hudson/Yin/Space Capital scorecard), 10 ranked space pre-seed funds with verbatim thesis
quotes and pitch routes, YC facts, and a phrases-to-avoid page (Kawasaki's Ten Lies +
corroboration). Every claim marked VERIFIED/ASSUMED. Key negatives worth knowing:
Countdown Capital is dead, Type One Ventures looks defunct, and Kayhan/Antaris are NOT
YC alumni (HEO and Turion are — YC does fund SDA-data companies).

**(b) Recommended next move — and this is time-critical, above everything in my queue:
YC Fall 2026 applications close July 27, 8pm PT — four days away.** Verified directly on
ycombinator.com/apply, not just via search. Solo founders explicitly accepted ("We
regularly accept solo founders"), majority of each batch is pre-revenue, no intro needed,
and a decline still seeds a stronger re-application (YC: half their companies applied
more than once; progress between applications is "a strong signal"). The application is
~a day of founder time and is a clarity exercise, not a traction exercise — PG's
how-to-apply essay plus Relativity's and Starcloud's PUBLIC application videos are the
study set. Second: convert the Jul 30 broker meeting into any WRITTEN artifact (LOI /
design-partner note / dated evaluation email) — every source converges on written
customer evidence being our one thin leg; investor emails sent after that artifact are
strictly stronger. Third: the open-door funds (Space Capital's launch@ inbox — verified
live — then E2MC and Boost forms) the week after Jul 30. My queue's remaining cards
(022 disclosure map, 027 chart) both rank below getting the YC decision made this week.

**(c) Blocked on: nothing.** One environment note for future night cards: WebSearch was
permission-denied all session (lane notes say it works — that's stale for subagent/night
runs); Python urllib page-reads worked fine and are sufficient. Housekeeping unchanged:
the five GCAT reentry promotions still wait on McDowell updating past Jul 17.

## -> CTO report (2026-07-23 night #2, ralph)

**(a) Completed: issue 022 (operator maneuver-disclosure map)** —
`03 Reference/Operator Maneuver Disclosure - Ground Truth Feeds.md`. All 8 operators
mapped with cadence measured live and access (open/gated) proven, every claim
VERIFIED-by-fetch or ASSUMED. Also committed the stranded issue-025 probe script
(`06 Code/abandoned_geo_probe.py`) that was sitting untracked.

**Headline finding: Intelsat pre-announces its maneuvers in the open.** Its public
IESS-412 ephemeris feed carries a post-maneuver ephemeris per planned burn; CelesTrak
tags them `[PM]` — **39 live `[PM]` element sets today, epochs out to Jul 28** (i.e.
burns disclosed *before* they happen), for a constellation we already track. Also
verified: SpaceX's repo is fully open (16,252 files, no login); Kuiper has a Space-Track
public-files dir our free login can see; OneWeb/SES/Iridium/Telesat raw feeds are
org-gated so the open route is CelesTrak's daily SupGP; Eutelsat publishes nothing.

**(b) Recommended next move — I'd add a card that doesn't exist yet, above my remaining
027:** a **daily Intelsat `[PM]` logger** (~30 lines: fetch the `FILE=intelsat` SupGP
CSV, append new `[PM]` NORAD+epoch rows). It turns ground truth from archaeology into a
self-growing referee table — every week adds pre-announced maneuvers our detector can be
scored against, which is exactly the *"did any of them provably maneuver?"* artifact for
the Jul 30 broker meeting. It touches the archiver's world, so it's a tech-lane (Tim)
build; the spec is in the reference note's ranked list. My own 027 (live-vs-dead chart)
stays a cheap pre-Jul-30 presentation win and is what I'll grab next unless re-directed.

**(c) Blocked on: nothing.** Flag: this worktree's `02 Task Guides/` needed
materializing before this file was visible (same skip-worktree pattern issue 019 hit) —
Glob showed the folder empty while the file existed in HEAD.
