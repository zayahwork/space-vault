---
date: 2026-07-22
type: opsec finding
severity: HIGH — blocks publication of the clip as shot
clip: "Videos/space folder/2026-07-22 13-59-23.mp4"
---

# 🚨 OPSEC — the newest clip cannot ship as shot

`2026-07-22 13-59-23.mp4` · 2:46 · 1080p60 · webcam PiP bottom-right · −23.5 LUFS

This is the first footage with **your face and your screen in one recording**, which makes
it genuinely valuable. It is also **the most sensitive footage in the entire pool**, and it
is not close.

## What is readable on screen

I pulled full-resolution crops at 0:08 and 1:35. At 1080p the terminal text is **plainly
legible** — not squint-legible, *readable*. Four terminal windows are tiled and every one
of them is captured:

| Window | What's exposed |
|---|---|
| `roster-update-cto-org` | **"the two 'go's on Kelso/Deidra"** — two real people, named |
| `Casual conversation check-in` | **"The one that'll save Tim's sanity"** — named |
| `Review email queue…` | The whole outreach state: *"24 have no email address at all"*, *"6 are paper authors deliberately blocked until someone writes the question by hand"*, *"mostly the insurers"* |
| `Tech stack discussion` | Internal verdicts on the detector, GEO archive gaps |
| `Plan YouTube series…` | This conversation — the channel's own strategy, on screen |

**Real people are named on screen.** That breaks the rule you locked today —
*no named people, ever* — inside the very first clip shot after you locked it.

Also exposed, lower stakes but worth a decision rather than an accident: the outreach
funnel's actual numbers, the fact that some targets are deliberately blocked, and the whole
multi-window agent setup. None of that is dangerous to third parties, but publishing it is
a **strategic** choice and should be yours to make deliberately, not a by-product of
leaving OBS running.

## Why blurring won't save it

Blur works for a name that crosses frame once. Here the text is **the entire frame, for the
entire 2 minutes 46 seconds**, on four windows that scroll and change. Tracking blurs over
that is hours of work and one missed frame is the whole leak. Not worth it.

## What we can still use — the PiP

The webcam insert is **~640×460 inside the 1080p frame** and it's the best-lit footage we
have of you: natural window light from the right, face clear, and the bedroom visible
behind — the desk, the chair, the window. That is *exactly* the "building this from my
bedroom" shot the channel needs, and it's better exposed than `IMG_5167` by a mile.

**Cropping to the PiP alone means upscaling ~3×.** It'll be soft — fine for a 2–4 second
insert or a punch-in reaction, not for a hero shot.

→ Usable: **crop to the webcam region, discard the rest of the frame entirely.** Never
show the desktop from this recording, at any size. Scaling it down doesn't help; text
that's illegible on your monitor is still legible to anyone who pauses at 4K on a TV.

## 🔧 The standing fix — capture clean at the source

This is a capture problem, not an edit problem, and the fix costs nothing:

1. **Make an OBS scene that captures one window, not the desktop.** The detector output,
   the charts, the terminal you *want* on camera. Not the whole screen.
2. **Second scene: webcam full-frame.** Then you have a real A-cam for free, at full
   resolution instead of a 640-pixel crop.
3. **Before recording the desktop at all:** close the agent windows, the email queue, and
   anything with a person's name in it.
4. **The charts in `06 Code/output/` are the screen content that actually sells the
   channel** — orbital plots nobody else has. Those are safe, and they're better B-roll
   than a terminal full of internal chatter.

## Status

- ❌ `2026-07-22 13-59-23.mp4` — **not publishable as shot.** PiP crop only, everything
  else discarded
- ⚠️ The 14.6 hours of earlier OBS capture has **not** been scanned yet and is very likely
  to have the same problem. Assume it does until I've been through it.
