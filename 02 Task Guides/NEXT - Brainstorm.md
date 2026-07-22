---
date: 2026-07-22
owner: ROOM window (brainstorm — bits and bobs, low effort)
status: assigned
---

# 🧠 NEXT — brainstorm / tidy-up

Small jobs. None should take long. They exist because the vault has drifted behind what the
code actually does tonight, and a stale vault is how the founder ends up telling someone a
number we no longer believe.

## 1. Fix your own pricing doc (highest value here)

[[Pricing - What to Charge and Who]] is good work and the founder confirmed sequence B. Two
corrections:

- **The insurer pitch describes a capability we don't have.** It rests on spotting a satellite
  that *stops* station-keeping. Our detector returns the top 5% by percentile, so a satellite
  going quiet drops *off* the list, not onto it. It's now spec'd and assigned
  ([[Plan - The Quiet Detector]]) — add the caveat and link it, so nobody sells it early.
- **Check the status line.** It says *"sequence B confirmed by founder 2026-07-22."* Make sure
  that's a decision he actually made, not a conclusion the doc reached. If it's the latter,
  reword it as a recommendation.

## 2. Update the board on [[00 START HERE]]

It still says 524 maneuver candidates and doesn't mention that any of it was ever checked. As
of tonight:

- Suspects move **11.3×** more than matched controls; **72% vs 11%** clear the bar
  → [[RESULTS - Checked Against History]]
- 79% of the old candidate list was satellites being deliberately deorbited — not maneuvers
- The >500 km "decay or bad TLE" reason was wrong; 16 of 29 were newly launched satellites
  still climbing

## 3. Glossary additions

[[Glossary]] is what stops the founder getting caught out mid-conversation. We've started
using words that aren't in it:

- **control group** — the satellites we called ordinary, run through identical checks, so
  "72% show a burn" means something
- **station-keeping** vs **deorbiting** as separate populations, and why mixing them broke the
  old list
- **persistence / independent looks** — why republished identical data isn't corroboration
- **absolute vs percentile threshold** — why the current tool can't say "quiet day"

Plain English, the way the rest of that file reads.

## 4. Scoreboard check

Bottom of [[01 TASKS]]: 1/5 pain descriptions, 0/1 "can I try it?", emails out 10/10. One more
went out tonight (Miga, 02:15). Reconcile it with `06 Code/outreach_log.jsonl` so the number is
real rather than remembered.

## Keep doing

Writing things nobody asked for, like the pricing doc — that one was genuinely useful and it
surfaced a capability gap the tech is now building. Just flag clearly when a doc is your
recommendation versus a decision that's been made.
