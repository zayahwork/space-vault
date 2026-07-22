---
date: 2026-07-22
role: cameraman / editor lane
status: system defined, nothing cut yet
---

# 🎥 VIDEO — START HERE

Channel: **Zayah in Orbit** — a 19-year-old building a space startup from his bedroom,
documented as it actually happens.

## The cadence (locked 2026-07-22)

Post **every 3 days**, each episode covering the ~2 days of footage before it.
Thumbnail carries the day number: **Day 1 → Day 3 → Day 6 → Day 9 → …**

- **Day 1 = 2026-07-22** (today). Episode 1 covers Jul 21–22 footage.
- Day 3 = Jul 24 · Day 6 = Jul 27 · Day 9 = Jul 30 (this one lands *after* the Jul 29
  `quiet.py` unlock — that's the season finale beat, see [[Idea - The Week Before Jul 29]]).

## Format (locked)

| | |
|---|---|
| Length | **8–10 min** (locked by founder 2026-07-22) — Erik's 76k video is 8:43, the shortest of the three references ([[Reference - Style Teardown]]) |
| Spine | **You, talking POV** (iPhone, day-in-the-life). Screen capture is B-roll *under* your voice, never the main event |
| Shorts | 2–3 cut out of each long-form, not shot separately |
| Structure | Open on a **goal**, spend the episode on the real attempt, close on the verdict + the next goal |

### The goal rule (important — this is where honesty lives)

You want each episode framed around a goal you've *already* passed. That works and it's
honest **on one condition**: the goal has to be one you actually wrote down *before* the
footage was shot. The vault date-stamps everything, so this is easy to keep clean.

- ✅ **Allowed:** "Today I'm finding out if this thing only works on Starlink." That was a
  real open question in [[Plan - Verify the Detector]] before Jul 22. You just don't
  spoil the answer in the first 30 seconds.
- ❌ **Not allowed:** inventing a goal you never had, or narrating a result as if it were
  still uncertain when the footage shows you already knew. That's the one thing that
  kills a build-in-public channel, and it's unnecessary — the real story is better.

**Rule I'll follow:** every episode goal gets sourced to a vault note dated *before* the
first frame of that episode's footage. If I can't source it, I won't write it.

## 🔒 OPSEC — read before anything is marked ready to publish

Your screen capture is 14+ hours of your actual desktop. It contains other people's
private contact details. **25 unique real email addresses** live across these files, and
any one of them on screen for a single frame is a doxx:

| Danger on screen | Where it lives |
|---|---|
| 📇 Real people's emails | `06 Code/outreach_targets.csv`, `06 Code/contact_check.csv`, [[Outreach Emails]], [[Outreach Emails - Batch 2]] |
| 👤 A named real person | [[One-Pager - Melissa Heldreth]], [[Insurer Target List]], [[Guide - Moriba Jah Call]] |
| 🔑 Space-Track login | the auth file ([[Guide - First Maneuver Chart]]) — **never on screen, ever** |
| 📞 Your own phone/email | [[01 TASKS]], anything with your signature block |
| 📬 Gmail / inbox | any browser tab showing sender names |

**Hard rule: nothing gets marked ready-to-publish until I've done an OPSEC pass and
listed every timestamp needing a blur or a cut.** No exceptions, no "it's only a second."

> [!danger] Locked by founder 2026-07-22: **NO NAMED PEOPLE. EVER.**
> No third party's name appears on screen *or is spoken on the audio track*. Not
> researchers, not brokers, not insurers, not people who replied to you. They're "a broker
> in Seattle", "the guy who wrote the paper". This is stricter than blurring and it's
> simpler to enforce: if a name is in the frame or in the mouth, it's cut.

Blur is fine for a UI element in passing. **Cut** for anything with an @ in it, any real
person's name, and the auth file always.

## Footage inventory (as of 2026-07-22)

**On disk — 14h 37m, all 1080p60 with audio, all OBS screen capture:**

| File | Length |
|---|---|
| `Videos/space folder/2026-07-21 03-17-43.mp4` | 9h 22m (25 GB) |
| `Videos/space folder/2026-07-21 21-38-54.mp4` | 2h 38m |
| `Videos/space folder/2026-07-21 17-18-36.mp4` | 1h 47m |
| `Videos/space folder/2026-07-21 19-05-47.mp4` | 45m |
| `Videos/2026-07-22 11-38-58.mp4` | 19m |
| `Videos/space folder/2026-07-22 11-37-17.mp4` | 55s |

**Not on disk yet:** the iPhone POV talking clips — uploading to Google Drive → **SPACE
WORK**. These are the spine of the episode; no edit can start without them.
→ they need to land in a local folder ffmpeg can read (Drive for Desktop, or just
download the folder). Suggested home: `Videos/space folder/phone/`.

**Tools confirmed on this machine:** OBS Studio · Adobe Premiere Pro 2026 + Media Encoder
2026 · ffmpeg + ffprobe on PATH. `yt-dlp` is *not* installed.

## Who does what

- **You:** shoot the POV, pull the phone clips to Drive → local. Review my shortlist.
- **Me:** machine pass over the 14.6 hours (find every talking moment, every scene change,
  every leak), episode structure, script, titles, thumbnails, shorts, OPSEC sign-off.
  You should not be scrubbing 25 GB by hand — that's the entire point of me.

## Where things live

- [[Reference - Style Teardown]] — the 3 reference videos, what's verified, what isn't
- [[Shot List - Episode 1]] — what to film, and what's missing from Jul 21–22
