---
status: blocked
type: AFK
owner: Tim (tech)
blocked-by: [archive-depth]
unblocks: ~2026-07-29
---
# Why does SES still miss live? (suspect selection, not verification)

**Goal:** the referee settled the verifier question, but the LIVE SES miss remains unexplained — which now points at `detect.py`'s GEO suspect *selection*, not verification. Find out with a real n.

**Done when:** with ≥1 week of GEO archive, the SES suspect list is analyzed against the ground-truth and quiet-exam tables: are we ranking the wrong observable at GEO, is the mixed GEO+MEO population still distorting the bins, or is SES genuinely quiet? Answer with numbers in `RESULTS - Beyond Starlink.md`; the "no confirmed explanation" line gets replaced by whichever explanation survives.

**Notes:** filed from Tim's own consult flag. Blocked until the archive gives GEO a real n (~Jul 29+). Don't start early — n=4 anecdotes are how we got burned last time.
