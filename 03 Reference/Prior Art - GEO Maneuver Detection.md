---
title: Prior Art — GEO maneuver detection from public element sets
type: reference
status: sweep complete 2026-07-22; every claim marked verified or assumed
audience: whoever builds the GEO verifier (Tim)
context: "[[RESULTS - Ground Truth]], [[RESULTS - Beyond Starlink]]"
---

# 📚 Prior art — spotting GEO station-keeping and relocations from public elements

> [!important] Read this first — it will save you a week
> **1. Every published method here works on the public catalog alone.** None of them use
> operator-supplied ephemeris (SupGP). Our gap-vs-catalog signal isn't in this literature —
> which is good for us commercially, but it means **you cannot lift their thresholds
> directly.** For the GEO verifier, build on `GP_HISTORY`; that's where the prior art lives
> and where our archive is actually deep.
>
> **2. Two independent groups measured the detection lag we hit yesterday.** Decoto reports
> detections landing **an average of 4 days late (min 0, max 7)**; Kelecy builds an explicit
> **"lag parameter"** into his algorithm for the same reason. Our `WINDOW_DAYS = 3.0` is
> below the floor the field already knows about. That's now three sources, not a hunch.
>
> **3. Don't trust a headline accuracy number in this field.** Roberts reports **99.7%
> accuracy and 28.9% precision on the same task.** See §"The precision trap".

---

## The seven methods, at a glance

| # | Method | Signal it reads | Threshold / setting | Our archive can feed it? |
|---|---|---|---|---|
| 1 | **Decoto & Loerch 2015** — RIC lead/trail comparison | Radial+InTrack (E–W), CrossTrack (N–S) | 2σ potential, 1σ confirm, 20 km filter | ✅ **yes, best fit** |
| 2 | **Kelecy et al. 2007** — polynomial segment differencing | orbital energy (a), inclination | user-set σ + explicit lag term | ✅ yes |
| 3 | **Lemmens & Krag 2014** — TCC + TTSA | published vs propagated state; element series | not published in the abstract | ✅ yes (TCC), ⚠️ TTSA needs tuning |
| 4 | **Roberts & Linares 2021** — CNN on longitude | ECEF longitude/lat/alt time-series | 28-day frames, 14-day step | ⚠️ yes, but needs labels |
| 5 | **Li et al. 2024** — 2D CNN, 3-class | TLE series → EW / EW-NS / NM | classification, not detection | ⚠️ needs labels |
| 6 | **Lim & Colombo 2025** — inverse Gauss planetary eqns | element deltas → ΔV vector | least-squares, no σ gate | ✅ yes, as a *characteriser* |
| 7 | **Patera** — moving-window anomaly filter | orbital energy | not verified — see caveat | ✅ presumed |

---

## 1. Decoto & Loerch (2015) — the closest thing to a blueprint

**VERIFIED.** *Technique for GEO RSO Station Keeping Characterization and Maneuver
Detection*, Jacob Decoto & Patrick Loerch, Orbital ATK, AMOS 2015.
<https://amostech.com/TechnicalPapers/2015/SSA/Decoto.pdf>

**This is the one to copy.** GEO-specific, built explicitly "to work within the limitations
of the Two Line Element (TLE) data from the public catalog," and it publishes its numbers.

**Method (verified, §3.2):** filter single-point outliers; then for every orbit state, take a
window of **3 leading + 3 trailing states**, propagate them and the centre state to common
epochs, and compare each pair **over one orbital period**. Record max Radial, In-Track and
Cross-Track deltas in the RIC frame — **9 comparisons per state**. Then:
- **Out-of-plane (N–S) → CrossTrack component**
- **In-plane (E–W) → Radial + In-Track components**

**Thresholds (verified, Table 1 — GEO defaults):**

| parameter | GEO default | their LEO/Envisat setting (Table 3) |
|---|---|---|
| Lead/Trail Range Filter | **20 km** | 2 km |
| Potential Maneuver Threshold | **2 σ** | 4 σ |
| Maneuver Flag, Lead vs. Trail | **1 σ** | 0.75 σ (0.6 σ in-plane) |
| Maneuver Flag, Lead vs. Centre | **1 σ** | 0.75 σ (0.6 σ in-plane) |
| Frequency Fit Window | **4 days** | 4 days |

**Validation (verified):** on Envisat, Jan–Jun 2003, **all 8 ESA-reported maneuvers detected,
2 false positives** — and detections landed **an average of 4 days after the true epoch, min
0, max 7.**

**Second method worth stealing — the frequency fit.** Rather than finding individual burns,
it fits a *station-keeping cadence*: it tests every whole-number period from **8 to 65 days**
with phasing in **0.5-day increments (4,234 combinations)**, and picks the pair that best
explains the residuals. **This is the closest published thing to what `quiet.py` is trying to
do** — and it's a brute-force grid search, not ML. Cheap to implement.

**Known requirement (verified):** the default metric needs **three consistent orbit states
before a maneuver** to fire. Sparse GEO data will silently suppress detections.

**GEO physics constants it gives you for free (verified, §2):**
- Inclination drifts **~0.85°/year**, costing **~46 m/s/year** — N–S is usually the biggest
  propellant line item.
- Longitude drifts toward **gravity wells at 73°E and 104°W**.
- E–W station-keeping imparts **0.05–0.2 m/s per maneuver**.
- Station-keeping boxes are typically **±0.1° or less**.
- **Chemical propulsion → burns weekly to every couple of months. Electric → often multiple
  times per day.** *(This is why cadence-based detection needs to know the propulsion type
  first — an electric bird has no "quiet" gaps to notice.)*

> **Sanity check against our own data:** we measured AMC 11's N–S corrections at
> 0.0435–0.0471°. At Decoto's 0.85°/yr natural drift that's ~3 weeks of accumulated
> inclination per burn — consistent with the chemical-propulsion cadence above.
> → [[RESULTS - Ground Truth]]

---

## 2. Kelecy, Hall, Hamada & Stocker (2007) — the classic, but it's a LEO paper

**VERIFIED.** *Satellite Maneuver Detection Using Two-line Element (TLE) Data*, AMOS 2007.
Boeing LTS / Pacific Defense Solutions / AFRL DET-15.
<https://amostech.com/TechnicalPapers/2007/Modeling_Analysis_Simulation/Kelecy.pdf>

**Method (verified):** fit a polynomial to a trailing segment and a leading segment, take the
difference at an extrapolated midpoint, and flag anything exceeding a user-defined σ
threshold computed from the data's own noise statistics.

**The bit that matters for us (verified, direct quote):** the algorithm includes a **"lag
parameter"** for the gap between the detection peak and the true maneuver time — *"There is
likely some characteristic time, measured on the order of days, that is required for the
state to converge."* **Independent confirmation that catalog lag is structural, not a bug in
our code.**

**Performance (verified via Decoto's citation):** 49 of 78 Envisat maneuvers detected
(**63%**) with no false positives, over three years.

⚠️ **Caveat — mark this before you lean on it.** Kelecy's worked examples are **Topex and
Envisat, both LEO**. It is the field's standard reference, but it is *not* a GEO result. Its
σ-threshold approach transfers; its tuning does not.

**ASSUMED:** that Kelecy's approach applies cleanly at GEO. Nobody in this sweep demonstrated
that; Decoto effectively re-derived it for GEO instead.

---

## 3. Lemmens & Krag (2014) — the ESA pair, TCC and TTSA

**VERIFIED (existence, venue, method names).** *Two-Line-Elements-Based Maneuver Detection
Methods for Satellites in Low Earth Orbit*, S. Lemmens & H. Krag (ESA/ESOC), **Journal of
Guidance, Control, and Dynamics, 37(3), pp. 860–868, 2014**, DOI `10.2514/1.61300`.
<https://arc.aiaa.org/doi/10.2514/1.61300>

Two named methods, described here as summarised by Lim & Colombo (§1 of their paper):
- **TCC — TLE Consistency Check:** compare a *published* state against a *propagated* state.
  Cheap, stateless, and **this is the closest published analogue to our gap detector** — the
  difference being that both their states come from the catalog, where one of ours comes from
  the operator.
- **TTSA — TLE Time Series Analysis:** extrapolate the element series and test epochs outside
  the extrapolation window, using robust statistics and harmonic analysis.

⚠️ **Title says Low Earth Orbit.** The abstract claims the methods "process the entire
two-line element catalog… in the different orbital regimes," but the paper is framed as LEO.

**ASSUMED:** the specific σ thresholds. **I could not read them** — the paper is paywalled at
AIAA and I did not obtain the full text. Do not quote numbers from this one until someone
reads it.

---

## 4. Roberts & Linares (2021) — MIT, CNN on longitude, and the honest failure numbers

**VERIFIED.** *Geosynchronous satellite maneuver classification via supervised machine
learning*, Thomas G. Roberts & Richard Linares (MIT), AMOS 2021.
<https://amostech.com/TechnicalPapers/2021/Machine-Learning-for-SSA-Applications/Roberts.pdf>

**Method (verified):** convert TLEs to **geographic position histories** (longitude, latitude,
altitude in ECEF) using SGP4/SDP4 via PyEphem, segment into **28-day frames with a 14-day
step**, normalise longitude to [0,1], and train a CNN to spot six maneuver components:

| code | meaning |
|---|---|
| IE / IW | initiate eastward / westward drift |
| EE / EW | end eastward / westward drift |
| JE / JW | "jump" — start *and* end a drift inside the duration threshold |

Trained on 2010–2019, tested on the whole GEO population in 2020.

**Practical constraint (verified):** *"TLEs should not be propagated forward or backwards by
more than two weeks."*

**Useful base rate (verified):** only **71 GEO satellites performed a longitudinal shift
maneuver of any kind in all of 2020.** Relocations are rare events — plan your false-positive
budget accordingly.

### The precision trap — the single most useful table in this note

**VERIFIED, Table 2:**

| class | accuracy | recall | **precision** | F1 |
|---|---|---|---|---|
| IE | 99.7% | 65.0% | **28.9%** | 40.0% |
| EE | 99.5% | 91.3% | **18.1%** | 30.2% |
| JE | 99.8% | 64.6% | **16.3%** | 26.0% |
| IW | 99.7% | 89.6% | **50.9%** | 65.0% |
| EW | 99.7% | 91.6% | **36.4%** | 52.1% |
| JW | 99.8% | 98.1% | **11.7%** | 20.9% |

**MIT, ten years of training data, and the best precision on the board is 50.9%.** Four
classes are under 30% — i.e. **two to eight false alarms for every real maneuver.** The 99.7%
accuracy is an artefact of ~400,000 true negatives; it means nothing.

**What this tells you before you write a line of code:** GEO relocation detection from public
elements is a *low-precision* problem at the state of the art. If our verifier comes out at
50% precision, that is **competitive**, not broken. And if it comes out at 95%, check for a
bug before celebrating.

---

## 5. Li et al. (2024) — 3-class station-keeping classifier, and why its 94% isn't comparable

**VERIFIED (existence, venue, metrics).** *A station-keeping maneuver detection method of
non-cooperative geosynchronous satellites*, **Advances in Space Research, vol. 73, p. 160
(2024)** (online Oct 2023). ADS: `2024AdSpR..73..160L`.
<https://www.sciencedirect.com/science/article/abs/pii/S0273117723008141>

**Method (verified):** 2-D CNN on public TLE series, classifying into three categories —
**EW** (east–west station-keeping), **EW-NS** (simultaneous), and **NM** (no maneuver). The
labels describe *which station-keeping is being maintained*, not the impulse direction.

**Results (verified):** macro **F1 94.45%**, precision **94.48%**, recall **94.46%**.

⚠️ **Do not compare this to Roberts' numbers.** This is a **classification** task — given a
window, which of three classes is it? Roberts solves **detection** — find the rare events in a
continuous stream against ~400,000 negatives. Class balance explains nearly the whole gap.
**Ours is a detection problem, so Roberts is the fair benchmark, not this.**

**ASSUMED:** the full author list. I have the ADS bibcode (first author surname begins with L)
but did not verify the names — the paper is paywalled. Cite it by title until someone checks.

---

## 6. Lim & Colombo (2025) — reconstructs the ΔV, doesn't just flag it

**VERIFIED.** *Manoeuvre Identification and Characterisation from Two Line Elements*,
Yeerang Lim & Camilla Colombo, Politecnico di Milano. **9th European Conference on Space
Debris (SDC9), Bonn, 1–4 April 2025**, paper 241.
<https://conference.sdo.esoc.esa.int/proceedings/sdc9/paper/241/SDC9-paper241.pdf>

**Method (verified):** least-squares estimation that **inverts Gauss' planetary equations** to
recover the ΔV vector *and its epoch* from a change in orbital elements. Uses argument of
latitude in place of argument of perigee + true anomaly, for measurement-accuracy reasons.
Validated against Envisat TLE history.

**Why it's worth knowing:** every other method answers *"did something happen?"* This one
answers *"how big was the burn, in which direction."* **That's the difference between an alert
and an insurance-grade report** — the buyer in [[Idea - Who Else Pays for Went Quiet]] cares
about magnitude, not just occurrence.

**Stated limitation (verified):** it must *assume* a burn direction (e.g. along-track only) to
close the solution, and the authors say plainly it "is not valid for an unexpected event such
as collision or explosion." **So it cannot characterise the Intelsat 33e class of event** —
exactly the events an insurer would ask about. Detection first, characterisation second.

**Bonus — a TLE outlier-filter recipe (verified, 5 steps):** drop TLEs that merely correct the
immediately-previous element set (minimum update-time threshold); identify large gaps to
define outlier-search windows; drop incoherent inclination values; drop incoherent
eccentricity values; drop negative B\* drag terms.

---

## 7. Patera — the moving-window ancestor

⚠️ **ASSUMED — attribution only.** Lim & Colombo credit R. Patera with the **moving-window
method** for filtering orbital anomalies from perturbation noise, applied to an orbital-energy
plot and used for collisions, maneuvers and even solar-activity effects. **I did not locate or
read the original Patera paper in this sweep**, so treat the method description as
second-hand. If you want the primary source, that's an open item.

---

## What our archive can and cannot feed

| data we hold | depth | feeds which methods |
|---|---|---|
| **Space-Track `GP_HISTORY`** (public catalog, all past versions) | **years**, ~2–4 epochs/day at GEO | **1, 2, 3, 4, 5, 6, 7 — all of them** |
| Space-Track `SATCAT` (decay records) | full | ground truth only |
| **Our SupGP archive** (operator ephemeris) | **12 hours of catalog-bearing snapshots** | **none of them** |

**The operative conclusion for the GEO verifier: build it on `GP_HISTORY`, not on the SupGP
archive.** Every method in this sweep runs on catalog history, our catalog history is years
deep, and our SupGP archive is twelve hours deep. The SupGP gap signal is our commercial
differentiator, but it is not what a GEO verifier should be made of today.

## Suggested build order

1. **Decoto's RIC lead/trail comparison** at the published GEO defaults (2σ / 1σ / 20 km,
   3 lead + 3 trail). It is the only GEO-specific method in the literature with published
   thresholds and a published validation.
2. **Split in-plane from out-of-plane** the way Decoto does — CrossTrack for N–S, Radial +
   In-Track for E–W. This is the "independent inclination channel" from
   [[RESULTS - Ground Truth]], and the prior art says to build it that way.
3. **Set the detection window to ≥7 days, not 3.** Decoto measured max 7 days late; Kelecy
   built a lag term for it; we measured +10 days on Intelsat 33e. Three is indefensible.
4. **Judge yourself against Roberts, not against Li.** Detection, not classification. ~50%
   precision is the bar to beat.
5. Later, add **Lim & Colombo's Gauss inversion** to turn a detection into a ΔV number.

---

## Evidence marks — summary

| claim class | mark |
|---|---|
| Methods 1, 2, 4, 6 — full text read, thresholds and results quoted from the PDFs | **verified** |
| Method 3 (Lemmens & Krag) — existence, venue, DOI, method names | **verified** |
| Method 3 — its σ thresholds | **assumed / unread** (paywalled) |
| Method 5 — existence, venue, F1/precision/recall | **verified** |
| Method 5 — author list | **assumed** (ADS bibcode only) |
| Method 7 (Patera) — attribution via Lim & Colombo | **assumed** (primary not read) |
| That Kelecy's LEO tuning transfers to GEO | **assumed — and I doubt it** |
| SDC9 = Bonn, 1–4 April 2025 | **verified** |

## Sources

- Decoto & Loerch, AMOS 2015 — <https://amostech.com/TechnicalPapers/2015/SSA/Decoto.pdf>
- Kelecy, Hall, Hamada & Stocker, AMOS 2007 — <https://amostech.com/TechnicalPapers/2007/Modeling_Analysis_Simulation/Kelecy.pdf>
- Lemmens & Krag, JGCD 37(3):860–868, 2014 — <https://arc.aiaa.org/doi/10.2514/1.61300>
- Roberts & Linares, AMOS 2021 — <https://amostech.com/TechnicalPapers/2021/Machine-Learning-for-SSA-Applications/Roberts.pdf>
- Li et al., Adv. Space Res. 73:160, 2024 — <https://www.sciencedirect.com/science/article/abs/pii/S0273117723008141>
- Lim & Colombo, SDC9 paper 241, 2025 — <https://conference.sdo.esoc.esa.int/proceedings/sdc9/paper/241/SDC9-paper241.pdf>
- Roberts, *Satellite Repositioning Maneuver Detection in GEO Using TLE Data* (1-D CNN on longitude) — <https://www.researchgate.net/publication/344631183>
- 9th European Conference on Space Debris, dates/venue — <https://spacepolicyonline.com/events/9th-european-conference-on-space-debris-apr-1-4-2025-bonn-germany/>

**Not found in this sweep:** any CNES-authored GEO maneuver-detection paper. I searched for
one specifically and came up empty — that's a gap in this note, not evidence that none exists.
