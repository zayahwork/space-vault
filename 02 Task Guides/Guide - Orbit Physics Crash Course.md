# 📚 Guide — Orbit Physics Crash Course

Only 4 concepts matter for our product. Keep [[Glossary]] open. Ask Claude to explain anything
weird with pictures/analogies — that's what it's for.

## 1. The 6 orbital elements
Six numbers fully describe any orbit: size, shape, tilt, two orientation angles, and
where-on-the-orbit-right-now. A satellite's data record is basically these 6 + a timestamp.
*Why we care: our ML watches these numbers over time.*

## 2. OMM + SGP4 (data → position)
**OMM** is the modern data format (replaced TLE when the catalog passed 100,000 objects this
month). **SGP4** is the standard math that turns one record into "the satellite is HERE at
time X." Python's `sgp4` library does it for us.
*Why we care: it's the plumbing under everything we build.*

## 3. Why maneuvers = jumps
Physics only changes an orbit smoothly (drag, gravity ripples). A thruster firing changes the
orbit's *energy* suddenly → the elements **jump** between one record and the next. A jump that
physics can't explain = a maneuver. **That sentence is our entire product.**

## 4. Conjunction basics (talk-shop level only)
**Conjunction** = predicted close approach. Key words: *miss distance* (how close),
*probability of collision* (how likely), *screening* (the scan that finds them — runs ~every
8 hrs today; operators need ~16 hrs lead time — that slowness is part of our opening).

## Sources (in order of friendliness)
1. CelesTrak columns — Kelso's own plain-language writeups: `celestrak.org/columns/`
2. `skyfield` docs (the Python library we use): `rhodesmill.org/skyfield/`
3. Vallado's *Fundamentals of Astrodynamics* — the field's bible. Reference, not bedtime reading.
