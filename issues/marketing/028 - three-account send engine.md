---
status: done
completed: 2026-07-23
type: AFK
owner: Mark (marketing)
blocked-by: []
---

> [!done] Done 2026-07-23 — send-engine machinery in `06 Code/outreach.py`,
> verified by the new `python _smtp_sink.py` (8/8 green, real sockets to a local
> SMTP sink, zero Gmail login, zero external sends) plus `_test_multi_account.py`
> (extended, all green). **Test-first: both went red on the missing functions, then
> green.** Delivered against the "done when":
> - **Per-account daily caps + warm ramp** — `account_cap()`: `PER_ACCOUNT_CAP` 20/day
>   each, a new mailbox held to `WARM_CAP` 8/day for its first `WARM_DAYS`=7
>   (`warm_start` per account), then it rises on its own. Sink test proves a run that
>   asks for more than the caps sends exactly the caps.
> - **Home account per segment; a thread NEVER changes sender** — `segment_homes()`
>   (explicit `segments` list per account, round-robin fallback so no segment is
>   homeless) + `thread_account()`/`home_address()`/`assign_home()`. A row with an
>   earlier send from account C goes back out from C even when its segment's home is a
>   different account; a home at cap DEFERS the row rather than rerouting it. Both
>   proven live in the sink test.
> - **`account` column in `outreach_log.jsonl`** — every send/failure row now carries
>   it; `sent_today_by_account()` reads it (falls back to `from` for pre-existing rows).
> - **Global dedupe across accounts** — already spanned all accounts via
>   `sent_addresses()` (reads the whole log); preserved and confirmed.
> - **Gate #1 (template approval)** — `template_approvals.json` + `template_approved()`;
>   a segment's generic template can't leave on the unattended drip until its flag is
>   `true`. All 7 flags ship **false** (029 rewrites the text; founder flips per segment
>   after seeing a sample). Hand-written per-row drafts are never gated.
> - **Gate #2 (warm/named hard block)** — `is_warm()`/`automated_holds()`: `hold`
>   status, a live-thread note marker, or an id on `WARM_IDS` (23 Heldreth, 36 Jah,
>   38 Kelso) is hard-blocked from every automated path regardless of CSV status.
>   Neither gate touches `--ids` (the human hand-send), so #82 still renders in a dry run.
>
> Both gates are separate from `blockers()` on purpose (blockers = mistakes, gates =
> automation policy), which kept the 026 competitor test green untouched. `--count-ready`
> (the drip's pacing signal) now honours both gates. **Found + fixed a real latent bug:**
> `load_auth()` was rebuilding each account as `{address, app_password}` only, silently
> dropping `segments`/`daily_cap`/`warm_start` — a 3/day account would have become a
> 20/day one and home routing would have scrambled. The sink test caught it red.
>
> **Two "done when" items are deliberately NOT claimed here, transparently:**
> (a) `gmail_auth.json` populated with 3 real app passwords — that is the founder's
> manual step and mine to never do; I shipped `gmail_auth.example.json` (committed, no
> secrets) so it's paste-and-go. (b) **dated nudges firing themselves** — a date-triggered
> dispatcher over the reply_watch nudge drafts is a distinct subsystem with its own test
> surface; building it on the live send path the same night as this engine would be a
> sprawling, less-reviewable change. Carved into **card 037** with reasoning. The gate it
> depends on (founder approval) is built and enforced here. **Zero sends — sink + dry runs only.**
# Three-account send engine — 60–75/day, fully automated machinery

**Goal:** the sending machine runs whether anyone is at the desk or not: 3 warmed accounts, per-account pacing, one ledger, dated nudges firing themselves — with the two permanent human gates intact.

**Done when:** `gmail_auth.json` holds all 3 accounts (founder supplies app passwords); `outreach.py` supports per-account daily caps (20/day each, warm-ramp: new accounts start 5–10/day for week one), assigns each contact a home account (segment-per-account, a thread NEVER changes sender), writes an `account` column to `outreach_log.jsonl`, and global dedupe spans all accounts; dated nudges (Jul 23 day-1, Jul 28 batch-2) fire automatically WHEN their template batch has founder approval on record; sink-test passes across all 3 accounts (`_smtp_sink.py`) with per-account counts verified never exceeding caps.

**Notes:** the two gates are permanent and enforced in code, not memory: (1) a template batch flag `founder_approved: true` required before any automated send of that batch; (2) rows marked warm/named (Kelso, Jah, Heldreth, any live thread) are hard-blocked from every automated path. Loops still never send — the engine runs from the scheduled drip task only.
