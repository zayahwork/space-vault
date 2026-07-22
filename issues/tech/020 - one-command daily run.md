---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# One-command daily run: `detect.py --all`

**Goal:** the whole morning verdict is one command — all four fleets scored, one summary anyone can read.

**Done when:** `python detect.py --all` runs starlink, oneweb, intelsat, ses in sequence (alert mode, stored bars), writes one combined summary block (per fleet: over-bar count, persistent count, data-quality count, "quiet day" if zero) to stdout AND appends it to `RESULTS - Alert Log.md` in the existing format; a failure in one fleet reports and continues instead of killing the run; covered by a test that fakes one fleet failing.

**Notes:** the scheduled task should switch to `--all` once this lands — note that in the RESULTS file but don't touch the scheduled task itself (founder's machine config).
