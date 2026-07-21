---
updated: 2026-07-21
---

# 🏢 THE OFFICE

> [!tip] What this folder is
> Everything about **how we work** — the room, the people, their memory, the money.
> The *work itself* lives in [[01 TASKS]] and the results notes. This is the machinery.

## Open the room

```
cd "C:\Space\06 Code"
jarvis
```

A browser opens at `127.0.0.1:8770`. Talk normally. They answer out loud, in their own
voices, and you watch who's speaking. **End call** shuts it down completely.

> [!warning] Use `jarvis`, not `jarvis.ps1`
> PowerShell refuses to run unsigned `.ps1` files under the default policy. `jarvis.cmd`
> sidesteps that entirely, so nothing on the machine needs changing.

## The desk

| | Note | What's in it |
|---|---|---|
| 🖥️ | [[The Room]] | Every control, the echo fix, calibration, troubleshooting |
| 👥 | [[The Team]] | Who they are, what they own, who reports what |
| 🧠 | [[Brains]] | Their memory — how it works, what's banked, how to add |
| 💰 | [[Money]] | The $150K plan, hours vs salaries, what's been spent |
| 🎫 | [[Work Queue]] | Handing jobs to Claude Code — built, one edit from live |

## Where the office stands today

| | |
|---|---|
| **Team** | 6 + CTO. Newest hire: 📚 Tim, Researcher (2026-07-21) |
| **Memory** | 14 lessons banked — 8 proven, 6 hypotheses |
| **Money** | $1,276 charged of a $127,500 labour pool |
| **The room** | Working. Talks, listens, sees. Local brain is the weak part. |
| **Work queue** | Built and tested; the last connecting edit is blocked |
| **Undo** | `C:\Space` is under git as of `2a581d1`. Any bad edit is one command back. |

## The one rule the office runs on

**Nothing on the screen moves without a real number behind it.** Every ring is RMS from
actual audio. Every figure on the board is read off a real file when you ask for it. If a
number can't be read, its row is left out rather than guessed.

This isn't decoration — it's a direct response to `/app` at Remend shipping a fake progress
bar and a `setTimeout` that flipped a label to "Fixed". A screen that invents motion teaches
you to trust a demo instead of a system.
