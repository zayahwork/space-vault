---
date: 2026-07-22
type: contact-source
status: 42 papers mined, ~130 addresses; 6 curated contract drafts written, all on hold
parent: "[[Contract Work - Space ML Subcontract]]"
---

# 📇 ESA SDC7 + SDC8 — the contract bench

Same method as [[ESA SDC9 - Paper Author Contacts]], two older conferences and a wider keyword
list (*manoeuvre, maneuver, pattern of life, machine learning, anomaly, catalogue, conjunction,
two-line, space traffic, neural*). **57 papers matched, 42 printed at least one address** —
roughly 130 in total.

## The six worth writing for contract work

Each has a **curated draft already written** — every one opens on their specific paper, because
a contract pitch that could have been sent to anyone gets deleted by everyone.

| # | Who | Their paper | The hook | Draft |
|---|---|---|---|---|
| **59** | **Jonas Radtke** — OKAPI:Orbits | *Impact of Collision Avoidance Manoeuvres on Large Satellite Constellations* (SDC8) | They sell CA screening as a service. If a screening pipeline treats catalog disagreement as movement, part of what it reacts to is data age — that's our measurement landing on their product | `drafts/59.txt` |
| **60** | **Emma Kerr** — Deimos Space | *State of the Art and Future Needs in Conjunction Analysis* + *Light Curves for GEO Characterisation* (SDC8) | She literally wrote the future-needs paper, so "is this gap still a gap?" is a question she'd enjoy. The GEO work also feeds our insurer story | `drafts/60.txt` |
| **61** | **Keiran McNally** — GMV NSL | *AI for Space Resident Object Characterisation with Lightcurves* (SDC8) | **Strongest contract target.** That paper carries contributors from outside GMV NSL — proof this team already brings in outside help for AI work | `drafts/61.txt` |
| **62** | **Islam Hussein** — Applied Defense Solutions | *Geometric restructurisation of the space object tracking problem* (SDC7, with Moriba Jah) | Closest US company to our method, and honest about uncertainty rather than confident | `drafts/62.txt` |
| **63** | **Agnieszka Sybilska** — Sybilla Technologies | *WebPlan — web-based sensor scheduling* (SDC8) | Our ranked list is literally a scheduling prior: "which objects deserve a sensor tonight" | `drafts/63.txt` |
| **64** | **Duncan Smith** — Beechleaf Consulting | co-author on the GMV NSL paper above | **Not a client.** An independent consultant already doing what Zayah wants to do. The email asks how he built it and offers nothing — no pitch | `drafts/64.txt` |

> [!warning] Rows 59–64 are `hold`, and the note on the Hussein draft
> All six are hand-sends. The drip cannot touch a `hold` row — verified.
>
> The Hussein draft originally carried an optional line mentioning that Moriba Jah has answered
> our questions. **I removed it.** Jah is a co-author on that paper and a live thread of ours;
> implying a warmth or endorsement he hasn't given is exactly the move that costs both
> relationships. If the founder judges it fair to mention, that's his call to add, not a
> default in a draft.

## The bench — everything else worth keeping

**Big institutional clusters** (product outreach, not contract):

- **Aerospace Corporation — 6 named addresses** on one paper (Sorge, Henning, Peterson, Jenkin,
  McVey, Mains, all `first.last@aero.org`). **This unblocks CSV row #50**, which has been stuck
  on "403 to script, browser-only form" since batch 2. We now have real humans there.
- **ESA — 11 addresses**, including `Jan.Siminski@esa.int` (confirms SDC9) and
  `Tim.Flohrer@esa.int`, who heads the Space Debris Office.
- **GMV — 12 more** `@gmv.com` addresses beyond the SDC9 haul; **AIUB Bern** (Schildknecht —
  *Using Conjunction Analysis Methods for Manoeuvre Detection*, directly our problem);
  **DLR** (Bergmann — *Integrated manoeuvre detection and estimation*).

**Smaller commercial shops worth a second pass:** Capgemini (catalogue analysis), D-Orbit,
Space Insight (UK), CT Ingénierie, Deimos `spacesafety@` shared inbox.

## What this pass cost and what it's worth

About forty minutes, mostly waiting on downloads. It produced more verified, published,
opt-in-by-authorship addresses than every other method we've tried combined — and unlike
scraped data, every one of them was printed by the person themselves on a document they chose
to publish.

## SDC6 + the rest of SDC9 — done 22 Jul

**21 more papers with addresses, ~50 more contacts.**

> [!note] Method gotcha, worth remembering
> The keyword filter returns **nothing** for SDC6 — old conferences have no keyword metadata,
> so the search silently finds zero and looks like an empty result rather than a broken query.
> The way in is the **conference filter** (`?conference=7` is the 6th European Conference),
> then filter titles yourself: 198 papers listed, 23 relevant, 21 of those printed addresses.
> Re-running the full ten keywords against SDC9 also found **13 papers the first five missed**.

**New targets queued (rows 65–68):**

| # | Who | Their work | Why | Status |
|---|---|---|---|---|
| **65** | **Kaarel Hanson** — Guardtime | *Space Traffic Coordination Monitor*, with ESA | A coordination monitor has to answer "did the object actually do what it said?" — independent, permissionless verification is the half we produce | `hold`, draft `65.txt` |
| **66** | **Daniel Novak** — CGI | Web-based engineering solution supporting conjunction analysis (SDC6) | CGI builds the tooling under other people's space-safety work, and consultancies carry work that outlasts their headcount | `hold`, draft `66.txt` |
| **67** | **Klaus Merz** — ESA Space Debris Office | Geometric conjunction filters | With **Tim Flohrer** (heads the office) and **Jan Siminski**, that's the institutional trio. One shot each, hand-written only | `hold` |
| **68** | **Thomas Schildknecht** — AIUB Bern | *Using Conjunction Analysis Methods for Manoeuvre Detection* | Our exact problem from the observatory side | `todo` — placeholder guard blocks it until the paper is read |

**Also on the bench, not queued:** Thomas Kelecy (Boeing, long-time SSA researcher), Thales
Alenia Space, QinetiQ Belgium, Schafer, RAND Europe (cislunar weak signals — interesting for
the *who-else-pays* thinking rather than outreach), plus ten more `@gmv.com` and nine more
`@esa.int`.

**Data hygiene:** one extracted address came out as `.rfernandez@upm.es` — a leading dot from
the PDF's text layer. Anything harvested this way needs an eyeball before it's used; the
extractor is good, not perfect.

**Still unmined:** SDC5 and earlier (1993–2009 — old enough that addresses will have rotted),
the NEO/Debris Detection conferences, and the Collision Avoidance Competition Workshop, which
is small but exactly our topic.
