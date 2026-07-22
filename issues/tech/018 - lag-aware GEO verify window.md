---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Make the shipped verifier lag-aware at GEO (±10-day window)

**Goal:** act on the referee verdict (issue 015). The shipped `verify.py` / `verify_geo.py` still use `WINDOW_DAYS = 3.0`; against 14 documented GEO maneuvers that window catches 10/14 while ±10 days catches 12/14 (2/6 vs 4/6 double-sourced), because the public catalog records GEO burns up to ~10 days late. The window should be regime-aware: ±3d stays right for LEO (daily cadence, fast catalog), ±10d at GEO.

**Done when:**
- GEO objects are verified with a ±10-day step window whose null/control bar is measured at the SAME width (referee lesson: a wider window against a narrow-window bar manufactures catches — `referee_geo.py` re-measures the bar per width; reuse that discipline).
- LEO behavior byte-identical (Starlink/OneWeb numbers unchanged — check figure by figure).
- `_test_referee.py`'s assertion that the shipped window matches what the referee scored is updated deliberately, not deleted.
- Live Intelsat/SES verify re-run with the new window; result (either way) appended to `RESULTS - Beyond Starlink.md`.

**Notes:** do NOT widen the LEO window "for consistency" — LEO catalog lag is not the measured problem and a wider window only feeds the bar more noise. Keep inclination as a secondary channel; it uniquely caught MEV-2 inside ±3d.
