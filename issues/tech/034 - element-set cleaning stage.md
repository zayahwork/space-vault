---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Dedicated element-set cleaning stage (the Digantara lesson)

**Goal:** a named, testable data-cleaning stage in front of detection — out-of-pattern element sets eliminated explicitly, not implicitly scattered across gates. Digantara (real SSA company, own sensors) told us unprompted this was their hard-won prerequisite; we have pieces (MAX_PLAUSIBLE_KM, age bins, deorbit split, per-regime floors) but no single stage with its own contract.

**Done when:** `detect.py` has an explicit clean() stage that runs first and emits a per-snapshot cleaning report (rows in → rows dropped by reason → rows out): implausible orbits, duplicate/republished elsets, negative-age entries, regime-impossible values, epoch anomalies. Every drop reason counted, nothing silently discarded — "real but anomalous" candidates get quarantined + listed, never deleted (the interesting tail is the product). Covered by tests; one RESULTS note documents the cleaning rates per fleet. If Dr. Neelakantan's reply (thread live as of Jul 23) reveals criteria we lack, fold them in with attribution in the note.

**Notes:** this formalizes what we half-do. The quarantine-not-delete rule is the difference between us and a naive cleaner — our whole wedge is that the "dirty" data contains the signal.
