---
status: open
type: AFK
owner: Mark (marketing)
blocked-by: []
---
# Three-account send engine — 60–75/day, fully automated machinery

**Goal:** the sending machine runs whether anyone is at the desk or not: 3 warmed accounts, per-account pacing, one ledger, dated nudges firing themselves — with the two permanent human gates intact.

**Done when:** `gmail_auth.json` holds all 3 accounts (founder supplies app passwords); `outreach.py` supports per-account daily caps (20/day each, warm-ramp: new accounts start 5–10/day for week one), assigns each contact a home account (segment-per-account, a thread NEVER changes sender), writes an `account` column to `outreach_log.jsonl`, and global dedupe spans all accounts; dated nudges (Jul 23 day-1, Jul 28 batch-2) fire automatically WHEN their template batch has founder approval on record; sink-test passes across all 3 accounts (`_smtp_sink.py`) with per-account counts verified never exceeding caps.

**Notes:** the two gates are permanent and enforced in code, not memory: (1) a template batch flag `founder_approved: true` required before any automated send of that batch; (2) rows marked warm/named (Kelso, Jah, Heldreth, any live thread) are hard-blocked from every automated path. Loops still never send — the engine runs from the scheduled drip task only.
