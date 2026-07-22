---
date: 2026-07-22
type: reply-watch
status: standing by — 8 emails out (02:15–02:37 Jul 22) + Heldreth pending; answer within the hour when one lands
parent: "[[Guide - Handling Replies]]"
---

# ⚡ Reply Watch — everyone contacted in the last 24h

> Per [[Guide - Handling Replies]]: reply inside the hour, aim every exchange at a 15–20 min
> call, offer 2–3 concrete times. These are pre-written *skeletons* — swap the bracketed
> slots with whatever they actually said before sending. **Never send one unedited**: a reply
> that ignores their words is worse than a slow reply.

> [!warning] The number changed — use the new wording
> Earlier drafts of this page quoted **"11.3× more movement than controls."** That number was
> true on one snapshot at one cut and moved to 23.8× six hours later — medians of a
> heavy-tailed quantity do that. [[RESULTS - Checked Against History]] retires it from
> anything customer-facing. **Say this instead:**
>
> *"About two-thirds of my top candidates show independent movement in the catalog's own
> history, against a ~10% base rate for matched controls — and the full flagged list, all
> ~490 objects, still verifies at nearly 4× the control rate."*
>
> Add the caveat in the same breath, every time: **two of my own methods agreeing, not
> operator ground truth.**

## 1 — Melissa Heldreth, Gallagher (highest stakes, not yet contacted)

Draft sits at `06 Code/drafts/23.txt`; row 23 is on **hold** so nothing sends automatically.
She is a **broker** — she doesn't buy, she introduces. Every reply aims at *one more name*,
not a sale. Leave-behind for any meeting: [[Leave-Behind - Heldreth (one page)]].

**If she answers the question (what underwriters actually get told):**

> That's the piece I couldn't see from outside — thank you. [ONE sentence reacting to what
> she actually said. If she says nobody prices on behavior, that isn't bad news and you should
> say so: it means the gap is real, and the question becomes who moves first.]
>
> Rather than pitch you anything, here's the offer: name me a fleet — ideally GEO, 10–40
> satellites, insured by someone you place with — and I'll watch it for 60 days and send you a
> plain-English report once a month. No invoice, no contract, and nothing needed from you or
> the operator; all the data is public. If it's useless you say so and we stop.
>
> Coffee anywhere between Seattle and Snohomish, or 15 minutes on the phone — [DAY] at [TIME]
> or [DAY] at [TIME] Pacific, or name your own.

**If she says "send me something I can show people":** the leave-behind as a PDF, nothing else
attached. One page is the whole point — a deck would undo it.

**If she's warm but has no fleet to offer:** ask for the *next* name instead —
*"Who in this market would tell me I'm wrong fastest? I'd rather hear it early."* Underwriters
respect a broker's referral, which is the entire reason to start with her.

**If silence:** she is NOT on the drip and gets no machine nudge. One hand-written bump after
5 business days, then leave it — a Seattle event is the better second try.

## 2 — Patrick Miga, Advanced Space (likeliest replier — a peer who wrote the adjacent paper)

**If he engages ("interesting, tell me more" / pokes a hole):**

> Thanks for the straight answer — exactly what I was after. [One sentence reacting to HIS
> point — if he found a flaw, concede or test it honestly. Nothing earns a second reply like
> taking the hit well.]
>
> Since I wrote you, the detector got its first check it didn't grade itself: about two-thirds
> of my top candidates show independent movement in the catalog's own altitude history against
> a ~10% base rate for matched controls, replicated on two snapshots six hours apart. The
> whole flagged list — ~490 objects, nothing cherry-picked — still runs near 4× controls. Two
> of my own methods agreeing, not ground truth, which is partly why I wanted your eyes on it.
>
> Would 15 minutes work? I'm free [DAY] at [TIME], [DAY] at [TIME], or [DAY] at [TIME]
> Pacific — or send a time and I'll make it work. I'll have the before/after deorbit picture
> and the method up on screen.

**If he says "not my area / busy":** one line — *"Understood, thanks for reading at all. If
the catalog-staleness angle ever crosses your desk, my door's open."* Then let go.

## 3 — Prof. Linares, MIT ARCLab

**If he asks for the write-up (he was promised plots + method):**

> Attached: the method on one page and the two plots — the suspects-vs-controls comparison
> and STARLINK-3200's deorbit caught from the free catalog. [ATTACH: method one-pager —
> **write it before sending, a promise was made**; output/starlink_deorbit_detected.png;
> the verify.py table.]
>
> The result I most want your read on: the large majority of raw catalog-vs-operator
> disagreement is data *age*, not movement. If that holds, detectors trained on raw
> disagreement — including anything benchmarked on SPLID with real catalog inputs — are
> partly learning latency. Am I fooling myself?
>
> 15 minutes whenever suits — [DAY]/[DAY]/[DAY] all work, or name a time.

**If a student/postdoc replies instead:** same content, warmer — they're the ones who'd
actually run our method against SPLID internals. That's a *better* outcome than a busy PI.

## 4 — The peers: Digantara, Vyoma, Neuraspace

**If any says "it's known/solved":** the honest-win reply —

> That's genuinely useful — saved me weeks of rediscovering it. Two follow-ups if you'll
> indulge me: how do you handle it — filter it upstream, or does the model absorb it? And is
> there a place the public catalog still surprises you? [Then the call ask, 2–3 times.]

**If any says "interesting, show us":** send the deorbit picture and the suspects-vs-controls
table inline, ask for 15 minutes, offer to screen-share a live run — peers respect a live run
over a PDF.

**If any treats it as a competitive probe:** say the true thing plainly — *"I'm one person
with public data and no sensors. I'm not going to out-build you; I'm trying to find out
whether the cheap layer underneath what you sell is worth anything to anyone."*

## 5 — LeoLabs (went to `sales@` — expect sales qualification, not an engineer)

They own radar. We are not a competitor and must not sound like one.

> To be clear which door I'm at: I'm not a buyer and I'm not selling you anything. I'm one
> engineer doing detection from free public data, and the honest position is that my layer is
> a **pre-filter** — it narrows ~4,900 apparent movers down to ~490 worth a real sensor look.
> That stops at the edge of what your radar does; it doesn't overlap it.
>
> If there's an astrodynamicist who'd enjoy telling me where that breaks, 15 minutes with them
> is worth more to me than a quote.

## 6 — COMSPOC (`info@` — the goal is to get out of the inbox)

Ask for the technical person by role, not by name, and make the router's job easy:

> This isn't a purchase enquiry, so it's probably the wrong inbox — apologies. Could you point
> me at whoever handles catalog data quality? My question is one line: how do your customers
> tell a genuine burn from an element set that has simply gone stale? I've measured how often
> the second gets mistaken for the first, and I'd like to know whether that matches what you
> see.

## 7 — Stoke Space (referral ask — different goal: a NAME, not a call)

**If they name someone:**

> Thank you — exactly what I hoped for. I'll write [NAME] directly and keep it short. If it
> ever runs the other way and someone asks you about tracking after deployment, happy to be
> the person you point at.

Then a fresh CSV row for the referred person, `why_them: "referred by Stoke Space"` — a warm
referral outranks every cold row in the queue. **Write to them the same day.**

## 8 — Role-inbox routing successes (COMSPOC / LeoLabs / Kratos forms)

If a real engineer surfaces from a forwarded role-inbox email, they chose to pick it up —
treat as warm as a direct reply. Log who they are and their title in the CSV notes first,
then reply within the hour.

## The log

Every reply → the table in [[Guide - Handling Replies]] + `--replied <id> --note "..."` so
the ledger knows. The scoreboard metric is unchanged: pain described unprompted, and
"can I try it?"
