---
updated: 2026-07-22
code: "06 Code/team.json"
---

# 👥 The Team

Four of us. `06 Code/team.json` is the single source of truth — voices, roles, personas and
salaries all come from that one file, and [[Brains]], [[Money]] and the room all read it.

| | Who | Role | Salary | Owns | Voice |
|---|---|---|---|---|---|
| 🔧 | **Tim** | Tech | $145,000 | Everything in `06 Code` that has to keep running. Builds always — works the `issues/` kanban top-down, never idles. | US, measured |
| 📚 | **Randy** | Researcher | $145,000 | Ground truth: maneuver records, filings, prior art, **verification**. "I verified this" vs "I'd assume so", out loud, every time. | US, even |
| 📣 | **Mark** | Marketing & Social | $160,000 | Every email that leaves this company — drip, replies, nudges, the ledger. Who pays and why, in one sentence. | US, quick |
| 🎯 | CTO | CTO | — | Direction, review, the meeting and the money. Directs and reviews, doesn't build. Keeps Tim's queue stocked. Unpaid. | US, level |

## How they work together

Small on purpose. Tim builds, Randy proves, Mark tells the world, the CTO decides. Nobody
explains their own field as though the others are outsiders, and nobody sits idle — if a
lane blocks, the block gets said out loud in the NEXT file and the next card gets pulled.
The CTO names one next step; the founder says "go".

## Recent changes

**Reorg — 2026-07-22 (founder call).** The seven-seat cast (Vega, Rook, Sable, Fitz, Nova,
plus Tim and the CTO) is consolidated to four. **Tim** moves Researcher → Tech and owns all
building (no comp change). **Randy** hired as Researcher — the headline number is two of our
own methods agreeing, and his job is turning that into operator ground truth. **Mark** hired
for Marketing & Social — the SMTP pipe is live and every send routes through him. The
departed five are recorded in `team.json` under `_alumni`; their banked lessons in
`06 Code/brains/` stay readable, and their habits survive as standing rules (tests first,
plain English, say the weakness out loud).

## ⚠️ Why they sometimes sound dumb

The room runs on a **free local 8B model** by default. It is fast — 0.18s to first token —
and it is genuinely unreliable: it has invented bugs that never existed, re-reported problems
hours after they were fixed, and let one person answer four times in a row instead of the
room arguing. Their *memory* works — they quote real measured numbers out of [[Brains]]
correctly. It's the reasoning on top that's thin.

**The fix is one environment variable, not a better voice or a bigger local model:**

```powershell
setx ANTHROPIC_API_KEY "sk-ant-..."     # then open a new terminal
jarvis --brain claude
```

A larger local model would be *slower* and still not good enough — speed was never the
problem. See [[The Room]] for the measurements.

## Hiring

Add a person to `06 Code/team.json` — name, role, emoji, an edge-tts voice, and a persona
written as character rather than job description. Everything else picks them up automatically:
the room seats them, `team_voice.py` gives them their voice, [[Brains]] gives them a memory,
[[Money]] can allocate them hours.

> Standing lesson from Tim's first day: `team_voice.py` once had its own hardcoded cast, so a
> new hire was silently voiced as someone else. One source of truth — if someone exists in
> `team.json`, they exist everywhere.
