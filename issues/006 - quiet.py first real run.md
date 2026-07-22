---
status: blocked
type: AFK
blocked-by: [archive-depth-7-days]
unblocks: ~2026-07-29
---
# quiet.py first real run + weekly bar re-learn

**Goal:** the went-quiet detector produces its first real verdicts the day the archive hits 7 days (~Jul 29 — check `supgp_archive/` depth, don't trust the calendar).

**Done when:**
- `python quiet.py` runs against the full archive and its verdicts (including "nothing went quiet") land in a RESULTS note.
- Weekly bar re-learn executed: `python detect.py --group <g> --learn-baseline --pct 99` for all four groups, with the new bars' provenance recorded.
- Any satellite flagged quiet gets cross-checked against the alert log history before we breathe a word of it externally.

**Notes:** standing rule from the plan doc applies with force here: **never shrink the history window to force output.** If the archive says 6.5 days on Jul 29, quiet.py keeps refusing and that's correct behavior. This issue feeds directly into 005 (demo).
