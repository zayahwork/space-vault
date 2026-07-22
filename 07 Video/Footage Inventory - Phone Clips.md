---
date: 2026-07-22
type: inventory
card: 011 — inventory the phone clips
status: DONE — 4 clips probed and eyeballed frame by frame
---

# 📱 Phone clip inventory (Day 1 pool)

Location: `C:\Users\Administrator\Videos\space folder\` — landed 2026-07-22 ~13:40.
**All four are 4K 60fps HEVC**, which is the good news: we can punch in hard and crop and
still deliver 1080p clean. That's a real editing weapon and it's worth knowing we have it.

| Clip | Length | Orientation | Exposure | Verdict |
|---|---|---|---|---|
| **IMG_5170** | 0:30 | landscape | clean, even, white wall | ⭐ **best-looking of the four.** First ~6s is junk (camera being placed) — starts usable ~0:07 |
| **IMG_5169** | 1:41 | **vertical** (rotation −90) | bright, clear | ⭐ strongest talking clip. Lying down, hood up. **Native 9:16 — this is a Short for free** |
| **IMG_5153** | 0:29 | landscape | warm, hazy, slightly soft | ✅ usable. Close handheld, in bed |
| **IMG_5167** | **2:29** | landscape | ⚠️ **near-black** | ❌ **mostly unusable — see below** |

**Total: 5m 10s. Realistically usable: ~2m 40s.**

## ⚠️ The problem: the longest clip is the darkest

`IMG_5167` is 2:29 — **half of all the phone footage we have** — and it is shot in a dark
room with the hood up and almost no light on the face. In the contact sheet you're a
silhouette; several stretches read as pure black. HEVC 4K has some shadow latitude so a
lift in grade will recover *something*, but it will come back noisy and it will look bad
next to `IMG_5170`, which is clean.

**What this means for the episode:** the phone POV is supposed to be the spine, and after
dropping 5167 we have about **2m 40s of usable talking head for an 8–10 minute video.**
That's thin. Two ways out, and they're not exclusive:

1. **Reshoot the 5167 content.** Whatever you said in those 2.5 minutes, say it again with
   a lamp on your face. This is the cheap fix and it's the one I'd take.
2. **Lean harder on screen capture + charts** in the body, with phone POV reserved for the
   hook, the SES beat, and the outro.

→ Lighting is now the single highest-leverage change to the whole channel. One lamp,
off to the side, pointed at your face. It costs nothing and it fixes every future episode.

## Audio

All four are quiet — **−25.6 to −30.5 LUFS** integrated, against our −14 LUFS delivery
target. That's normal for raw phone audio and normalisation handles it, but `IMG_5169` at
−30.5 needs **+16 dB** of gain, which will lift the room noise with it. Budget for noise
reduction on that one.

`IMG_5169` is also **mono 44.1 kHz** while the other three are stereo 48 kHz (plus a
4-channel spatial track). Conform everything to 48 kHz on ingest or Premiere will resample
it mid-timeline and drift.

## 🎬 Free multicam pair — worth knowing

`IMG_5169` is stamped **2026-07-22 11:37:19** and the OBS capture
`space folder\2026-07-22 11-37-17.mp4` starts **11:37:17** — two seconds apart, 1:41 and
0:55 long respectively. **These are almost certainly the same moment from two angles**:
your face on the phone, your screen in OBS. Confirm by lining up the audio, then it cuts
as a two-camera scene — the single most produced-looking thing available to us in the
whole Day 1 pool.

## Shot-by-shot

- **IMG_5153** (Jul 21, 0:29) — handheld close, in bed, warm haze. Reflective register.
- **IMG_5167** (Jul 22, 2:29) — dark room, hood up, talking at length. **Content unknown to
  me because I can't see it.** If it's the SES beat, it needs reshooting, not rescuing.
- **IMG_5169** (Jul 22, 1:41, vertical) — bright, lying down, hood. Best delivery of the four.
- **IMG_5170** (Jul 22, 0:30) — sitting against a white wall, clean and even. Best image.
  Junk first 6s.

## Ingest checklist

- [ ] Conform all audio to 48 kHz stereo on import
- [ ] Rotate `IMG_5169` to portrait via its rotation flag — don't hand-rotate, the flag is correct
- [ ] Trim `IMG_5170` head at 0:07
- [ ] Noise-reduce `IMG_5169` after gain
- [ ] Decide 5167: reshoot or bin

## 🔒 OPSEC

Phone clips are low risk — no screens visible in any of the four. **The 14.6 hours of OBS
capture is where the danger is**, and per the locked decision **no named people ever**,
that now also means: no third-party name spoken on the audio track, not just on screen.
That includes anything said out loud in `IMG_5167`, which I cannot check because the
footage is too dark to read and I haven't been through the audio yet.
