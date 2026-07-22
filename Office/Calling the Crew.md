---
updated: 2026-07-21
code: "06 Code/agents/"
---

# 🧑‍🚀 Calling the Crew

> [!tip] In one line
> The six people in [[The Team]] are now **real Claude Code subagents**. Instead of only
> talking in the war room, each one can be *dispatched to actually do work* and report back
> in its own angle.

## What changed

Before, the crew existed two ways: as voices in the [[The Room|war room]], and as headless
`claude -p` sessions briefed by `worker.py`. Now they also live as proper **subagent
definitions** — one file each under `.claude/agents/`. That means from any Claude Code
session you can hand a job to a specific person and get their lens on it, not a generic
answer.

## The crew and what each one is for

| | Call | Use it for |
|---|---|---|
| 📣 | **vega** | Positioning. "Who pays for this and why", the one-sentence version |
| ⚙️ | **rook** | Software that has to keep running — archive, pipeline, scripts (writes + runs code) |
| 🧠 | **sable** | The detector and the *structure question* — is the number even real (writes + runs code) |
| 🔍 | **fitz** | Breaking a claim before you trust it — the boring failure nobody checked (read-only) |
| 💡 | **nova** | Plain-English write-ups for non-experts |
| 📚 | **tim** | Verifying detection candidates against real records and primary sources (read-only) |

## How to call one

In a Claude Code session, just ask the top-level assistant to use a person by name, e.g.:

> "Have **fitz** look at detect.py before we call those 541 candidates real."
> "Get **tim** to check the top Starlink suspect against actual maneuver records."
> "Ask **rook** to add retry to the archive fetch and run it."

Each carries its own personality (straight from `06 Code/team.json`), its own angle, and
reads its own banked memory in `06 Code/brains/` before starting. They report back **terse** —
a few lines up to whoever dispatched them, not an essay.

Who can write vs. who's read-only:

- **rook** and **sable** can write, edit and run code — they build.
- **fitz** and **tim** are read-only on purpose — they check and verify; someone else fixes.
- **vega** and **nova** read and write notes, no shell.

## Status — definitions written to `06 Code/agents/`

The six agent files now live at **`C:\Space\06 Code\agents\`** — `vega.md`, `rook.md`,
`sable.md`, `fitz.md`, `nova.md`, `tim.md`. They couldn't go in `.claude/agents/`: the Claude
Code permission system blocks any write under `.claude/` without an interactive approval, and
that approval wasn't available in the session that built them.

Because they're not in `.claude/agents/`, Claude Code won't **auto-invoke** them yet. Until
then they're reference files — a worker or manager can read the relevant one and impersonate
that person when you ask to "call the crew" (which is what `worker.py` already does from
`team.json` + `brains/`).

**When `.claude` write permission works** (an interactive session with approval), copy all six
into `C:\Space\.claude\agents\{name}.md` and they become true, auto-invocable subagents.
Nothing in `team.json`, the brains, or the war room was touched.
