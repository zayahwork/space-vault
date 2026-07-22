---
status: done
type: AFK
owner: Randy (research)
priority: 1
blocked-by: []
---
# Pre-build the quiet detector's exam (before it wakes up Jul 29)

**Goal:** when `quiet.py` produces its first verdicts (~Jul 29, the day before the broker meeting), they land as a GRADED result — "caught X of Y known-dead satellites, Z false alarms on known-healthy ones" — not raw output. This also produces the company's first measurable false-positive rate: documented non-events don't exist for maneuvers, but they DO for "went quiet" (known-active, station-kept satellites are documented non-events).

**Done when:**
- A per-satellite **operational-status table** exists (`06 Code/quiet_exam.csv` + a note in `03 Reference/`) for the Intelsat, SES, and OneWeb fleets: status (active-stationkept / dead / abandoned / degraded / relocated), source (McDowell geotab status codes, operator fleet pages, ITU/FCC filings), and verified/assumed per row.
- Every one of the **44 objects with ≥3 spikes on record** has a **pre-registered expected verdict** written down BEFORE Jul 29: what quiet.py should say about it if it's working, based on documented status.
- A short scoring recipe: on Jul 29, compare quiet.py's verdicts to the table and report catch rate on known-dead + false-alarm rate on known-healthy, in one table.

**Notes:** this outranks 022 (operator disclosure map) — 022's findings partially fall out of this work anyway; finish this first. The known failure mode to watch for (from `_test_quiet.py`): "healthy satellite declared dead" — that's the worst output to hand a broker unscored, which is why the exam exists. Contact no one; WebSearch yes, WebFetch no (Python urllib).

**Closed 2026-07-22 (night, ralph).** All three done-whens demonstrated:
- `06 Code/quiet_exam.csv` — **140 rows**, per-object status from McDowell GCAT `geotab.tsv`
  (stamp `Updated 2026 Jul 17 2058:25`), every row marked verified/assumed (131/9) and every
  row carrying a pre-registered expected verdict. Note at
  `03 Reference/Quiet Detector Exam - pre-registered.md`.
- **Exam set = 67 objects** (Intelsat 34, SES 33), all 67 joining cleanly to live archive
  NORADs. Verdicts pre-registered before any quiet.py output exists.
- Scoring recipe written: false-alarm rate, catch rate, gate coverage — all three reported
  **with denominators**.

**Two deliberate departures from the card, both recorded in the note:**
1. The card asked for verdicts on "the 44 objects with ≥3 spikes". That 44 is a **Starlink**
   figure, and no documented per-satellite status exists for Starlink — those objects cannot
   be graded at all. The exam instead pre-registers a verdict for every object where
   documented status exists, keyed by NORAD, so whichever objects clear the gate on Jul 29
   already have an expectation on record.
2. **OneWeb is not examinable.** `geotab` is GEO-only and no public per-satellite health
   source for OneWeb was found. 0 of 651 tracked OneWeb objects have documented status.

**The finding that matters, and it inverts the card's premise:** the exam can measure a
false-alarm rate but **cannot measure a catch rate**. Of 67 objects with documented status,
**66 are documented healthy and 1 is documented dead** — no catch denominator. And that one
cannot be caught anyway: `MIN_SPIKES = 3` requires evidence of station-keeping, so an object
already abandoned when the archive began never spikes, never reaches 3, and reports
`no rhythm yet` forever. `WENT QUIET` is reachable only by a satellite that stops *during*
our window. **A catch rate of nothing on Jul 29 is the expected result, not a failure** — and
must be reported as "not measurable", never as 0%. Follow-up filed as **issue 025**.
