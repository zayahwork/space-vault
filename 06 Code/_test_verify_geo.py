"""Proves the GEO verifier's measures, before it is allowed to say anything about a fleet.

The claim this code exists to support is "these GEO candidates really moved", and the
number that carries it is a ratio against a control group. If the measures underneath are
wrong, the ratio is still a ratio and still looks like evidence - so the measures get
checked against GEO physics that is true independently of this repo.

The load-bearing one: a satellite whose semi-major axis is 1 km above geostationary drifts
west at about 0.0128 deg/day. That constant is standard station-keeping arithmetic, and it
is derived here from nothing but detect.py's Kepler and the sidereal day.

  python _test_verify_geo.py
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402
import verify_geo as vg  # noqa: E402

T0 = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)


def pts(spec):
    """spec: list of (day_offset, inclination_deg, drift_deg_per_day)."""
    return [(T0 + timedelta(days=d), inc, dr) for d, inc, dr in spec]


def near(got, want, tol):
    return abs(got - want) <= tol


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}{'' if ok else '   <- ' + detail}")
    return ok


passed = True
print("\n  longitude drift, against GEO arithmetic that predates this repo\n")

passed &= check("exactly synchronous -> zero drift",
                vg.drift_deg_per_day(vg.GEO_SYNC_REV_DAY) == 0.0)

# The sidereal day is the whole basis of the number, so pin it.
passed &= check(f"synchronous mean motion is {vg.GEO_SYNC_REV_DAY:.8f} rev/day",
                near(vg.GEO_SYNC_REV_DAY, 1.00273791, 1e-8), f"{vg.GEO_SYNC_REV_DAY}")

# One turn per SOLAR day is slower than synchronous, so it slips west by ~0.986 deg/day.
passed &= check("1.0 rev/day (a solar day) -> drifts west at 0.9857 deg/day",
                near(vg.drift_deg_per_day(1.0), -0.98565, 1e-4),
                f"{vg.drift_deg_per_day(1.0)}")

passed &= check("faster than synchronous -> drifts EAST (positive)",
                vg.drift_deg_per_day(vg.GEO_SYNC_REV_DAY + 1e-4) > 0)
passed &= check("slower than synchronous -> drifts WEST (negative)",
                vg.drift_deg_per_day(vg.GEO_SYNC_REV_DAY - 1e-4) < 0)

# The textbook cross-check. Raise the orbit 1 km and it must drift west ~0.0128 deg/day.
# Built from detect.altitude_km's Kepler, so it also ties the two modules' physics
# together: if either drifts from reality this fails.
geo_alt = detect.altitude_km(vg.GEO_SYNC_REV_DAY)
lo, hi = vg.GEO_SYNC_REV_DAY * 0.9, vg.GEO_SYNC_REV_DAY * 1.1
for _ in range(200):                       # find the mean motion 1 km higher up
    mid = (lo + hi) / 2
    if detect.altitude_km(mid) > geo_alt + 1.0:
        lo = mid
    else:
        hi = mid
drift_1km = vg.drift_deg_per_day(lo)
passed &= check(f"1 km above geostationary -> {drift_1km:.5f} deg/day west "
                f"(textbook -0.0128)", near(drift_1km, -0.0128, 5e-4), f"{drift_1km}")

print("\n  finding the step a burn leaves behind\n")

# Inclination is component 1, drift rate component 2.
series = pts([(-5, 0.050, 0.001), (-1, 0.051, 0.001),
              (0, 0.090, 0.001),          # a north-south burn: 0.039 deg of inclination
              (2, 0.091, 0.020)])         # and later an east-west one: 0.019 deg/day
passed &= check("finds the inclination step",
                near(vg.biggest_step(series, T0, 1), 0.039, 1e-9),
                f"{vg.biggest_step(series, T0, 1)}")
passed &= check("finds the drift-rate step",
                near(vg.biggest_step(series, T0, 2), 0.019, 1e-9),
                f"{vg.biggest_step(series, T0, 2)}")

# A burn that happened last month is not what the detector reacted to.
old = pts([(-40, 0.05, 0.0), (-39, 0.90, 0.0), (0, 0.90, 0.0)])
passed &= check("a step outside the window is ignored",
                vg.biggest_step(old, T0, 1) == 0.0, f"{vg.biggest_step(old, T0, 1)}")

# A burn that REDUCES inclination is still a burn - N-S burns usually do exactly that.
down = pts([(-1, 0.900, 0.0), (0, 0.100, 0.0)])
passed &= check("a decrease counts as a step (N-S burns reduce inclination)",
                near(vg.biggest_step(down, T0, 1), 0.800, 1e-9))

passed &= check("no history -> no step", vg.biggest_step([], T0, 1) == 0.0)
passed &= check("a single record -> no step",
                vg.biggest_step(pts([(0, 0.05, 0.0)]), T0, 1) == 0.0)

print("\n  suspects against controls\n")

# Controls all quiet, suspects all moved: the ratio must be large and the bar low.
v = vg.compare("test", "deg", [0.5] * 10, [0.001] * 10)
passed &= check("clear separation -> big median ratio", v["med_ratio"] > 100)
passed &= check("  and every suspect over the controls' bar",
                v["over_s"] == 10, f"{v['over_s']}/10")
passed &= check("  bar is the controls' 90th percentile", near(v["bar"], 0.001, 1e-12))

# The case that must NOT flatter us: the two groups are identical.
v = vg.compare("test", "deg", [0.01] * 10, [0.01] * 10)
passed &= check("identical groups -> ratio 1.0, no signal", near(v["med_ratio"], 1.0, 1e-9))
passed &= check("  and nobody clears a bar set at their own level",
                v["over_s"] == 0, f"{v['over_s']}")

# One loud suspect must not carry nine quiet ones - the median is the guard.
v = vg.compare("test", "deg", [0.001] * 9 + [5.0], [0.001] * 10)
passed &= check("one outlier among nine quiet suspects -> median ratio stays 1.0",
                near(v["med_ratio"], 1.0, 1e-9), f"{v['med_ratio']}")

# The case this verifier actually hit on Intelsat, and the reason the rule needs BOTH
# readings: suspects' median is above the controls', yet they clear the controls' bar
# LESS often. Those two disagree, and reading the flattering half alone reports a
# separation that is not there.
v = vg.compare("test", "deg", [0.0023] * 4, [0.0019] * 13 + [0.02, 0.03])
passed &= check("median above 1.2x but bar-clearing WORSE than controls -> no signal",
                v["signal"], f"med {v['med_ratio']:.2f}x, rate {v['rate_ratio']:.2f}x")
passed &= check("  (the median ratio alone would have claimed one)",
                v["med_ratio"] >= 1.2, f"{v['med_ratio']}")

# And a clean both-ways separation must still register.
v = vg.compare("test", "deg", [0.5] * 8, [0.001] * 10)
passed &= check("median AND bar-clearing both strong -> signal", v["signal"], "")

print()
print("  all passed" if passed else "  SOMETHING FAILED")
sys.exit(0 if passed else 1)
