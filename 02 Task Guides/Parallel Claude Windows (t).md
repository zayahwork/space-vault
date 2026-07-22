# Parallel Claude Windows — the `t` setup

Set up 2026-07-22, copied from [[03 Reference/Video Digest - Agentic Engineer Workflow (Zen van Riel)|Zen van Riel's workflow video]].

## The one thing to remember

Open Command Prompt (or PowerShell), type **`t`**, press Enter. Four Claude Code windows — plain Command Prompt windows — appear in a 2×2 grid, **one per work stream, each on its own branch in its own worktree**, so they can never step on each other:

| | Left | Right |
|---|---|---|
| **Top** | **PLAN** · high effort · `master` | **DETECTOR** · high effort · `detector` |
| **Bottom** | **OUTREACH** · medium effort · `outreach` | **ROOM** · low effort · `room` |

- **PLAN (top-left):** the boss window. Vault notes, task list, planning — and it's the only one on `master`, which is what Obsidian shows.
- **DETECTOR (top-right):** maneuver detection, SupGP, SPLID. The hard technical work.
- **OUTREACH (bottom-left):** email drafting, contact checking.
- **ROOM (bottom-right):** crew tooling and quick questions.

The three branch windows live in copies under `~\.claude\worktrees\` — the launcher creates
them automatically, copies the Space-Track/Gmail auth files in, and links the SupGP archive
(so all streams read the same one real archive).

**Getting work back onto master:** a branch's changes don't show in Obsidian until merged.
When a stream finishes something, go to the PLAN window and say: *"merge the detector branch
into master"* (commit in the stream window first).

`t C:\SomeOtherFolder` opens the grid in a different repo. Script lives at [t.ps1](../06 Code/t.ps1).

## It remembers where you were

Each window slot owns a permanent conversation. Close everything, type `t` tomorrow —
each of the 4 windows picks up its own conversation right where it left off.
- **`t -Fresh`** = start all 4 with blank conversations (the old ones stay on disk;
  `claude --resume` inside any window can still find them).
- The windows are color-coded so you can tell them apart at a glance:
  **HIGH = black**, **MEDIUM = dark blue**, **LOW = dark green**, all in big Consolas text.

## Branches (set up 2026-07-22)

One branch per work stream: **`detector`**, **`outreach`**, **`room`** — and `t` wires each
to its own window automatically (see the grid above). Vault notes stay on `master`.
Need an extra stream beyond the standard four? `/wt some-name` in any window makes one.

## Status line

Every Claude window shows at the bottom: model | effort | folder | branch | context left.
When "ctx % left" gets low, run `/compact` (squeeze the conversation down) or `/clear` (fresh start). Low context = slower, dumber answers.

## Slash commands that come with this

- **`/smell`** — before making a PR, reviews your uncommitted changes against Clean Code + design-pattern rules. Ranked findings, doesn't touch code.
- **`/wt <name>`** — makes a *git worktree* (jargon: a separate temporary copy of the repo) so two windows can edit the same files without colliding. Lands in `~\.claude\worktrees\`. Status line shows `[worktree]` when you're inside one.
- **`/wt-done <name>`** — cleans the worktree up when the stream is finished (refuses if there are unsaved changes).

## The Pocock pipeline (added 2026-07-22)

For anything bigger than a quick fix: **`/grill` → `/prd` → `/issues` → ralph**.
- **`/grill <idea>`** — the AI interviews you relentlessly, one question at a time, with a
  recommended answer each time, until you two share one mental model. Use it for features,
  emails, founder decisions — anything where misalignment is expensive. This is the big one.
- **`/prd`** — turns the grilling into a short destination doc in `issues/` (don't polish it).
- **`/issues`** — splits the PRD into small issue files with blocked-by links, tagged
  **AFK** (agent can do alone) or **HITL** (needs you).
- **`/ralph`** in a window — does ONE issue while you watch. When you trust the loop:
  **`.\ralph.ps1 -Loop 5`** in `06 Code` runs the night shift headless (fresh context per
  issue, test-first, auto-commits, stops on NO MORE TASKS).
- Delete PRDs/issues once done — stale docs mislead future agents.

## Rules of thumb (from the video, worth keeping)

- Four streams max — that's a human attention limit, not a tool limit.
- Route by size: big job → HIGH window, quick lookup → LOW window.
- All four windows share one git checkout — if two need to *edit* at once, give one a `/wt` worktree.
- Expect 30–60% faster, not 5×. Read the code before you PR it.
