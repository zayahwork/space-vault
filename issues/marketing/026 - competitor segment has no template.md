---
status: done
completed: 2026-07-22
type: AFK
owner: Mark (marketing)
blocked-by: []
---

> [!done] Done 2026-07-22 — chose **(a): a `competitor` template now exists** in `outreach.py`.
> Posture matches `reply_watch/replies/43-digantara.md`: one ML engineer on free public data,
> "I'm not a customer, and I'm not going to pretend to be one", asking where the method breaks.
> Option (b) was rejected because the `partner` template ("comparing notes, happy to share what
> I've measured") hides who we are from companies that sell what we build.
> Test-first: `_test_competitor_template.py` (red on the old code, now green — a template-less
> competitor row passes `blockers()` clean). `_test_multi_account.py` and `check_reply_watch.py`
> still green. `python outreach.py --send --ids 82` renders in a dry run (via #82's tailored
> hand draft, which correctly outranks the template). **Zero sends — dry runs only.**
# `competitor` rows can never send — no template exists

**Goal:** a `competitor` row is either sendable or honestly re-tagged; right now it is silently unsendable.

**Found during card 019.** `outreach.py` has templates for operator / insurer / partner / academic / gov. Row **#82 NorthStar Earth & Space** was held back at preflight with `no template for segment 'competitor'`, and row **#43 Digantara** only went out because someone hand-wrote a draft for it. Any future competitor row hits the same wall — the guard catches it, so nothing bad ships, but the row sits in the queue looking ready and never goes.

**Done when:** either (a) a `competitor` template exists that is honest about who we are — not a customer, not a threat, one person on free data asking where the method breaks — and a dry run of #82 renders it; or (b) the segment is retired and its rows re-tagged to `partner` with a note saying why. Decide, don't do both. `python outreach.py --send --ids 82` must render an email in a dry run when the card is done.

**Notes:** Zero sends. Keep the "do not pretend to be a buyer" posture that `reply_watch/replies/43-digantara.md` already documents.
