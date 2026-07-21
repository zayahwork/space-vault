---
title: Research + Outreach Week — Plan, Outreach List, First-Pass Research Answers
type: working-doc
status: active
created: 2026-07-20
parent: SPACE_PROJECT_CONTEXT.md
tags: [space, ssa, sbir, outreach, research, week-1]
---

# Research + Outreach Week

> [!warning] This is a REFERENCE doc now — day-to-day work lives in `01 This Week` (one file
> per day). Come here only for background/reasoning. Some early details were corrected as we
> verified them; the day files and [[DEEP_RESEARCH_2026-07-20]] are the most current truth.

> Companion to `SPACE_PROJECT_CONTEXT.md`. Delivers §10's three asks:
> (1) day-by-day plan, (2) the 8–10 person outreach list + warm email,
> (3) first-pass answers to the §6 research questions.
> Dates/topic numbers marked **[VERIFY LIVE]** must be checked this week — they move.

---

## THE ONE INSIGHT THAT SHAPES EVERYTHING

**The bottom of the SSA stack is being nationalized and given away for free.**

The Office of Space Commerce's **TraCSS** (Traffic Coordination System for Space) is now
delivering basic conjunction warnings to operators **free of direct user fees**, taking over
the "safety" function that the 18th Space Defense Squadron used to run. Commercial pathfinder
partners (LeoLabs, Slingshot, COMSPOC) are feeding it.

**Consequence for a solo founder:** selling "collision alerts" or "a catalog" is walking into
a wall — the government is now the free competitor at that layer, on top of the $27M-funded
incumbents. The money is moving **up the stack**: not *"there's a warning,"* but
*"which warning actually matters, what is that object doing, and what should I do about it."*

That is an **analytics/ML problem, not a sensor problem** — which is exactly the founder's
strength and exactly a $0-hardware business. It reframes the wedge question below.

---

## PART A — Day-by-day plan (research + outreach in parallel)

Rule from the brief: **outreach starts Day 1** so emails marinate while you learn. Research
feeds the emails; emails feed the research. ~50 hrs across the week ≈ 7 hrs/day.

### Day 1 (Mon) — Set the table, fire the first shots
- **Outreach (AM):** Send the **first 3 emails** — the two easiest local warm targets
  (UW A&A + Starfish Space, Kent WA) and one evangelist (Moriba Jah / Privateer). Don't wait
  for a "perfect" email; the template in Part B is ready.
- **Research (PM):** Register on **Space-Track.org** and **CelesTrak**. Pull a week of TLE
  history for ~5 objects (e.g. ISS, a Starlink, a known-maneuvering GEO sat). Goal: *see the
  raw material with your own eyes.* Skim the SPACE_PROJECT_CONTEXT competitor list.
- **End-of-day artifact:** a note file "who I emailed + when + follow-up date (+3 business days)."

### Day 2 (Tue) — Data reality + next outreach batch
- **Research:** Install `sgp4` + `skyfield` (Python). Propagate one TLE to a position/velocity.
  Plot one object's orbital elements over 30 days — *look for the discontinuity that is a
  maneuver.* This is the core of the recommended wedge; prove to yourself you can see it.
- **Outreach:** Send emails **4–6** (Kayhan Space, Xplore Bellevue, one SSA startup engineer
  found on LinkedIn). Keep the same curious-local framing.

### Day 3 (Wed) — SBIR deep-dive
- **Research:** Go to **spacewerx.us/get-funded** and the **DSIP portal**. Find the current
  **Open Topic** window and any SDA/SSA-flavored topics **[VERIFY LIVE]**. Read what a Phase I
  Open Topic proposal + customer-discovery phase actually requires. Start **SAM.gov**
  registration (it takes days — start it now, don't finish it perfectly).
- **Outreach:** Send emails **7–8** (Office of Space Commerce / TraCSS ecosystem contact +
  Washington NASA Space Grant). Reply to anything that came back from Day-1 sends.

### Day 4 (Thu) — Skill-gap close + the wedge memo
- **Research:** Focused study block on the 4 orbital-mechanics concepts you actually need
  (Part C, Q4). Write a **1-page wedge memo**: "maneuver / anomaly detection from public
  catalog data" — who buys it, why now, why me. This memo becomes your SBIR seed + your
  sharper outreach pitch.
- **Outreach:** Send emails **9–10** (a second evangelist/founder + AMOS-community contact).
  You've now sent all 10. Log follow-up dates.

### Day 5 (Fri) — Prototype spike + first calls
- **Research:** Build the smallest possible **maneuver-detector demo**: pull one satellite's
  TLE history, compute a per-epoch orbital-element series, flag the day an element jumps beyond
  a threshold. Ugly is fine. A working "I detected this maneuver from free data" screenshot is
  worth 100 emails.
- **Outreach:** Take any calls that landed. **Listen for pain described unprompted** (the
  stopping-rule signal from the brief). Send +3-day follow-ups to non-responders from Day 1–2.

### Day 6 (Sat) — Synthesize
- Write up: what the data can/can't do, what the SBIR path looks like, which 2–3 wedge
  variants survived contact, and what every conversation actually said. Update this file.

### Day 7 (Sun) — Decide the next week
- Pick **one** wedge to go deeper on. Schedule week-2 follow-ups. Decide: is there enough
  early signal to aim a Phase I Open Topic proposal at the next window?

**Weekly scoreboard (the honest one):** replies ≠ signal. Track **genuine conversations where
the person describes the pain unprompted** (target 5+) and **anyone who asks to try it / what
it costs, unprompted** (target ≥1). That is the only stopping rule that means anything.

---

## PART B — Outreach list (10) + the warm email

**Framing (from the brief):** a conversation, not a sale. Curious-local. Mission-driven and
technical people rarely refuse "help me understand where it actually hurts." Send from a real
name, keep it under ~120 words, one clear ask, no attachments, no pitch deck.

### The email template

> **Subject:** Curious question from a Seattle person digging into space-object tracking
>
> Hi [Name],
>
> I'm an ML engineer near Seattle going deep on how we detect and track objects in Earth
> orbit — debris, maneuvers, conjunctions. I'm early and doing my homework by talking to
> people who actually live this rather than guessing from the outside.
>
> Could I ask you a few questions sometime — 15–20 min, whenever's easy? I'm mostly trying to
> understand **where the tracking / collision / data problems actually hurt** for someone in
> your seat, and what the incumbents *don't* solve well.
>
> Not selling anything — genuinely just learning. Happy to work around your schedule.
>
> Thanks,
> Zayah Nelson · 425-409-8684

*Tuning notes:* for UW, swap the opener to "I'm exploring a space-object-detection idea and
UW A&A is right in my backyard." For a founder, add one specific line showing you did your
homework on their company. For the gov/TraCSS contact, emphasize "commercial ecosystem
feedback."

### The 10 targets (local-first, then SSA world, then gov)

| # | Target | Why them | Warm angle |
|---|--------|----------|-----------|
| 1 | **UW Aeronautics & Astronautics** — Prof. **Kristi Morgansen** (Professor, Boeing Egtvedt Chair — NOT dept chair; also *directs the WA NASA Space Grant*) & Prof. **Anshu Narang-Siddarth** (GNC) | Local; estimation-with-limited-sensing = the exact math of tracking; she's a double network node | "In my backyard, want to learn" — **SENT 7/20** |
| 2 | **Starfish Space** (Kent, WA) | LOCAL. Satellite servicing / rendezvous-proximity ops = needs precise relative object detection & tracking. Perfect pain-owner nearby | Same-region founder curiosity |
| 3 | **Moriba Jah** — Privateer co-founder, UT Austin prof, ASTRIAGraph | The field's open-data evangelist; famously takes curious calls; deep on why current SSA is broken | "You're the person people told me to ask" |
| 4 | **Kayhan Space** | Conjunction assessment + autonomous maneuver planning startup; startup-friendly; lives the "which alert matters" problem | Founder-to-founder, decision-support angle |
| 5 | **Xplore** (Bellevue, WA) | LOCAL. ~~Deep-space~~ **CORRECTED 7/20:** hyperspectral LEO constellation + Major Tom ops software — they're an operator AND run ops for other operators | Operator-pain angle — **SENT 7/20** |
| 6 | **Brian Williams, Slingshot** (engineer; AMOS 2025 Golden Ticket for ML event detection) | Engineers describe real technical pain more freely than execs | Congrats-on-award email (guessed address — NO LinkedIn, ever; user is banned) |
| 7 | **Office of Space Commerce / TraCSS** ecosystem contact | They *want* commercial-ecosystem feedback; tells you where the free baseline stops and paid value starts | "Commercial feedback on TraCSS" |
| 8 | **Washington NASA Space Grant** (UW-hosted) | Local funding/network node; knows every space person in the state | "Who locally should I be talking to?" |
| 9 | **Dr. T.S. Kelso, CelesTrak** (`TS.Kelso@celestrak.org`) | THE community elder since 1985; wrote the data docs we build on; famously answers email; lives on Maui (AMOS bridge) | "Building OMM-native because of your docs" |
| 10 | **AMOS conference community contact** | AMOS (Maui, Sept) is the SSA field's technical watering hole; one intro cascades | "Hoping to learn before AMOS season" |

**Bench (if any bounce):** Aerospace Corporation (Seattle presence), RBC Signals (Seattle,
ground-station data), Stoke Space (Kent), COMSPOC, Vyoma (Germany), LeoLabs eng team.

---

## PART C — First-pass answers to the §6 research questions

### Q1 — The wedge (where does a solo outsider fit?)

**Do NOT compete on catalog or collision warnings** — TraCSS gives that away free and the
incumbents own the sensors. Compete **one layer up, on ML-driven behavior**, where nobody's
funding buys them out of the founder's actual advantage.

**Recommended primary wedge → "Maneuver / anomaly detection & pattern-of-life from public
catalog data."** Using ML on the public TLE/element-history time series to detect *when an
object maneuvered or is behaving anomalously* — no sensors, no hardware.

Why this one:
- **$0-feasible** — public TLE history is enough to build a real demo (see Q2).
- **Maximizes the ML edge** — it's anomaly/change-point detection on time series, the
  founder's home turf, not orbital-mechanics grunt work.
- **Clean SBIR/defense story** — "custody" and "is that adversary satellite maneuvering?" are
  named Space Force needs. Maneuver detection is a live pain even for operators (screening runs
  only every ~8 hrs; operators need ~16 hrs of lead time — slow, coarse, improvable).
- **It's the same brain the dream needs** — "detect + characterize object behavior from sparse
  observations" is *literally* the skill that later points at asteroids. You build the brain
  once.

**Reality check (pass-2 research — be honest with yourself):** maneuver / pattern-of-life
detection from TLEs is an *active* research area (multiple 2024–25 papers; MIT ARCLab even runs
a public AI challenge on it — see Research Log). So the raw *capability* is not virgin
territory. **Your wedge is therefore NOT "I can detect maneuvers" — it's the packaging + the
buyer:** a pure-software product on *free public data*, aimed at a specific underserved segment
(a small operator, a non-US operator, an insurer/analyst, or a defense custody use-case), while
every incumbent doing this does it as a bolt-on to an expensive *sensor* network. Nobody sells
the clean free-data ML layer as its own product to that buyer. Prove the capability fast (the
labeled SPLID dataset makes that a weekend, not a quarter), then spend your real effort finding
the one buyer who wants it standalone.

**Stretch/differentiator wedge → Cislunar (XGEO) SDA.** A named SpaceWERX priority, very few
incumbents, and conceptually the bridge to deep space. Harder (data is scarcer, buyer is almost
purely government) — keep as the ambitious second bet, not the day-1 target.

**Ruled out as entry points:** raw catalog/tracking (incumbent + TraCSS wall); basic
collision alerts (now free); a live-3D viz *as the product* (great differentiator later, not a
business by itself — keep it as an asset per the brief).

### Q2 — Free/cheap data reality (what's buildable at $0, where costs start)

**Free, and genuinely enough for the recommended wedge:**
- **CelesTrak** — free, no login. Curated TLE/GP data + SATCAT. Best for fast prototyping.
- **Space-Track.org** — free with registration (accept the data-sharing agreement). TLEs,
  full SATCAT (~50,000+ tracked objects), decay/launch data, and **free close-approach / CDM
  notifications**. Respect the API rate limits (there's an official best-practices doc; batch
  your queries, cache locally).
- **TraCSS** (Office of Space Commerce) — the new public system; CDMs free of direct user fees.
  Build *around* it and know exactly where its free baseline stops (that gap = your paid value).

**Gated / partner-only (relevant once you're in SBIR, not day 1):**
- **UDL (Unified Data Library)** — central government SSA repository; access requires being a
  credentialed partner. A target to plug into later, not an open faucet now.

**Where real costs start (so you're honest with buyers):**
1. **Small objects** — public catalog floors around ~10 cm; below that, commercial data.
2. **Higher accuracy / cadence** — sub-catalog precision and frequent updates = paid sensor data.
3. **Raw observations / astrometry** — you don't own sensors; buying obs is expensive.
4. **Compute at scale** — fine for a prototype, a line item at production.
5. **Commercial-use licensing** — check terms before selling deliverables built on any feed.

**Bottom line:** a compelling "I detected this maneuver from free public data" demo costs **$0**.
That's the whole point of picking this wedge.

### Q3 — First SBIR / SpaceWERX topic

- **The program is live and just reopened** — SBIR/STTR was reauthorized (spring 2026) and
  AFWERX/SpaceWERX reopened solicitations. Long runway (authorized through FY2031).
- **Your door = Open Topic** (dual-use, no pre-defined requirement — built for newcomers).
  Phase I = feasibility (~$150K) **and includes a customer-discovery phase** — they literally
  pay you to validate demand, which *is* your outreach track. Plain Open Topic Phase I does
  **not** need a pre-identified customer; **D2P2** requires a signed **Customer Memorandum**
  (a government sponsor) — a reason to be nurturing gov contacts (target #7) now.
- **Relevant topic areas seen in 2026:** cislunar SDA, "novel sensing for ground and space."
  SDA/SSA is squarely in scope. **[VERIFY LIVE on DSIP/spacewerx.us this week]** for exact open
  topic numbers + close dates — windows are short (often ~4 weeks) and rotate.
- **Mechanics / eligibility:** U.S.-owned small business (≤500), **SAM.gov** registration (get
  your UEI — *start this Day 3, it's slow*), PI must be U.S. citizen or permanent resident.
  Submit via the **DSIP portal**. Notifications ≤90 days from close; contract ≤180 days.
- **How to play it (from the brief's hard-won lesson):** treat SBIR as **non-dilutive fuel for
  the maneuver-detection product you'd build anyway**, with a commercial/dual-use path so
  you're never hostage to one Phase III. Avoid the "SBIR mill" trap.

### Q4 — Technical skill gap (on top of existing ML)

The ML is the hard part and you have it. The orbital layer is ~2–3 focused weeks:

1. **Orbital mechanics basics** — the six Keplerian elements, coordinate frames (ECI/TEME/ECEF),
   time systems (UTC/Julian/GPS). Enough to know what each number in a TLE *means*.
2. **TLE format + SGP4/SDP4 propagation** — turning a TLE into position/velocity over time.
   Python: **`sgp4`**, **`skyfield`** (start here — friendliest), `astropy`/`poliastro`;
   `orekit` if you go heavy later.
3. **Orbit determination / estimation** — least squares + Kalman/UKF. This *overlaps your ML
   background directly* — maneuver detection is essentially change-point/anomaly detection on
   OD residuals or element time series.
4. **Conjunction basics (literacy only)** — probability of collision, miss distance, covariance,
   screening volumes. Enough to speak the language; not your core product.
5. **Data plumbing** — pulling + versioning TLE history, handling catalog quirks (epoch drift,
   object re-designations, element-set noise).

**Reference stack:** Vallado, *Fundamentals of Astrodynamics and Applications* (the bible);
**CelesTrak / Dr. T.S. Kelso**'s writeups (accessible, authoritative); `skyfield` + `sgp4` docs.

### Q5 — Who to email (the research answer behind Part B)

Three pools, local-weighted:
- **Local (highest warmth):** UW A&A (Morgansen, Narang-Siddarth) · Starfish Space (Kent) ·
  Xplore (Bellevue) · Washington NASA Space Grant · (bench: Aerospace Corp Seattle, RBC
  Signals, Stoke Space Kent). Seattle/Puget Sound has a real space cluster — use it.
- **SSA world (curious calls):** Moriba Jah / Privateer (start here — evangelist) · Kayhan
  Space · engineers at Slingshot / LeoLabs / Vyoma / Digantara (LinkedIn, not execs).
- **Gov / ecosystem:** Office of Space Commerce / TraCSS · SpaceWERX engagement events ·
  the **AMOS conference** community (Maui, Sept — the SSA field's annual watering hole).

---

## Open items to close this week
- [ ] **[VERIFY LIVE]** exact current Open Topic window + SDA topic numbers (DSIP / spacewerx.us)
- [ ] Start SAM.gov registration (slow — begin Day 3)
- [ ] Confirm real email addresses for the 10 targets (dept pages / LinkedIn / company contact)
- [ ] Stand up the $0 maneuver-detector spike (Day 5) — the screenshot that changes every convo

---

## Sources (research pulls, 2026-07-20)
- SpaceWERX — Get Funded: https://spacewerx.us/get-funded/
- AFWERX — Open Topic: https://afwerx.com/divisions/sbir-sttr/open-topic/
- AFRL — AFWERX/SpaceWERX reopen SBIR/STTR after reauthorization: https://www.afrl.af.mil/News/Article-Display/Article/4473004/
- Space-Track.org documentation: https://www.space-track.org/documentation
- CelesTrak (via KeepTrack overview): https://keeptrack.space/resources/celestrak
- Office of Space Commerce — TraCSS update: https://space.commerce.gov/tracss-update-expanding-space-safety-partnerships/
- SpaceNews — Getting SSA off the ground: https://spacenews.com/getting-ssa-off-the-ground/
- AMOS technical papers (mission-oriented SSA evaluation, 2025): https://amostech.com/TechnicalPapers/2025/SDA/Schmedeman.pdf
- UW A&A — Space systems research: https://www.aa.washington.edu/research/space-systems
- UW A&A — Faculty finder: https://www.aa.washington.edu/facultyfinder

---

## Research Log — 2026-07-20 (pass 2)

New findings that change or sharpen the plan.

### 🎁 A public, labeled dataset drops the prototype risk to near-zero
- **MIT ARCLab SPLID** (Satellite Pattern-of-Life Identification Dataset) is **public**, with a
  **devkit on GitHub** (`github.com/ARCLab-MIT/splid-devkit`) and docs at
  `splid-devkit.readthedocs.io` / `arclab.mit.edu/aichallenge`.
- ~2,402 trajectories, 6 months, 2-hr resolution, built from TLEs + VCM; **labeled maneuvers**.
  Public challenge split = 500 trajectories. Prior-winner solutions are on GitHub to study
  (e.g. `DavidBaldsiefen/splid-challenge`, 1st place 2024).
- **Why it matters:** your Day-5 demo doesn't need you to hand-label anything — SPLID is
  ML-ready and framed as an AI challenge. **Doing well on a public benchmark = instant, cheap
  credibility** (the 2024 winners got MIT recognition + Air Force attention). This is arguably
  the single fastest "proof I can do this" available to you.
- **Action:** SPLID is now the recommended substrate for **Research 5** (still validate on live
  Space-Track TLEs afterward, since SPLID is partly synthetic).

### The field is consolidating into defense primes — reinforces the SBIR/dual-use path
- **Anduril acquired ExoAnalytic (March 2026)** — absorbed its ~400-telescope network + tracking
  algorithms. Signal: SDA is coalescing into a layered *military* enterprise (Lockheed Space
  Fence, Northrop DARC, LeoLabs radar, Slingshot optical, Kratos RF, L3Harris).
- **Read-through:** a solo software play must be niche and nimble, not head-on — and the
  government/defense buyer (via SBIR) is where the money and the consolidation are. Confirms the
  wedge should have a clean dual-use/defense custody story.

### Maneuver detection: the incumbents all pair it with sensors — that's your gap
- Everyone doing pattern-of-life / maneuver detection (ExoAnalytic→Anduril, Slingshot, LeoLabs,
  Kratos, MIT academically) does it **fused with their own expensive sensor data**. The
  *pure-free-public-data software product* aimed at an underserved buyer is the unclaimed slice.
- Foundational reading: **Kelecy, "Satellite Maneuver Detection Using TLE Data," AMOS 2007** —
  the classic starting reference. Then the 2024–25 ML papers (CNN GEO repositioning, LSTM PoL,
  deep-learning LEO orbit-prediction) for the modern state of the art.

### AMOS 2026 = the field's watering hole, and it's soon
- **Sept 15–18, 2026, Wailea Beach Resort Marriott, Maui** (virtual option). ~1,000 attendees,
  150+ talks, SPACECOM commander keynoting. Tracks include cislunar SDA + AI.
- Abstract deadlines for 2026 have very likely **passed** (it's July; AMOS abstracts close in
  spring) — so treat AMOS as a **networking + learning** target this year (attend/virtual, work
  the room, line up intros), and a **submit-an-abstract** goal for **AMOS 2027** once you have
  the SPLID result to show.

### Concrete contacts found
- **Starfish Space (Kent, WA):** general `hello@starfishspace.com`, press `press@starfishspace.com`.
  Seattle-area, ~90 people, $150M+ raised, flew Otter Pup 2 (summer 2025). Local + credible.
- **Kayhan Space:** contact via `kayhan.space/root/contact`.
- **Xplore (Bellevue):** contact page not confirmed this pass — grab it during Email 5.

> **➡️ 2026-07-20 evening: full deep-research pass complete → [[DEEP_RESEARCH_2026-07-20]].**
> Headlines: Kayhan's public pricing anchors operator willingness-to-pay (~$23–30K/yr);
> USSF's own words for 2026 are "predictive SDA" (= the wedge); a Specific-Topic SBIR window
> **opens Jul 22 / closes Aug 18** — check DSIP on Day 3; Slingshot's **Agatha** already does
> maneuver-anomaly analytics at the enterprise tier, so the wedge is now precisely
> *"Agatha for people who will never buy Slingshot"* (small ops, insurers, SBIR niches);
> and the catalog crossing 100,000 (Jul 11) means **build OMM-native, never TLE parsers**.

### Sources (pass 2)
- MIT ARCLab SPLID devkit: https://github.com/ARCLab-MIT/splid-devkit
- SPLID dataset docs: https://splid-devkit.readthedocs.io/en/latest/dataset.html
- MIT News — ARCLab AI Innovation in Space winners: https://news.mit.edu/2024/mit-arclab-announces-winners-inaugural-prize-ai-innovation-space-0711
- Kelecy, TLE Maneuver Detection, AMOS 2007: https://amostech.com/TechnicalPapers/2007/Modeling_Analysis_Simulation/Kelecy.pdf
- SDA ecosystem consolidation / Anduril–ExoAnalytic: https://newspaceeconomy.ca/2026/01/31/the-global-ecosystem-of-space-situational-awareness-and-traffic-management/
- MIT AeroAstro — GEO Pattern-of-Life: https://aeroastro.mit.edu/arclab/research/geosynchronous-satellite-pattern-of-life-characterization/
- AMOS 2026 dates: https://spacepolicyonline.com/events/amos-2026-sept-15-18-2026-maui-hawaii-virtual/
- Starfish Space contact: https://www.starfishspace.com/contact/
- Kayhan Space contact: https://kayhan.space/root/contact
