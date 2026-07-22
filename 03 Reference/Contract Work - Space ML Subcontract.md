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

### Leads found — 22 Jul 2026

> [!danger] Privateer is **not** clean — removed from this list
> **Moriba Jah is Privateer's co-founder and Chief Scientist**, and he has a **live reply
> thread** with us ([[Guide - Moriba Jah Call]]). A contract pitch into that company right now
> lands next to a conversation that is already working. Rule 3 applies: **wait.** If the call
> happens and goes well, "are you ever short an ML pair of hands?" is a question you ask a
> person who already likes you — not a cold email.

| Who | Company | Why them | Address |
|---|---|---|---|
| **Adrian Thompson** — Chief of AI & Data Science | Slingshot Aerospace | Best fit on the list. Hired Nov 2025 out of Waymo/TuSimple to own AI across their products — a new AI chief has a backlog and no team yet | ❌ none published; two scraper sites disagree on the domain (`slingshot.space` vs `slingshotaerospace.com`), so **don't guess** — route via the site contact form and ask for him by name |
| **Douglas Hendrix** — CEO & co-founder | ExoAnalytic Solutions | Optical telescope network at scale: enormous data, and their leadership page lists no ML title anywhere | ✅ **`hendrix@exoanalytic.com`** — printed on their own ESA space-debris conference paper. `info@exoanalytic.com` is the published fallback |
| **William Therien** — CTO · **Ben Lane** — VP Engineering | ExoAnalytic Solutions | The two who'd actually own the work | ❌ no address. Only one sample of their convention (`lastname@`), which isn't enough to infer from |
| **Jeff Aristoff** — VP, Space Systems · **Joshua Horwood** · **Navraj Singh** | Numerica | Publishes the exact work we do — tracking algorithms, uncertainty, automated indications & warning. They'd understand the portfolio in one read | ⚠️ convention appears to be `First.Last@numerica.us` (e.g. `jeff.aristoff@numerica.us`) but the source PDF rate-limited twice — **verify before sending** |
| **Nicholas Liapis** — CTO | Katalyst Space | Small, fast, Flagstaff AZ | ❌ none published |
| **Chad Fish** — VP Strategy & CTO · **Geoff Crowley** — CEO | Orion Space Solutions (now under Arcfield) | ~76 people, R&D shop that subcontracts routinely | ❌ none published; a scraper claims `FLast@astraspace.net` (their old ASTRA domain) — unverified, don't use |

**Read on the whole set:** only one address is send-ready. That's normal for engineering leads —
unlike insurance, this industry publishes papers, not staff directories. Which points at the
better route below.

### The better route for four of these: the paper, not the person

Numerica, ExoAnalytic and Slingshot all publish at **AMOS** every year, and AMOS papers print
author emails. We already mine papers for contacts ([[Guide - Competitor Papers]]). One pass
through the last two years of AMOS papers from these three companies would likely produce
several *working engineer* addresses — better targets than a CTO, because the engineer knows
exactly what's stuck and has a manager who'd rather buy hours than wait for a req to close.

Worth an hour, and it doubles as product research. **Ran it — see below.**

### The AMOS pass — ran it 22 Jul, and the idea was wrong

Pulled the 2023 and 2024 AMOS technical-paper listings, found every paper from our three
target companies, downloaded **22 PDFs**, and extracted the text of each front page.

**Result: zero email addresses. AMOS papers don't print them.** Different venues have
different house style, and AMOS puts a copyright line where other conferences put author
contacts. The hypothesis was reasonable and it is dead — recording it here so nobody spends
the hour again.

Two things worth having came out of it anyway.

**1. The Slingshot bench, by name and by paper.** These people work on exactly our problem:

| Paper (AMOS 2024) | Authors, all Slingshot Aerospace |
|---|---|
| *Action-Free Inverse Reinforcement Learning for Evaluating Satellite Similarity and **Anomaly Detection*** | D. Witman, T. Olson, B. Williams, D. Kesler, B. Marchand |
| *Contextual Predictive Model for Early Identification of High-Covariance Conjunctions* | **T. Olson**, C. Reid, J. Stauch, C. Grey, D. Kesler, B. Marchand |

**Timothy Olson is the target.** Lead author on one, co-author on the other — anomaly detection
*and* conjunction prediction, which is our exact overlap. Better than writing the Chief of AI:
Olson is the person whose backlog the contract hours would actually clear.

Revised route for Slingshot: their contact form, asking for **Tim Olson by name and citing the
paper**. A form message that names a specific engineer and a specific paper doesn't read as
spam, and it gets forwarded.

**2. Two companies we didn't know were in this business:**

- **Auria** — *Machine Learning for Space Domain Awareness Sensor Scheduling* (Dhingra, DeJac,
  McGuire, AMOS 2024). Doing ML for SDA in production.
- **Data Fusion & Neural Networks, LLC** (Carlsbad CA) — *Neural Network Enhanced Numerical
  Propagation*, by **Duane DeSieno, CTO**. A tiny company whose CTO writes the papers is
  exactly the shape that subcontracts.

> [!note] Correction to the target table above
> The listing-page scrape mis-attributed several papers to Numerica by proximity. Checked
> against the PDFs themselves: Dhingra is **Auria**, Vanslette is **RTX BBN**, DeSieno is
> **Data Fusion & Neural Networks**, Shepperd is **Iridium**, Magnus is **Office of Space
> Commerce**. Numerica had no matching AMOS 2024 paper. The Numerica names in the table above
> came from their own earlier papers and still stand.

### Where author emails *are* printed: ESA, not AMOS

`hendrix@exoanalytic.com` came off an **ESA Space Debris Conference** paper, and that venue
prints author contacts as house style. **SDC9 (Bonn, April 2025)** proceedings are public at
`conference.sdo.esoc.esa.int/proceedings/sdc9/`. Same method, better-chosen venue — that is the
next hour to spend, and it applies to product outreach as much as contract work.

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
