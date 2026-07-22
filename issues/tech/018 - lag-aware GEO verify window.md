---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Make the shipped verifier lag-aware at GEO (asymmetric −3/+14 day window)

**Goal:** act on the referee verdict (issue 015). The shipped `verify.py` / `verify_geo.py` still use `WINDOW_DAYS = 3.0`; against 14 documented GEO maneuvers that window catches 10/14 while a lag-aware **−3/+14 day** window catches 13/14 (2/6 vs 5/6 double-sourced), because the public catalog records GEO burns up to ~11 days late. The window should be regime-aware: ±3d stays right for LEO (daily cadence, fast catalog), −3/+14d at GEO.

**Two corrections to the first draft of this card, both measured in the final 015 run — read before implementing:**
- **The window must be ASYMMETRIC, not just wider.** Catalog lateness runs one way only. A symmetric ±14d window credits MEV-2 and Intelsat 1002 with inclination steps landing **12.3 days *before* the docking**, at 5.2× and 5.0× the bar. A plain `WINDOW_DAYS = 3.0 → 14.0` edit introduces exactly that failure. Implement it as (days_before, days_after) = (3, 14).
- **±10 days is one day short.** Intelsat 33e's step lands at **+10.98 days**; `ground_truth.csv` rounds its lag column to 10, which is what made ±10 look sufficient. 14 is the constant that works.

**Done when:**
- GEO objects are verified with a −3/+14 day step window whose null/control bar is measured at the SAME window shape (referee lesson: a wider window against a narrow-window bar manufactures catches — `referee_geo.py` re-measures the bar per window; reuse that discipline).
- LEO behavior byte-identical (Starlink/OneWeb numbers unchanged — check figure by figure).
- `_test_referee.py`'s assertion that the shipped window matches what the referee scored is updated deliberately, not deleted.
- Live Intelsat/SES verify re-run with the new window; result (either way) appended to `RESULTS - Beyond Starlink.md`.

**Notes:** do NOT widen the LEO window "for consistency" — LEO catalog lag is not the measured problem and a wider window only feeds the bar more noise. Keep inclination as a secondary channel; it uniquely caught MEV-2 inside ±3d.
