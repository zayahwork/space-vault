---
title: Deep Research — Buyers, Live SBIR, Build Plan, Competitive Gap
type: research
status: complete (living doc — update as verified)
created: 2026-07-20
parent: RESEARCH_AND_OUTREACH_WEEK.md
tags: [space, ssa, research, sbir, buyers, competition, splid]
---

# Deep Research — 2026-07-20 evening pass

> Four threads, one doc. Read §2 first — it has a **date-sensitive action for tomorrow (Jul 22)**.
> Then §4, which honestly revises the wedge. §1 ranks who actually pays. §3 is the build spec.

---

## 1. WHO ACTUALLY PAYS — ranked buyer map

### The pricing anchor (real numbers, finally)
**Kayhan Space publishes its prices** (kayhan.space/products/satcat):
- **Essentials: FREE** — basic avoidance recommendations, CDM event history (2 wks), on-demand tracking.
- **Pro: $1,900/mo (≤3 sats), $2,500/mo (≤5 sats)** — autonomous traffic coordination, catalog
  screening, optimal maneuver recommendations, unlimited CDM history. ≈ **$23K–$30K/yr**.
- **Enterprise: custom** — OD, covariance realism, SME support.

**What this tells you:** (a) the *bottom* of operator decision-support is already free (consistent
with TraCSS — the floor is commoditized); (b) small operators demonstrably pay **~$25K/yr** for
tooling that tells them *what to do*, not just *that there's a risk*; (c) a solo founder doesn't
need many $10–25K customers to be alive. Seradata (Slingshot's database product) benchmarks at
**~$9.5K–$40K/yr** — same order of magnitude for "space intelligence" subscriptions.

### Ranked buyer segments

**#1 — U.S. Space Force / defense, via SBIR. (Beachhead. Start here.)**
- The demand signal is explicit and current: S4S leadership frames the **2026 mission as
  "predictive SDA"** — shifting from cataloging stable orbits to **predicting behavior** in a
  contested domain, exactly because adversary satellites now maneuver. That is your product
  described in their words.
- Money is flowing: **Andromeda** — a 10-year, **$1.8B** next-gen SDA contract vehicle with 14
  named vendors (Anduril, True Anomaly, Turion, L3Harris, Lockheed...). You won't be prime on
  that, but it proves the mission area is funded for a decade, and SBIR is the outsider's door
  into the same ecosystem.
- Why it fits you: they pay *before* the product exists (Phase I), the need (maneuver/behavior
  detection = "custody," "predictive SDA") is named, and no sensor ownership is required.

**#2 — Small/budget satellite operators. (Commercial leg of dual-use. Validate via outreach.)**
- Willingness to pay proven at ~$25K/yr (Kayhan Pro), but the free floor (TraCSS, Kayhan
  Essentials) keeps rising. Don't sell alerts. Sell the layer the frees don't do:
  **"which conjunction actually matters this week + is the other object behaving normally?"**
  — risk triage informed by the *other* object's pattern-of-life.
- Screening-cadence pain is real and documented: the authority screens every ~8 hrs and operators
  need ~16 hrs of maneuver-plan lead time. Faster/cheaper behavior context has room.
- This is exactly what the outreach calls must test. Do NOT assume it; ask.

**#3 — Space insurers / underwriters. (Sleeper wedge. Genuinely underserved. One email to test.)**
- Munich Re, Swiss Re, Lloyd's syndicates are now integrating orbital tracking + AI analytics
  into underwriting; in congested LEO, **premiums run 5–10% of total mission budget**; industry
  chatter includes insurers *requiring* operators to subscribe to a recognized collision-avoidance
  service (the "ships must carry radar" model).
- Nobody sells underwriters a cheap, standalone **behavioral risk score** for the neighborhood an
  insured asset flies in ("how often do objects near your insured sat maneuver unexpectedly?").
  They don't own sensors, don't want a $250K platform, and think in risk scores — perfect
  free-data ML customer profile.
- Action: add ONE insurance-side contact to the outreach bench (a space underwriter at a Lloyd's
  syndicate or broker like Marsh/AXA XL space practice). One conversation tells you a lot.

**#4 — Non-US / APAC operators. (Real growth, wrong first target.)**
- LEO SSA market ≈ **$667M (2025) → ~$992M (2033)**; **APAC is the fastest-growing region
  (7%+ CAGR)** with many new operators lacking in-house flight dynamics. Real, but relationship-
  and export-control-heavy for a solo Seattle founder. Revisit after a US beachhead.

**Bottom line:** SBIR/defense first (funded, named need), small-operator triage second (test in
calls), insurers as the creative differentiator (one probe email), APAC later.

---

## 2. LIVE SBIR WINDOWS — including one that opens TOMORROW

Verified on spacewerx.us/get-funded (2026-07-20):

| Solicitation                                     | Pre-release | Opens                       | Closes           |
| ------------------------------------------------ | ----------- | --------------------------- | ---------------- |
| **DOW SBIR Specific Topic 26.BX Release 4**      | Jul 1       | **Jul 22, 2026 (tomorrow)** | **Aug 18, 2026** |
| DOW SBIR Specific Topic 26.BZ Release 3          | Jun 3       | Jun 24                      | Jul 22, 2026     |
| PY26.2 TACFI (Phase II grads only — not you yet) | —           | Jun 5                       | rolling          |

Plus (from news, needs DSIP confirmation): **six SpaceWERX opportunities currently active**,
topic areas including **cislunar SDA** and defensive cyber.

**What to do with this (folds into Day 3's SBIR block, but one bit is tomorrow):**
1. **Tomorrow (Jul 22):** when 26.BX Release 4 opens on DSIP, read the actual topic list.
   Specific Topics have pre-identified customers — if one matches SDA/maneuver-detection, that's
   a live door with an Aug 18 close. **Note:** pre-release Q&A with topic authors *ends* when
   the window opens — a lesson for next cycle: engage during pre-release.
2. **Realism check:** you have no entity, no SAM.gov registration, no UEI yet. A credible
   proposal by Aug 18 is *possible* but hostile to quality. Default plan: use this cycle to
   **learn the mechanics** (read a live topic, understand Volume structure), finish SAM.gov,
   and aim properly at the **next Open Topic window** — unless tomorrow's list contains a
   perfect-fit SDA topic, in which case decide deliberately whether to sprint.
3. The **Open Topic** (your real entry, no pre-identified customer needed, includes paid
   customer discovery) runs on its own periodic cycle — find the next window on DSIP while
   you're in there. Open Topic D2P2 needs a signed Customer Memorandum; plain Phase I doesn't.

---

## 3. TECHNICAL BUILD PLAN — SPLID spec + a live-right-now data gotcha

### ⚠️ The Alpha-5 / OMM break (you watched it happen)
On **July 11, 2026** the catalog crossed **100,000 objects** (you saw the banner: numbering
jumped 69,999 → 100,000). Consequences, straight from Space-Track/CelesTrak guidance:
- Legacy fixed-width **TLE/3LE cannot represent numbers >99,999**. The **Alpha-5** scheme
  stretches TLEs to 339,999, **but newly cataloged objects ≥100,000 get NO TLE-format data at
  all** — they are published **only via the CCSDS OMM standard** (GP / GP_History API classes in
  JSON/XML/CSV/KVN).
- **Decision (locked): build OMM-native from day one.** Query `GP_HISTORY` as JSON; never write
  a fixed-width TLE parser in 2026. Python `sgp4` supports OMM init and Alpha-5.
- **Strategic bonus:** half the field's legacy tooling is breaking on this *right now* (that's
  why the banner exists). "I'm OMM-native for the >100K-object era" is a credible, current
  conversation opener with every person on your outreach list.

### SPLID — exact spec (from the devkit docs + challenge paper)
- **Data:** 2,402 GEO trajectories (public split: 500), **6 months each at 2-hr resolution**,
  mix of high-fidelity simulation + real historical data.
- **Labels:** expert-annotated, time-stamped **pattern-of-life nodes** — each row =
  `{time index, direction (EW / NS), node type (e.g. station-keep ↔ drift transitions), propulsion type (chemical/electric)}`.
- **Task:** detect the nodes (when behavior changed) and classify the modes between them.
  Scoring uses an F-measure with a tolerance window around node times — i.e., it literally is
  **change-point detection + segment classification on a 2-hr-cadence time series.** Home turf.
- **Winner to study:** `github.com/DavidBaldsiefen/splid-challenge` (1st place 2024) — plus the
  challenge-results paper (Springer, *J. Astronautical Sciences* 2025) which describes what the
  top teams did and where they all still failed (useful: the failure modes are your research
  edge, not just the wins).

### Build sequence (replaces the vague Day-5 plan)
1. **Clone `splid-devkit`**, run its baseline heuristic end-to-end. (Half a day.)
2. **Reproduce the winner's approach** well enough to score against the public split. (1–2 days.)
3. **Your own pass** — change-point detection + mode classifier with your ML instincts;
   beat the baseline, approach the winner. (The real work; ~1 week honest.)
4. **Transfer to live data:** pull `GP_HISTORY` (OMM/JSON) for a few real GEO sats with known
   behavior — a station-keeping Intelsat/SES bird and a known relocation — and show your
   detector flagging the real maneuver. **That screenshot (real sat, real maneuver, free data,
   benchmark-scored method) is the demo.**
5. Context stat for every conversation: screening today runs ~8-hourly with ~16-hr operator
   lead times — your pitch is the behavior layer that makes those windows smarter.

---

## 4. COMPETITIVE GAP — honest revision after finding Agatha

**Correction to the earlier framing.** I previously wrote "nobody sells the standalone
behavior/analytics layer." **Partially wrong:**

- **Slingshot Aerospace sells exactly this at the high end:** "Pattern of Life Insights"
  (descriptors + orbital characteristics + **maneuver detection**) and **Agatha AI** —
  "identifies unexpected behavior… from uncoordinated maneuvers to patterns of life that may
  indicate emerging risks," with explainable alert scoring. In **April 2026** they launched
  **Portal**, an AI-driven platform wrapping all of it. ExoAnalytic's algorithms went inside
  **Anduril** (March 2026). The analytics layer at the **enterprise/government tier is
  occupied.**

**Where the gap actually survives (narrower, but real):**
1. **Price/segment:** Slingshot sells platforms to governments and large enterprises. The
   $5K–$30K/yr buyer — small operator, insurer, analyst, university, allied-nation civil
   agency — has no standalone option. Kayhan's ladder (free → $23K) proves that segment
   transacts; nobody's Agatha-equivalent exists at that altitude.
2. **Data source as a feature:** incumbents' analytics are bolted to their proprietary sensor
   networks (that's their moat *and* their price floor). A **public-catalog-only** product has a
   different cost structure, no procurement entanglement, and is honest about its accuracy
   envelope — "good-enough behavior context, 100x cheaper."
3. **The OMM/>100K era:** legacy tools are breaking as of July 11. A born-OMM lightweight
   product has a timing edge no incumbent bothers to market.
4. **Insurers specifically:** no evidence anyone packages behavioral risk for underwriters
   (§1 #3). Slingshot could, but doesn't appear to; their motion is upmarket (Portal, DoD).

**Reframed wedge (one sentence):**
*Slingshot's Agatha for people who will never buy Slingshot — standalone, public-data,
OMM-native behavior anomaly detection at a $5K–$30K price point, validated on the public MIT
SPLID benchmark, aimed first at the Space Force's stated "predictive SDA" need via SBIR and
tested in parallel on small operators + one insurer.*

**Falsifiable this week:** if outreach calls reveal small operators don't care about behavior
context (only maneuver-planning, which Kayhan owns) **and** the insurer probe is a shrug, the
commercial leg weakens → the play becomes SBIR-first defense-heavy. That's exactly what the
week's calls must find out. Don't skip the falsification.

---

## Sources (deep pass)
- Kayhan Satcat pricing: https://kayhan.space/products/satcat
- SpaceWERX Get Funded (windows verified): https://spacewerx.us/get-funded/
- S4S "predictive SDA" 2026: https://www.dvidshub.net/news/559386/
- Andromeda $1.8B / 14 vendors: https://defensescoop.com/2026/04/10/space-force-contract-andromeda-program-vendors/
- Slingshot Agatha AI: https://www.slingshot.space/product-agatha
- Slingshot Portal launch (Apr 2026): https://www.slingshot.space/news/slingshot-aerospace-launches-portal-an-ai-driven-platform-for-mission-ready-space-operations
- Seradata pricing benchmark: https://softwarefinder.com/facility-management-software/seradata
- Space insurance / underwriting analytics: https://ts2.tech/en/space-at-stake-the-boom-in-satellite-insurance-risk-management-2025-2032/ · https://satnews.com/2026/02/08/satellite-insurers-driving-costs-in-a-hyper-congested-orbital-environment/
- CelesTrak GP data formats (Alpha-5/OMM): https://www.celestrak.org/NORAD/documentation/gp-data-formats.php
- Space-Track documentation: https://www.space-track.org/documentation
- SPLID dataset docs: https://splid-devkit.readthedocs.io/en/latest/dataset.html
- SPLID challenge results paper: https://link.springer.com/article/10.1007/s40295-025-00515-5
- SPLID 2024 winner: https://github.com/DavidBaldsiefen/splid-challenge
- LEO SSA market size/APAC: https://www.grandviewresearch.com/industry-analysis/leo-space-situational-awareness-market-report
