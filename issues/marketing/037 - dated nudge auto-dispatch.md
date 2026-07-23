---
status: open
type: AFK
owner: Mark (marketing)
blocked-by: [029]
---
# Dated nudges fire themselves — auto-dispatch over the reply_watch nudge drafts

**Carved out of card 028 (2026-07-23).** The three-account send engine (per-account
caps + warm ramp, home routing, thread stickiness, the two founder gates, the
`account` column, the `_smtp_sink.py` feedback loop) is built and tested. The one
piece of 028's goal not delivered there is the machine firing *dated nudges* on its
own — a distinct subsystem that deserved its own card rather than a rushed change on
the live send path.

**Goal:** a contact who has gone quiet for the drafted interval gets their already-
written nudge sent automatically on its due date, from the SAME account the original
thread went out on, and only if that nudge batch has founder approval on record.

**Done when:** the scheduled drip can dispatch the `06 Code/reply_watch/nudges/*`
drafts: each nudge carries a due date (day-1 ≈ Jul 23, batch-2 ≈ Jul 28) and the id
of the thread it chases; on/after that date the engine renders and sends it through
the existing send path, so it inherits thread stickiness (`home_address` already
routes a known thread back to its original sender), the per-account cap accounting,
the `account` column, global dedupe, and bounce handling for free. A nudge whose
batch is not `founder_approved` is held exactly like a template row is
(`automated_holds` / `template_approvals.json` — reuse it, do not invent a second
gate). Warm/named rows (`is_warm`) are still hard-blocked. A `_test_*` feedback loop
proves: a nudge before its due date does not fire; on its due date it fires from the
original account; an unapproved nudge batch is held; a nudge to a `hold` row never fires.

**Notes:** no new sending machinery — bolt onto `send_batch` / the drip, reuse the
gates and routing card 028 already ships. Zero sends in this card — sink + dry runs
only, and `founder_approved` stays false until the founder has seen each nudge batch.
The nudge drafts themselves already exist from card 017; this is the dispatch layer,
not new copy.
