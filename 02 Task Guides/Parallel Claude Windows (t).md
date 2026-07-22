# Parallel Claude Windows — the `t` setup

Set up 2026-07-22, copied from [[03 Reference/Video Digest - Agentic Engineer Workflow (Zen van Riel)|Zen van Riel's workflow video]].

## The one thing to remember

Open Command Prompt (or PowerShell), type **`t`**, press Enter. Four Claude Code windows — plain Command Prompt windows — appear in a 2×2 grid:

| | Left | Right |
|---|---|---|
| **Top** | HIGH effort | HIGH effort |
| **Bottom** | MEDIUM effort | LOW effort |

- **Top row (HIGH):** big stuff — planning, features, anything that needs real thinking.
- **Bottom-left (MEDIUM):** normal everyday tasks.
- **Bottom-right (LOW):** quick questions ("what does this file do?"). Answers fast, costs little.

`t C:\SomeOtherFolder` opens the grid in a different repo. Script lives at [t.ps1](../06 Code/t.ps1).

## Status line

Every Claude window shows at the bottom: model | effort | folder | branch | context left.
When "ctx % left" gets low, run `/compact` (squeeze the conversation down) or `/clear` (fresh start). Low context = slower, dumber answers.

## Slash commands that come with this

- **`/smell`** — before making a PR, reviews your uncommitted changes against Clean Code + design-pattern rules. Ranked findings, doesn't touch code.
- **`/wt <name>`** — makes a *git worktree* (jargon: a separate temporary copy of the repo) so two windows can edit the same files without colliding. Lands in `~\.claude\worktrees\`. Status line shows `[worktree]` when you're inside one.
- **`/wt-done <name>`** — cleans the worktree up when the stream is finished (refuses if there are unsaved changes).

## Rules of thumb (from the video, worth keeping)

- Four streams max — that's a human attention limit, not a tool limit.
- Route by size: big job → HIGH window, quick lookup → LOW window.
- All four windows share one git checkout — if two need to *edit* at once, give one a `/wt` worktree.
- Expect 30–60% faster, not 5×. Read the code before you PR it.
