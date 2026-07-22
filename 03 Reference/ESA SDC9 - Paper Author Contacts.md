---
date: 2026-07-22
type: contact-source
status: 25 published addresses harvested — 5 queued as CSV rows, rest are bench
parent: "[[Contract Work - Space ML Subcontract]]"
---

# 📇 ESA SDC9 — paper authors who print their email

The AMOS pass found nothing because AMOS doesn't print author contacts. The **9th European
Conference on Space Debris** (Bonn, April 2025) does — it's the venue's house style. Same
method, right conference.

**How it was done** (repeatable in ~15 minutes): the ESA Proceedings Database at
`conference.sdo.esoc.esa.int/proceedings/list` has a keyword filter. Searched *manoeuvre*,
*maneuver*, *pattern of life*, *machine learning*, *anomaly* → **16 SDC9 papers**, downloaded
each PDF, pulled the addresses off the front page. **11 of 16 printed at least one.**

## The ones that matter — our exact problem, in someone else's words

| Paper | Who | Address | Why they matter |
|---|---|---|---|
| **Manoeuvre identification and characterization from two-line elements** | Yeerang Lim, **Camilla Colombo** — Politecnico di Milano | `yeerang.lim@polimi.it` · `camilla.colombo@polimi.it` | **This is our method, published.** TLE-only manoeuvre ID. Read it before writing — the email must engage with what they actually did |
| **Unsupervised learning-based manoeuvre detection for RSO pattern-of-life** | Enrico Raviola, Riccardo Cipollone — PoliMi | `enrico.raviola@mail.polimi.it` | Unsupervised, pattern-of-life — the same wedge from the academic side |
| **Improving Metrics for Satellite Anomaly Detection** | **Jan Siminski — ESA Space Debris Office** | `jan.siminski@esa.int` | The institution that *runs* European debris work. "How should anomaly detection be scored" is exactly our unanswered question |
| **Algorithms for robust tracking of manoeuvring space objects in catalogues** | Alejandro Pastor + 8 others — **GMV** | `apastor@gmv.com` (also `jrgarcia@`, `aflorez@`, `daranda@`, `enasini@`, `felix.stechowsky@`, `juan.velasco.mariscal@`) | GMV is a top-tier European SST contractor. Nine published addresses in one paper |
| **Efficient Cataloguing of Manoeuvrable Satellites** | Paula Díaz Morales + 3 — **Indra** | `pdmorales@indra.es` (also `dgilc@`, `arigo@`, `amazzoleni@`) | Spanish defence/space prime doing catalogue maintenance for manoeuvring objects |
| **Approximating Orbit Uncertainties using Neural Networks** | Matthew Popplewell, Samuel Kwon — **Advanced Space** | `matthew.popplewell@advancedspace.com` · `samuel.kwon@advancedspace.com` | See the convention note below |
| **ML for Identification of LEO objects** | Bogachan Ondes, Norman Fitz-Coy — Univ. of Florida | `bogachan.ondes@ufl.edu` · `nfc@ufl.edu` | Academic, adjacent, easy first reply |
| **Single-photon light-curve feature extraction** | Nadine Trummer — Austrian Academy of Sciences | `nadinemaria.trummer@oeaw.ac.at` | Adjacent; useful if the photometry angle ever opens |

> [!success] Free cross-check: Advanced Space's email convention is confirmed
> Two Advanced Space authors print `first.last@advancedspace.com`. That independently confirms
> `patrick.miga@advancedspace.com`, the address we mailed at 02:15 on Jul 22 — it was right.
> **Do not write Popplewell or Kwon.** Same company, live thread with Miga, and the conflict
> rule says one ask per company at a time.

> [!warning] One to leave alone for now
> Paper 48, *Starlink Satellite Classification and Orbit Maneuver Detection* — `wangrl@nssc.ac.cn`,
> **National Space Science Center, Chinese Academy of Sciences**. Same satellites, same problem,
> genuinely relevant work. But a US space startup opening a channel with a Chinese state
> research institute is a decision for the founder, not a routine outreach row. Parked, not
> queued. Worth reading the paper regardless — it's public.

## What went into the CSV

Rows **54–58**: Lim/Colombo, Raviola, Siminski, Pastor (GMV), Díaz Morales (Indra).

All five are filed as segment `academic` **on purpose**, even the two industry ones. The
academic template contains a deliberate placeholder — *"[ONE specific question about their
paper]"* — and `outreach.py` refuses to send any email that still contains it. So these rows
sit in the queue visibly but **cannot go out until someone reads the paper and writes the
question by hand**. That is the correct behaviour for paper authors: a generic email to a
researcher is a wasted email, and this one is wasted on the people closest to our own problem.

## Do this again

The same 15 minutes works for **SDC8 (2021)** and **SDC7 (2017)** — that's where
`hendrix@exoanalytic.com` came from — and the keyword list can widen (*conjunction*,
*catalogue*, *TLE*, *space traffic*). Roughly two dozen more published addresses are sitting
there. Cheapest contact source found so far, by a distance.
