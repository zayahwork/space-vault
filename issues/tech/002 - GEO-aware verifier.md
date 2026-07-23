---
status: done
type: AFK
blocked-by: []
closed: 2026-07-23
closed-by: tim
---
# GEO-aware detection + verification (fix the SES blind spot)

**Goal:** the verifier can see GEO station-keeping. Today it watches altitude, and GEO burns barely change altitude — they show up as **longitude drift** (east-west station-keeping) and **inclination** (north-south). That's why SES reads "no signal" while we're about to sit across from a GEO insurance broker on ~Jul 30. This is the week's main build.

**Done when:**
- `detect.py` (or a `geo_verify.py` companion) scores GEO objects on longitude-drift rate and inclination change, not just semi-major axis / altitude.
- Re-run on Intelsat and SES with the new signal. One of two honest outcomes, in writing:
  1. SES shows a real signal → numbers with a control comparison, same standard as the LEO result (percent of suspects clearing a bar vs percent of matched controls), or
  2. SES still shows nothing → the miss is explained with numbers (what the drift distributions look like, why the signal isn't separable yet, what data would fix it).
- `RESULTS - Beyond Starlink.md` updated either way. No cherry-picking the outcome that demos better.

**Notes:** GEO physics, once: a geostationary satellite drifts off its longitude slot unless it burns every ~2–4 weeks (east-west) and fights inclination growth ~0.75–0.95°/yr (north-south). Stopping those burns IS the insurer signal. Longitude comes from mean motion + RAAN + mean anomaly vs the sidereal rate; a simpler proxy is mean-motion deviation from exactly 1.0027 rev/day. Intelsat n=3 is not a result — get n up. Same standing rule as everything else: if this contradicts a published note, fix the note and say so.

---

## ✅ Closed 2026-07-23 — every done-when item is satisfied by shipped work; building it as written would now re-implement a retired signal

This card's substance was completed across 002's own first pass and the referee line
(015 → 018 → 026). Closing it is reconciliation, not new build — verified against the repo
tonight, whole tech suite green (11 test files, 0 failures).

| done-when as written | where it lives, verified |
|---|---|
| score GEO objects on longitude-drift rate + inclination | `06 Code/verify_geo.py` (built under this card, 2026-07-22), regression `_test_verify_geo.py` |
| re-run on Intelsat and SES with the new signal | done 2026-07-22; fleet table in `RESULTS - Beyond Starlink.md` (inclination 1.21×–15×, drift column measured on all four fleets) |
| honest outcome in writing | outcome 2, with a twist the card didn't anticipate: SES *appeared* to separate on both new observables, then the LEO negative control killed the drift column (~63–70× on every fleet from 475 km to GEO — it reflects the detector's own selection axis) and the referee (015) refuted the card's premise that GEO burns are altitude-invisible: N–S burns move fitted altitude 0.84–3.00 km and altitude beats inclination at every window width. The real GEO defect was the ±3-day timing window (shipped fixed as −3/+14 d in 018). |
| `RESULTS - Beyond Starlink.md` updated either way, no cherry-picking | updated repeatedly, including striking this card's own premise and my own "blind by construction" claim |

**What survives of this card:** inclination stays as a secondary channel (uniquely catches
MEV-2 inside ±3 d); the longitude-drift column is retired by both sides and stays retired.
**What the card was really chasing — the live SES miss — is not solved and is not this
card:** every documented SES event is caught by the altitude verifier as shipped, so the
suspicion moved to `detect.py`'s GEO suspect selection. That is card **025**, archive-gated
to ~Jul 29. Closing 002 does not close the SES question; it routes it to where the evidence
now points.
