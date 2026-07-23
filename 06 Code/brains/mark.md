# Brain — Mark (marketing lane)

Lessons banked by ralph iterations. PROVEN = verified in this repo by a
feedback loop or by events; HYPOTHESIS = believed once, not yet re-verified.
Never re-learn what is already here.

## PROVEN

- **Check the RESULTS pages before quoting any number, every card** (banked
  2026-07-22, card 023). The customer-facing figure changed twice in ONE day
  (11.3× retired in the morning; 68–72% struck for 96% vs 11% by evening).
  Every outreach card that touches language must re-read
  `RESULTS - Checked Against History` first — the approved sentence in NEXT
  can be a full revision behind the measurement. When they disagree: use the
  approved language, flag the gap loudly to the CTO, never switch the external
  number unilaterally. Verified: caught the 96%-vs-11% gap this shift only
  because of this check; the drip was live-sending the stale sentence.

- **Prose linters must whitespace-normalize before phrase checks** (banked
  2026-07-23, card 030). Markdown wraps at ~80 cols, so a required phrase like
  "not operator ground truth" can split across a line break and a contiguous
  regex misses it — `check_investor_prep.py` flagged a caveat that WAS present
  in the cold email for exactly this reason. Fix: run required-phrase regexes
  on `re.sub(r"\s+", " ", body)`. Verified red → green this shift. (The older
  `check_segment_notes.py` has the same latent bug — its checks happened to
  pass because those phrases never wrapped; fix it next time it's touched.)

## HYPOTHESIS

- **Segment templates rot faster than hand drafts** (2026-07-22, card 023).
  Sweeps target `drafts/*.txt` because they're greppable per-row; the
  `TEMPLATES` dict inside `outreach.py` gets missed — it survived both number
  sweeps unchanged and now 33 queued rows would send the pre-verification
  pitch. When auditing language, always scan BOTH the drafts folder and the
  templates in code.
