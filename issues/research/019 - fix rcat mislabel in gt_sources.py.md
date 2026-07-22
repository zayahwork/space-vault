---
status: open
type: AFK
owner: Randy (research)
blocked-by: []
---
# Fix the `rcat` mislabel in `06 Code/groundtruth/gt_sources.py`

**Goal:** `gt_sources.gcat_phases()` documents its `which` parameter as `'satcat' (in orbit)
or 'rcat' (reentered)`, and `gcat_updated()` defaults to `which="rcat"`. **Both are wrong.**
Per GCAT's own catalog index, `rcat` is the *"Suborbital Rocket (Exoatmospheric) Catalog —
objects whose apogee was 80 km or more"*. It contains suborbital rockets, not reentered
satellites. Reentries live in `satcat.tsv` as a phase with Status `R` and a `DDate`.

Found while doing issue 018. The CSV and `RESULTS - Ground Truth.md` have been corrected;
the helper module has **not**, because `06 Code/groundtruth/` is outside the research lane's
sparse-checkout scope. Left as an issue rather than reaching across lanes.

**Why it matters:** the mislabel silently produces false negatives. Querying `rcat` for a
payload returns nothing whether or not it reentered, so a caller gets "no corroboration"
without ever having looked in the right catalog. That is exactly the wrong reasoning that
went into the first pass of the five pending reentry rows — right answer, invalid method.

**Done when:** in `06 Code/groundtruth/gt_sources.py`, the `gcat_phases()` docstring
describes `rcat` correctly (suborbital rockets), `gcat_updated()` defaults to `"satcat"`
instead of `"rcat"`, and a one-line comment records that reentries are `satcat` Status `R`
with a `DDate`. Verify with `python gt_sources.py updated` returning the `satcat.tsv` stamp.

**Notes:** whoever picks this up needs `06 Code/groundtruth/` in their checkout — the four
files are committed and present in HEAD but marked `skip-worktree` in the research worktree
by the lane's sparse-checkout config. No behaviour outside the docstring/default should
change; the data-fetching logic itself is correct.
