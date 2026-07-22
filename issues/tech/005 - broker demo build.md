---
status: blocked
type: AFK
blocked-by: [006-archive-depth]
unblocks: ~2026-07-27
---
# Broker demo — heartbeat chart + book view

**Goal:** the two-view demo spec'd in `04 Ideas/Idea - Jul 29 Broker Demo.md`, built for the Heldreth meeting (~Jul 30–Aug 1): the per-satellite "heartbeat" (station-keeping cadence over time, with the quiet gap visually obvious) and the "book view" (an insurer's whole fleet on one screen, green/amber/red).

**Done when:** both views render from the real archive + `quiet.py` output for at least one GEO fleet (Intelsat or SES) and one LEO constellation, and a dry-run script exists (what we click, what we say, what number is on each screen).

**Why blocked:** `quiet.py` needs ~7 days of archive (unlocks ~Jul 29; archive depth was 0.24 days on Jul 22). Building the demo against synthetic data means demoing a fiction — we don't do that. **Do not start before ~Jul 27**, when there's enough real archive to lay out the views against.
