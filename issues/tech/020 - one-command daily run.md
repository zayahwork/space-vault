---
status: done
type: AFK
owner: Tim (tech)
blocked-by: []
closed: 2026-07-23
closed-by: tim
---
# One-command daily run: `detect.py --all`

**Goal:** the whole morning verdict is one command — all four fleets scored, one summary anyone can read.

**Done when:** `python detect.py --all` runs starlink, oneweb, intelsat, ses in sequence (alert mode, stored bars), writes one combined summary block (per fleet: over-bar count, persistent count, data-quality count, "quiet day" if zero) to stdout AND appends it to `RESULTS - Alert Log.md` in the existing format; a failure in one fleet reports and continues instead of killing the run; covered by a test that fakes one fleet failing.

**Notes:** the scheduled task should switch to `--all` once this lands — note that in the RESULTS file but don't touch the scheduled task itself (founder's machine config).

---

## ✅ Closed 2026-07-23 — shipped, and its first real run caught the ledger lying dead

`python detect.py --all` (detect.py: `score_fleet` / `fleet_line` / `run_all`) scores all
four fleets against their stored bars, applies persistence over the last 4 snapshots, prints
one block, and appends it to `RESULTS - Alert Log.md` — deduped by snapshot heading, same
ledger rule `daily_alert.py` keys on. Per-fleet lines carry over-bar / **persistent** /
deorbiting / data-quality counts and the top suspect; zero reads as 🔇 quiet; a fleet with
no baseline says so instead of vanishing. One fleet failing is reported **in its line** and
the run continues; exit code is nonzero only when every fleet fails. Test-first:
`_test_all.py`, 12 cases, all on fakes (no archive, no network), including the required
one-fleet-fails case.

**What the first real run found — the reason this card ranked as feedback-loop infra.**
SES came back `FAILED - TypeError: '>=' not supported between float and list`. Root cause:
SES re-learned as a mixed GEO+MEO fleet on Jul 22 evening, and `learn_baselines`
(correctly) stamps a mixed fleet's applied floor as a list — `"min_km": [1.0, 2.0]` — which
`daily_alert.py` forwards to `analyze()` as if scalar. **The scheduled ledger had been
crashing on every snapshot since 2026-07-22/1400Z** — silently, because nothing isolates a
fleet failure there. Fixed at the source: `load_baselines` reads a list floor back as
`None`, which analyze() resolves to exactly the per-object regime floors the learn run
applied. Regression banked in `_test_alert.py` (now 20 cases). The two missed snapshots
(2026-07-22/2000Z, 2026-07-23/0200Z) were backfilled by the revived `daily_alert.py`, in
order; the one buggy block my pre-fix run appended was removed rather than left to confuse
the ledger.

Scheduled-task switch note appended to `RESULTS - Alert Log.md` as required; the task
itself untouched (founder's machine). Whole tech suite green: 10 test files including the
new one.
