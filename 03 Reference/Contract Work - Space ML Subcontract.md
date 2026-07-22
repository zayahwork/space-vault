---
date: 2026-07-22
type: income
status: plan + drafts ready — nothing sent; these are hand-sends, not drip rows
parent: "[[Pricing - What to Charge and Who]]"
---

# 💼 Contract ML work — subcontracting to small space companies

The runway play, not the company play. Goal: **paid hours inside the same industry we're
selling to**, so the work funds the build instead of competing with it.

## Why this beats Upwork

An open **ML job req is allocated budget that somebody is failing to spend.** Small space
companies post ML roles and then wait months, because they need two rare things in one person:
machine learning *and* orbital mechanics. That pool is tiny. We are already in it — with
public evidence, which is more than a résumé.

The pitch is therefore **not** a job application. It's: *you have work queued behind a hire
that hasn't happened; I can take some of it now, by the hour, and you can stop when you like.*

## What we're actually selling

Not "ML engineer for hire" — too generic to price. Three concrete shapes:

1. **Data-quality / detection work** — the exact thing already built: catalog staleness,
   anomaly ranking, verification against controls. Portfolio exists and is public-data, so
   there's nothing proprietary blocking a demo.
2. **Pipeline plumbing** — snapshot archives, baselines, alerting that refuses to fire on a
   quiet day. Unglamorous, always needed, easy to scope.
3. **A second pair of eyes on someone's model** — "is this detector learning the signal or
   learning latency?" is a question we have already answered once, publicly and honestly.

## Rate card

| Shape | Price | When to use |
|---|---|---|
| Hourly | **$110–150/hr** | Default. The ML+orbits combination is not a $60/hr skill set |
| Scoped project | **$6–12K** for 2–4 weeks, fixed deliverable | Better for them; better for us — no timesheet arguments |
| Paid trial | **one week, scoped, ~$3K** | The de-risker. Offer it early; it converts skeptics |

Never free. The free pilot is the *product* motion ([[Leave-Behind - Heldreth (one page)]]);
mixing them teaches people our time is free.

## The proof, in one line

*"I built maneuver detection from free public tracking data and then checked it against the
catalog's own history: about two-thirds of my top candidates show independent movement against
a ~10% control base rate. The code has tests, and the tool refuses to answer when the archive
is too short."*

That last clause is the hire signal. Anyone technical reads "it refuses rather than guessing"
and knows what kind of engineer wrote it.

## Targets

> [!warning] The conflict rule — read before writing anyone
> Most good subcontract targets are **already product-outreach targets**. Two different asks
> landing on the same human makes us look confused and burns both. Rules:
> 1. **Never send both asks to the same person.** Product ask outranks; it's the bigger prize.
> 2. If the company is already in the CSV, the contract pitch goes to a **different human**
>    (engineering lead / hiring manager), never the inbox we already used.
> 3. If a product thread is *live* (they replied), the contract pitch waits. Don't muddy a
>    conversation that's working.

### Clean — no existing product thread, write these first

| Company | Why them | Route |
|---|---|---|
| **Slingshot Aerospace** | Big SSA/analytics shop, constantly hiring, ML-heavy product | careers page → find the eng lead |
| **Privateer Space** | Data-quality is literally their thesis; small team | site contact |
| **ExoAnalytic Solutions** | Optical tracking at scale — drowning in data, thin on ML | site contact |
| **Numerica** | Astrodynamics + tracking algorithms, defense-adjacent | site contact |
| **Katalyst Space** | Small, fast, servicing-focused | site contact |
| **Orion Space Solutions / SpaceNav** | Small SSA shops that subcontract routinely | site contact |

### Conflicted — a product email already went out; different human or wait

| Company | Existing thread | Handling |
|---|---|---|
| **Advanced Space** | Patrick Miga, emailed 02:15 Jul 22 — and they have an **ML Engineer req open** | Best-fit target in the whole list, worst timing. **Do not** send Miga a job pitch. If he replies warmly, the natural line is *"unrelated, but I saw you're hiring ML — is any of that contractable?"* Otherwise wait for the thread to close |
| **Kayhan Space** | Row #4, day-1, silent; nudge due Thu Jul 23 | ML is core to their collision-avoidance product. Contract pitch goes to an engineering lead, **after** the nudge resolves |
| **Scout / Aerospace Corp / RBC Signals / COMSPOC / LeoLabs / Vyoma / Neuraspace / Digantara** | Batch-2, sent Jul 22 | Product thread is 12 hours old. Leave them alone entirely for now |

## Where to send it

`careers@` and application portals are the wrong door — they route to a hiring pipeline that
is looking for a full-time employee and will discard a contractor. Aim for:

1. **The engineering lead** named in the job post, or the CTO of a <50-person company.
2. Failing that, the **general contact** with a subject line that says *contract*, so whoever
   opens it knows immediately it isn't an application.
3. Never both, never twice.

## The email

Reusable skeleton at `06 Code/drafts/contract-pitch.txt` — **not a CSV row**, because these
must never go out on the drip. Hand-sends only, one at a time, tailored per company.

## Honest risks

- **We are one person with a startup.** Some will read "contractor who'll leave the moment
  he raises money." Answer it before they ask: the work is scoped and finite, and the startup
  is why the orbital knowledge exists at all.
- **Bandwidth.** Every contract hour is an hour not spent on the wedge. Cap it — 15–20 hrs/week
  maximum, and revisit the moment a pilot converts to paid.
