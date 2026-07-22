---
status: done
type: AFK
blocked-by: []
closed: 2026-07-22
closed-by: tim
---
# Tests for detect.py's pure functions

**Goal:** `06 Code/tests/test_detect.py` exists and passes — the first real automated feedback loop in this repo.

**Done when:** `python -m pytest "06 Code/tests" -q` passes, covering at least: the age-binning logic (an object lands in the right bin; bins below MIN_PER_BIN widen instead of producing noise percentiles), the MAX_PLAUSIBLE_KM sanity gate (a 5,000 km gap is bucketed as data-quality, never as a detection), the FALLING_KM_PER_DAY deorbit filter, and the independent-looks persistence rule (two byte-identical snapshots must count as ONE look).

**Notes:** detect.py is 815 lines; test the pure math by importing its functions, not by hitting the network — build tiny synthetic element-set fixtures in the test file. Do not restructure detect.py beyond what's needed to import cleanly (if `if __name__ == "__main__"` guarding is missing, add it — nothing more). pytest may need `pip install pytest`. One quiet bug in this math silently corrupts every downstream RESULTS number, which is why this is the first issue.

---

## ✅ Closed 2026-07-22 — all four required areas covered, 81 cases passing

| the issue asked for | where it lives now |
|---|---|
| age-binning; thin bins widen instead of inventing percentiles | `_test_learn.py` (half-open bands, exactly 24.0 h → 24–48, n=5 band falls back to whole regime), `_test_alert.py` |
| `MAX_PLAUSIBLE_KM` gate — 5,000 km is data-quality, never a detection | `_test_alert.py`, `_test_learn.py` (also proves it never reaches the learned bar) |
| `FALLING_KM_PER_DAY` deorbit filter | `_test_orbital.py` (sign convention both ways, n-dot/2 applied as 2× not 1×, threshold at `MEAN_MOTION_DOT` 6.5232e-04 asserted from both sides) |
| independent-looks rule — two identical snapshots = ONE look | `_test_detect.py` (pre-existing), re-checked in `_test_quiet.py` |

**Suite:** `_test_detect` 9 · `_test_quiet` 14 · `_test_alert` 19 · `_test_learn` 15 · `_test_orbital` 24 = **81 cases, all passing.**

### Two deviations from the issue as written

1. **Layout.** Tests are `06 Code/_test_*.py`, run as `python _test_x.py`, not `06 Code/tests/test_detect.py` under pytest. That matches the house style already established by `_test_detect.py` and keeps the suite runnable with no dependency to install. pytest 9.1.1 *is* installed if we'd rather convert — say so and it's a small job.
2. **No restructuring of `detect.py`.** None was needed: it already had its `if __name__ == "__main__"` guard and imports cleanly in 0.15 s with no network access.

### What testing this actually found

- **`quiet.py` false positive (fixed).** An object flagged on three consecutive 6-hourly snapshots — i.e. what a PERSISTENT SUSPECT looks like — got a "typical rhythm" of 0.25 days, so the next ordinary overnight gap of 0.70 days read as 2.8× its rhythm and the satellite was reported **WENT QUIET**. Healthy hardware declared a possible loss of control, aimed squarely at the objects the product exists to watch. Fixed with a 1.0-day floor (`MIN_TYPICAL_DAYS`). The 7-day gate was hiding this, not preventing it — 44 objects already had ≥3 spikes on record.
- **`load_baselines` silent-rank hazard (fixed, latent).** A baseline file missing a regime handed `classify()` a `None`, which it reads as *rank mode* — so alert mode would have silently ranked a whole regime while still calling itself alert mode. Now guarantees a key per regime. Never live: `learn_baselines` always writes both.
- **`learn_baselines` and the orbital math: no defects.** Worth recording plainly. GEO altitude comes out at 35,786.0 km against a textbook 35,786, and J2000 at exactly JD 2451545.0.

### Still not covered (the honest remainder)

`analyze()` and `main()` end-to-end — they need the archive and the network, so they are exercised by running them, not by tests. Nothing here validates a candidate against a **real maneuver record**; that remains the biggest unverified claim in the project and is not what this issue was for.
