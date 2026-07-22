---
title: Outreach Emails — Batch 2 (12 new targets, not yet sent)
type: working-doc
created: 2026-07-21
parent: Outreach Emails.md
tags: [outreach, ssa, batch-2]
status: drafted, not sent
---

# Outreach Emails — Batch 2 (drafted, not sent)

> Batch 1 (10 sent, 2 replies — Moriba Jah, T.S. Kelso) lives in [[Outreach Emails]]. This batch
> is new people, not already contacted. Same rules: **email, contact forms, X/Twitter only — never
> LinkedIn** (permanently banned account). Read each aloud before sending, tweak one line so it
> doesn't read as copy-paste, space them out.
>
> **What's new since batch 1 that these emails lean on:** a real, measured result —
> ranking Starlink by raw catalog-vs-operator disagreement flags 3,555 objects as "maybe
> maneuvered"; accounting for how stale each catalog entry is cuts that to 541. **85% of the
> naive list was just old data, not a burn.** That's the hook. It's a finding, not a sales claim,
> so it survives being said to an expert.
>
> **Attach when a picture helps:** the one-image proof at
> [[RESULTS - One Picture (Starlink deorbit)]] — `06 Code/output/starlink3200_deorbit.svg`.
> STARLINK-3200 holds 547 km flat for months then breaks into a controlled deorbit on July 2,
> caught from free public data. Good for the "show, don't tell" replies (Kelso, Moriba, Linares)
> where a plain before/after picture lands faster than the 85% number alone.

---

## 1 — Patrick Miga, Advanced Space (fallback from Brian Williams bounce) · patrick.miga@advancedspace.com

**Subject:** your low-latency maneuver paper — something I stumbled into

Patrick,

Your AMOS paper on low-latency detection pipelines has been open in a tab for a week. I'm
working a nearby corner of it, but from free catalog data only — no sensor feed of my own.
The thing that surprised me: rank Starlink by how far the catalog drifts from the operator's
published orbit and you get thousands of "maneuvers," but 85% of them evaporate once you
correct for how stale the entry is. Old data, not a burn.

Ten minutes to poke holes in it? I've got a clean before/after picture of one Starlink
actually deorbiting that I can send too. I'd rather be corrected than keep guessing solo.

Zayah Nelson
425-409-8684

---

## 2 — Dr. Richard Linares, MIT ARCLab (runs SPLID, the pattern-of-life dataset) · linaresr@mit.edu

**Subject:** using SPLID as an answer key — and one thing it surfaced

Prof. Linares,

I've been leaning on your SPLID devkit as ground truth while building a maneuver detector
that runs on free public catalog data. Something fell out of it that might actually matter
to the dataset itself. When I rank Starlink by catalog-versus-operator disagreement, it looks
like thousands of maneuvers. Then I account for how old each catalog entry is, and 85% of
them disappear. They were never movement — just stale elements.

I've got it down to one page, plus a picture of STARLINK-3200 breaking into a real deorbit
that I caught the same way. Fifteen minutes to tell me whether I'm fooling myself?

Zayah Nelson
425-409-8684

---

## 3 — Digantara founders (they wrote the AMOS "Maneuver Pattern of Life Violations" paper) · via digantara.co.in/contact

**Subject:** your pattern-of-life-violation paper, from a cheaper angle

Hi,

Read the AMOS paper on unsupervised detection of pattern-of-life violations — good work. I'm
chasing the same problem but with almost no budget: public catalog data, nothing proprietary.
What I keep running into is that most of the catalog-versus-operator disagreement isn't a
maneuver at all. It's just stale data. 85% of my Starlink candidates fold once I control for
how old each entry is.

Could one of you spare a short call? I want to show you the output and hear where it breaks
against what you've already built. I have a deorbit example that lands the point fast.

Zayah Nelson
425-409-8684

---

## 4 — Kratos (authors of the passive-RF pattern-of-life AMOS paper) · via kratosdefense.com/contact-us

**Subject:** pattern-of-life, but from the orbit catalog instead of RF

Hi,

Your AMOS paper on passive-RF pattern-of-life detection got me thinking. I'm building the
same behavior-baseline idea off a totally different and free input: the public orbit catalog.
It's producing real signal — 541 genuine maneuver suspects out of 10,780 Starlink satellites,
once I strip out the ones that only look like they moved because their catalog entry is old.

Could I get 15 minutes with whoever owns this on your side? Mostly I want to know whether it
overlaps your RF approach or covers a blind spot in it. I can bring a worked example.

Zayah Nelson
425-409-8684

---

## 5 — LeoLabs engineering/data team (radar SSA network — data partner angle, not rival) · via leolabs.space/contact

**Subject:** a free-data pre-filter that might feed your radar, not fight it

Hi,

Quick one from someone with no hardware. I built a maneuver detector on free public catalog
data alone, and the main thing it taught me is that most apparent maneuvers in that data are
just stale catalog entries — 85% of them in a Starlink run. That makes it a cheap first pass
that could sit in front of radar tracking like yours rather than compete with it.

Would someone spend 10 minutes on the output and tell me straight whether it's useful or
already handled inside LeoLabs? Happy to send a picture of one real deorbit it caught.

Zayah Nelson
425-409-8684

---

## 6 — COMSPOC (astrodynamics software house, sells to operators) · via comspoc.com/contact

**Subject:** a filter your operator customers might actually want

Hi,

I'm an ML engineer near Seattle. Built a maneuver detector on free public catalog data and
measured something that surprised me: most objects that look like they moved are just running
on a stale element set. 85% of my Starlink candidates vanish once I correct for the age of
the catalog entry.

Your customers are the people watching for the real burns, so you'd know fast whether this is
old news or a genuine gap. Fifteen minutes to look and tell me which? I can attach a clean
before/after of one Starlink deorbit I caught this way.

Zayah Nelson
425-409-8684

---

## 7 — Vyoma (European SSA startup, peer stage) · via vyoma.space/contact

**Subject:** peer to peer — a free-data finding I want a sanity check on

Hi,

We're roughly at the same stage, so I'll just say it plainly. I'm doing maneuver and
pattern-of-life detection from free catalog data — no radar, no telescopes. The finding I
can't stop thinking about is that most catalog-versus-operator disagreement is stale data,
not real movement. 85% in my Starlink test. A team like yours would know instantly whether
that's obvious internally or genuinely new.

Anyone up for a short call where I show the output and you tell me if I'm kidding myself? Not
selling anything, just want eyes from people who do this every day.

Zayah Nelson
425-409-8684

---

## 8 — Neuraspace (European collision-avoidance SaaS, peer) · via neuraspace.com/contact

**Subject:** would value your read on a free-data pre-filter

Hi,

Maneuver detection out of free public catalog data, no proprietary feeds — that's what I've
been heads-down on. The headline so far: rank objects by catalog-versus-operator disagreement
and you'd swear there were thousands of maneuvers. Control for catalog age and 85% of them are
just stale data. Not burns.

Your product sits right next to the conjunction and maneuver question, so your read carries
weight with me. Fifteen minutes to look at what I've got and tell me if it's useful or already
old news? I can send a real deorbit example along with it.

Zayah Nelson
425-409-8684

---

## 9 — Digantara or Vyoma's AMOS speaker contact — placeholder for whoever answers first / Scout Space · via scout.space/contact

**Subject:** in-space sensing team — a free-data companion finding

Hi,

I'm building maneuver detection purely from free public catalog data, and think it could be
a useful cheap companion to whatever your in-space sensors are catching directly — mainly as
a first-pass filter, since 85% of what looks like "movement" in raw catalog data turns out to
just be stale entries, not real maneuvers.

Would someone be willing to take a quick look at what I've built and tell me if it's a blind
spot worth filling, or something you've already solved? 15 minutes, happy to work around you.

Thanks,
Zayah Nelson
425-409-8684

---

## 10 — Aerospace Corporation (Seattle-area presence, bench name from research doc) · via aerospace.org/contact-us

**Subject:** local ML engineer, one finding to show you

Hi,

I'm near Seattle, building a maneuver detector from free public catalog data — no proprietary
sensors. Main result so far: most objects that look like they maneuvered are actually just
running on stale element sets; only 5% hold up as real suspects once you correct for that
(541 out of 10,780 Starlink satellites).

Is there someone on a tracking or space-object-behavior team who'd be willing to look at 10-15
minutes of my output and tell me honestly whether it's useful or redundant? I'd rather find
out now.

Thanks,
Zayah Nelson
425-409-8684

---

## 11 — RBC Signals (Seattle, ground-station data company — bench name from research doc) · via rbcsignals.com/contact

**Subject:** neighbor with a free-data finding on satellite behavior

Hi,

I'm just up the road near Snohomish, an ML engineer building a maneuver detector using only
free public catalog data. Since you handle ground-station data for a lot of operators, I'd
guess you have a good read on how often "did it maneuver?" actually comes up as a real
question versus noise.

Would someone there be willing to look at 10 minutes of what I've got (the short version:
85% of apparent maneuvers in raw catalog data are just stale entries) and tell me if it's
worth anything to people you work with?

Thanks,
Zayah Nelson
425-409-8684

---

## 12 — Stoke Space (Kent, WA — bench name, launch provider, may know downstream operators) · via stokespace.com/contact

**Subject:** local question about what happens after you deliver a satellite to orbit

Hi,

I'm a fellow Kent/Snohomish-area space person building a maneuver-detection tool from free
public catalog data. I don't expect this is your problem directly, but you talk to a lot of
operators right after they reach orbit — would you be willing to point me at one or two people
who deal with tracking/conjunction headaches once a satellite is flying? Even a name would
help.

If useful, I'd also be glad to show whoever that is what I've already built — 15 minutes,
no pitch.

Thanks,
Zayah Nelson
425-409-8684

---

## Channel check — done 2026-07-21, every route tested

Ran `06 Code/contact_check.py --batch2` (HTTP status on every form URL, MX lookup on every
mail domain) then `06 Code/contact_find.py` to hunt the real door where the first one 404'd.
Full table: `06 Code/contact_check.csv`. Result: **8 of 12 now have a direct email address,
up from 2. All 12 are reachable. 6 of the 12 URLs in the draft above were dead.**

| # | Target | Use this | Evidence |
|---|--------|----------|----------|
| 1 | Advanced Space — Miga | `patrick.miga@advancedspace.com` | MX live; confirmed in batch 1 |
| 2 | MIT — Linares | `linaresr@mit.edu` | **verified** — MIT AeroAstro directory, office 37-327, 617-258-6738 |
| 3 | Digantara | `info@digantara.co.in` | `/contact` is **404**; info@ published on site, MX live |
| 4 | Kratos | https://www.kratosdefense.com/contact | form live (200) |
| 5 | LeoLabs | `sales@leolabs.space` | no contact page at all; sales@ on homepage, MX live |
| 6 | COMSPOC | `info@comspoc.com` + https://comspoc.com/contact-us | `/contact` 404, `/contact-us` is the live one |
| 7 | Vyoma | `contact@vyoma.space` | `/contact` **404**; contact@ on homepage |
| 8 | Neuraspace | `info@neuraspace.com` + https://www.neuraspace.com/contact | both live |
| 9 | Scout Space | https://www.scout.space/contact | form live, no public email |
| 10 | Aerospace Corp | https://aerospace.org/contact-us | **403 to any script** (WAF) — open in a browser by hand |
| 11 | RBC Signals | https://rbcsignals.com/contact/ | **403 to any script** — browser only. Phone 425-201-5629 |
| 12 | Stoke Space | `info@stokespace.com` + https://www.stokespace.com/contact/ | both live; media@ and careers@ also published |

### What this changes about sending
- Eight of these can go out as **real email**, not a form — which means they can be drafted,
  logged and sent by `outreach.py` instead of typed into a web form by hand.
- Two (Aerospace Corp, RBC Signals) will **never** work from a script. Their front door blocks
  automated requests. Those two are manual, in a browser, on purpose.
- The role addresses (`info@`, `contact@`, `sales@`) are front desks, not people. Still worth
  sending — but a named human found via a team page, paper author line, or conference speaker
  list beats them every time. **Never LinkedIn.**
