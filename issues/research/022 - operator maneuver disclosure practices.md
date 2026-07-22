---
status: open
type: AFK
owner: Randy (research)
blocked-by: []
---
# Which operators disclose maneuvers, and how

**Goal:** a map of where ground truth comes from continuously — which operators publish maneuver plans, ephemerides, or notifications, so verification stops being an archaeology project.

**Done when:** a note in `03 Reference/` lists, per operator (Intelsat, SES, OneWeb, SpaceX, Iridium, Eutelsat, Telesat, Amazon/Kuiper): what they disclose (planned maneuvers / post-hoc ephemerides / nothing), where (Space-Track ephemeris uploads, operator portals, ITU/FCC filings), at what cadence, and whether access is open or gated. Every claim marked verified/assumed with the source linked. Ends with a ranked list: the 3 best continuous ground-truth feeds we could tap starting this week.

**Notes:** SpaceX uploads ephemerides to Space-Track publicly — start there. WebSearch works, WebFetch doesn't (Python urllib). Contact no one.
