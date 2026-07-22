---
date: 2026-07-22
type: reference
status: metadata verified · music/transitions NOT yet verified (see gap at bottom)
---

# 🎬 Style teardown — the 3 references

> [!warning] What I could and couldn't do
> I pulled **hard metadata straight from YouTube** — titles, lengths, views, dates, tags,
> descriptions. All of that below is real, not guessed.
> **I could not watch them.** YouTube won't hand over the video or the captions to me, and
> `yt-dlp` isn't installed on this machine. So the music and transition analysis you asked
> for is *not* done yet — see [[#The gap]] for the 5-minute fix.

## The three

### 1. Erik Cupsa — *Realistic Week As A 22 Y/O Tech Startup Founder In Toronto (raw coding vlog)*
`@SWErikCodes` · **8:43** · **76,064 views** · 2026-06-23 · Science & Technology

> Every single week is more busy than the last. Can't believe I shipped everything we did
> in this week AND got it all documented […] #startup #ai #entrepreneur #founder
> #techstartup #toronto #buildinginpublic #softwareengineer #coding #computerscience

**Best performer of the three, and the closest to you.** Note what's doing the work in
that title: **"Realistic"** and **"(raw coding vlog)"** — both are promises of *low
polish*. He's selling access, not production value. Age in the title ("22 Y/O") is doing
real work too, and **you're 19** — that's a sharper version of the same lever.

### 2. Alex Liu — *building my startup as a solo founder*
`@AlexLiu1` · **16:38** · **19,695 views** · 2025-10-19 · People & Blogs

> Episode 5 of how I'm building my startup / brand Zelos. From coding, marketing, content
> creation I'll be showing you the entire process as I try to figure it out as a 25 year old
> entrepreneur!
> **camera: Sony ZV-E1 · editing: DaVinci Resolve**

All-lowercase title, **numbered as a series** ("Episode 5") — the exact serial structure
you're proposing with Day 1 / 3 / 6 / 9. He publishes his camera and editor in the
description, which is a small trust move worth copying.

### 3. Linq — *A Day In the life of a Tech Startup CTO*
`@thelinqapp` · **11:21** · **34,874 views** · 2025-09-20 · People & Blogs

This one is **a company marketing video, not a solo founder vlog** — the description is a
funnel to their app. Treat it as a *format* reference, not a voice reference. Its real
lesson is the SEO: it's the only one of the three with a full tag stack, 20 of them:

`day in the life cto` · `tech startup life` · `startup cto` · `day in the life tech executive` ·
`startup culture` · `cto daily routine` · `software engineering leadership` ·
`startup behind the scenes` · `coding at a startup` · `life of a cto` · `startup grind` ·
`day in the life programmer` · `tech entrepreneur vlog` · `startup office tour` ·
`day in the life engineer` · `building a startup` · `startup leadership` ·
`tech startup vlog` · `what does a cto do` · `day in the life tech startup`

## What the numbers actually tell us

**Length: 8:43 · 16:38 · 11:21.** Our 9–12 min target sits right in it. The 76k video is
the *shortest*. Don't pad.

**Titles — all three lead with the person, not the product.** Nobody's title mentions what
the software does. Applied to you:
- ✅ *"Realistic Day Building a Space Startup at 19 (raw)"*
- ✅ *"i tried to prove my satellite detector wasn't a fluke"* (Liu-style lowercase, series)
- ❌ *"Maneuver Detection Pipeline Validation"* — nobody clicks this

**Your unfair advantages over all three:** you're younger than every one of them, and your
subject is *satellites*, not another CRM or productivity app. Erik gets 76k for shipping
web features. You're catching real spacecraft moving in orbit from free public data. Lean
on the imagery — the charts in `06 Code/output/` are genuinely arresting and none of these
channels have anything like them.

**Category:** two of three are **People & Blogs**, not Science & Tech. The vlog beats the
tech framing on this platform. Ship as People & Blogs.

## Description template (synthesised from all three)

```
[1–2 sentences, first person, what actually happened in these 2 days.]

[One honest line about the hard part — the thing that didn't work.]

What I'm building: [one line, no jargon]

camera: iPhone · screen: OBS · editing: Premiere Pro

#startup #space #buildinginpublic #solofounder #satellites #entrepreneur
#coding #spacetech #19yearold #dayinthelife
```

## The gap — music & transitions, not yet analysed

You said you like the music and the transitions, and that's the part I can't see from
metadata. **The fix:** download the three videos to a local folder (any browser-side
downloader, or `winget install yt-dlp`) and tell me the path. Then I can actually measure
it with ffmpeg, not guess:

- **cut rate** — scene-change detection gives me cuts-per-minute and where the pace lifts
- **music beds** — a loudness curve shows exactly where music enters, ducks under speech,
  and drops out for the emotional beats
- **transitions** — sampled frames across each cut boundary tell me whether it's a hard
  cut, whip pan, zoom punch, or match cut
- **hook** — frame-by-frame on the first 15 seconds of the 76k video is the single highest
  value thing I can study

That's a real teardown with numbers, and it takes me one pass. Until then I'm not going to
invent descriptions of transitions I haven't seen.
