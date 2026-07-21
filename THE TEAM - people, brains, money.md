---
date: 2026-07-21
code: "06 Code/team.json · brain.py · payroll.py"
---

# 👥 The team — who they are, what they've learned, what they cost

## The roster

| | Who | Role | Salary (notional) | Owns |
|---|---|---|---|---|
| 📣 | **Vega** | Marketing | $165,000 | Who pays and why. The one-sentence version. |
| ⚙️ | **Rook** | Software Engineer | $195,000 | Anything that has to keep running. The archive. |
| 🧠 | **Sable** | ML Engineer | $225,000 | The detector, and **the structure question** |
| 🔍 | **Fitz** | Debugger | $190,000 | Finding the boring failure nobody checked |
| 💡 | **Nova** | Explainer | $155,000 | Plain English. No hiding behind terms. |
| 📚 | **Tim** | Researcher | $145,000 | **NEW 2026-07-21.** Primary sources, prior art, verification |
| 🎯 | CTO | CTO | — | Runs the meeting and the money. Founder-equivalent, unpaid. |

**Sable's raise:** +$20,000 → $225,000 on 2026-07-21. Cited: consistently the one who says
whether a number is real.

**Tim's remit** (why we hired): the detector now produces 541 candidates and we have *no way
to check them*. Tim reads maneuver records, papers and primary sources so a claim can be
verified rather than inferred from a chart. He states which of *"I verified this"* and
*"I'd assume so"* applies, every time.

## 🧠 Their brains — how they actually learn

Each person has a memory file in `06 Code/brains/`. It's read back before they speak, so what
they learned in June still applies in September. **This is the same design as Remend's
playbook**: proven outcomes get distilled into reusable lessons and retrieved next time.

The rule that keeps it honest: a lesson is `proven` only when something demonstrated it.
Everything else is `hypothesis` and says so. A brain full of confident guesses is worse than
no brain — it launders yesterday's guess into today's fact.

```bash
python brain.py                    # who knows what
python brain.py Sable              # read one brain
python brain.py --learn Tim "..." --evidence "..." --proven
python brain.py --demote Fitz 2    # that one didn't hold up
```

**Banked so far:** Sable 2 proven · Rook 2 proven · Fitz 2 proven · Vega 1 hypothesis ·
Tim 1 hypothesis · Nova 1 hypothesis.

> Why not fine-tune a model per person? You'd need thousands of examples each, a training run
> every time anyone learns anything, and you'd get a model that *sounds* like them rather than
> one that *knows more than yesterday*. Wrong tool. Memory beats weights here.

## 💰 The money — what $150,000 actually buys

> [!warning] The honest answer first
> These six at full salary cost **$1,075,000/yr**. $150,000 does not pay that team. It does
> not pay *any one of them* for a year. `payroll.py` refuses to pretend otherwise.

$150K isn't a random number — it's the size of an **SBIR Phase I**. So we stop thinking in
salaries and think in **hours**: salary ÷ 2,080 = an hourly rate, and the budget buys a number
of hours. That's also how a real Phase I budget is written, so the exercise isn't make-believe.

**Phase I — prove maneuver-vs-stale on live public data (6 months)**

| Who | $/hr | Hours | Cost | Why this many |
|---|---|---|---|---|
| 🧠 Sable | $108 | 400 | $43,269 | Owns the detector and the structure question |
| ⚙️ Rook | $94 | 350 | $32,812 | Archive and pipeline must not stop |
| 📚 Tim | $70 | 300 | $20,913 | Verification is now the bottleneck |
| 🔍 Fitz | $91 | 150 | $13,702 | The reason we don't publish something wrong |
| 📣 Vega | $79 | 120 | $9,519 | Customer conversations — the only real scoreboard |
| 💡 Nova | $75 | 90 | $6,707 | Writing it down so a stranger can follow it |
| | | **1,410** | **$126,923** | + $22,500 non-labor (compute, data, travel, filings) |

**$150,000 buys 12% of one team-year** — about **9 hours per person per week** for 26 weeks.

**The allocation rule:** hours follow the phase's risk, not seniority and not fairness. Right
now the entire risk is *"can we tell a maneuver from stale data"*, so ML and engineering get
the hours. When the risk moves, the allocation moves.

```bash
python payroll.py                                   # the plan
python payroll.py --charge Sable 6 "detector v1"    # log real work
python payroll.py --report                          # spent vs remaining
```

**Charged so far:** $1,276 of the $127,500 labor pool (Sable 6h, Rook 4h, Fitz 2h, Tim 1h).
