# 🛰️ Guide — Your First Maneuver Chart

**What this is:** pull 4 months of the ISS's orbit history from Space-Track (free), chart it,
and watch its **maneuvers** appear as visible jumps. The ISS re-boosts itself every few weeks
(drag slowly pulls it down, thrusters push it back up), so the chart shows a beautiful sawtooth —
each tooth edge is a real thruster firing, detected by *your* code from *free* data.
This is the seed of the entire company, on one screen.

## Step 1 — the auth file (2 minutes, you only)

1. In the sidebar open `06 Code/spacetrack_auth.json` (or open it in Notepad)
2. Replace the two placeholder texts with your **Space-Track email and password** (the account
   you made today — zayahwork@gmail.com + the password you set)
3. Save.

> [!warning] Why Claude doesn't do this part
> Passwords never pass through Claude — rule, no exceptions. The file stays on your machine;
> only the script reads it.

## Step 2 — run it (with Claude)

Say **"go run the chart"** in the Claude Code session. Claude writes/runs the script:
pulls the history (in **OMM/JSON** — the modern format; see [[Glossary]]), converts orbit
numbers to altitude, plots it, and marks every jump it detects.

## Step 3 — look at it

- The saved image lands in `06 Code/output/`
- Sawtooth going up-drop-up-drop = drag vs. reboosts. Each marked line = a detected maneuver.
- **Screenshot/keep it.** This picture goes in every future pitch.

## Then (same session, easy wins)
- Chart a **Starlink** (they maneuver constantly, autonomously)
- Chart a **GEO satellite** (station-keeping = small regular nudges)
- Each one teaches the detector something different.
