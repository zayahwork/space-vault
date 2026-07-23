# Brain — Randy (research lane)

Lessons banked from completed cards. PROVEN = demonstrated/verified on shift;
HYPOTHESIS = believed, not yet verified. Never re-learn what's already here.

## PROVEN

- **(2026-07-23, card 031) WebSearch is permission-denied in night/subagent sessions
  even though the lane notes say "WebSearch works" — but Python urllib page-fetches work
  every time.** Verified across three parallel research subagents plus my own direct
  fetch the same night. Consequences: (a) plan research cards around reading known
  primary URLs directly (fund sites, ycombinator.com, investor blogs), not around search;
  (b) DuckDuckGo lite via urllib works briefly for discovery, then rate-limits — spend
  those queries on URL discovery only; (c) a claim only earns VERIFIED when the page
  text was actually read — search snippets alone stay ASSUMED; (d) time-critical facts
  found by a subagent (deadlines, contact addresses) are worth one direct re-fetch of
  your own before they go in a report the founder will act on.

- **(2026-07-23, card 022) CelesTrak's SupGP index page IS the operator-disclosure map —
  read it before hand-researching operators one by one.** Verified: one fetch of
  `https://celestrak.org/NORAD/elements/supplemental/` enumerates every operator that
  shares ephemerides, the channel (Space-Track vs own portal), and the conventions —
  including that Intelsat publishes future-dated post-maneuver element sets tagged `[PM]`
  (39 live on 2026-07-23, epochs 5 days ahead = burns disclosed in advance). Also proven
  the same night: `spacetrack_auth.json` in `06 Code/` logs in fine from this lane, and
  Space-Track `publicfiles/query/class/dirs` shows which operator feeds a basic account
  can actually see (NASA JSC / Kuiper / SpaceX only — the rest are org-gated).

- **(2026-07-23, card 027) The lane's own `groundtruth/gt_sources.py` is the fastest route
  to any Space-Track/GCAT data — check it before writing a new fetcher, and remember the
  files may need materializing (`git update-index --no-skip-worktree` + checkout) because
  the sparse config hides them while `git ls-files -v` shows `S`.** Verified: `history()`
  (cached GP_HISTORY) + `geotab()` gave card 027 both series and both classifications in
  ~15 lines of new code; the same skip-worktree pattern has now bitten three cards (019,
  022's task-guide, 027). Also proven on the same card: pin a chart's date window instead
  of "last N days from today" so the cached pull and figure reproduce byte-identically,
  and make the script assert the chart's claim (live < 0.5 deg, dead > 10 deg) before
  drawing — a presentation artifact can still have a feedback loop.
