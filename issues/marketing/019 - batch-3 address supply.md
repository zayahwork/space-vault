---
status: done
completed: 2026-07-22
type: AFK
owner: Mark (marketing)
blocked-by: []
---

> [!done] Done 2026-07-22 — CSV rows **#76–95**, written up in [[Outreach - Batch 3 Address Supply]]
> 20 new rows, every address printed by its owner on their own ESA Space Debris Conference
> paper — no guessing. 8 companies (money-shaped), 4 agencies/funders, 8 researchers. Each row
> carries a named person, the paper URL as `contact_route`, a one-line why-them, and a segment.
> **134 more verified addresses are on the bench**, with the deliberate skips documented
> (one ask per company: GMV, ESA, Deimos, Aerospace, Sybilla, OKAPI, Guardtime, CS Group, IMS,
> PoliMi all already have a row). Verified by `outreach.py --status` and a dry run.
> **Zero sends.** Row #82 exposed a pre-existing gap → new card 026.
# Batch-3 address supply — 20 new named contacts

**Goal:** the pipeline's real ceiling is reachable named humans, not send capacity. Build the next batch: 20 new contacts who are named people with published addresses, not info@ inboxes.

**Done when:** 20 new rows in `outreach_targets.csv`, each with: a named person, a published address (paper author blocks, conference proceedings, operator technical staff pages — no pattern-guessing after the Williams bounce), a one-line note on why THEY specifically (their paper/talk/role), and a segment tag so the drip rotation can use them. Rows without a verifiable address get logged as documented dead ends instead of guesses. Zero sends — supply only.

**Notes:** mine AMOS/ESA proceedings beyond the six already used, operator engineering blogs, X profiles that link a contact page. No LinkedIn ever. Duplicate-check against every existing row before adding.
