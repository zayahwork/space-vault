---
date: 2026-07-22
type: PRD
owner: VIDEO window (cameraman)
status: aligned — grilled with founder 2026-07-22
---

# PRD — "Zayah in Orbit" vlog system

## 1. Problem

The company has one marketing channel (cold email) and a founder banned from LinkedIn. Meanwhile the actual story — a 19-year-old running an AI team against live satellite data from his bedroom, with a real countdown to Jul 29 — is more compelling than any cold email, and it's currently evaporating unrecorded. Raw material exists (14h 37m of OBS capture, iPhone POV clips) but 25 GB of footage is unwatchable without an editor, and a screen full of terminals is meaningless to a normal viewer.

## 2. Solution

A build-in-public vlog channel ("Zayah in Orbit") run by the cameraman lane: high-intensity day-in-the-life episodes every 3 days (Day 1→3→6→9, Day 1 = Jul 22), 8–10 min plus 2–3 shorts cut from each, edited backwards from the known ending with an always-visible goal tracker and plain-English popups so anyone can follow. Founder on camera as the spine, AI voices and screen capture as b-roll, hard OPSEC (no named people, no addresses, published numbers only), founder approves every cut before upload.

## 3. User stories

- As a viewer with zero space knowledge, I always know the episode's goal, where we are against it, and what just happened — the tracker and popups tell me within 2 seconds.
- As a viewer, when the terminal grid appears, the background blurs and an animated popup with a clean AI voice tells me in one sentence what the machine just did.
- As the founder, I can film 20-second check-ins and dump footage; the cameraman finds the story — I never scrub 25 GB by hand.
- As the founder, nothing publishes until I've watched the final cut, and no frame ever exposes a name, address, credential, or unpublished number.
- As the CTO, each episode's goal is sourced to a vault note dated before the footage — the channel can never be caught faking drama.
- As a future customer/contact, I can watch the channel and verify these people are real and honest before replying to their email.

## 4. Module map

All in the video lane (branch `video`), text in vault, media outside git:

- `07 Video/00 VIDEO - START HERE.md` — system doc (exists; update cadence numbering + no-named-people rule).
- `07 Video/Reference - Style Teardown.md` — measured style bible (exists, done).
- `07 Video/Shot List - Episode N.md` — per-episode (Episode 1 exists).
- `07 Video/Style Test - Notes.md` — NEW: founder's verdict on the 60s test; becomes the binding style reference.
- `07 Video/Overlay System.md` — NEW: the popup/tracker spec + Premiere Essential Graphics template location. **This is the deep module** — every episode reuses it; if it's right once, comprehension is solved forever.
- `07 Video/Voices.md` — NEW: 3 edge-tts auditions + founder's pick.
- `07 Video/Publish Checklist.md` — NEW: OPSEC pass + timestamp list + metadata (title, description, tags, Day-N thumbnail) per episode.
- `02 Task Guides/NEXT - Video.md` — CTO orders channel (written 2026-07-22).
- Media: `Videos/space folder/` (OBS), `Videos/space folder/phone/` (iPhone via Drive), renders + Premiere projects outside the vault. Never committed.

## 5. Implementation decisions

- Purpose: marketing asset, not diary — but shot as authentic day-in-the-life; real deadlines are the drama, nothing invented.
- Cadence every 3 days; Day-N counter burned on screen and thumbnail; Day 1 = Jul 22; Day 9 ≈ the Jul 29–31 finale arc.
- 8–10 min band (teardown evidence over gut feel); hook = cut-storm first 60s; music bed never silent; master −14 LUFS, peak ≤ −1 dBFS.
- Comprehension layer: blur background → animated popup + AI voice one-liner; persistent goal tracker ticking toward the episode goal; jargon popup within 2s.
- Voices: edge-tts neural (best free, same stack as team_voice.py); founder picks from 3 auditions.
- Anonymization: no named people ever — roles only ("a broker at a major insurance firm"); blur for incidental names, cut for anything with an @; auth files never on screen.
- Goal rule: every episode goal sourced to a pre-dated vault note; results never narrated as uncertain when footage shows we knew.
- Workflow: cameraman delivers draft → founder notes → revise; 60-second style test approved before any full episode.
- Episode 1 arc (locked): "does it only work on Starlink?" → OneWeb win → SES miss as the honest low → Jul 29 countdown close.

## 6. Testing decisions

- **Style test = the unit test**: 60s cut → founder verdict in `Style Test - Notes.md`. Nothing else proceeds until it passes.
- **Overlay template**: render one popup + tracker over real grid footage; pass = founder can follow it with the sound off.
- **Voices**: 3 × 10s samples; pass = founder picks one without asking "is this the cheap one?"
- **Per-episode**: OPSEC pass produces a timestamp list (blurs/cuts) BEFORE founder review; loudness verified with ffmpeg (−14 LUFS ± 1); every episode goal has its pre-dated vault source linked in the shot list.
- **Channel-level**: retention on the first 60s (did the cut-storm hook hold?) reviewed after each upload; adjust the style reference only via founder-approved notes.

## 7. Out of scope

- **Daily uploads** — editing would eat the company; every 3 days is the ceiling.
- **Live streaming** — no OPSEC pass possible on live frames.
- **Named people / private threads on screen** — one leak kills warm conversations; roles only.
- **Footage or renders in git** — 25 GB files would destroy the worktree system.
- **Paid voice/TTS services** — edge-tts free tier is broadcast-adequate; revisit only if founder rejects all 3 auditions.
- **Faked reactions or invented goals** — the one thing that kills a build-in-public channel; the real story is better.
- **Cameraman touching other lanes' files** — isolation stands; facts arrive via `NEXT - Video.md`.
