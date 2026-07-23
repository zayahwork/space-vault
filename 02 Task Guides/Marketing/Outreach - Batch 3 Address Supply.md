---
date: 2026-07-22
type: contact-source
status: 20 new named rows queued (CSV #76–95) · 134 more verified addresses on the bench
issue: "issues/marketing/019 - batch-3 address supply.md"
---

# 📇 Batch 3 — 20 named humans, every address printed by its owner

The pipeline's ceiling was never send capacity. It was **reachable named people**: 26 of 33
space companies publish no address at all, so the drip had chewed through nearly everything
with a public inbox. This batch fixes supply the only way that has ever worked — by taking
addresses off papers the authors published themselves.

**Method (repeatable in ~20 minutes, and now scripted):** the ESA Proceedings Database at
`conference.sdo.esoc.esa.int/proceedings/list` has a keyword search *and* an
**author-organisation** filter. Ten search terms (*manoeuvre, maneuver, catalogue maintenance,
space traffic, conjunction, pattern of life, machine learning, anomaly, orbit determination,
TLE*) across SDC4–SDC9 returned **80 papers**; 59 of them printed at least one address on the
front page. **150 addresses that weren't already on file.** Zero guessing — every one is
printed by the author on their own paper. AMOS still prints none.

## The 20 queued — CSV rows 76–95

### Companies (money-shaped: they subcontract, or they'd buy analysis)

| # | Who | Why them |
|---|---|---|
| 76 | **Mark A. Skinner** — The Aerospace Corporation | Runs their Space Traffic Management research programme. **Unblocks row #50** — Aerospace's web form 403s to scripts, so until now we had no route in at all. |
| 77 | **Thomas Paulet** — CS Group | Wrote the open-source TLE-based orbit determination work. We live entirely on TLEs. |
| 78 | **Paul Lehenaff** — MDA Space UK | Co-author, ML detection & identification of on-orbit objects. A prime doing our exact ML. |
| 79 | **M. Perez** — LMO Space | Lead author on that same paper. Small UK SSA company — the size that subcontracts. |
| 81 | **Harriet Brettle** — Astroscale | Debris-removal services for large constellations. **Supersedes the info@ row #69** — write her, never both. |
| 82 | **Shrouti Dutta** — NorthStar Earth & Space | Collision-avoidance decision support — the layer our ranked list would feed. |
| 83 | **Daniele Bella** — IMS Space Consultancy | Studied differential drag for collision avoidance; differential drag is the exact signal our detector reads. Ex-UKSA/ESA secondee. |
| 85 | **Giuseppe Di Pasquale** — IENAI SPACE | Electric propulsion. Low thrust is where our detector is both weakest and most interesting. |

### Agencies and funders (slow, formal, hold the budget)

| # | Who | Why them |
|---|---|---|
| 84 | **Andrew Ratcliffe** — UK Space Agency | Co-author on the differential-drag study; the government side of who pays for this analysis. |
| 86 | **Sophie Laurens** — CNES | Analysed maneuver errors during station-keeping of an **electric** satellite — our hardest case, done rigorously. |
| 87 | **Christoph Bergmann** — DLR | Integrated manoeuvre detection and estimation with nonlinear Kalman filters. The rigorous version of what we do crudely. |
| 95 | **Igone Urdampilleta Aldama** — CDTI (Spain) | ML for SST **sensor tasking** — a ranked "look here tonight" list is exactly a tasking prior. |

### Researchers (they judge methods, not products — the only people who have ever replied)

| # | Who | Why them |
|---|---|---|
| 80 | **Prof. Djamila Aouada** — Univ. of Luxembourg SnT | Senior author on the SnT vision-for-space work; SnT runs on industry contracts. |
| 88 | **Prof. Hodei Urrutxua** — Universidad Rey Juan Carlos | AI for all-vs-all conjunction screening — the scaling problem our list shrinks. |
| 89 | **Giacomo Acciarini** — Univ. of Strathclyde | Built **Kessler**, the open ML library for collision avoidance. Closest thing to an ML-for-SSA community. |
| 90 | **Atılım Güneş Baydin** — Univ. of Oxford | The ML researcher on that same paper. |
| 91 | **Prof. Roberto Armellin** — Univ. of Auckland | Low-thrust collision-avoidance design and probabilistic orbit determination. |
| 92 | **Prof. Kyle J. DeMars** — Texas A&M | Estimation under uncertainty — the discipline our control-group workaround is standing in for. US timezone. |
| 93 | **Bogachan Ondes** — Univ. of Florida | Adjacent ML work, and the likeliest of these to simply reply. Write the student, not the advisor. |
| 94 | **Nadine M. Trummer** — Austrian Academy of Sciences | Light-curve ML — an **independent observable** that could corroborate a maneuver we only infer from the catalog. |

## Deliberately not queued (one ask per company at a time)

These addresses are verified and on file, and writing them would collide with a row we already have:

- **GMV** — 20 addresses harvested. Row #57 (Pastor) and #61 (GMV NSL) already cover them.
- **The Aerospace Corporation** — Sorge, Bernstein, Muelhaupt, Henning, Peterson, Jenkin, McVey, Mains. Skinner is the ask.
- **ESA** — 11 more addresses incl. Lemmens, Letizia, Bastida Virgili. Rows #56 and #67 already cover ESA.
- **Deimos Space** — Lubián, Grande, Piña. Row #60 (Kerr) covers them.
- **Sybilla / OKAPI / Guardtime** — rows #63, #59, #65 already cover them, all on `hold` as contract pitches.
- **CS Group** — Cazabonne, same paper as Paulet.
- **IMS** — Vitali Braun, same paper as Bella.
- **PoliMi** — Gonzalo, Palermo. Rows #54/#55 cover them.

## Parked, needs a founder decision

- **NSSC / Chinese Academy of Sciences** (`wangrl@nssc.ac.cn`) — *Starlink Satellite Classification and Orbit Maneuver Detection*. Same satellites, same problem, genuinely relevant. A US space startup opening a channel with a Chinese state research institute is the founder's call, not a routine row. **Read the paper anyway — it's public.**
- **RAND Europe** (4 addresses) — a policy shop that *buys* analysis, on a cislunar space-traffic concept note. Money-shaped but not technical; worth a decision on whether we sell analysis to think tanks at all.

## What's still on the bench

**134 verified addresses** remain unqueued after the conflict rules above — the harvest, the
extraction and the dedupe are scripted, so widening the keyword list or adding IAC/AMOS-adjacent
venues costs about twenty minutes. **Supply is no longer the binding constraint; the constraint
is now how many hand-written emails we can honestly produce per day.**

> [!warning] These rows are supply, not sends
> Nothing here was emailed. The eight `academic` rows physically cannot be sent by machine — the
> academic template carries a placeholder `outreach.py` refuses to send — so each needs a real
> question written after reading the paper, exactly like rows 54–58 and 68.
