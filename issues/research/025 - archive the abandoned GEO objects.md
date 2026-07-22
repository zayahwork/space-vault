---
status: open
type: AFK
owner: Randy (research)
blocked-by: []
---
# Give quiet.py a population it can actually be graded on

**Goal:** issue 024 pre-registered the quiet detector's exam and found it has **66 documented-healthy
objects and 1 documented-dead one**. There is no catch-rate denominator, so the Jul 29 run can
measure a false-alarm rate and nothing else. This card is about fixing that for the *next* run.

**Why the denominator is missing** — two compounding causes, both structural:
1. **Operators stop publishing SupGP for satellites they have abandoned.** Only 1 of the 65
   documented-abandoned GEO objects in `quiet_exam.csv` appears in our tracked fleets at all.
   Our detector reads operator-vs-catalog, so the population we can see is, by construction,
   the population someone is still flying.
2. **`MIN_SPIKES = 3` needs evidence of station-keeping.** An object abandoned before our
   archive began never spikes, so it reports `no rhythm yet` forever and can never be called
   `WENT QUIET`.

**The idea worth testing:** those 65 abandoned objects are still in the **public catalog (GP)**,
which we already download every snapshot — we simply don't build histories for objects absent
from the operator feed. A catalog-only cadence track for known-abandoned objects would give
quiet.py a real negative population: satellites that provably are not station-keeping. It would
not produce `WENT QUIET` verdicts (no spikes to lose), but it *would* let us state what a dead
satellite's cadence trace actually looks like next to a live one — which is the comparison a
broker will ask for.

**Done when:** a note in `03 Reference/` answers, with evidence: how many of the 65
documented-abandoned GEO objects appear in the archived `gp_active` snapshots; whether their
catalog-side behaviour is separable from the 66 documented-healthy ones on any measure we
already compute (gap, gap variance, epoch refresh cadence); and a recommendation on whether a
catalog-only cadence track is worth building, with the honest case against it if not.

**Notes:** this is a research/measurement card, not a build card — the recommendation may well
be "not worth it". The archived snapshots hold `gp_active.csv.gz` from `2026-07-22/0200Z`
onward (earlier snapshots are operator-side only). `quiet_exam.csv` already carries the
documented status per object with `in_exam_set` marking the 67 we currently track. Contact no
one; WebSearch yes, WebFetch no (Python urllib).
