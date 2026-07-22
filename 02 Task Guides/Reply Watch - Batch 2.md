---
date: 2026-07-22
type: reply-watch
status: standing by — 8 emails out (02:15–02:30 Jul 22), answer within the hour when one lands
parent: "[[Guide - Handling Replies]]"
---

# ⚡ Reply Watch — batch 2 (drafts ready to fire)

> Per [[Guide - Handling Replies]]: reply inside the hour, aim every exchange at a 15–20 min
> call, offer 2–3 concrete times. These are pre-written *skeletons* — swap the bracketed
> slots with whatever they actually said before sending. **Never send one unedited**: a reply
> that ignores their words is worse than a slow reply.
>
> New ammunition since the emails went out: the verified number. If they engage at all,
> the follow-up can say *"since writing you I've also verified it against 30 days of
> altitude history with a matched control group — suspects move 11.3× more than controls,
> 72% vs 11% clear the burn bar. Two of my own methods agreeing, not ground truth."*

## 1 — Patrick Miga, Advanced Space (likeliest replier — a peer who wrote the adjacent paper)

**If he engages ("interesting, tell me more" / pokes a hole):**

> Thanks for the straight answer — exactly what I was after. [One sentence reacting to HIS
> point — if he found a flaw, concede or test it honestly. Nothing earns a second reply like
> taking the hit well.]
>
> Since I wrote you, the detector got its first independent check: against 30 days of altitude
> history with a matched control group, flagged satellites move 11.3× more than the ones it
> calls ordinary, and 72% clear a burn bar only 11% of controls clear. Two of my own methods
> agreeing — not ground truth, which is partly why I wanted your eyes on it.
>
> Would a 15-minute call work? I'm free [DAY] at [TIME], [DAY] at [TIME], or [DAY] at [TIME]
> Pacific — or send a time and I'll make it work. I'll have the before/after deorbit picture
> and the method up on screen.

**If he says "not my area / busy":** one line — *"Understood, thanks for reading at all. If
the catalog-staleness angle ever crosses your desk, my door's open."* Then let go.

## 2 — Prof. Linares, MIT ARCLab

**If he asks for the write-up (he was promised plots + method):**

> Attached: the method on one page and the two plots — the suspects-vs-controls comparison
> and STARLINK-3200's deorbit caught from the free catalog. [ATTACH: method one-pager —
> **write it before sending, promise was made**; output/starlink_deorbit_detected.png;
> the verify.py table.]
>
> The result I most want your read on: 85% of raw catalog-vs-operator disagreement is data
> age, not movement. If that holds, detectors trained on raw disagreement — including anything
> benchmarked on SPLID with real catalog inputs — are partly learning latency. Am I fooling
> myself?
>
> 15 minutes whenever suits — [DAY]/[DAY]/[DAY] all work, or name a time.

**If a student/postdoc replies instead:** same content, warmer — they're the ones who'd
actually run our method against SPLID internals. That's a *better* outcome than a busy PI.

## 3 — The peers (Vyoma / Neuraspace / Digantara)

**If any says "it's known/solved":** the honest-win reply —

> That's genuinely useful — saved me weeks of rediscovering it. Two follow-ups if you'll
> indulge me: how do you handle it (filter upstream, or does the model absorb it)? And is
> there a place the public catalog still surprises you? [Then the call ask, 2–3 times.]

**If any says "interesting, show us":** send the deorbit picture + the 11.3× table inline,
ask for 15 minutes, offer to screen-share the run live — peers respect a live run over a PDF.

## 4 — Stoke Space (referral ask — different goal: a NAME, not a call)

**If they name someone:**

> Thank you — exactly what I hoped for. I'll write [NAME] directly and keep it short. If it
> ever runs the other way and someone asks you about tracking after deployment, happy to be
> the person you point at.

Then a fresh CSV row for the referred person, `why_them: "referred by Stoke Space"` — a warm
referral outranks every cold row in the queue. **Write to them the same day.**

## 5 — Role-inbox routing successes (COMSPOC / LeoLabs / Kratos forms)

If a real engineer surfaces from a forwarded role-inbox email, they chose to pick it up —
treat as warm as a direct reply. Log who they are and their title in the CSV notes first,
then reply within the hour.

## The log

Every reply → the table in [[Guide - Handling Replies]] + `--replied <id> --note "..."` so
the ledger knows. The scoreboard metric is unchanged: pain described unprompted, and
"can I try it?"
