---
date: 2026-07-22
type: idea
status: recommendation, not decision
context: "[[RESULTS - The Quiet Detector]], [[Pricing - What to Charge and Who]]"
---

# 💡 The July 29 demo — making a broker lean forward in 30 minutes

**The unlock:** ~Jul 29 `quiet.py` can make a per-satellite cadence claim — "this one
stopped station-keeping" vs "this one is fine." That's the insurer signal from
[[Pricing - What to Charge and Who]]. Design the coffee demo around it.

## What's on screen (three things, in this order, nothing else)

1. **One satellite's heartbeat.** A single chart: months of a healthy satellite's
   station-keeping spikes at a steady rhythm — then a second satellite whose spikes
   *stop*. Two lines, no jargon. The broker's eye finds the flatline without help.
   That flatline IS the product.
2. **The book view.** A plain list styled like an insurance schedule: satellite name,
   insured-value-sized rows, and one column — *rhythm normal / went quiet / just
   started watching*. Use real objects from the archive. Crucially, show that **most
   rows say "normal"** — a tool that flags everything is noise; ours can say "nothing
   happened" (`--mode alert`, live now) and that's the credibility feature.
3. **The receipts, if asked.** `baselines.json` provenance and the honest-refusal
   output ("we will not pretend otherwise"). Don't lead with it — have it ready. To an
   actuarial buyer, a tool that *refuses to guess* is worth more than one that always
   answers.

## The one sentence

> **"Every one of these satellites has a heartbeat we can hear from free public data —
> and I can tell you which ones in your book just went quiet, before the claim."**

## What we ask for at the end

Not money, not a pilot. Ask: **"Give me the (public) list of satellites on one book you
care about, and I'll watch them for 30 days for free. If nothing goes quiet, I'll tell
you that too."** One yes = the "can I try it?" scoreboard number, a validation partner,
and a reference — without spending an insurer conversation on an unvalidated pitch.

## Honesty constraints (say before they ask)

- On Jul 29 the archive spans ~1 week. A rhythm learned from 1 week is a *young* rhythm —
  demo with satellites whose cadence is fast enough to have ≥3 spikes on record.
- False-positive rate is still unvalidated against real maneuver records (Tim's
  bottleneck). The 30-day free watch is precisely how we buy that number.

## Recommendation

Build the two-chart screen (heartbeat + book view) as the *only* deliverable for the
demo. Everything else — decks, docs, pricing — stays in the folder.
