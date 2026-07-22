---
date: 2026-07-22
owner: DETECTOR window (tech — heavy lifting)
status: assigned
---

> [!todo] ⚡ CTO update ~04:30 — the second catalog snapshot is BANKED (`0750Z`)
> Persistence can run **right now**: `python detect.py --group starlink`. Do it first — it's
> one command, it splits the candidates into *persisted* vs *one-off*, and it's the second
> number for the Kelso conversation. Update [[RESULTS - Maneuver vs Stale]] with the split,
> then carry on with the quiet detector below.

# 🔧 NEXT — tech

> [!success] What you just did matters
> **11.3×** is the first number this company has that survives *"how do you know?"* The
> control group is why it counts. That number is going in front of Kelso and Moriba.
> Everything below protects it or extends it.

## 1. Quick win first — re-run the persistence split (minutes, not hours)

The archiver banks a catalog every run. The moment a second snapshot has `gp_active.csv.gz`
beside it:

```bash
cd "C:\Space\06 Code"
ls supgp_archive/*/*/gp_active.csv.gz     # 2+ = go
python detect.py --group starlink
```

That splits the candidate list into **persisted** vs **one-off** — a second number for the
Kelso conversation, and it costs one command. Update [[RESULTS - Maneuver vs Stale]] with it.

## 2. Main build — the quiet detector

Full spec: [[Plan - The Quiet Detector]]. Approved by the founder, it's on the roadmap.

Short version: every threshold we have is a percentile, so the tool always returns the top 5%
and can never say "nothing happened." Worse, a satellite that **stops** station-keeping drops
*off* the list instead of onto it — and that absence is the health signal the insurer pitch is
priced on ($150K–400K/yr, [[Pricing - What to Charge and Who]]).

Two parts:
- **Absolute thresholds** learned from the archive and stored with their provenance, so zero
  is a possible answer. Buildable today.
- **Per-object cadence**, so each satellite is judged against its own rhythm. Needs weeks of
  archive — build it and let it refuse loudly until there's enough, the way persistence does.

Don't shrink the history window to force output. We've caught ourselves doing that twice.

## 3. If there's time — harden the 11.3×

It went 8.3× at n=25 → 11.3× at n=75. It's strengthening, which is the right direction, but
it's the number we're about to stake the company's credibility on. Push n higher and see if it
holds. If it sags, we want to know before Kelso does, not after.

## Standing rule

Keep doing the thing you did in the verify commit: when the work contradicts something we've
published, say so and fix the note. You caught us on the >500 km reason — 16 of those were
newly launched satellites still climbing, not decaying junk. That correction is worth more
than the feature was.
