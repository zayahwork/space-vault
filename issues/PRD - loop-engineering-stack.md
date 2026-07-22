---
date: 2026-07-22
type: PRD
owner: CTO (infra) + Tim (Cognee) + Mark (email engine)
status: aligned — grilled with founder 2026-07-22 night
---

# PRD — Loop Engineering Stack

## 1. Problem

Today proved the company surges when the founder is present and stalls when he isn't: queues ran dry, loops died with closed terminals, usage blew to 17% of the weekly plan (cap: 14%), the CTO burned tokens doing deterministic git plumbing by hand, and a retired number nearly got mailed twice because decisions lived in chat. Momentum depends on humans being awake.

## 2. Solution

One organized loop stack: git+markdown stays the single source of truth; Windows Task Scheduler carries everything durable (8am harsh standup, nightly Cognee ingest); deterministic scripts do all plumbing for zero tokens (`gather.ps1`, `loop.ps1` control surface, kill-switch); `ralph.ps1` workers read their brain before work and bank a lesson after; a dated Decision Log makes rulings permanent; Cognee runs as a local, nightly-rebuilt, read-only knowledge index (vault always wins); email machinery goes fully automated at 60–75/day across 3 warmed accounts with exactly two human gates (new templates seen once; warm named threads never auto-replied).

## 3. User stories

- As the founder, at 8am my phone shows the harsh standup: per lane — shipped / blocked-with-blame / today's must-do / misses in bold — before I've had coffee.
- As the founder, I run `loop status` in any terminal and see every lane's state, budget remaining, and what's ready for a `/ralph`.
- As the founder, I stop everything instantly with `loop stop` — no killing processes, no faking budgets.
- As the CTO, gather/relay/status costs zero tokens — one script call.
- As a worker, I start every card knowing my banked lessons and end it having banked one more; I never re-learn a solved problem.
- As anyone, when I ask "didn't we decide this already?", the Decision Log or Cognee answers in seconds, with the date and the reasoning.
- As the founder, 60–75 curated emails leave per day whether I'm at the desk or not, and the only email I ever touch is a new template batch or a warm named thread.

## 4. Module map

- `06 Code/loops.json` — lane registry (worktree, branch, kanban, tools, enabled). Exists, uncommitted.
- `06 Code/loop.ps1` — NEW, control surface: `status | run | stop | budget`. **Deep module #1** — everything human-facing routes through it.
- `06 Code/gather.ps1` — NEW: merge lanes→master, pull/push origin, relay master→lanes, print status. Zero-token plumbing.
- `06 Code/standup.ps1` — NEW: assemble per-lane raw material (commits since yesterday, card states, → CTO reports, budget, countdown) + one low-effort claude pass for the harsh verdict → `STANDUP - <date>.md` + day-file link. Task Scheduler 7:57am.
- `06 Code/ralph.ps1` — MODIFIED: read `06 Code/brains/<lane>.md` before work, bank one lesson after (via brain.py); STOP_LOOPS flag check.
- `03 Reference/Decision Log.md` — NEW: dated rulings — decision / why / what evidence reverses it. Seeded with today's rulings.
- Cognee (Tim card): local install, local embeddings, `cognee_ingest.py` nightly rebuild from vault, query CLI. **Deep module #2** — read-only, disposable, vault always wins.
- Email engine (Mark card): 3-account config in `gmail_auth.json`, per-account 20/day + warm ramp, account column in ledger, segment-per-account, dated nudges auto-fire (approved templates only).

## 5. Implementation decisions

- Backbone: git+markdown; Airtable rejected for loops (revisit as outreach CRM at scale).
- Cognee adopted NOW at founder's call, as derived index only — nightly rebuild, local models, no credits, CTO-side first.
- Durability: Task Scheduler, not session cron, for anything load-bearing.
- Scripts before models; local 8B only for low-stakes classification; no voice system.
- Budget: 16 ralph iterations/day shared, tuned against the founder's usage page to hold 10–14% weekly-per-day.
- Email gates (permanent): new template batches get founder eyes once; warm named threads never auto-replied; loops never send.
- No subagents in this stack — worker opinions arrive via the → CTO report blocks.

## 6. Testing decisions

- `loop.ps1`: `status` matches reality (open cards, budget, running state) checked against git by hand once; `stop` halts a running ralph at the next iteration boundary.
- `gather.ps1`: run on a day with known lane commits — master ends up containing all, lanes end up containing master, zero conflicts unhandled.
- `standup.ps1`: dry-run produces a correct standup for today from real data before the schtask is registered.
- Cognee: acceptance = it answers 5 real questions (e.g. "why was 11.3× retired?") correctly from the graph, and a full delete + re-ingest reproduces identical answers.
- Email engine: sink-test (`_smtp_sink.py`) across 3 accounts before live; ledger shows account column; per-account counts never exceed config.

## 7. Out of scope

- Airtable (no capability gained at this scale) — revisit as CRM only.
- Voice/room theater in the standup — written verdict; unreliable 8B reasoning stays out of load-bearing paths.
- External memory DBs beyond Cognee (mem0/Letta/Zep) — one index is enough.
- Auto-replies to warm named threads and unsupervised new templates — reputation is unrecoverable in a market this small.
- Cameraman/video lane automation — founder's standing order.
