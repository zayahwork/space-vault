---
updated: 2026-07-21
code: "06 Code/payroll.py · 06 Code/budget.json"
---

# 💰 Money

> [!warning] The honest answer first
> The six of them at full salary cost **$1,075,000/yr**. $150,000 does not pay that team. It
> does not pay *any one of them* for a year. `payroll.py` refuses to pretend otherwise.

$150K isn't a random number — it's the size of an **SBIR Phase I**. So we stop thinking in
salaries and think in **hours**: salary ÷ 2,080 = an hourly rate, and the budget buys a number
of those hours. That's also how a real Phase I budget is written, so the exercise isn't
make-believe. (SBIR itself is [[Guide - SBIR Steps|parked]] — this is the model, not a plan.)

## The Phase I allocation — 6 months

Budget **$150,000** · non-labour reserve **$22,500** (15%: compute, data, travel, filings) ·
labour pool **$127,500**

| Who | $/hr | Hours | Cost | Why this many |
|---|---|---|---|---|
| 🧠 Sable | $108 | 400 | $43,269 | Owns the detector and the structure question |
| ⚙️ Rook | $94 | 350 | $32,812 | Archive and pipeline must not stop |
| 📚 Tim | $70 | 300 | $20,913 | Verification is the bottleneck |
| 🔍 Fitz | $91 | 150 | $13,702 | The reason we don't publish something wrong |
| 📣 Vega | $79 | 120 | $9,519 | Customer conversations — the only real scoreboard |
| 💡 Nova | $75 | 90 | $6,707 | Writing it down so a stranger can follow it |
| 🎯 CTO | — | — | $0 | Founder-equivalent, unpaid |
| | | **1,410** | **$126,923** | $577 unallocated |

**$150,000 buys 12% of one team-year** — about **9 hours per person per week** for 26 weeks.

## The allocation rule

**Hours follow the phase's risk, not seniority and not fairness.** Right now the entire risk
is *"can we tell a maneuver from stale data, and can we prove it"* — so ML, engineering and
verification get the hours. When the risk moves, the hours move.

Vega took the small number on one condition: that 120 hours is still enough to keep customer
conversations happening, because that's the only scoreboard that counts.

## What's been charged

**$1,276 of $127,500** — $126,224 left.

| Date | Who | Hours | Cost | Work |
|---|---|---|---|---|
| 2026-07-21 | 🧠 Sable | 6.0 | $649 | Age-binned maneuver-vs-stale detector + chart |
| 2026-07-21 | ⚙️ Rook | 4.0 | $375 | Archive: retry, explicit holes, health log, GP capture |
| 2026-07-21 | 🔍 Fitz | 2.0 | $183 | Found the Telesat hole and the CelesTrak 403 behaviour |
| 2026-07-21 | 📚 Tim | 1.0 | $70 | Onboarding; flagged the 1000km+ suspects as unverified |

## Using it

```
python payroll.py                                    the plan
python payroll.py --charge Sable 6 "detector v1"     log real work
python payroll.py --report                           spent vs remaining
python payroll.py --reset 150000                     start a new budget
```

## Two kinds of money

This ledger is **notional** — pretend salaries against a pretend Phase I, useful for deciding
where effort goes.

There's a second, real number coming: when [[Work Queue]] goes live, every job run through
Claude Code reports what it actually cost, and that goes on the board beside this one. Pretend
budget and actual spend, side by side, so neither one can quietly drift from reality.
