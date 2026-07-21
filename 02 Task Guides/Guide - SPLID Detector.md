# 🔧 Guide — The SPLID Detector (the real prototype)

**What SPLID is:** MIT's public dataset of satellite behavior where experts already labeled
every maneuver — a practice exam WITH the answer key. We train/test on it instead of spending
months hand-labeling. Scoring well on a public MIT benchmark = credibility money can't buy
(2024's winners got MIT + Air Force attention).

> [!note] Status Jul 20 night
> ✅ Devkit already cloned to `06 Code/splid-devkit/` — includes baseline code, **the winning
> solutions, the official scoring script, and small "toy" data files.**
> ⚠️ The full 500-trajectory dataset download FAILED (Dropbox's auto-zip breaks past 4 GB via
> script). **Plan B for the build session:** (1) run the whole pipeline on the included *toy*
> data first — proves everything works with zero download; (2) for the real dataset, open the
> Dropbox link from `splid-devkit/docs/dataset.md` in the **browser** and download the
> subfolders one at a time (browser handles big grabs better), or Claude finds a mirror.

## The sequence (do WITH Claude — say "let's build the SPLID detector")

1. **Get it running** — devkit is cloned; run THEIR baseline detector end-to-end on the toy
   data. Success = numbers come out. Don't improve anything yet.
2. **Study the winner** — `github.com/DavidBaldsiefen/splid-challenge` (1st place 2024).
   Understand their approach in plain terms before inventing our own.
3. **Our own pass** — change-point detection + behavior classification, your ML instincts.
   Target: beat the baseline on at least one metric. (Beating the *winner* is a later goal.)
4. **Reality transfer** — run the detector on LIVE Space-Track history (the ISS chart pipeline
   from [[Guide - First Maneuver Chart]]) and show it flagging a real satellite's real maneuver.
5. **Screenshot everything that works.** These images + benchmark scores ARE the pitch.

> [!note] Honesty rule
> SPLID is partly simulated data. Anything we claim publicly gets verified on live data first.
