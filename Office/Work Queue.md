---
updated: 2026-07-21
status: built, not yet connected
code: "06 Code/worker.py"
---

# 🎫 Work Queue

The idea: **you only talk to the room. The room does the work.**

You raise something out loud. They argue about it. One of them claims it, and that claim
becomes a job that runs through **Claude Code on this machine** — which reads files, writes
code, runs things, and comes back. The person who claimed it reports what happened, in their
own voice, and banks what they learned.

```
you talk → the room argues → ONE person claims it
                                     ↓
                        [WORK] add gap detection to supgp_archive.py
                                     ↓
                       claude -p  (Read, Write, Edit, Bash, in C:\Space)
                                     ↓
                    they report back out loud + bank a lesson
```

## Why serial, one at a time

Six agents firing jobs in parallel isn't a team, it's a race condition with personalities.
One ticket, finished and reported, then the next. That's also what makes it feel like an
organised office rather than noise.

## Claiming a job

The rules are already live in the room. Exactly one person per turn ends their line with a tag:

> ⚙️ Rook: I'll take that one. **[WORK]** add transient failure detection and retry to supgp_archive.py

- One tag per turn, from one person. Never two.
- Only for real work on files, code or data — never for thinking or opinions.
- One imperative sentence naming the thing to change.
- **Most turns should tag nothing.**

## Cost

`claude -p` runs through the `claude` CLI already on this machine, so **no new API key and no
separate bill** — it uses the existing plan. It reports what each job cost, and that real
figure goes on the board next to the notional ledger in [[Money]].

Measured: a headless round trip returns in **4.7 seconds**.

## Status — built, one edit from live

| Piece | State |
|---|---|
| `worker.py` — serial queue, runner, ledger, timeout, cost capture | ✅ written and importable |
| Room rules — they claim jobs correctly | ✅ live, tested |
| Git undo before anything can write | ✅ `2a581d1` |
| Permission rules in `.claude/settings.local.json` | ✅ added |
| **The ~10 lines connecting a claimed tag to the queue** | ❌ **blocked** |
| Approve-before-run button in the UI | ❌ not built |

**What blocked it:** the permission classifier in the Claude Code session refused that specific
edit repeatedly, even after the git baseline and the permission rules were in place. It was not
worked around, deliberately.

Right now the room *says* the tag out loud and nothing happens with it.

## The risk worth remembering when it does go live

The thing authoring those job descriptions is the same local model that invented a leap-year
bug and misreported a fix four hours after it shipped ([[The Team]]). It would be writing
one-line tasks that Claude Code then executes with file-write and shell access.

That's why the design has an approve step, and why git went in first. Recommended order:

1. Run the first few with **approve-before-run**, and read each task before pressing go.
2. Switch to `--brain claude` so the *author* of the task is a good model.
3. Only then consider `--auto`.
