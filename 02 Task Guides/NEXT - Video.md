---
date: 2026-07-22
owner: VIDEO window (cameraman — shoot support, edit, publish prep)
status: assigned
---

> [!warning] 🚪 Workspace rule (standing)
> Work ONLY in your lane (`07 Video/` + the footage folders outside the vault), on your own
> branch. Never touch master, other branches, or other lanes' files. Missing facts arrive in
> THIS note — if something is missing, say BLOCKED and state exactly what you need.

# 🎥 NEXT — video (cameraman)

> [!success] CTO review of your first commits
> The style teardown is exactly how this company works — measured, not guessed. The OPSEC
> table, the goal rule (episode goals sourced to vault notes dated before the footage), and
> the honest-beats shot list are all approved as written. Founder has reviewed the system.

## Decisions now locked (founder + CTO, 2026-07-22)

- **Cadence: every 3 days — Day 1 → 3 → 6 → 9. Day 1 = Jul 22**, Episode 1 covers Jul 21–22
  footage. Day 9 = Jul 30/31 window = season-finale beat (the capability unlock + the big
  meeting land there).
- **Length band: 8–10 min** (your teardown's evidence beat the CTO's 5–8 guess; Erik's 8:43
  is the best performer, so live at the bottom of your 9–12 when in doubt).
- **Day-N counter** burned on screen (top corner) AND on the thumbnail, every episode.
- **Founder is the publish gate.** Nothing uploads until he's watched the final cut. His
  review loop: you deliver a draft, he gives change notes, you revise.

## New orders, in priority order

### 1. The 60-second style test — FIRST, before any full episode work

Cut the **first ~60 seconds of Episode 1** from the existing footage (cold-open cut-storm
per your teardown: goal stated, stakes up, Day-1 card in). Founder reviews it and gives
notes; the approved test becomes the **binding style reference** for every future cut.
Cheap iteration now, zero style arguments later.

### 2. The "what's happening" popup system (founder order — this is the comprehension layer)

The 5-terminal grid means nothing to a normal viewer. Build a reusable overlay treatment:

- **Blur/dim the screen capture background**, then a **clean animated popup** slides in and
  a voice explains in one plain sentence what's happening ("the detector just re-checked
  489 satellites — two thirds of the suspects really moved").
- Every jargon term gets its plain-English popup within ~2 seconds of being spoken.
- A persistent **goal tracker** (the episode's goal + checklist that ticks as beats land)
  so the viewer always knows where we are — the episode is edited backwards from the known
  ending, the tracker is how the audience keeps up.
- Build it once as a Premiere template (Essential Graphics) so every episode reuses it.

### 3. Voices

- Narration popups use the **edge-tts neural voices** — the best free tier, same stack as
  `team_voice.py`. Pick voices that sound broadcast-clean, not robotic; audition 3 and put
  a 10-second sample of each in your lane for the founder to pick from.
- Music bed never fully silent (your own teardown finding #2); master **−14 LUFS, peak
  ≤ −1 dBFS**.

### 4. Anonymization language (extends your OPSEC table — founder order)

**No named people, ever** — not just no emails. Real outside parties become roles:
*"a broker at one of the biggest insurance firms," "a legend in the field replied,"
"we have a contract with a buyer."* Stakes survive anonymization; names don't come back
once leaked. Blur for a name in passing, cut for anything with an @ in it, auth files
never on screen. Your OPSEC pass + timestamp list stays mandatory before "ready to
publish."

### 5. Footage logistics

- iPhone POV clips: founder is uploading to Google Drive → they must land in a local
  folder ffmpeg can read (`Videos/space folder/phone/` as you suggested). If the Drive
  connector blocks unattended calls, say BLOCKED and the founder pulls them down by hand.
- Raw footage and renders stay OUT of git, as you're already doing. Text only in the vault.

## Deliverable order

1. 60-second style test → founder review.
2. Popup/tracker template + 3 voice auditions → founder picks.
3. Episode 1 full cut (using approved style + template) → OPSEC pass + timestamp list →
   founder review → publish prep (title, description, thumbnail with Day 1 card).
