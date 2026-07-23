---
status: done
type: AFK
owner: Randy (research)
blocked-by: []
---
# Which operators disclose maneuvers, and how

**Goal:** a map of where ground truth comes from continuously — which operators publish maneuver plans, ephemerides, or notifications, so verification stops being an archaeology project.

**Done when:** a note in `03 Reference/` lists, per operator (Intelsat, SES, OneWeb, SpaceX, Iridium, Eutelsat, Telesat, Amazon/Kuiper): what they disclose (planned maneuvers / post-hoc ephemerides / nothing), where (Space-Track ephemeris uploads, operator portals, ITU/FCC filings), at what cadence, and whether access is open or gated. Every claim marked verified/assumed with the source linked. Ends with a ranked list: the 3 best continuous ground-truth feeds we could tap starting this week.

**Notes:** SpaceX uploads ephemerides to Space-Track publicly — start there. WebSearch works, WebFetch doesn't (Python urllib). Contact no one.

**Closed 2026-07-23 (night, ralph).** Deliverable:
`03 Reference/Operator Maneuver Disclosure - Ground Truth Feeds.md`. All 8 operators
mapped, every claim VERIFIED (page/data actually fetched with urllib on 2026-07-23) or
ASSUMED, sources linked. Feedback loops run live: fetched CelesTrak's SupGP index and
per-operator CSVs (measured row counts + epoch freshness for all 8 feeds), fetched SpaceX's
open MANIFEST (16,252 ephemeris files, no login), and logged into Space-Track with our
stored creds to enumerate public-file dirs (NASA JSC / Kuiper / SpaceX only — proving
OneWeb/SES/Iridium/Telesat raw feeds are org-gated and the open route is CelesTrak SupGP).

**Headline: Intelsat pre-announces maneuvers in the open.** Its public IESS-412 ephemeris
feed carries a post-maneuver ephemeris per planned burn; CelesTrak marks them `[PM]` —
39 live `[PM]` element sets on 2026-07-23 with epochs out to 2026-07-28 (future-dated =
disclosed *before* the burn). Continuous, per-maneuver ground truth for a constellation we
already track. Eutelsat is the only mapped operator with no feed at all.

Ranked top-3 taps (in the note): (1) daily Intelsat `[PM]` log — self-growing ground-truth
table; (2) SpaceX open ephemeris repo; (3) retain daily SES+OneWeb SupGP snapshots (zero
new engineering). Contacted no one; drafted nothing outbound.
