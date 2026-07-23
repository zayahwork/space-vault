# Operator Maneuver Disclosure — where continuous ground truth comes from

**Card:** issues/research/022 · **Written:** 2026-07-23 (night, Randy/research)
**Question:** which operators publish maneuver plans, ephemerides, or notifications — so
verification stops being an archaeology project and becomes a feed.

**Method note:** WebSearch was unavailable this session (consistent with the lane brain);
every VERIFIED claim below means I fetched the page/data myself with Python urllib on
2026-07-23 and read it. ASSUMED means inferred or from secondary text, not directly read.

Jargon: an **ephemeris** is a predicted position table for a satellite, published by the
operator from their own tracking — far more accurate than public radar catalogs. **SupGP**
is CelesTrak's service that converts operator ephemerides into standard element sets daily.

---

## The headline finding

**Intelsat publishes its maneuvers, in advance, in the open.** Their public ephemeris feed
(IESS-412 format) contains both a nominal and a **post-maneuver** ephemeris per planned
burn; CelesTrak converts both to element sets and marks the post-maneuver ones `[PM]`.
On 2026-07-23 the live Intelsat SupGP file had **127 rows, 39 of them `[PM]`**, with epochs
running out to **2026-07-28 — five days in the future**. Each `[PM]` epoch is effectively a
disclosed maneuver time for a satellite we already track. This is per-maneuver ground truth
on tap, not archaeology. (VERIFIED — fetched
`https://celestrak.org/NORAD/elements/supplemental/sup-gp.php?FILE=intelsat&FORMAT=csv`
and counted; the CelesTrak SupGP page documents the `[PM]` convention:
`https://celestrak.org/NORAD/elements/supplemental/`.)

---

## Per-operator map

Freshness = epoch range I measured in each CelesTrak SupGP file on 2026-07-23 ~08:00 UTC.

| Operator | What they disclose | Where | Cadence (measured) | Access |
|---|---|---|---|---|
| **Intelsat** | Full-fleet ephemerides **incl. planned post-maneuver sets** (IESS-412 Rev 3) | Own public portal `https://my.intelsat.com/ephemeris/public#/`; mirrored as CelesTrak SupGP with `[PM]` tags | 127 rows; epochs 07-09 → **07-28 (future-dated = pre-announced burns)** | **Open** (VERIFIED: portal linked from CelesTrak; SupGP file fetched & counted) |
| **SpaceX / Starlink** | Full-constellation post-hoc + predictive ephemerides, plus pre-launch/post-deploy state vectors per launch | Own open repository `https://api.starlink.com/public-files/ephemerides/` (MANIFEST.txt → **16,252 files** when fetched); also a copy on Space-Track public files | Continuous; SupGP epochs 07-21 → 07-23 (≈daily refresh, 10,860 rows) | **Open, no login** (VERIFIED: fetched MANIFEST.txt myself) |
| **SES** | Fleet ephemerides shared to Space-Track "with permission" | Space-Track (org-gated); open derivative = CelesTrak SupGP `FILE=ses` | 68 rows; epochs 07-22 → 07-23 (daily) | Raw feed **gated**; SupGP derivative **open** (VERIFIED: SupGP fetched; gating VERIFIED by absence from our account's public-files dirs — see below) |
| **OneWeb** | Fleet ephemerides shared to Space-Track "with permission" | Same pattern; CelesTrak SupGP `FILE=oneweb` | 651 rows; epochs 07-22 → 07-23 (daily) | Raw **gated**; SupGP **open** (VERIFIED as SES) |
| **Iridium** | Fleet ephemerides shared to Space-Track | CelesTrak SupGP `FILE=iridium` | 80 rows; epochs 07-22 → 07-23 (daily) | Raw **gated**; SupGP **open** (VERIFIED as SES) |
| **Telesat** | Fleet ephemerides shared to Space-Track | CelesTrak SupGP `FILE=telesat` | 15 rows; epochs 07-17 → 07-23 (slower/smaller fleet) | Raw **gated**; SupGP **open** (VERIFIED as SES) |
| **Amazon / Kuiper** | Ephemerides shared to Space-Track; a **public-files directory exists** (`public-data-files-24206-kuiper-prod`) | Space-Track public files (free login); CelesTrak SupGP `FILE=kuiper` | 393 rows; epochs 07-22 → 07-23 (daily) | Public-files dir **free-login**; SupGP **open** (VERIFIED: logged into Space-Track with our stored creds, listed `publicfiles/query/class/dirs`) |
| **Eutelsat** | **No ephemeris feed found.** Not on CelesTrak's SupGP source list at all | Only post-hoc channels: ITU filings / FCC market-access filings for relocations, press releases | n/a | **Nothing continuous** (VERIFIED absence from the SupGP index page; "no other channel exists" is ASSUMED — I did not exhaustively search Eutelsat's site) |

**Space-Track public-files detail (VERIFIED by logged-in query 2026-07-23):** our basic
account sees exactly three public-file sources: NASA JSC (ISS), Kuiper, SpaceX. The
OneWeb/SES/Iridium/Telesat ephemerides CelesTrak receives are **not** visible to a basic
account — so for those five operators the *open* route is CelesTrak's daily SupGP
derivative, not Space-Track itself.

**Post-hoc/regulatory channels (all operators, GEO):** FCC IBFS and ITU filings disclose
relocations and slot changes weeks-to-months later; Space-Track decay messages and GCAT
cover reentries. Useful for the historical CSV, useless as a *continuous* feed. (ASSUMED —
consistent with all prior ground-truth work in this lane, not re-verified tonight.)

---

## Ranked: the 3 feeds to tap starting this week

1. **Intelsat `[PM]` post-maneuver ephemerides (via CelesTrak SupGP).** The only feed that
   names the maneuver itself, in advance, for a constellation we already track. One daily
   fetch of `FILE=intelsat`, log every `[PM]` row (NORAD, epoch) → a self-growing
   ground-truth table our detector can be scored against *every week*, replacing the
   archaeology that built `ground_truth.csv`. ~39 events on the wire right now.
2. **SpaceX open ephemeris repository (`api.starlink.com`).** 16k files, no login, refreshed
   continuously, and the files carry predicted trajectories — comparing consecutive
   ephemerides yields planned-maneuver deltas at LEO scale. Heaviest to process, biggest
   event volume; our archiver already touches the SupGP derivative, so the raw repo is an
   incremental step.
3. **Daily SupGP snapshots for SES + OneWeb (CelesTrak).** Zero new engineering — the
   archiver already pulls operator-side SupGP; the point is retention: keep every daily
   snapshot so epoch-cadence changes and element jumps become a continuous record for the
   other two constellations we track. (Telesat/Iridium/Kuiper come free with the same loop
   if ever wanted.)

**One caution for whoever builds #1:** CelesTrak's own page footnotes that source-data
problems occasionally stall a feed (their SES 11-parameter note, their Starlink asterisk).
A tap should log staleness, not assume the file is always current. (VERIFIED — footnote read
on the SupGP index page.)
