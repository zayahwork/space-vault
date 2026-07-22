---
date: 2026-07-22
type: idea
status: recommendation, not decision
context: "[[Idea - Jul 29 Broker Demo]], [[RESULTS - The Quiet Detector]], [[Guide - Insurer Probe]]"
---

# 💡 The week before Jul 29 — sequence the capability and the meeting

**The point:** `quiet.py` unlocks ~Jul 29 by itself — nothing to build. The thing that
*doesn't* happen by itself is having someone across the table that week. Coffee with a
broker takes days to land, so the outreach has to start **now**, before the capability
exists, timed so the meeting falls *after* it does.

## The timing math

- Today is Jul 22. A cold-ish "coffee next week?" email typically takes 2–5 days to get
  a reply and a slot.
- Sent this week, the natural landing zone is **Jul 30 – Aug 1** — exactly when cadence
  verdicts are live and have a day or two of shakeout behind them.
- Sent *after* Jul 29, the meeting lands mid-August and the unlock sits idle for two
  weeks. The archive keeps growing either way, but momentum and the founder's calendar
  don't.

## What to do each day (recommendation)

- **Jul 22–23:** Marketing drafts the Heldreth (Gallagher, Seattle — local, coffee is a
  real ask) note. One paragraph, no deck: *"I watch satellite behavior from public
  data. Next week I switch on the part that spots a satellite that's stopped
  station-keeping — before anyone files a claim. 30 minutes over coffee to show you?"*
  The capability being *days away* is a feature — it's a reason the meeting is now.
- **Jul 24–28:** Pick the 3–5 demo satellites (fast-cadence objects with ≥3 spikes
  banked, per [[Idea - Jul 29 Broker Demo]]) and dry-run the two screens. Tech lane.
- **Jul 29:** Run `python quiet.py` for real. If it produces garbage, we still have a
  day or two of slack before any meeting — that slack only exists if the email went
  out on the 22nd–23rd.
- **Fallback:** if Heldreth doesn't bite, the same email works for the [[Guide -
  Insurer Probe]] targets — but spend Heldreth first; a local coffee beats a cold
  video call.

## The risk this manages

If the meeting is booked and Jul 29 slips (archive gap, bug), the demo degrades
gracefully: alert mode and the checked-against-history numbers (11.3×, 72% vs 11%) are
live *today* and carry a 30-minute coffee on their own. The reverse failure — capability
live, calendar empty — has no fallback.

## Routing

This is marketing's send and tech's dry-run; nothing here is mine to implement. The
one decision the founder/CTO owns: **greenlight the Heldreth email this week, yes/no.**
