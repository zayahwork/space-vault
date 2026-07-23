---
status: done
completed: 2026-07-22
type: AFK
owner: Mark (marketing)
blocked-by: []
---

> [!done] Done 2026-07-22 — `06 Code/drafts/SEGMENT_NOTES.md`, verified by the new
> `python check_segment_notes.py` (test-first: red on the missing file, green now).
> Notes cover all **7 segments actually in the drip rotation** (operator / insurer /
> partner / academic / contract / gov / competitor — the card's "launch-adjacent" has no
> rows; `contract` and `competitor` do, so they got notes instead). Each: pain in their
> words, the dated verified number, the caveat at their sophistication, one ask. The
> linter enforces the language rules (no retired multiple, GEO only via the external-safe
> sentence, no named people, dated number + caveat + ask per section).
> Audit of all 78 queued rows done — **mismatches listed, not rewritten**: the big one is
> **33 template-only rows whose `outreach.py` segment templates still carry the
> pre-verification pitch with no number**; also #23 (insurer, hold) missing the verified
> rate its spec requires, and 7 first-gen contract drafts undated / weak-caveat.
> Also flagged: RESULTS re-measured the headline to **96% vs 11%** late today — notes use
> the approved 68–72% language and explicitly wait for a CTO language ruling. **Zero sends.**
# Per-segment value notes — say it in their language

**Goal:** every segment in the drip rotation gets its own one-paragraph value proposition, so batch-3 emails read like they were written for the recipient's job, not ours.

**Done when:** a note beside the drafts holds one tight paragraph per segment (operator / insurer-broker / SSA vendor / academic / launch-adjacent): the pain in their words, which of our verified numbers matters to them (dated), the honest caveat phrased for their sophistication level, and the one ask that fits them. Existing queued drafts get a pass to check they match their segment's note — mismatches listed, not silently rewritten.

**Notes:** GEO claims use only the external-safe sentence. No named people. Zero sends.
