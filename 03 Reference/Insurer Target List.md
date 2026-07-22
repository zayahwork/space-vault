---
date: 2026-07-22
type: research
status: ADDRESSES FOUND 2026-07-22 — parked on `hold`, nothing sends automatically
parent: "[[Guide - Insurer Probe]]"
---

# 🛡️ Insurer Target List — who actually underwrites satellites

> [!warning] No sending
> [[Guide - Insurer Probe]] is a later move. This market is tiny — a few dozen people
> worldwide make the underwriting decisions — so every first conversation counts and none
> get spent on a cold template. This page turns "a handful of Lloyd's syndicates and
> specialists" into names. That's all it does.

## The one to meet first — she's in Seattle

**Melissa Heldreth** — Director, US Space Practice, **Gallagher** (broker). Hired Dec 2025
from Baldwin (led their aerospace & tech division). **Based in Seattle.** New in a role
she's building out, which means she's *looking* for reasons to talk to local space people.
A broker, not an underwriter — she sits between operators and capacity, so one good
conversation maps the whole market. Coffee-distance from Snohomish.

## Underwriters (the people who price the risk)

| Who | What | Why they matter | Signal on in-orbit data |
|---|---|---|---|
| **AXA XL — Chris Kunstadter**, Global Head of Space | Market leader by capacity; teams in London/Paris/NY | The most public-facing person in space insurance; NASA/ESA talks, SSPI podcast; sits on the Office of Space Commerce ACES advisory committee | **Partnered with SpaceAble (2021)** specifically for LEO SSA data to support underwriting — proof the market buys behavior data |
| **Atrium — David Wade**, space underwriter (+ Lee Davis, Brian Spark) | Runs the **Atrium Space Insurance Consortium (ASIC)**: 8 Lloyd's syndicates, launch + in-orbit | 30 yrs in the sector; ASIC is the classic Lloyd's specialist route; publishes on space risk | Known for engineering-level risk assessment — the kind of desk that would actually read our method |
| **Llift Space** (Brit + Hiscox MGA, consortium of 18 syndicates) | $25M capacity per risk, new-space focused | The other Lloyd's aggregation point; built for smallsat/new-space risks — our exact segment's insurers | Consortium model = one conversation reaches 18 syndicates |
| **Munich Re** | One of the few large reinsurers still in space | Survived the loss years that pushed AIG/Swiss Re/Allianz out; publishes on satellite insurance solutions | Still-standing = pricing discipline; would value better loss-discrimination data |
| **Global Aerospace** | Specialty aviation/space underwriter | Already row #25 in our CSV | — |
| **Chubb, Beazley, Hiscox** (direct) | Specialty/secondary capacity | Beazley already row #28 | — |

**Market exits worth knowing:** Swiss Re, Allianz (AGCS), AIG, and Brit have reduced or
exited *direct* space underwriting after consecutive loss years. The market concentrated
into Lloyd's syndicates + Munich Re + specialists. → Our CSV rows for Allianz (#27) target
a shrinking desk; deprioritize.

## Brokers (the people who see every deal)

| Who | Why |
|---|---|
| **Gallagher — Melissa Heldreth** (Seattle) | See above. Also publishes *Plane Talking*, the market's clearest public report |
| **Marsh** (space practice, since 1977) | Intermediates the majority of large satellite/launch placements with WTW |
| **Willis Towers Watson** | The other half of that majority |
| **Aon** | Third major intermediary |
| **Lockton** (row #24) | Independent broker with space desk |
| **Assurspace, Argo** | Boutiques competing for mid-market/new-space mandates — closer to our customer size |

## Why this market should care about our wedge (their own words)

- Analysts: insurers that incorporate **real-time SSA data feeds and ML-based anomaly
  detection** into constellation risk frameworks "will be well positioned to win mandates."
- Policy language now emerging: premiums linked to **maneuver frequency** (e.g. >5 avoidance
  actions/year), STM-compliance clauses, EOL disposal requirements. Every one of those
  clauses needs a way to *verify behavior* — which is precisely what we measure from free data.
- In-orbit is the **fastest-growing segment** (~11% CAGR projected), concentrated at ~550 km —
  the Starlink shell where our 11.3× result lives.
- AXA XL already paid for this category once (SpaceAble). Precedent, not speculation.

## Addresses — found 2026-07-22

Every one of these came from a document the company itself published. None came from a
scraper site (ZoomInfo/RocketReach mask the address and charge for the rest anyway). All
domains have live MX.

| Who | Address | How we know |
|---|---|---|
| **Chris Kunstadter** — Global Head of Space, AXA XL | `chris.kunstadter@axaxl.com` | ✅ **Verified** — printed in his own slide decks, twice: the NASA SCAF space-insurance update and the ESA/indico version |
| **David Wade** — Space Underwriter, Atrium/ASIC | `David.wade@atrium-uw.com` | ✅ **Verified** — published on Atrium's own space page, with +44 207 050 3000 |
| **Lee Davis** — Deputy Space Underwriter, ASIC | `Lee.davis@atrium-uw.com` | ✅ **Verified** — same page. The backup if Wade goes quiet |
| **Denis Bensoussan** — Head of Space, Beazley | `denis.bensoussan@beazley.com` | ✅ **Verified** — Beazley's own people page, with +44 20 7674 7844 |
| **Melissa Heldreth** — Director US Space Practice, Gallagher | `Melissa_Heldreth@ajg.com` | ⚠️ **Inferred** — Gallagher's own *Plane Talking* PDF prints five US staff as `First_Last@ajg.com` (Adam_Sullivan, Steve_Lloyd, Grant_S_Robinson…), and the same names appear on the current team page. Her address is not published anywhere; the pattern is |

**Still no address, and why:**

- **Marsh** — found the human: **Patton Kline**, US Aviation & Space Practice Leader, New York.
  Marsh publishes no addresses at all; convention unconfirmed. Old CSV route was a 404, fixed.
- **Munich Re** — page 403s a script and names nobody. Still one of the few big reinsurers in
  space. This one is a phone call, not an email.
- **Global Aerospace** — only `beaproducer@`, which is broker recruitment, i.e. the wrong door.
  Underwriting line: +1 888-228-0001.
- **WTW / Lockton** — nothing published; both sit behind Gallagher and Marsh in priority anyway.
- **Allianz** — marked **dead** in the CSV. They've pulled back from direct space underwriting;
  a shrinking desk isn't worth an email.
- **Llift Space** (the 18-syndicate NewSpace consortium) — humans identified, **Gary Brice**
  (Brit, Head of Marine & Space) and **Pascal Lecointe** (Hiscox, Space Line Underwriter). No
  addresses yet. Worth another pass: 18 syndicates through one conversation, aimed at exactly
  our size of customer.

## How this updates the CSV (rows 21–28, 53)

- Rows 21 (AXA XL), 23 (Gallagher), 28 (Beazley) and new row 53 (Atrium/ASIC) now carry a real
  address and are set to **`hold`** — *not* `todo`.
- **`hold` is deliberate.** The drip only picks up `todo`/`drafted`, so parking them means the
  automatic sender cannot reach them. Four named humans in a market of a few dozen decision
  makers is exactly the list you do not want a segment template landing on. They get written by
  hand, one at a time, or not at all.
- **Order when the probe opens**: Heldreth (local, new in role, broker view of everything) →
  Kunstadter (already paid for this data category once) → Wade/ASIC (technical desk, 8
  syndicates) → Bensoussan (built a satellite book from nothing, will have opinions).

Sources: [Lloyd's — Space](https://www.lloyds.com/about-lloyds/our-market/what-we-insure/space) · [New Space Economy — orbital insurance market](https://newspaceeconomy.ca/2026/03/29/the-orbital-insurance-market-how-underwriters-are-pricing-constellation-scale-risk/) · [Atrium ASIC](https://www.atrium-uw.com/specialisms/space/asic/) · [AXA XL × SpaceAble](https://www.insurancejournal.com/news/international/2021/04/22/610964.htm) · [Kunstadter — Office of Space Commerce ACES](https://space.commerce.gov/advisory-committee-on-excellence-in-space-aces/aces-membership/christopher-kunstadter/) · [The Insurer — Heldreth appointment](https://www.theinsurer.com/ti/news/gallagher-names-baldwins-heldreth-director-of-us-space-practice-2025-12-11/) · [Gallagher aerospace](https://www.ajg.com/gallagher-specialty/industries/aerospace-aviation/) · [Marsh — Space](https://www.marsh.com/en/industries/aviation-space/expertise/space.html) · [Munich Re — space solutions](https://www.munichre.com/en/solutions/for-industry-clients/space-and-satellite-insurance-solutions.html) · [ts2 — satellite insurance boom](https://ts2.tech/en/space-at-stake-the-boom-in-satellite-insurance-risk-management-2025-2032/) · [Insurance Business — $6bn market stress test](https://www.insurancebusinessmag.com/us/news/breaking-news/the-6-billion-space-insurance-market-faces-its-biggest-stress-test-yet-578992.aspx)
