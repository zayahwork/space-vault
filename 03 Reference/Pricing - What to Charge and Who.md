---
date: 2026-07-22
status: sequence B confirmed by founder 2026-07-22; numbers unvalidated
type: strategy
---

# 💰 Pricing — what to charge, and who to charge it to

> [!tip] The one idea
> **You don't price the software. You price the thing that goes wrong if they don't have it.**
> Same engine, same output — worth $25K to one buyer and $200K+ to another, because their
> downside is a different size.

---

## The $25K anchor is a trap

Kayhan charges small operators roughly **$25K/yr**. Copying that number is the obvious move and
the wrong one. Understand *why* it's $25K first:

An operator's pain is **operational**. They get a conjunction warning — *"you might hit
something"* — and have to choose: burn fuel to dodge, or ignore it. A wrong dodge costs fuel,
fuel is satellite lifetime. Real pain, but **small and repeated** — a few thousand dollars per
bad call. Price lands in the tens of thousands.

**$25K is the ceiling of that particular pain, not a market rate.** Carry it onto a buyer with a
different pain and you leave 10× on the table.

## The insurer's pain is a different animal

A space insurer writes a policy on a satellite. If it dies, they pay out — **$50M–$300M, one
event.** Their whole job is estimating *"how likely is this thing to die."*

The leverage: they estimate that today from **launch vehicle history and manufacturer
reputation.** They have almost nothing on how the satellite *behaves once it's up there*.

We have behaviour. Maneuver cadence is a health signal — an object that **stops station-keeping**
is a satellite in trouble — and we can see it across the whole population, from free public data,
without asking the operator's permission.

> [!success] The insurer pitch (not "maneuver detection")
> **"I can tell you which satellites in your book are behaving abnormally — before the claim."**

### What that's worth, out loud

- A book of ~50 satellites, ~$100M average insured value.
- Repricing or declining **one** bad risk a year = eight figures avoided.
- Even a fractional shift in loss ratio across the book = millions.

Against that, **$150K–$400K/yr is a rounding error to them and 10× the operator price.**

## The catch — say it before they do

Insurance is a **relationship business built on actuarial credibility**. Which means:

- **Long sales cycles.** Nobody buys from a solo founder in month one.
- **They will ask "what's your false positive rate."** Today the honest answer is *unvalidated* —
  zero candidates checked against a real maneuver record. And the list itself is still moving:
  the 2026-07-22 pass found ~79% of the old candidate list was deorbiting hardware (now judged
  separately), and the 29 ">500 km" discards look like new satellites orbit-raising, not bad data
  ([[RESULTS - Maneuver vs Stale]]). That number is a **prerequisite** to charging insurer
  prices, not a detail.
- **The market is small.** A handful of Lloyd's syndicates and specialists. No numbers game —
  every conversation counts, so don't spend one early.

---

## ✅ The decision: sequence B

| | Move | Verdict |
|---|---|---|
| A | Operators first at ~$25K | Fast, but anchors us cheap and it's hard to climb later |
| **B** | **Operators to prove it, insurers to get paid** | ✅ **this one** |
| C | Insurers only | Highest ceiling, but selling unvalidated output to the most credibility-sensitive buyer alive. Too early |

**B in one line:** *use operators to earn the proof, then use the proof to charge insurers properly.*

Two buyers, two different jobs:

1. **Operators = the validation customers.** Cheap, or even free. We are not there for their money
   — we are there because they can tell us *"that one was a real burn, that one wasn't."* That's
   how the false-positive number gets built, and it's the number everything else depends on.
2. **Insurers = the revenue customers.** Approached **second**, priced at **$150K+**, and only
   once we can answer *"how often are you wrong?"* — with operator logos behind the answer.

The order is the whole point. Do it backwards and we burn our few insurer conversations pitching
a number we can't defend.

> [!warning] What has to be true before an insurer conversation
> A real false-positive rate from [[RESULTS - Maneuver vs Stale]]. Until then, insurers are a
> **research** conversation, not a sales one — and worth saying so to their face, because
> admitting it is the credibility asset.

## Related

- [[RESULTS - Maneuver vs Stale]] — the engine and its honest caveats
- [[Kelso Reading - Digest]] — the second wedge (new-object ID) that may reprice all of this
- [[Guide - Moriba Jah Call]] — he will push on exactly the credibility gap above
- [[Glossary]] — station-keeping, conjunction, loss ratio
