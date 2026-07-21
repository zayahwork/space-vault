# 🛰️ Day 2 — Tuesday, July 21

> [!tip] Today in one sentence
> Finish the last 2 emails, then the fun part: **write your first orbit code and SEE a satellite maneuver with your own eyes.**

## ⏰ Anchors (same every day)
`06:30` wake → `07:45` deep work → `10:00` 🏋️ LIFT → `11:00` shower → `11:30` lunch → `12:15` deep work → `17:30` dinner → `22:00` sleep

---

## Morning block (07:45–10:00)

- [ ] **Email 7 — Office of Space Commerce / TraCSS.** We don't have an address yet. Find it: go to `space.commerce.gov` → Contact page → send draft #7 from [[Outreach Emails]] (or their form).
- [ ] **Email 10 — AMOS organizers.** Contact form at `amostech.com/contact` (they're run by the Maui Economic Development Board). Draft #10 in [[Outreach Emails]] — fill the greeting with whatever name their contact page shows, or just "Aloha."
- [ ] **Check inbox** for replies to yesterday's 8 sends. Any reply → answer within the hour if you can (speed = respect). Log who replied at the bottom of this note.
- [ ] **Moriba thread:** if he answered our reply → book the 15 min via his EA (`team.moriba@outlook.com`) for any day AFTER Thu (he's back Jul 23). Then tell Claude — we'll build a tight prep sheet: 3 questions max, listen-mode.
- [ ] If Brian's email bounced yesterday: send draft #6 (tweak the name/company lines) to **Patrick Miga, Advanced Space** → try `patrick.miga@advancedspace.com` — he wrote a 2025 paper literally about low-latency maneuver detection.

## 🏋️ 10:00 — LIFT. Non-negotiable. Then shower + lunch.

## Afternoon block (12:15–15:00) — FIRST CODE 🎉

Goal: a chart of one satellite's orbit over 30 days where a **maneuver** (thruster firing — see [[Glossary]]) shows up as a visible jump in the line.

- [ ] Open a terminal in `C:\Space` and tell Claude Code: **"let's build the maneuver chart"** — we do it together, step by step
- [ ] `pip install sgp4 skyfield requests matplotlib`
- [ ] Pull orbit history from your Space-Track account — **as OMM/JSON, not TLE** (old format broke at 100,000 objects — [[Glossary]] explains)
- [ ] Plot one element (like altitude/mean motion) over 30 days for a GEO satellite
- [ ] Find the jump. Screenshot it. That screenshot is the seed of the whole company.

## Late block (15:20–17:30)

- [ ] Play with the data more — plot 2–3 more satellites (ISS, a Starlink)
- [ ] Log any replies / send thank-yous
- [ ] Skim tomorrow's file ([[Day 3 - Wed Jul 22]]) — SBIR day, one thing has a real deadline

## 🌙 21:30 — Review
- [ ] Tick what got done, move anything unfinished to tomorrow's file
- [ ] Write 2 lines at the bottom: what happened, how it felt

---

### 📓 Today's log (write here)
-
