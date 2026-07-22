---
title: Can we give quiet.py a catch-rate population from abandoned GEO objects?
type: reference
status: measured 2026-07-22 night; recommendation = NO (cadence track), with a cheaper alternative
issue: research/025
depends_on: "[[Quiet Detector Exam - pre-registered]]"
data: "geotab.tsv (populations), gp_active snapshots (presence), Space-Track GP_HISTORY (separability)"
---

# 🪦 Abandoned GEO objects as a catch-rate population — the measurement

Issue 024 found the quiet detector's exam can measure a **false-alarm rate** (66 documented-healthy
objects) but **no catch rate** — only 1 documented-dead object in our tracked fleets. This card asked:
can the 65 documented-abandoned GEO objects, which live in the public catalog, become that missing
denominator? **Measured answer: no, not worth building.** Three findings, then the recommendation.

## Finding 1 — 63 of the 65 abandoned objects are not even in our archive

Populations from McDowell's `geotab` (Intelsat + SES): **65 abandoned (`GEO/ID`), 66 healthy (`GEO/S`).**
Looked each up across the four `gp_active` snapshots (2026-07-22, 0200Z–2000Z):

| population | present in `gp_active` |
|---|---|
| healthy (`GEO/S`) | **66 / 66** |
| abandoned (`GEO/ID`) | **2 / 65** |

**Mechanism, verified:** the archiver (`supgp_archive.py`) fetches CelesTrak's **`GROUP=active`** GP
feed (16,188 objects, 587 at GEO). "Active" **excludes abandoned satellites by definition** — that is
what the word means in that feed. The 2 that slipped through are borderline/recently-abandoned objects
CelesTrak still lists. So the abandoned population is absent from our archive **by construction**, not
by chance. Building a catalog-only cadence track over them would first require a **tech-lane change to
`supgp_archive.py`** to pull a different feed (full GEO catalog, or Space-Track GP_HISTORY per NORAD).

## Finding 2 — even with the data, the two populations are already trivially separable

To test separability I pulled **60 days of Space-Track `GP_HISTORY`** for a 10-object sample of each
population (the full catalog, which *does* include abandoned objects), and computed the measures the
issue named:

| measure | abandoned (n=10) | healthy (n=10) | separator? |
|---|---|---|---|
| **inclination, median** | **11.95°** | **0.03°** | ✅ ~400×, decisive |
| inclination change / 60d | +0.109° | +0.015° | ✅ abandoned still drifting up |
| catalog refresh cadence | 2.76 epochs/day | 3.65 epochs/day | ⚠️ weak — both well-tracked |

**Inclination alone separates them completely** — a dead GEO satellite's plane has fallen over
(uncontrolled, ~0.85°/yr, already at ~12°); a live one is pinned near zero by N–S station-keeping.
But this **is exactly what `geotab` already encodes** as `GEO/ID` vs `GEO/S`. We would be building a
cadence pipeline to re-derive a classification McDowell hands us for free. The one measure a cadence
track would add — **refresh cadence** — is the weakest separator here: abandoned GEO objects are large
radar targets and stay well-tracked (2.76/day), so "the catalog stopped updating it" is **not** a
reliable dead-satellite signal at GEO. (It is a signal in LEO, where a decaying object's TLEs degrade —
but that is a different mechanism and a different population.)

## Finding 3 — it still would not produce catch-rate objects for quiet.py

Even with abandoned objects archived, `quiet.py` **cannot** return `WENT QUIET` for them. `WENT QUIET`
requires ≥3 **spikes** (evidence of prior station-keeping) that then stop. An object abandoned *before*
our archive began never spikes, so it reports `no rhythm yet` forever — the structural point from
[[Quiet Detector Exam - pre-registered]]. Archiving the abandoned population changes the input feed but
not this fact. The only true catch-rate object is one that was **healthy during our window and stopped
during our window** — rare by design, which is the entire product thesis.

## Recommendation — do NOT build a catalog-only cadence track

The honest case against, in order of weight:
1. **Wrong feed:** the data is not in our archive and getting it needs a tech-lane archiver change.
2. **Redundant:** abandoned vs healthy is already a solved classification (`geotab` `GEO/ID` vs `GEO/S`,
   inclination ~12° vs ~0°). A cadence pipeline re-derives it more expensively.
3. **Weak on its own measure:** the thing a cadence track would uniquely add — refresh cadence — barely
   separates the two at GEO (2.76 vs 3.65 epochs/day). Both stay tracked.
4. **Doesn't solve the actual gap:** it still yields zero `WENT QUIET`-able objects for quiet.py.

**The one thing worth doing instead — cheaply.** A broker will still ask *"show me what a dead
satellite looks like next to a live one."* That is a **one-off chart, not a pipeline**: overlay 60 days
of inclination history for one `GEO/S` object (held flat near 0°) against one `GEO/ID` object (drifting
up through ~12°). It makes the point in one picture, uses `GP_HISTORY` we can already pull, and needs no
change to the archiver or to `quiet.py`. Filed as a follow-up (issue 027) rather than done here, since
this card was scoped as measurement, not chart-building.

**Net:** the catch-rate gap in the quiet exam is real and it is **structural, not a data-collection
problem**. It closes only when a satellite we are actively watching goes quiet on our watch — so the
right move is to keep the archive growing and let the first real event be the first real catch, not to
manufacture a synthetic dead population that the classification already covers.

## Evidence marks

| claim | mark |
|---|---|
| 2/65 abandoned present in `gp_active`; 66/66 healthy | **verified** (measured on the archived snapshots) |
| `gp_active` = CelesTrak `GROUP=active`, excludes abandoned by definition | **verified** (`supgp_archive.py:258` fetches `param="GROUP"`, `"active"`; feed semantics) |
| inclination 11.95° vs 0.03°, refresh 2.76 vs 3.65/day | **verified** (60d `GP_HISTORY`, 10+10 sample) |
| a cadence track would add little over `geotab` classification | **assumed** (judgement from the above, not a built comparison) |

## Sources
- McDowell GCAT `geotab.tsv` — populations, stamp `Updated 2026 Jul 17 2058:25`
- `06 Code/supgp_archive/2026-07-22/*/gp_active.csv.gz` — presence (4 snapshots)
- Space-Track `GP_HISTORY`, 60-day window — separability sample
- `06 Code/supgp_archive.py` — the `GROUP=active` fetch that scopes what we archive
