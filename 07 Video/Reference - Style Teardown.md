---
date: 2026-07-22
type: reference
status: COMPLETE — metadata, cut rate, loudness and frames all measured from the actual files
---

# 🎬 Style teardown — the 3 references

All three downloaded to `C:\Users\Administrator\Videos\reference\` (outside the vault, not
committed — they're someone else's copyrighted work, kept locally for study only).
Everything below is **measured with ffmpeg**, not guessed.

| | Erik Cupsa | Alex Liu | Linq |
|---|---|---|---|
| Title | Realistic Week As A 22 Y/O Tech Startup Founder In Toronto (raw coding vlog) | building my startup as a solo founder | A Day In the life of a Tech Startup CTO |
| **Views** | **76,064** | 19,695 | 34,874 |
| Length | 8:43 | 16:38 | 11:21 |
| **Cuts** | **119 (13.7/min)** | 97 (5.8/min) | **174 (15.3/min)** |
| Median shot | **1.6s** | 4.9s | **2.0s** |
| **Loudness** | **−12.1 LUFS** | −18.5 LUFS | −18.4 LUFS |
| Silent gaps | **0** | **17** | **0** |
| First spoken word | **2.1s** | 19.8s | 14.1s |
| Category | Science & Tech | People & Blogs | People & Blogs |

## 🔑 The three findings that matter

### 1. The hook is a cut-storm, and then the video calms down

Erik's cuts per minute, minute by minute:

```
min:  0    1   2   3   4   5   6   7   8
cuts: 38  12   5   7   2   3  15   8  29
      ▲▲▲                        ▲▲
    the hook                  the outro
```

**38 of his 119 cuts — a third of the entire video — are in the first 60 seconds.** Then
it drops to 2–7/min through the middle and spikes again at the end. Linq does the identical
thing: 38 cuts in minute 0, tapering to 3 by minute 11.

Alex Liu, the weakest performer, is *flat* — 12 cuts in minute 0 and an even amble after.

**This is the single most copyable thing here.** The hook isn't a slower version of the
video, it's a different object: a trailer. Median shot in Erik's first 20s is well under a
second; some are 0.2s. Then he lets shots run 13s+ in the body so you can actually follow
the work.

### 2. The audio floor never hits zero

Erik and Linq both have **literally zero silent gaps** across the whole video. Music runs
wall to wall, ducking under speech and coming back up. Alex has 17 audible dropouts — and
the lowest views of the three.

Erik masters at **−12.1 LUFS**, a full **6 dB louder** than the other two. (He's actually
clipping — peak +2.9 dBFS. Don't copy that part.) YouTube normalises to about −14 LUFS, so
Alex's −18.5 will play back noticeably quieter than everything around it.

→ **Master at −14 LUFS, peak no higher than −1 dBFS, and never let the bed go silent.**

### 3. Erik's cold open is other people's words over disconnected B-roll

From the frames and the caption track, his first 20 seconds are:

```
0:02  "I can't believe we built this in 30 hours."   ← over a phone-screen product shot
0:07  [music]
0:09  "Whether it's your fault or not, like other circumstances…"  ← B&W insert, serious beat
0:12  [music]
0:15  "We've got a lot of big things coming."        ← walking shot, night city
0:18  "Founder and CEO of Meuze. Welcome to the show." ← podcast/TV footage (social proof)
```

The audio is a **montage of the best lines from the whole week**, laid over visuals that
have nothing to do with each other — city establishers, a hand on a keyboard, a phone
screen, a desaturated black-and-white insert for the emotional line. Nothing in the cold
open is in chronological order. He earns the next 8 minutes in 20 seconds.

**Linq is the opposite and also works:** 14 seconds of *no talking at all* — pure music
over a coffee run, with a title card ("DAY IN THE LIFE OF A TECH STARTUP CTO") burned over
moving footage. Then section cards on black — **"COFFEE RUN"** — as chapter markers through
the day.

## What I'm stealing for us

| Device | Where from | How it maps to you |
|---|---|---|
| **Cut-storm cold open** | Erik + Linq | 20s of your best lines from the 2 days over your best visuals. **The orbital charts belong here** — no other channel in this niche has them |
| **Burned-in subtitles, always** | all three | Erik and Linq both burn captions the whole way. Non-negotiable for retention |
| **Section cards on black** | Linq | Your day already has structure — `DEEP WORK 1` · `LIFT` · `THE SES PROBLEM`. Free chapter markers |
| **B&W insert for the serious beat** | Erik | Use it exactly once: the SES miss. Desaturate, drop the music, let it breathe |
| **Continuous music bed** | Erik + Linq | Never a silent frame |
| **Body shots run long** | Erik (13s+ p90) | When you're explaining the detector, stop cutting. The hook earns you that patience |
| **People & Blogs category** | 2 of 3 | The vlog framing beats the tech framing on this platform |

## Titles — all three lead with the person, not the product

Nobody's title says what the software does. Erik's title sells *low polish* twice
("Realistic", "raw coding vlog") and puts his age in it. **You're 19** — a sharper version
of the same lever.

- ✅ *"Realistic Day Building a Space Startup at 19 (raw)"*
- ✅ *"i tried to prove my satellite detector wasn't a fluke"* (Liu-style lowercase, serial)
- ❌ *"Maneuver Detection Pipeline Validation"* — nobody clicks this

## Tags — copy Linq's stack, swap the noun

Linq is the only one running full tag SEO, 20 of them: `day in the life cto`, `tech startup
life`, `startup grind`, `what does a cto do`, `tech entrepreneur vlog`… Same shape works
for us with `space startup` / `satellite` / `solo founder` / `19 year old founder`.

## Description template

```
[1–2 sentences, first person, what actually happened in these 2 days.]

[One honest line about the hard part — the thing that didn't work.]

What I'm building: [one line, no jargon]

camera: iPhone · screen: OBS · editing: Premiere Pro

#startup #space #buildinginpublic #solofounder #satellites
#entrepreneur #coding #spacetech #dayinthelife
```

Alex publishes his camera and editor in the description — small trust move, worth copying.

## Reproduce any of this

```bash
cd "C:\Users\Administrator\Videos\reference"
ffmpeg -i QMk2-tQJKyg.mp4 -an -vf "scale=320:-2,select='gt(scene,0.25)',metadata=print:file=cuts.txt" -f null -
ffmpeg -i QMk2-tQJKyg.mp4 -af "ebur128=peak=true,silencedetect=n=-45dB:d=0.4" -f null -
ffmpeg -ss 0 -t 20 -i QMk2-tQJKyg.mp4 -vf "fps=2,scale=320:-1,tile=6x7" -frames:v 1 hook.png
```
