---
status: open
type: AFK
blocked-by: []
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
