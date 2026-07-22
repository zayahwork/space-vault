---
status: open
type: AFK
owner: Randy (research)
blocked-by: []
---
# Ground-truth maneuver set — turn "verified" into "confirmed"

**Goal:** today our false-positive rate is control-group-based: two of our own methods agreeing. The first technical question from Kelso, Jah, or any broker's engineer will be *"did any of these satellites actually, provably maneuver?"* Build the set that answers it.

**Done when:**
- A ground-truth table exists (`06 Code/ground_truth.csv` + `RESULTS - Ground Truth.md`): NORAD ID, date window, source, source type (operator announcement / regulatory filing / published schedule / press), and whether our detector flagged it.
- At least 15–20 externally documented maneuver events are collected across our four constellations (Starlink deorbits announced by SpaceX, OneWeb relocations, Intelsat/SES station-keeping or relocation filings and press, ILS/FCC orbital-slot moves).
- First honest recall/precision estimate: of externally documented events in our data window, how many did we flag? Of our top suspects, how many can be externally confirmed?
- Every row states which of **"I verified this"** or **"I'd assume so"** applies. No inferred ground truth.

**Notes:** sources to mine: operator press releases and status pages, FCC/ITU filings for GEO relocations, Space-Track decay messages, Jonathan McDowell's GCAT and launch/deorbit logs, NASA CARA / conjunction bulletins, AMOS papers with named events. Web access rule: WebSearch works in non-interactive sessions, WebFetch doesn't — fetch pages with Python urllib. This dataset also becomes the demo's credibility slide.
