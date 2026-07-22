---
status: open
type: AFK
blocked-by: []
---
# Tests for detect.py's pure functions

**Goal:** `06 Code/tests/test_detect.py` exists and passes — the first real automated feedback loop in this repo.

**Done when:** `python -m pytest "06 Code/tests" -q` passes, covering at least: the age-binning logic (an object lands in the right bin; bins below MIN_PER_BIN widen instead of producing noise percentiles), the MAX_PLAUSIBLE_KM sanity gate (a 5,000 km gap is bucketed as data-quality, never as a detection), the FALLING_KM_PER_DAY deorbit filter, and the independent-looks persistence rule (two byte-identical snapshots must count as ONE look).

**Notes:** detect.py is 815 lines; test the pure math by importing its functions, not by hitting the network — build tiny synthetic element-set fixtures in the test file. Do not restructure detect.py beyond what's needed to import cleanly (if `if __name__ == "__main__"` guarding is missing, add it — nothing more). pytest may need `pip install pytest`. One quiet bug in this math silently corrupts every downstream RESULTS number, which is why this is the first issue.
