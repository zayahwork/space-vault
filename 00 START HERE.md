# 🚀 START HERE

> [!tip] The whole system in one line
> Open **[[01 TASKS]]** → work the bullets top to bottom → each bullet links to a guide with
> *everything* (steps, addresses, drafts) → tick the box → tell Claude when a chunk is done.

## 📊 The board — what actually exists right now (updated 2026-07-21)

| | Thing | State | Where |
|---|---|---|---|
| 🛰️ | **Maneuver-vs-stale detector** | **Working.** 524 maneuver candidates from 10,780 Starlink (17 impossible >500 km jumps gated out as data-quality flags); 85% of the naive list was just old data | [[RESULTS - Maneuver vs Stale]] |
| 📡 | SupGP + public-catalog archive | Running every 6h, now with retry + health log + GP capture | `06 Code/supgp_archive.py --health` |
| 📈 | First maneuver charts | 3/3 ISS maneuvers, Starlink deorbit caught | [[RESULTS - First Charts]] |
| 📬 | Outreach machine | 52 targets loaded (40 + batch 2's 12), batch 2 **drafted, not sent** | [[Guide - Daily Outreach]] · [[Outreach Emails - Batch 2]] |
| 🏛️ | SBIR / SAM.gov | **Parked.** Weekly watcher armed — it un-parks itself | [[Guide - SBIR Steps]] |
| 🏢 | **The office** — the room, the team, their brains, the money | 7 people · 14 lessons banked · $1,276 of $127,500 charged | **[[00 THE OFFICE]]** |
| 🖥️ | **The war room** — see them at the table and talk to them | Working. `cd "C:\Space\06 Code"` then type `jarvis` | [[The Room]] |
| 🗣️ | **Scoreboard** | **1 / 5** pain descriptions · **0 / 1** "can I try it?" | bottom of [[01 TASKS]] |

## Where everything lives

| Place | What it is | When to open |
|---|---|---|
| **[[01 TASKS]]** | THE list. Every task, in order, with checkboxes. | **Always. This is home.** |
| **02 Task Guides** | One how-to note per task — you only get there via the links in the list | When a bullet sends you |
| **03 Reference** | [[Glossary]] (what words mean) · [[Outreach Emails]] (drafts) · [[Daily Schedule]] · big research docs | When a guide sends you |
| **04 Ideas** | Parked visions ([[Space Highway - the far-future vision\|Space Highway]]) | Rarely — on purpose |
| **05 Routine (powers calendar)** | Feeds the daily calendar (🏋️ 10:00 lift, meals, sleep) | Never — it just works |
| **Office** | How we work: the room, the team, their memory, the money | [[00 THE OFFICE]] — start there |
| **06 Code** | The actual programs + their output charts | During build sessions with Claude |
| **99 Archive** | Everything old (the day-file system, the planner before that) | Never, unless digging history |

## The mission (so you never lose the plot)

Software that learns every satellite's normal routine from **free public orbit data**, then
flags when one moves unexpectedly (**maneuver detection** / **pattern of life** — [[Glossary]]).
Sell it cheap to the buyers the big players ignore; get the government to fund the build
(**SBIR**). Same detection brain later points at asteroids. Way later: the space highway.

## The only scoreboard that matters
🗣️ **5+ people describing their pain unprompted** · 💰 **1+ "can I try it / what would it cost?"**
(Live tally at the bottom of [[01 TASKS]].)
