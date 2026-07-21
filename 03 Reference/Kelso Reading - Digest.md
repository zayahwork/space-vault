---
title: "Kelso reading digest — what his roadmap actually says"
type: reference
created: 2026-07-21
tags: [kelso, ssa, research, wedge]
---

# 📖 Kelso reading digest (Jul 21)

What his curated reading list actually contains, plus **our own analysis of his live data**.
Two findings change the plan — they're at the bottom, don't skip them.
PDFs saved locally: `03 Reference/kelso-pdfs/`.

---

## 1. SMOPS-2026 keynote — "Today's Challenges in SSA"

His public numbers, useful in any conversation:

- CelesTrak processes **11,571 of ~14,985 active satellites**; no data for **~a quarter** of the active population.
- **1,073 unknown objects** in the Space-Track SATCAT; 303 decayed while still unidentified.
- GPS satellites lost for **20 days**; another **10 days and off by over 500 km** — while the operator was publishing maneuver notices the whole time.
- One active satellite untracked **240 days** despite daily operator data sharing.
- SSN takes **almost a week** to identify Starlink objects. **CelesTrak does it in 8 hours.**
- 2,800 dead satellites + 2,180 rocket bodies uncontrolled.

## 2. IAC-2025 — "Data Limitations for Conjunction Assessments" (the important one)

> "Sure, the force models are pretty simplistic and they don't include maneuvering… If you think it's because of the SGP4 force model, you would be wrong."

**Why public GP data is wrong isn't SGP4 — it's the pipeline:**
- SSN sensors still return **3 observations per pass** (first, middle, last), unchanged for decades, and are mostly Northern-Hemisphere.
- **Short fit spans are chosen deliberately "to avoid processing through unknown—and unmodeled—maneuvers."**
- 18 SDS maneuver-detection techniques "aren't particularly efficient" — built when few satellites maneuvered.
- **SP data is not the escape hatch.** GP is *derived from* SP via `eGP`. "If the GP data is bad, so is the SP data." Neither models maneuvers. Same for the coming XP.
- The **CDM has no maneuver force term** — fitting an ephemeris to the CDM's force model "smoothed out any maneuver information." His fix: carry the original OEM/OPM/OMM instead of inventing a fourth format.

> ⚠️ **Read this against our detector:** the public data we're using is *actively smoothed around the
> exact events we're trying to detect*, and short fit spans hide maneuvers by design. That's not a
> reason to stop — it's the reason GOES-18 came out noise-drunk, and it means our accuracy ceiling
> on raw GP alone is real. It also means anyone claiming clean maneuver detection from GP data
> without saying this is either naive or bluffing. **Saying it out loud is a credibility asset.**

**The mitigation he built — and this is the gift:** **SupGP** (Supplemental GP). He fits operator
ephemerides/almanacs with SGP4 to produce high-accuracy TLE-format data, for **9,621 of 12,557
active satellites (76.6%)**, refreshed **every 30 minutes**, all free and public:

| What | URL |
|---|---|
| SupGP vs GP RMS comparison (the disagreement table) | `celestrak.org/NORAD/elements/supplemental/table-rms.php?UNIQUE&WORSE-THAN=25` |
| Same, Starlink only | `…table-rms.php?STARLINK&WORSE-THAN=25` |
| Active satellites with oldest (stalest) GP data | `celestrak.org/NORAD/elements/table.php?GROUP=active&SHOW-OPS&OLDEST` |
| Per-object **2.5-year SupGP history graph** — maneuvers visible | linked from each SupGP table row |

Real magnitudes he cites: GPS BIII-7 GP data 11 days stale, RMS diff **89.269 km**. One live case of
SupGP-vs-source ~600 m while GP-vs-SupGP was **~4,400 km**. **1,031 of 8,381** Starlink objects with
SupGP had GP RMS over 25 km (**12.3%**). Comparing 9,734 element sets at 1-min intervals over 6 hours:
**11.794 seconds**.

## 3. IAC-2017 — "Challenges Identifying Newly Launched Objects"

**His technique, concretely:** an assignment/matching algorithm. Not instantaneous range — he found
that insufficient because two orbits can be close at one instant then drift apart. Instead:
**RMS difference between each pair of orbits propagated over several orbits**, used as the assignment
metric (close proximity *and* matching mean motion). Auto-pulls latest data from both sides each run.
Output has four sections: best mapping, unique mappings, multiple-match candidates, and **no-match**.

**Results:** validation had zero false positives/negatives; matches ran 0.1–15 km RMS (most under 2 km),
non-matches in the *thousands* of km — a clean separation. Daily runs took **about a minute** for 104
objects. On PSLV-C37 (104 payloads) it beat JSpOC by a week-plus; JSpOC hadn't finished some initial
identifications **5 weeks after launch**. By KANOPUS-V-IK it was down to a couple of days.

> 🚨 **The catch that decides the wedge:** the technique needs **independent operator orbital data**
> on the other side of the match — Planet's own two-way ranging. Kelso says it plainly: *"when operator
> data was not available for other payloads, associations of TLEs with specific objects was
> significantly delayed."* And in 2025: *"We regularly have problems on Transporter and Bandwagon
> launches where objects aren't identified for months (some never)."*

---

## 4. 🔬 Our own analysis of his live data (not in any paper)

Pulled the full `first-gp-by-launch` table (2.8 MB, 156 launches in 2026) and computed the trend.
Script-reproducible; numbers as of 2026-07-21.

**Median days from launch to first GP data, all launches:**

| 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| 0.65 | 0.72 | 0.68 | 0.88 | 0.93 | 1.15 | 1.58 | **2.71** |

**The median has more than quadrupled since 2019, and has risen every year since 2021.** This is the
median, not an outlier artifact — the typical launch, not the worst one. Kelso's "getting worse" is
quantitatively true.

**The rideshares are the extreme, exactly as he said:**
- **TRANSPORTER-17** (launched Jul 7) — **12.62 days** to first GP: *the single worst delay of all 156
  launches in 2026*. Still carried as **"OBJECT A", source "TBD"** — unattributed 14 days after launch.
- **TRANSPORTER-16** (launched Mar 30) — 8.33 days, **also still "OBJECT A" / "TBD"** nearly four
  months later. This is his "some never" case, live.

**Honest counter-observation (don't overclaim):** Starlink's own median actually *improved* slightly
YoY (7.02 d in 2025 → 5.67 d in 2026), though within 2026 it drifted worse (5.00 d Jan–Mar → 6.50 d
Apr–Jul). The degradation is in the *population as a whole*, not uniform across operators.

**Bonus catch:** `2026-164 / AAGAMAN` carries NORAD catalog number **100080** — six digits. The 5-digit
catalog overflow isn't approaching, it's *in the published table now*. Confirms the Day-1 read that
legacy TLE-format software is breaking, and it's a good conversation opener.

---

## 5. ⚖️ Two findings that change the plan

### A. SupGP is a better validation set than SPLID
We committed to an honesty rule: SPLID is partly simulated, so claims get verified on live data.
**SupGP is the live data with near-truth attached** — 76.6% of active satellites, refreshed every 30
minutes, free, with a published per-object 2.5-year history and an RMS disagreement table that is
effectively *a continuously-updated label of where the public catalog is wrong.*

Concretely: where GP-vs-SupGP RMS spikes, something happened that GP missed — often a maneuver.
That's a training signal and a scoreboard, generated by someone else, for free. **Use SPLID to learn
the problem shape; validate against SupGP-vs-GP.** Worth raising at the SPLID build session before
we sink days into the 4 GB download.

### B. The launch-ID wedge is real but narrower than it looked
Kelso **solved the cooperative case in 2017** — if you have operator data, his matcher works and it's
about a minute of compute. Building an ML version of that is re-solving a solved problem, and he'd
know immediately.

**What's still open is the non-cooperative case:** attributing unknown objects when *only the public
side exists* — no operator ephemeris to match against. That's what leaves TRANSPORTER-16 and -17
sitting as "OBJECT A / TBD" today. The available signal is thin and indirect (deployment sequence and
timing, orbit clustering, ballistic-coefficient/drag signature as a proxy for form factor, launch
manifests). Genuinely hard — which is why it's open nine years later.

**So the honest framing is:** *"Kelso solved this when operators cooperate. The open problem is the
launches where they don't."* Sharper than "launch ID is unsolved," true, and it shows we read the
paper instead of the abstract. Take it to [[Guide - Week Synthesis|synthesis]] as a candidate — still
not a pivot.
