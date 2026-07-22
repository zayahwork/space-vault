"""Proves the orbital math under every number this company publishes.

altitude_km, descent_km_per_day, epoch_jd, capture_jd and rms_difference sit beneath
every figure in every RESULTS note. Unlike persistence or alert mode, nothing gates
these: there is no "refuses until the archive grows" to hide a mistake behind. A wrong
constant or a flipped sign flows straight into the published numbers and looks exactly
like a real result.

These are the only functions here with external ground truth, so they are checked
against physics rather than against themselves:
  - geostationary altitude is a textbook constant, 35,786 km
  - the ISS sits near 420 km, Starlink's shell near 550 km
  - J2000 is JD 2451545.0 at 2000-01-01 12:00 UTC, by definition
  - Kepler's third law, written a different way than detect.py writes it

  python _test_orbital.py
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from sgp4.api import Satrec

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

# A real ISS element set. Epoch 24001.50000000 = 2024 day 1.5 = 2024-01-01 12:00 UTC.
ISS_1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  30777-3 0  9993"
ISS_2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.50377579 20000"


def near(got, want, tol):
    return abs(got - want) <= tol


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}{'' if ok else '   <- ' + detail}")
    return ok


def manifest_jd(stamp):
    """capture_jd against a hand-written manifest."""
    tmp = Path(tempfile.mkdtemp(prefix="cap_"))
    try:
        (tmp / "manifest.json").write_text(json.dumps({"captured_utc": stamp}),
                                           encoding="utf-8")
        return detect.capture_jd(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


passed = True
print("\n  altitude_km against orbits whose altitude is known\n")

# The strongest check available: geostationary altitude is a published constant.
geo = detect.altitude_km(1.0027379)          # one sidereal day
passed &= check(f"geostationary -> {geo:.1f} km (textbook 35,786)",
                near(geo, 35786.0, 2.0), f"{geo}")

iss = detect.altitude_km(15.50377579)        # from the real ISS element set above
passed &= check(f"ISS mean motion -> {iss:.1f} km (ISS flies 400-430)",
                400.0 < iss < 430.0, f"{iss}")

sl = detect.altitude_km(15.06)               # Starlink's main shell
passed &= check(f"Starlink mean motion -> {sl:.1f} km (shell is ~550)",
                540.0 < sl < 560.0, f"{sl}")

# Kepler's third law written a different way than detect.py writes it. detect.py goes
# via the period; this goes via mean motion in rad/s. Algebraically identical, so a
# disagreement means a mistyped constant rather than a physics error.
for mm in (1.0027379, 15.06, 15.50377579, 12.5):
    n_rad_s = 2.0 * np.pi * mm / 86400.0
    independent = (detect.MU_KM3_S2 / n_rad_s ** 2) ** (1.0 / 3.0) - detect.EARTH_RADIUS_KM
    passed &= check(f"cross-check at {mm} rev/day agrees to <1e-6 km",
                    near(detect.altitude_km(mm), independent, 1e-6),
                    f"{detect.altitude_km(mm)} vs {independent}")

# Faster orbit = lower orbit. If this ever inverts, "falling" inverts with it.
alts = [detect.altitude_km(mm) for mm in (14.0, 15.0, 15.5, 16.0)]
passed &= check("higher mean motion -> lower altitude, strictly",
                all(a > b for a, b in zip(alts, alts[1:])), f"{alts}")

print("\n  descent_km_per_day - the sign convention the deorbit filter rides on\n")

# FALLING_KM_PER_DAY is negative and `falling = drop < -0.4`. If this sign ever flips,
# the detector separates exactly the wrong population and every regime-split number
# in the RESULTS notes inverts.
passed &= check("no drag term -> exactly zero, not a rounding artifact",
                detect.descent_km_per_day(15.06, 0.0) == 0.0)
passed &= check("positive MEAN_MOTION_DOT -> NEGATIVE (falling)",
                detect.descent_km_per_day(15.06, 1e-4) < 0)
passed &= check("negative MEAN_MOTION_DOT -> POSITIVE (being raised)",
                detect.descent_km_per_day(15.06, -1e-4) > 0)

# OMM's MEAN_MOTION_DOT is n-dot/2, so a day changes mean motion by TWICE it. Using
# the raw value would understate every descent by half and quietly reclassify
# deorbiting hardware as station-keeping.
d = 1e-4
doubled = detect.altitude_km(15.06 + 2 * d) - detect.altitude_km(15.06)
single = detect.altitude_km(15.06 + d) - detect.altitude_km(15.06)
passed &= check("the n-dot/2 convention is applied (2x, not 1x)",
                near(detect.descent_km_per_day(15.06, d), doubled, 1e-9)
                and not near(detect.descent_km_per_day(15.06, d), single, 1e-6))

# Where the published 0.4 km/day threshold actually sits, so a constants change is loud.
lo, hi = 0.0, 1e-3
for _ in range(80):
    mid = (lo + hi) / 2
    if detect.descent_km_per_day(15.06, mid) > detect.FALLING_KM_PER_DAY:
        lo = mid
    else:
        hi = mid
passed &= check(f"-0.4 km/day threshold sits at MEAN_MOTION_DOT {lo:.4e}",
                near(lo, 6.523e-4, 1e-6), f"{lo}")
passed &= check("  an object just past it is called falling",
                detect.descent_km_per_day(15.06, lo * 1.01) < detect.FALLING_KM_PER_DAY)
passed &= check("  and one just short of it is not",
                detect.descent_km_per_day(15.06, lo * 0.99) > detect.FALLING_KM_PER_DAY)

print("\n  epoch_jd and capture_jd - both must speak the same calendar\n")

sat = Satrec.twoline2rv(ISS_1, ISS_2)
passed &= check("TLE epoch 24001.5 -> JD 2460311.0 (2024-01-01 12:00 UTC)",
                near(detect.epoch_jd(sat), 2460311.0, 1e-6), f"{detect.epoch_jd(sat)}")

# J2000 by definition. This is the join between the two clocks: gp_age_h is a capture_jd
# minus an epoch_jd, so an offset in either would poison every age bin in the project.
passed &= check("2000-01-01 12:00 UTC -> JD 2451545.0 exactly",
                manifest_jd("2000-01-01T12:00:00+00:00") == 2451545.0,
                f"{manifest_jd('2000-01-01T12:00:00+00:00')}")
passed &= check("  a naive timestamp is read as UTC, not local time",
                manifest_jd("2000-01-01T12:00:00") == 2451545.0,
                f"{manifest_jd('2000-01-01T12:00:00')}")
passed &= check("  a non-UTC offset is converted, not ignored",
                manifest_jd("2000-01-01T07:00:00-05:00") == 2451545.0,
                f"{manifest_jd('2000-01-01T07:00:00-05:00')}")
passed &= check("  half a day later is +0.5 JD",
                near(manifest_jd("2000-01-02T00:00:00+00:00"), 2451545.5, 1e-9))

print("\n  rms_difference\n")

passed &= check("an element set against itself -> exactly 0 km",
                detect.rms_difference(sat, sat) == 0.0)

# Same satellite, mean anomaly shifted by 0.01 deg - a real but small disagreement.
shifted = Satrec.twoline2rv(ISS_1,
                            "2 25544  51.6416 247.4627 0006703 130.5360 325.0388 "
                            "15.50377579 20000")
gap = detect.rms_difference(sat, shifted)
passed &= check(f"a 0.01 deg shift in mean anomaly -> {gap:.4f} km, small but nonzero",
                0.0 < gap < 5.0, f"{gap}")

# Symmetry is the guard on the max(epoch_a, epoch_b) start time: comparing from one
# satellite's epoch instead of the later of the two would break this.
passed &= check("the comparison is symmetric in its arguments",
                near(detect.rms_difference(sat, shifted),
                     detect.rms_difference(shifted, sat), 1e-9))

# A bigger element change must produce a bigger disagreement, or the metric is not
# measuring what the whole project claims it measures.
more = Satrec.twoline2rv(ISS_1,
                         "2 25544  51.6416 247.4627 0006703 130.5360 325.5288 "
                         "15.50377579 20000")
passed &= check("a 50x larger shift -> a larger gap",
                detect.rms_difference(sat, more) > gap * 5,
                f"{detect.rms_difference(sat, more)} vs {gap}")

print()
print("  all passed" if passed else "  SOMETHING FAILED")
sys.exit(0 if passed else 1)
