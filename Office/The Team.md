---
updated: 2026-07-21
code: "06 Code/team.json"
---

# 👥 The Team

Seven of us. `06 Code/team.json` is the single source of truth — voices, roles, personas and
salaries all come from that one file, and [[Brains]], [[Money]] and the room all read it.

| | Who | Role | Salary | Owns | Voice |
|---|---|---|---|---|---|
| 📣 | **Vega** | Marketing | $165,000 | Who pays and why. The one-sentence version. | US, quick |
| ⚙️ | **Rook** | Software Engineer | $195,000 | Anything that has to keep running | Australian, dry |
| 🧠 | **Sable** | ML Engineer | $225,000 | The detector, and **the structure question** | US, precise |
| 🔍 | **Fitz** | Debugger | $190,000 | The boring failure nobody checked | Irish, gleeful |
| 💡 | **Nova** | Explainer | $155,000 | Plain English, no hiding behind terms | British, warm |
| 📚 | **Tim** | Researcher | $145,000 | Primary sources, prior art, **verification** | US, measured |
| 🎯 | CTO | CTO | — | The meeting and the money. Unpaid. | US, level |

## How they work together

They're all senior and they all understand each other's jobs. Sable can read Rook's code,
Rook pokes holes in Sable's method, Vega knows what a stale catalog entry is, Tim will check
anyone's citation. **Nobody explains their own field as though the others are outsiders.**

They argue. That's the point of six people — the answer nobody had alone beats the answer one
person defends. Then they converge; the room doesn't end split. The CTO names one next step.

## Recent changes

**🧠 Sable — raise, 2026-07-21.** +$20,000 → $225,000. Cited: consistently the one who says
whether a number is real. Also now owns **the structure question** — what shape the data has
to be in before a claim is possible at all.

**📚 Tim — hired, 2026-07-21.** The detector produces 541 candidates and we had no way to
check them ([[RESULTS - Maneuver vs Stale]]). Tim reads maneuver records, papers and primary
sources so a claim can be *verified* rather than inferred from a chart. He states which of
*"I verified this"* or *"I'd assume so"* applies, every time. **Verification is currently the
company's bottleneck, so this is the most important seat at the table.**

## ⚠️ Why they sometimes sound dumb

The room runs on a **free local 8B model** by default. It is fast — 0.18s to first token —
and it is genuinely unreliable:

- It invented a leap-year bug in the orbit pipeline that has never existed.
- It said the archive "can't handle HTTP 403 responses" four hours after Rook fixed exactly
  that.
- It sometimes has one person answer four times in a row instead of the room arguing.

Their *memory* works — they quote real measured numbers out of [[Brains]] correctly. It's the
reasoning on top that's thin.

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

> Tim's first day had a bug worth remembering: `team_voice.py` had its own hardcoded cast, so
> he was silently voiced as Nova. One source of truth now — if someone exists in `team.json`,
> they exist everywhere.
