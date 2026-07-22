"""Proves the orbital-regime handling that lets the detector run outside LEO.

Every constant in detect.py was calibrated on Starlink, at 475 km, in thick air. Pointed
at a GEO bird 75x higher the same code still runs, still prints a table and still sounds
confident - while two of its three filters cannot fire at all. That is the failure this
covers: not a crash, but a confident-looking GEO number produced by LEO physics.

Measured on the real archive, 2026-07-22:

    starlink    475.2 km   -55.44 .. +24.18 km/day   1021 "falling"
    intelsat 35,786.6 km    -0.077 .. +0.160 km/day     0 "falling"
    ses      35,786.0 km    -0.085 .. +0.192 km/day     0 "falling"

  python _test_geo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

LEO, MEO, GEO = 475.0, 8066.0, 35786.0      # Starlink, SES's O3b, geostationary


def rows(specs):
    """specs: list of (gap_km, min_km). One age bin, all station-keeping."""
    return [{"gap_km": g, "gp_age_h": 15.0, "min_km": m, "verdict": "agrees",
             "flagged": False} for g, m in specs]


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
    return ok


passed = True
print("\n  naming the regime\n")

passed &= check("a Starlink shell -> LEO", detect.orbital_regime([LEO] * 50), "LEO")
passed &= check("a geostationary fleet -> GEO", detect.orbital_regime([GEO] * 50), "GEO")
passed &= check("an O3b-height fleet -> MEO", detect.orbital_regime([MEO] * 50), "MEO")
passed &= check("nothing to judge -> unknown", detect.orbital_regime([]), "unknown")
passed &= check("altitudes all NaN -> unknown",
                detect.orbital_regime([float("nan")] * 5), "unknown")

# Boundaries, stated so a constant change is loud rather than silent.
passed &= check("2,000 km is still LEO", detect._regime_of_one(2000.0), "LEO")
passed &= check("2,001 km is MEO", detect._regime_of_one(2001.0), "MEO")
passed &= check("34,000 km is GEO (band low edge)", detect._regime_of_one(34000.0), "GEO")
passed &= check("37,000 km is GEO (band high edge)", detect._regime_of_one(37000.0), "GEO")
passed &= check("beyond the GEO band -> unknown", detect._regime_of_one(42000.0), "unknown")

# The median is used so a handful of graveyard or transfer orbits cannot rename a fleet.
passed &= check("40 GEO + 5 MEO -> still GEO",
                detect.orbital_regime([GEO] * 40 + [MEO] * 5), "GEO")

# But a genuinely straddling operator gets no single label. This is SES as it actually
# is on 2026-07-22: 38 birds at GEO and 30 more at 8,066 km.
passed &= check("SES's real 38 GEO + 30 MEO split -> mixed",
                detect.orbital_regime([GEO] * 38 + [MEO] * 30), "mixed")

print("\n  the profile each regime gets\n")

passed &= check("LEO keeps the 5 km floor the published numbers were made with",
                detect.regime_profile("LEO")["min_km"], 5.0)
passed &= check("  and its decay split genuinely works",
                detect.regime_profile("LEO")["decay_filter"], True)
passed &= check("GEO gets a 1 km floor",
                detect.regime_profile("GEO")["min_km"], 1.0)
passed &= check("  and its decay split is declared inert",
                detect.regime_profile("GEO")["decay_filter"], False)
passed &= check("MEO sits between them", detect.regime_profile("MEO")["min_km"], 2.0)

# An unrecognised regime must not quietly inherit LEO's constants as though they fit.
unknown = detect.regime_profile("something else")
passed &= check("an unrecognised regime says so in its note",
                "UNRECOGNISED" in unknown["note"], True)

print("\n  the floor is per object, not per constellation\n")

# Two objects, identical 3 km gap, in the same age band. One is a GEO bird (1 km floor),
# one a Starlink (5 km floor). A single constellation-wide number would have to be wrong
# for one of them - which is exactly SES's situation.
mixed = rows([(3.0, 1.0), (3.0, 5.0)] + [(0.5, 1.0)] * 30)
detect.classify(mixed, 50.0, 5.0, stored_cuts={(12, 24): 2.0})
passed &= check("the GEO object clears its own 1 km floor -> flagged",
                mixed[0]["flagged"], True)
passed &= check("the LEO object does not clear its 5 km floor -> not flagged",
                mixed[1]["flagged"], False)

# An explicit --min-km must still win outright, or the flag stops meaning anything.
override = rows([(3.0, 9.0), (3.0, 9.0)])
detect.classify(override, 50.0, 9.0, stored_cuts={(12, 24): 2.0})
passed &= check("an explicit floor above both gaps -> nothing flagged",
                sum(1 for r in override if r["flagged"]), 0)

# Rows with no floor stamped fall back to the scalar, so older callers still work.
legacy = [{"gap_km": 8.0, "gp_age_h": 15.0, "verdict": "agrees", "flagged": False}]
detect.classify(legacy, 50.0, 5.0, stored_cuts={(12, 24): 2.0})
passed &= check("a row with no stamped floor uses the scalar", legacy[0]["flagged"], True)

print()
print("  all passed" if passed else "  SOMETHING FAILED")
sys.exit(0 if passed else 1)
