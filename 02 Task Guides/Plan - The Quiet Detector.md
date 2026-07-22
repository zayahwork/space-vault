---
date: 2026-07-22
owner: DETECTOR window
status: approved by founder, build after verify.py
priority: high — this is the insurer capability
---

# 🔇 Plan — teach the detector to say "nothing happened"

> [!tip] The one line
> Everything we've built **ranks**. Nothing we've built can return **zero**, and nothing can
> notice an **absence**. Those are the same missing capability, and it's the one the business
> is about to get sold on.

## Why this is now real work

You flagged it yourself in `0584744`:

> *"a percentile cut can never say 'quiet day'. Fine for ranking, wrong for alerting."*

That's exactly right, and it's bigger than a footnote. [[Pricing - What to Charge and Who]]
puts the insurer pitch at $150K–400K/yr, and the pitch is:

> *"I can tell you which satellites in your book are behaving abnormally — before the claim."*

The health signal underneath that is **a satellite that stops station-keeping**. A working
satellite maneuvers on a rhythm. One that stops has usually lost something — thruster, fuel,
attitude control, or the whole bus.

**We cannot currently detect that.** A percentile cut returns the top 5% no matter what, so
an object going silent doesn't show up — it does the opposite, it drops *off* the list. So
today the pricing doc is selling a capability that does not exist. Building it is what makes
that page honest.

## The root cause, stated once

Every threshold we have is **relative to the population on the day**:

```python
cut = np.percentile(gaps[sel], pct)     # detect.py, classify()
```

Relative thresholds can only ever answer *"who is most unusual right now."* They structurally
cannot answer:

- *"Did anything happen at all today?"* → 5% always exceeds the 95th percentile. Always.
- *"Has this object stopped doing what it used to do?"* → quiet objects rank **low**.

Same lesson as the last two fixes, one level further: age-binning judged like against like,
regime-binning judged like against like — now judge **an object against its own past**.

## Part 1 — absolute thresholds, so zero is possible

Learn each cohort's normal band from the archive **once**, write it to disk, and hold it
fixed. Then flag objects that exceed the stored band rather than exceeding today's crowd.

- Reuse the cohort machinery you already built (age bin × orbital regime). **Don't invent new
  cohorts** — the point is to change what the threshold *is*, not what it's computed over.
- Persist to something like `06 Code/baselines.json`, with the snapshot range it was learned
  from stamped inside. A threshold nobody can audit is a tuned number wearing a lab coat.
- **Keep percentile mode.** Ranking and alerting are different questions and both are useful —
  add a mode, don't replace one with the other. Suggest `--mode rank|alert`.

Success test: on a genuinely uneventful day, `--mode alert` returns **zero flagged objects**
and says so. If it can never return zero, it isn't done.

## Part 2 — per-object cadence, so absence is visible

Give every object its own time series of gap-vs-catalog across snapshots.

A station-keeper shows a **repeating pattern**: burn → catalog falls behind → gap spikes →
catalog catches up → gap collapses → repeat. That rhythm is the object's normal.

Two things fall out once each object is its own control:

- **Went quiet** — the rhythm stops. Spikes that came every few days stop coming. That's the
  insurer signal.
- **Changed rhythm** — cadence shifts (more frequent, larger burns). That's a different signal
  and probably a more interesting one, since it can mean an orbit change campaign.

### The honest blocker — read this before starting Part 2

**We have about one day of archive.** Cadence needs weeks. You cannot measure "this object
stopped its usual rhythm" without first knowing its usual rhythm.

So: build the machinery, run it, and have it **refuse loudly** when an object's history is too
short — exactly the way the persistence check refuses today. That refusal was the right call
and it should be the pattern here too. The archive fills at ~4 snapshots/day on its own; the
code should unblock itself without anyone editing it.

Do **not** substitute a shorter window to make it produce output. A cadence claim from one
day of data is precisely the kind of thing this whole project keeps catching itself doing.

## Sequencing

1. **`verify.py` first** — already in progress, don't drop it. The false-positive number is
   the prerequisite for *every* claim, including the pricing one.
2. **Part 1** (absolute thresholds) — buildable today, no history needed beyond what we have.
3. **Part 2** (cadence) — build now, produces real output as the archive fills.

## Reuse

- `06 Code/detect.py` — cohort assignment (age bins, falling/station-keeping regimes) and
  `classify()`. Part 1 is a change to how the cut is *derived*, inside the structure you have.
- `06 Code/deorbit_check.py` — `descent_rate_km_per_day()`, already the shared definition of
  "falling." Keep it shared; two definitions of falling is a bug waiting to happen.
- `06 Code/supgp_archive/` — every snapshot needed for per-object history is already there.

## Done when

- `--mode alert` can return zero on a quiet day and says so plainly.
- Thresholds live in a file with their provenance stamped in, not in a percentile call.
- Per-object cadence runs, and refuses clearly where history is too thin.
- A short `RESULTS -` note saying what the tool can and cannot yet claim — so the pricing page
  can stop describing a capability we don't have.

## Related

- [[Pricing - What to Charge and Who]] — the reason this is priority, and the page this fixes
- [[Plan - Verify the Detector]] — do that first
- [[RESULTS - Maneuver vs Stale]] — where the percentile limitation is recorded
