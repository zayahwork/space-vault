# 🏛️ Guide — SBIR Steps (the government-pays-us-to-build path)

**Refresher:** SBIR = the US program that PAYS small companies to build new tech (not a loan,
not investors — you keep the company). Space Force's door = **SpaceWERX**. Full plain-English
decode in [[Glossary]]. Deep background: [[DEEP_RESEARCH_2026-07-20]] §2.

## 1) Read the topic list that opened Jul 22 — ⏰ closes Aug 18

- Go to `spacewerx.us/get-funded` → follow the link to the **DSIP portal**
- Find **"DOW SBIR Specific Topic 26.BX Release 4"** → read every topic title
- Looking for: anything about **SDA / tracking / maneuvers / space domain awareness**
- If one fits → copy its full text into the log below and tell Claude. We decide the
  "sprint to Aug 18?" question *deliberately* — no panic-applying.
- If none fit → fine. Our real target is the **Open Topic** anyway (next task).

## 2) Find the next Open Topic window
While on DSIP: Open Topic = pitch-your-own-idea, built for newcomers, Phase I ≈ $150K and
includes *paid* customer discovery. Find when the next window opens and note it below.

## 3) Start SAM.gov registration — ⏰ start NOW, it takes days–weeks
- `sam.gov` → register the business (free). This is the government's registry; no registration,
  no payment, ever. You'll need a business name — pick a working name; it can be simple.
- Expect identity checks and waiting. Start it, let it grind in the background.

## 4) Read what a Phase I proposal contains
On the SpaceWERX "Get Funded" pages: volumes, page limits, structure. Goal is only
familiarity — so when we write one, the format is already boring instead of scary.

## 📓 Log (write here)
- **26.BX topics found — 2026-07-21, scanned live: NOTHING FOR US.** `06 Code/sbir_scan.py`
  pulled all **72** pre-release/open DoD topics straight from the DSIP API. Component split:
  USAF 14, NAVY 15, MDA 10, OSD 10, DARPA 9, ARMY 7, DLA 3, DHA 2, SOCOM 2 — **zero USSF.**
  Only 3 topics are even space-adjacent (directed energy for space, commercial satellite
  imagery optimization, intra-satellite comms) and two of those **close Jul 22**. No SDA, no
  maneuver, no tracking, no catalog. **Decision: do not sprint for Aug 18.** Full report:
  [[SBIR Scan - 2026-07-21]]. Re-run the scanner any time: `python sbir_scan.py`.
- **Next Open Topic window: not announced.** SpaceWERX "Get Funded" lists only the specific-topic
  releases (26.BZ R3 closes Jul 22; 26.BX R4 opens Jul 22, closes Aug 18) plus continuous TACFI.
  The AFWERX Open Topic page still shows the 25.5/E Release 10 overview with no forward dates.
  Nothing to schedule around yet — the scanner will show a USSF row the moment one appears.
- SAM.gov status: **not started — this is now the only real SBIR deadline item.** It takes
  days to weeks and gates every future application, including the Open Topic we're actually
  aiming at. Starting it costs nothing and nothing else here is time-critical.
