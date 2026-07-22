---
date: 2026-07-21
status: pitch-ready proof image
satellite: STARLINK-3200 (NORAD 49753)
image: "06 Code/output/starlink3200_deorbit.svg"
code: "06 Code/starlink_heartbeat_chart.py"
---

# 🛰️ One picture — STARLINK-3200, caught leaving its orbit

The single simple proof Nova asked for: one well-known satellite, one clean before/after
picture, one plain-English sentence. No math on screen.

![[starlink3200_deorbit.svg]]

## The caption (attach this sentence with the image)

> **STARLINK-3200 held a rock-steady 547 km orbit for over three months, then on July 2 it
> broke into a clean, deliberate descent — that downward break is the satellite starting its
> controlled deorbit to burn up safely, and we spotted it using only free, public tracking
> data.**

## Why this one (and why it's credible, not junk)

- **Well-known:** it's a Starlink — everyone's heard of them.
- **Real, not a glitch:** the flat part is 356 tracking records all landing on the same
  547 km line for months (that flatness itself is the operator actively holding it there),
  and the drop is *sustained* over weeks — 547 → 491 km and still falling. A bad data point
  spikes once and comes straight back; this doesn't. It's the real thing.
- **Not one of the junk flags:** Fitz flagged the top of the suspect list (5,000–8,000 km
  disagreements) as implausible — no burn moves an object that far, they're bad element sets
  or reentering debris. This object sits in the credible middle of the list (a modest ~14 km
  catalog-vs-operator disagreement on a *fresh* catalog entry), which is exactly what a real,
  recently-executed maneuver looks like.

## Honest note

Public catalog data holds operational Starlinks so flat that a *small* routine station-keeping
nudge is nearly invisible in it (SpaceX's electric thrusters trim continuously). The changes
that *do* show up cleanly are the big deliberate ones — orbit-raising after launch, and this:
the start of a planned deorbit. That's still a maneuver, still detected from free data, and
it's the honest cleanest single image we have.

## Reproduce

```bash
cd "C:\Space\06 Code"
python starlink_heartbeat_chart.py   # pure stdlib, pulls the data and writes the SVG
```
