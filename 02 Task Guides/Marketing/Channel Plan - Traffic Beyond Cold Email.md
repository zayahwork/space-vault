---
date: 2026-07-23
owner: Mark (marketing)
card: issues/marketing/032
status: drafted — NOTHING POSTS WITHOUT FOUNDER APPROVAL (public = permanent)
linter: "06 Code/check_channel_plan.py"
---

# 📡 Channel plan — traffic beyond cold email

**The rule over everything here: nothing posts without founder approval.** Public is
permanent — every draft below is a proposal, not a queue. The permanently banned
network (the one the founder is banned from) is not a channel and is not evaluated.

**Language rules baked into every draft** (`06 Code/check_channel_plan.py` enforces
them mechanically, same conventions as the outreach linters): the only external rate is
the dated ~68–72% sentence with the verbatim caveat; the retired multiple and the
unruled re-measured figure appear nowhere; GEO only via the external-safe sentence; no
named people from our threads in anything that could become public.

**Four channels chosen, one killed.** The logic: cold email finds people one at a time
and burns an address per attempt; these channels let the field find *us*, and they feed
each other — the vlog already produces raw material, X distributes it in small pieces,
the citable posts give X and HN something permanent to link, and HN is a one-shot spike
that needs the other three standing first to catch what it throws off.

---

## CHANNEL: X/Twitter — the technical presence

**Why keep it:** this is where SSA actually talks — operators, trackers, and the
astrodynamics crowd are on X daily, and our email threads prove the field engages with
specific, checkable claims. A public technical feed also de-anonymizes the cold emails:
recipients who search us find evidence, not an empty profile. The launch-delay thread is
already drafted and is ready ammunition — **it stays gated on the Kelso reply going out
first; that gate stands** (his data, he hears it from us before the public does).

**What we post:** small, checkable findings — one chart or one number per post, always
from free public data, always with the honest caveat. Never a product pitch; the feed is
"one person measuring things in public."

**Cadence:** 2–3 posts/week to start (daily is the card's ambition — earn it once the
vlog-to-X pipeline makes material cheap). Replies answered same day.

**Effort:** ~30 min/post when the chart already exists in RESULTS (most do); the real
cost is restraint, not writing.

### First 2 weeks
- Week 1: intro post — the STARLINK-3200 deorbit picture (drafted below; chart exists:
  `06 Code/output/starlink3200_deorbit.svg`).
- Week 1: "how we check ourselves" post — the control-group idea in plain words, linking
  the verification write-up (citable post #1 below) when it's live.
- Week 1 (conditional): the launch-delay thread, 7 posts + chart, **only after the
  Kelso reply is out** — it is drafted and waiting, CelesTrak credited on the image.
- Week 2: "the detector can say nothing happened" — alert mode, why a zero is the hard
  part; screenshot of a quiet day from the alert log.
- Week 2: "we published a wrong reason and fixed it" — the >500 km gate correction,
  because the field trusts people who show their corrections.
- Week 2: reply-mining — quote-reply to one active SSA discussion with a measurement we
  already have (no drive-by pitching; add data or stay out).

### First post (drafted — needs founder approval)
```post
I spent the last two weeks building a satellite maneuver detector using only free,
public tracking data. Proof it sees real events: STARLINK-3200 held a rock-steady
547 km orbit for three months, then on July 2 broke into a clean, deliberate descent —
its controlled deorbit, visible in public data weeks before it's gone.

Chart from public catalog data (CelesTrak / Space-Track). I'll be posting what the
detector finds — and where it breaks — as I go.
```

---

## CHANNEL: Published findings — citable posts (GitHub/blog)

**Why keep it:** email dies in an inbox; a post with a URL compounds. Field people share
citable write-ups, our cold emails get a "here's the method in full" link (which is what
serious recipients check for anyway), and investors doing diligence find dated, public
evidence of speed. The RESULTS pages are already 80% of the writing.

**What we post:** long-form write-ups of finished findings — method, numbers, control
group, and the limits section kept intact (the caveats are the credibility). Public
GitHub repo page or simple blog; each post is the canonical link X and HN point at.

**Cadence:** 1 post per finished finding — realistically 1–2/month. Never on a schedule;
only when a result is verified and its language is ruled.

**Effort:** ~2–3 h per post, mostly adapting an existing RESULTS page for outsiders
(strip internal names, translate jargon, keep every caveat).

### First 2 weeks
- Post #1: "How we verified a maneuver detector without ground truth" — the
  matched-control method from RESULTS - Checked Against History, on the approved dated
  sentence (drafted below).
- Post #2 (gated): the launch-delay finding — write-up form of the X thread, CelesTrak
  credited; **publishes only after the Kelso reply is out**, same gate as the thread.
- Housekeeping: pick the venue (GitHub Pages on the existing repo is the zero-cost
  default), one about page reusing the investor one-liner's facts.
- Cross-link pass: once #1 is live, the X "how we check ourselves" post and the HN
  draft both point at it.

### First post (drafted — needs founder approval; abridged, full text adapts the RESULTS page)
```post
# How I verified a maneuver detector without operator ground truth

My detector ranks satellites by how far their operator-supplied orbit disagrees with
the public catalog. For two weeks it had a problem: it graded its own homework. Here is
how I checked it with a second, independent method — and what an honest control group
looks like when you don't have ground truth.

The check: 30 days of public altitude history per satellite, looking for the step a
burn leaves behind — shared nothing with the detector except the satellite. For every
suspect, a control satellite the detector called ordinary, matched on catalog age and
orbit regime, run through identical logic. The bar isn't ours either: it's the 90th
percentile of the controls' own movement.

Result (measured 2026-07-22): ~68–72% of our top suspects show a real,
independently-checked burn signature, against ~10% of matched controls. The honest
caveat, and it matters: this is two of our own methods agreeing, not operator ground
truth — operator maneuver logs aren't public for these fleets. The write-up covers the
limits: what the method is blind to, and a wrong claim we published and corrected.
```

---

## CHANNEL: Vlog — cross-promotion (already running)

**Why keep it:** it already exists and already documents the build in public — the
traction story investors and field people respond to ("built and verified in under two
weeks, documented publicly"). Zero new production cost; the job is wiring it to the
other channels instead of letting it stand alone.

**What we post:** what's already being made — build-log episodes. The change: each
episode ends with one 15-second pointer ("the write-up and charts are on X/the repo —
link below"), and each episode's best chart/moment becomes an X post the same week.
Episode descriptions gain the canonical links.

**Cadence:** unchanged from the founder's current rhythm; the cross-promo adds one
line per episode, not new episodes.

**Effort:** ~10 min/episode (end-card line + description links + flagging the one
clippable moment for X).

### First 2 weeks
- Add the standing end-card line + link block to the next episode (drafted below).
- Back-fill: add the link block to the descriptions of the existing episodes.
- Pick one already-published moment (the deorbit chart walk-through if it exists) and
  cut it into the week-1 X intro post's follow-up.
- Once citable post #1 is live, pin it in every episode description.

### First post (drafted — the standing end-card + description block; needs founder approval)
```post
End-card line (spoken, ~15 s): "Everything I showed you — the charts, the numbers, the
code — is public. The write-ups are linked below, and I post the findings as they land
on X. If you work with satellites and want to tell me where this breaks, my inbox is
open."

Description block (append to every episode):
— Findings & write-ups: [repo/blog link]
— Ongoing results feed: [X profile link]
— Built on free public tracking data (CelesTrak / Space-Track).
```

---

## CHANNEL: Hacker News — one Show HN, timed

**Why keep it:** the detector story is exactly HN-shaped — solo builder, free public
data, honest verification, working code. One good Show HN reaches more technical people
in a day than a month of cold email, and it recruits the adjacent audience (data
engineers, space-curious devs) that no SSA channel touches. It is a one-shot per story,
not a feed — so it fires only when there's something standing to catch the traffic.

**What we post:** one Show HN for the detector, linking the public repo/write-up. First
comment pre-drafted (method, limits, what feedback we want) because the first comment
decides the thread's direction.

**Cadence:** once, when ready — earliest week 2, and only after citable post #1 is live
and the repo README presents well. Future findings can earn their own posts months
apart.

**Effort:** ~2 h prep (title, first comment, README pass) + one half-day of being
present in the thread. The founder must be at the keyboard the day it fires — replies
within the first hour decide everything.

### First 2 weeks
- Week 1: README pass on the public repo — a stranger should reach "what it does, one
  chart, how verified, known limits" in 60 seconds.
- Week 1: pre-draft the first comment (below, part of the post draft).
- Week 2: fire the Show HN (founder at keyboard, morning US time), only if post #1 is
  live and the founder approves that week.
- Week 2: harvest — technical objections from the thread become the X reply-mining
  material and the next citable post's FAQ section.

### First post (drafted — title + first comment; needs founder approval)
```post
Title: Show HN: Detecting satellite maneuvers with only free public tracking data

First comment: I built this in about two weeks: it compares operator-supplied orbits
against the public catalog, age-aware, and ranks satellites that disagree more than
their data staleness explains. To keep myself honest it verifies against a second,
independent method — 30 days of public altitude history — with matched controls:
measured 2026-07-22, ~68–72% of top suspects show a real, independently-checked burn
signature vs ~10% of matched controls. Caveat up front: that's two of my own methods
agreeing, not operator ground truth (operator maneuver logs aren't public here).
Known limits are in the README — including a blind spot on low-thrust electric
maneuvers and a wrong claim I published and had to correct. I'd most value being told
where the method breaks.
```

---

## KILLED: Reddit/forums (r/space, NSF forums, CelesTrak community)

**Reason:** worst effort-to-reach ratio of the five, and the audiences are wrong or
already covered. r/space is enthusiast-scale, its mods treat builder posts as
self-promotion, and satellite *operators* are not there in buying capacity. The NSF
forums are a launch-watching culture — deep, but not our buyer or our data peer. The
CelesTrak community overlaps almost entirely with a relationship we already hold
directly by email, where every conversation counts — a forum post there risks the
relationship for zero new reach ("gated on the Kelso reply" applies to the whole
public story, and this community is the one place most likely to trip it). Each forum
also demands sustained presence to not read as drive-by marketing — sustained presence
× a solo founder × three forums is exactly the overcommitment this plan exists to
avoid. **Revisit** only if a specific thread cites our published findings first; then
we reply with data, which every forum culture welcomes.

---

## How this feeds the machine

Cold email stays the spine (25–50/day target); these channels compound around it.
Sequence that matters: citable post #1 → X intro + verification posts → HN (week 2,
founder's call) → vlog keeps stitching it together. The launch-delay material — our
single best public artifact — unlocks everywhere at once the moment the Kelso reply
goes out. Scoreboard, checked weekly: X follows/replies from field accounts, repo
stars, inbound email citing a post — inbound is the whole point.
