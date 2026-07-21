# 🔍 Fitz — Debugger

What Fitz has learned on this project. Written by `brain.py`; read back
before Fitz speaks. `proven` means something demonstrated it. `hypothesis`
means we think so and haven't shown it yet — say so out loud.

- [proven] 2026-07-21 — CelesTrak answers a redundant GP download with HTTP 403 and the text 'has not updated since your last successful download'. That is politeness enforcement, not an error, and retrying it three times is arguing with a server that is telling us to stop.  **How we know:** Reproduced twice; SupGP does not do this - back-to-back telesat fetches both returned 200.
- [proven] 2026-07-21 — A run that exits non-zero is not a warning if nobody reads exit codes. Telesat vanished from the 14:00Z snapshot, the script correctly returned 1, and it went unnoticed for seven hours.  **How we know:** Found by comparing manifest row counts by hand: 12,645 -> 12,630.
