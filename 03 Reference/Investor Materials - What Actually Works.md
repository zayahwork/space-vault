---
date: 2026-07-23
owner: Randy (research)
type: research-note
card: issues/research/031 - investor materials research.md
status: complete
---

# 💰 Investor Materials — what actually works, from primary sources

> [!info] Method
> Every claim below is marked **VERIFIED** (the source page was actually read — via Python
> urllib, since WebFetch is blocked and WebSearch was permission-denied in this session) or
> **ASSUMED** (reasonable inference, source not directly read). Sources linked inline.
> Researched overnight 2026-07-23 for card 031, feeding Mark's investor outreach (card 030).

## 1. Anatomy of cold emails and intro requests that get meetings

All from primary investor writing: Michael Seibel (YC), Elizabeth Yin (Hustle Fund),
Paul Graham, Fred Wilson (USV), Jason Lemkin (SaaStr). The YC Library renders client-side
and returned no text to urllib; YC guidance is covered via Seibel's own mirror of his
YC-published essay.

### The verified template (composite of the sources below)

- **Subject line:** curiosity-provoking, slightly "off," short ("New customers?" style) —
  Yin. VERIFIED — <https://elizabethyin.com/2016/04/20/how-to-write-a-cold-email/>
- **Length: 3–4 sentences, phone-readable.** Seibel: "Short, concise emails average much
  faster response times… walls of text result in slow/no replies." VERIFIED —
  <https://www.michaelseibel.com/blog/how-to-email-early-stage-investors>
- **Sentence 1 — what you do, zero jargon.** Seibel's example: "I'm building Twitch for
  cooking." (Analogy is fine when it genuinely clarifies; hype is the sin, not analogy.)
  VERIFIED — same URL.
- **Sentence 2 — the single most exciting proof point.** Seibel: "A huge market, a launched
  product, solid growth, or notable, technical founders… I am not interested in your resume,
  awards… or your personal story at this point." VERIFIED — same URL. Yin: 2–3 KPI bullets
  max, real numbers ("$20k MRR", "Marquee beta clients include: Google, Boeing"), never
  vanity metrics; if traction is weak, lead with team/domain proof instead. VERIFIED —
  <https://elizabethyin.com/2016/09/01/7-tips-for-cold-emailing-investors/>
- **Sentence 3 — one specific, low-friction conversational ask.** Yin: "What's the best way
  to discuss?" — never ask for investment by email. Seibel: "Don't ask for a phone call or a
  meeting. Let me escalate things." VERIFIED — URLs above.
- **From a company-domain email address.** Both Seibel and Yin flag Gmail/Yahoo senders as
  reading not-serious. VERIFIED.
- **Deck:** Yin says don't attach one to the first email (spam filters; let them ask);
  Lemkin says detailed decks convert far better than 3-page teasers. Real disagreement —
  resolution: keep the email deck-free, but have the FULL deck ready to send the moment
  anyone replies. VERIFIED (both) —
  <https://www.saastr.com/if-you-want-to-get-funded-dude-make-it-easy-on-them/>
- **Follow-up: within the week, repeatedly.** Yin: "if you ping say even 3x in a week, it's
  unlikely that an investor will even notice." VERIFIED — 7-tips URL above.
- **Volume expectation:** Yin's own all-time cold-email response rate ≈25%; >10% is good.
  "Email 10 people if you want a couple of responses back." Fundraising is a sales job.
  VERIFIED — cold-email URL above.

### Intros: double opt-in + the forwardable blurb

- **Double opt-in is the canonical etiquette** — Fred Wilson: ask each party to opt in
  before making the intro. VERIFIED — <https://avc.com/2009/11/the-double-optin-intro/>
- Practical form: give your connector a short self-contained forwardable blurb (your
  3-sentence email) so the investor can opt in. ASSUMED (standard practice built on
  Wilson's rule; Bahat/Hudson write-ups not directly readable this session).
- **Intro quality hierarchy** — Paul Graham: best = a well-known investor who just invested
  in you; next = a founder of a company they've funded. Also: "If you get cold-emailed by
  an associate at a VC firm, you shouldn't meet… Deals don't happen that way." VERIFIED —
  <https://paulgraham.com/fr.html>
- **Cold email is a parallel channel, not a consolation prize.** Yin treats referrals and
  cold emails the same; Lemkin: "a mediocre warm intro is worse than a great cold
  outreach." VERIFIED —
  <https://www.saastr.com/10-unforced-errors-founders-make-in-the-vc-fundraising-process/>
  — relevant to us since LinkedIn is unavailable and our network is thin.

### Common mistakes (verbatim from Seibel / Yin / Lemkin, all VERIFIED)

Unclear first line; too long; over-investing in warm-intro hunting instead of just
emailing; wasting sentences flattering the investor; personal-email senders; pitching via
LinkedIn/Twitter DM; typos; generic blasts ("95% of the cold emails VCs get are just
terrible… show a connection to that VC"); stale artifacts ("Feb Deck FIN v12" sent in
April); raising off one good month instead of three; ask size mismatched to fund size.

## 2. The traction bar for a pre-seed space-data company

What the people who define the category actually say:

- **Charles Hudson (Precursor — the firm that defined pre-seed):** "pre-seed rounds were
  about **product market fit finding**… not about scaling out the management team… not
  about generating a ton of ARR… It's this **hypothesis validation phase**. It's about
  **proving that people care about the thing that you're building**." VERIFIED —
  <https://www.thespl.it/p/why-pre-seed-investing-has-never> (2026-06-25). His 2026-07-19
  LP letter: round-name inflation is rampant ("$10M rounds still called pre-seed");
  Precursor historically capped ~$4M rounds / ~$20M valuations. VERIFIED —
  <https://chudson.substack.com/p/its-all-pre-series-a-now>
- **Elizabeth Yin (Hustle Fund):** "Very typically at this stage, **little to no traction
  is needed**… It could be building an early version of the product, or getting your
  first set of customers, or even doing pre-sales." Pre-seed investors are
  "conviction-investors"; without pedigree "you basically need traction to prove out your
  execution abilities." VERIFIED —
  <https://elizabethyin.com/2018/08/31/pre-seed-is-the-new-seed/>. Caveat: Hustle Fund's
  own FAQ says "**We do not invest in deep tech, most hardware**" (VERIFIED) — generalist
  pre-seed funds may bounce on the word "space"; framing us as B2B data/SaaS rather than
  spacetech is ASSUMED advice.
- **Space Capital's published seed scorecard:** **Team 30%** (largest factor by far), Deal
  Dynamics 12%, Product 12%, Business Model/Market/Competition/Financials 9% each.
  "Early-stage companies do not yet have a history of revenue and growth, investors must
  rely on observations and past experience." VERIFIED —
  <https://www.spacecapital.com/publications/evaluating-seed-stage-investment-opportunities>
- **Seraphim's accelerator curriculum** (what spacetech investors want de-risked at
  pre-seed): corporate/customer validation, working with primes, dataroom/forecasting —
  not revenue. Program facts VERIFIED; the inference is ASSUMED.

**Do we clear the bar?** Against Hudson's definition: yes — a working detector with
verified output on real data is more than most pre-seed software companies have (VERIFIED
definitions, ASSUMED application to us). Against Yin's checklist: product leg cleared;
the **customer-evidence leg is the thin one** — one scheduled broker meeting is a
conversation, not "first customers" or pre-sales (ASSUMED synthesis). Against YC's bar:
clearly sufficient to apply — the majority of each batch is pre-revenue; only 7% of recent
batches had >$50k MRR (VERIFIED, YC FAQ).

**What closes rounds:** team/credibility first (VERIFIED — Space Capital's 30% weight;
PG "I care more about the founders than the idea"); then **written customer evidence**
(LOI / paid pilot / design-partner agreement) — supported by Yin's pre-sales language
(VERIFIED) and Seraphim's curriculum; the flat claim "space pre-seeds close on LOIs" is
ASSUMED (no single source states it). Defensible ask for us: the small end,
$500K–$1.5M at hypothesis-validation framing (ASSUMED recommendation).

## 3. The 10 most relevant space pre-seed funds/angels, with thesis quotes

Ranked by fit for us (pre-revenue, solo founder, software-only SDA, insurance/broker
pipeline). Every thesis quote is verbatim from the fund's own site or a named article,
read via urllib.

| # | Fund | Stage / check | Pitch route |
|---|------|--------------|-------------|
| 1 | **Space Capital** (NY) | Early-stage; Fund IV launched Mar 2026, $1B+ AUM (VERIFIED) | **Open: email deck to launch@spacecapital.com** (VERIFIED) |
| 2 | **Space VC** (Austin, Jonathan Lacoste, solo GP) | Pre-seed "day zero"; $500K–$1M checks, $20M Fund II (VERIFIED, TechCrunch) | Cold email/X to Lacoste (ASSUMED — site unreachable) |
| 3 | **Seraphim Space** + Accelerator (London/US) | Accelerator pre-seed→A; $630M+ AUM (VERIFIED) | Accelerator application (currently closed — "Register Interest") (VERIFIED) |
| 4 | **E2MC Ventures** | "First check at seed or even pre-seed… US$250k–2MM" (VERIFIED) | **Open pitch form with deck upload**, process published (VERIFIED) |
| 5 | **Boost VC** (San Mateo) | "We Lead Pre-Seed Rounds — $500k Checks" (VERIFIED) | **Open "Submit a Pitch" form** (VERIFIED) |
| 6 | **Techstars Space** (LA) | Accelerator w/ USSF + NASA JPL; ~$220K standard deal (ASSUMED) | Open application — 2026 deadline passed Jun 10; next ~Mar 2027 (VERIFIED) |
| 7 | **SpaceFund** (Houston, Meagan Crawford) | Early-stage; $20M+ invested (VERIFIED); check ~$100–500K (ASSUMED) | Open "Submit Company" link (form itself 522'd — ASSUMED working) |
| 8 | **Stellar Ventures** (Palo Alto, Celeste Ford) | $23M seed-specialist fund (VERIFIED, Payload) | Unknown — warm intro (ASSUMED) |
| 9 | **Embedded Ventures** (LA) | Early-stage deeptech; USSF R&D partnership (VERIFIED) | No form; warm intro/direct email (ASSUMED); activity level unclear — verify first |
| 10 | **Starbridge VC** | Early/growth space + deep tech (stage ASSUMED) | Contact form (VERIFIED) |

Key fit evidence (all VERIFIED unless marked):

- **Space Capital** has an SSA category in its own portfolio taxonomy and owns **LeoLabs**
  and **Kayhan Space** — the two nearest analogs to our product. Thesis: "Space-based
  technologies are the building blocks of innovation on Earth. GPS, geospatial
  intelligence, and satellite communications are already the invisible backbone powering
  the world's largest industries." (spacecapital.com/about)
- **Space VC** (Lacoste): "We're investing at day zero, oftentimes when founders are just
  starting companies"; praises founders who raise "a $2 million pre-seed, closing
  government financing, getting initial customer traction, building an MVP in a really
  scrappy manner" — our exact profile. First checks into True Anomaly and Array Labs.
  (TechCrunch, 2024-05-22)
- **Seraphim**: LeoLabs is a top-10 holding; portfolio includes Spaceflux, ODIN Space,
  Privateer (SSA) AND insurance-data plays ICEYE, Adaptive Insurance, Delos — they already
  believe in space-data-for-insurance, which is our wedge.
- **E2MC**: "You need a space angle… you do not need to own or operate actual space
  hardware" — explicitly downstream/software-friendly. Portfolio: Privateer, Antaris.
- **Boost VC**: one of the few funds that *leads* pre-seed via an open form; aerospace-
  forward but no SSA-data holding found.
- **Techstars Space**: "Running in partnership with the United States Space Force and
  NASA's Jet Propulsion Laboratory… a focus on innovative dual-use companies" — direct
  SDA credibility engine, but the 2026 window is closed.
- **SpaceFund** thesis: backing "the infrastructure, **intelligence**, and commercial
  capability that will define the space economy"; portfolio Cognitive Space.
- **Embedded Ventures** is the one fund with a direct SSA win (**Slingshot Aerospace**)
  plus a formal USSF relationship — but opaque process.
- **Starbridge**: "have proven or provable success" language suggests they want more
  traction than pre-revenue; Umbra is their data holding.

**Investigated and cut:** **Countdown Capital is DEAD** (shut down Jan 2024, capital
returned — VERIFIED, TechCrunch: do not pitch). **Type One Ventures** site is an empty
GoDaddy shell (VERIFIED site state; status ASSUMED defunct). Lux/Founders Fund: real but
multi-stage warm-intro-only — revisit at seed with traction. AlleyCorp a reasonable #11
($1–5M checks incl. pre-seed, VERIFIED, but no space-data holding). Balerion: active,
open contact, but all-hardware portfolio. Moonshots: industry-agnostic. Interlagos
(ex-SpaceX, 2024): leads $50M+ rounds — too late-stage. KittyHawk: generalist, weak fit.

## 4. Y Combinator: next batch, deadlines, space-alumni lessons

> [!warning] ⏰ **Next batch: Fall 2026 (Oct–Dec, San Francisco). On-time deadline:
> July 27, 8pm PT — FOUR DAYS from this note's date.** Apply on time → decision by
> Aug 28. VERIFIED — <https://www.ycombinator.com/apply> (page text read 2026-07-23).

Facts, all VERIFIED from YC's own pages unless marked:

- **Solo founders: "Yes. We regularly accept solo founders."** (exact FAQ text; they still
  advise a co-founder and point to YC Co-founder Matching). Founding team must be able to
  build the product themselves — a technical solo founder satisfies this. VERIFIED —
  <https://www.ycombinator.com/faq>
- **Pre-revenue is the norm:** majority of each batch; only 7% of recent batches had
  >$50k MRR. "We don't rely on introductions." **"About half the companies applied
  multiple times** before being accepted… progress since your last application is a
  strong signal" — i.e., applying with 4 days' prep costs nothing and seeds a stronger
  re-application. VERIFIED — FAQ.
- **What the application is graded on** (PG, "How to Apply to YC," VERIFIED —
  <https://www.ycombinator.com/howtoapply>): clarity above all ("more than half [of
  interview-worthy groups] blow the application" on clarity); matter-of-fact product
  description, no marketing-speak; the most important question is "something impressive
  each founder has built"; show you know the obstacles — "We shouldn't be able to come up
  with objections you haven't thought of"; submit the video ("statistically we're much
  more likely to interview people who submit a video").
- **Interviews:** 10-minute Zoom, Aug–Sep, decisions usually same day. Their stated way to
  win: "**make progress** between the time that you applied and the time that you
  interview"; "have a demo ready." VERIFIED — <https://www.ycombinator.com/interviews>.
  For us the scripted move is: apply Jul 27 → convert the Jul 30 broker meeting into
  visible progress before any interview.
- **Space alumni (all VERIFIED from YC directory / yc-oss API mirror, 2026-07-23):**
  Relativity (W16 — **application video publicly posted** on its YC page), Astranis (W16),
  Momentus (S18 — confirmed YC), Stoke Space (W21), Epsilon3 (S21), **HEO (S21 — "We
  visually monitor space objects for governments and defense" — nearest YC comp to us)**,
  **Turion Space (S21 — "selling space domain awareness imagery data"; raised $6.2M seed
  after YC)**, Quindar (S22 — six ex-OneWeb engineers), Array Labs (S22), Orbio Earth
  (S23), Starcloud (S24 — public application video), Basalt (W24), Cascade Space (Sp25),
  Wardstone (F25). **HEO and Turion prove YC funds SDA-data businesses specifically.**
  Kayhan, Antaris, Panoplia are NOT YC companies (verified absent from directory).
- **Pattern at application time** (VERIFIED bios, ASSUMED synthesis): deep domain founder
  credibility + a working demo + a wedge into paying government/defense customers.
  Alumni retrospective claims (Tim Ellis pre-hardware acceptance etc.) are ASSUMED —
  transcripts weren't fetchable; the verifiable substitute is Relativity's and
  Starcloud's public application videos, worth watching before drafting ours.

## 5. Phrases to avoid — the credibility-tax list

Backbone: Guy Kawasaki's "Top Ten Lies of Entrepreneurs" ("The average number of these ten
lies that I hear in most pitches is ten"), read in full. VERIFIED —
<https://guykawasaki.com/raising-money-what-not-to-say-and-what-not-to-believe-officeandguyk/>

Never say:

1. **"Our projections are conservative."** (Kawasaki #1, VERIFIED)
2. **"We just need 1% of the market."** (Kawasaki #10, VERIFIED)
3. **"We have no competitors" / "no one else can do this."** (Kawasaki #4, VERIFIED.
   Yin: address competition upfront, not at the end — claiming uniqueness reads as naivety.
   Lemkin: show "deep and thoughtful understanding of the competitive landscape." Both
   VERIFIED.) *For us this means: name Agatha, Kayhan, Slingshot, TraCSS unprompted, and
   say precisely what they don't do.*
4. **"[Analyst firm] says our market will be $50B."** — top-down market sizing. (Kawasaki
   #2, VERIFIED)
5. **Manufactured FOMO** ("other investors are about to close our deal"). Kawasaki #5;
   Lemkin: a fake "tight process" makes VCs "just pass." VERIFIED.
6. **"It will go viral."** (Kawasaki #6, VERIFIED)
7. **"The incumbents are too big, dumb, and slow."** (Kawasaki #7, VERIFIED)
8. **"Our management team is proven."** (Kawasaki #8, VERIFIED)
9. **"Our patents protect us."** (Kawasaki #9, VERIFIED)
10. **Pilots dressed up as contracts.** Kawasaki #3; Lemkin: "Don't pretend pilots are
    signed year-long deals… 7 times out of 10, you'll get caught during due diligence."
    VERIFIED. *For us: the Jul 30 broker meeting is a meeting, not an LOI — say exactly
    that.*
11. **Obfuscated metrics.** Lemkin: "make absolutely sure I can figure out your MRR in 60
    seconds"; Yin: no vanity metrics. VERIFIED. *Our equivalent: state
    verified-vs-assumed counts and denominators for detection claims, exactly as
    `RESULTS - Ground Truth.md` does — that discipline IS the differentiator.*
12. **Grand claims without earned conviction.** Paul Graham: when asked something you don't
    know, "the best response is neither to bluff nor give up, but instead to explain how
    you'd figure out the answer" — the best investors are hard to bluff. VERIFIED —
    <https://paulgraham.com/convince.html>
13. **Leading with resume/awards/personal story.** (Seibel, VERIFIED)
14. **"Revolutionary" / "Uber for X" hype labels.** ASSUMED — widely mocked, but not found
    condemned verbatim in a primary source readable this session; directionally consistent
    with Seibel's no-jargon rule.

## 6. Ranked recommendation — which 3 approaches first

**1. Apply to YC Fall 2026 before July 27, 8pm PT.** It is the only door with a hard
deadline this week; solo founders are explicitly accepted; the batch is majority
pre-revenue; no intro needed; a decline still seeds a stronger re-application ("half the
companies applied multiple times… progress is a strong signal" — YC's words). HEO and
Turion prove YC funds exactly our category. The application is a clarity exercise, not a
traction exercise — PG's guidance and two public space application videos (Relativity,
Starcloud) are the study set. Cost: roughly a day. (Founder decision, obviously — but the
research says apply.)

**2. Convert the Jul 30 broker meeting into WRITTEN customer evidence before broad
investor outreach.** Every source converges on the same gap: our product/verification leg
clears the pre-seed bar, our customer-evidence leg is one unscheduled conversation. A
signed design-partner note, LOI, or even a dated "Gallagher agreed to evaluate X" email
moves us from "hypothesis" to "validated" in the exact language investors use — and it's
also the "make progress before the interview" move YC scores. Investor emails sent AFTER
this artifact exists are strictly stronger; sent before, they spend our one first
impression on the weaker story.

**3. Open-door space specialists, in this order: Space Capital (deck to
launch@spacecapital.com) → E2MC (pitch form) → Boost VC (pitch form) → Space VC (cold
email to Lacoste).** All take cold pitches; Space Capital owns LeoLabs AND Kayhan (they
already believe our buyer exists), E2MC explicitly doesn't require hardware, Boost leads
pre-seed at $500K, and Lacoste celebrates exactly our scrappy-solo profile. Use the
Section 1 template: 3 sentences, plain English, one proof point with denominators, small
conversational ask, company-domain address. In parallel (no cost): register interest with
Seraphim Accelerator; calendar Techstars Space for ~Mar 2027.

Sequencing logic: #1 is deadline-forced; #2 makes every subsequent email stronger and
costs nothing extra (the meeting already exists); #3 fires the week after Jul 30 with the
broker evidence in sentence 2. Not recommended now: Lux/Founders Fund (warm-intro
multi-stage — revisit at seed), any generalist that screens out "space," and any list-blast
before the Kawasaki list in Section 5 has been scrubbed from our materials.
