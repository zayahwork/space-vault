---
status: open
type: AFK
owner: Mark (marketing)
blocked-by: [028]
---
# Retire the pre-verification pitch from outreach.py templates

**Goal:** the code-level segment templates still carry the old "I'm trying to learn" no-number pitch; once the drip exhausts hand-drafted rows (33 of 78 are template-only), it would start mailing the outdated pitch automatically.

**Done when:** every template in `outreach.py` leads with the current CTO-ruled number language + honest caveat + one segment-fitting ask (use your 023 segment notes); template-only rows re-audited against the new text; linter (`check_reply_watch.py` conventions) passes; zero sends in this card. Flag `founder_approved` stays false on new template text until the founder has seen one sample per segment.

**Notes:** do NOT touch the currently-quoted number without the CTO language ruling — the 96%-vs-11% figure found in RESULTS is awaiting CTO verification; until that ruling lands, external language stays at the dated ~68–72% sentence.
