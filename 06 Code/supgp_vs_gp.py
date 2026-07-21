"""
supgp_vs_gp.py - does the archive actually find missed maneuvers?

THE CLAIM WE ARE TESTING
We started archiving SupGP on the theory that where CelesTrak's operator-derived
orbits disagree with the public 18 SDS catalog, something happened the catalog
missed - usually a maneuver. If that is true, the archive is a training set. If it
is false, we are burning disk on noise.

METHOD (this is Kelso's own comparison, reimplemented)
Take both element sets for the same object, propagate each with SGP4 over a 6-hour
span at 1-minute steps, and take the RMS position difference in km. That is exactly
what the SupGP-vs-GP table on CelesTrak reports.

THE CHECK THAT MAKES IT HONEST
Kelso published his own answer: 1,031 of 8,381 Starlink objects over 25 km RMS
(12.3%), as of 2025 Sep 12. Our numbers are from a different day so they will not
match exactly - but if our pipeline lands in the same ballpark, it is correct. If we
get 0.1% or 90%, we have a bug, not a discovery.

Usage:
  python supgp_vs_gp.py                      # newest archived snapshot, starlink
  python supgp_vs_gp.py --group oneweb
  python supgp_vs_gp.py --threshold 25
"""

import argparse
import gzip
import io
import sys
from pathlib import Path

import numpy as np
import requests
from sgp4 import omm
from sgp4.api import SatrecArray, Satrec, jday

ARCHIVE = Path(__file__).parent / "supgp_archive"
GP_URL = "https://celestrak.org/NORAD/elements/gp.php"
HEADERS = {
    "User-Agent": (
        "SpaceProject-SupGP-Archiver/1.0 "
        "(research: maneuver detection from public data; contact zayahwork@gmail.com)"
    )
}

SPAN_HOURS = 6
STEP_MINUTES = 1


def newest_snapshot(group):
    """Path to the most recent archived file for this group."""
    hits = sorted(ARCHIVE.glob(f"*/*/{group}.csv.gz"))
    if not hits:
        sys.exit(f"no archived snapshot for {group!r} - run supgp_archive.py first")
    return hits[-1]


def load_omm(text):
    """Parse OMM CSV into {norad: Satrec}. Later duplicates win."""
    sats = {}
    for fields in omm.parse_csv(io.StringIO(text)):
        sat = Satrec()
        try:
            omm.initialize(sat, fields)
        except (ValueError, KeyError):
            continue
        sats[sat.satnum] = sat
    return sats


def rms_difference(sat_a, sat_b):
    """RMS position difference in km over the span, or None if propagation fails."""
    # Start from the newer of the two epochs so neither is extrapolated backwards.
    start = max(sat_a.jdsatepoch + sat_a.jdsatepochF,
                sat_b.jdsatepoch + sat_b.jdsatepochF)
    steps = int(SPAN_HOURS * 60 / STEP_MINUTES)
    offsets = np.arange(steps) * (STEP_MINUTES / 1440.0)

    jd = np.full(steps, start)
    arr = SatrecArray([sat_a, sat_b])
    err, pos, _ = arr.sgp4(jd, offsets)

    if err.any():
        return None
    delta = pos[0] - pos[1]
    return float(np.sqrt((delta ** 2).sum(axis=1).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="starlink")
    ap.add_argument("--threshold", type=float, default=25.0, help="km")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    snap = newest_snapshot(args.group)
    print(f"SupGP snapshot : {snap.relative_to(ARCHIVE)}")
    sup = load_omm(gzip.open(snap, "rt", encoding="utf-8").read())
    print(f"                 {len(sup)} objects")

    print(f"GP catalog     : fetching {args.group} from CelesTrak")
    resp = requests.get(
        GP_URL, params={"GROUP": args.group, "FORMAT": "csv"},
        headers=HEADERS, timeout=120,
    )
    resp.raise_for_status()
    gp = load_omm(resp.text)
    print(f"                 {len(gp)} objects")

    both = sorted(set(sup) & set(gp))
    print(f"comparable     : {len(both)} objects\n")
    if not both:
        sys.exit("no overlap - nothing to compare")

    results, failed = [], 0
    for norad in both:
        val = rms_difference(sup[norad], gp[norad])
        if val is None:
            failed += 1
            continue
        results.append((val, norad))

    results.sort(reverse=True)
    vals = np.array([r[0] for r in results])
    over = vals > args.threshold

    print(f"{'RMS km':>12}  NORAD")
    for val, norad in results[: args.top]:
        print(f"{val:12.1f}  {norad}")

    print(f"\n  median   {np.median(vals):8.2f} km")
    print(f"  90th pct {np.percentile(vals, 90):8.2f} km")
    print(f"  max      {vals.max():8.1f} km")
    print(f"\n  over {args.threshold:g} km : {over.sum()} of {len(vals)} "
          f"({100 * over.mean():.1f}%)")
    if failed:
        print(f"  propagation failed on {failed} objects (usually reentering)")

    print("\n  Kelso's published figure for starlink: 12.3% over 25 km (2025 Sep 12).")
    print("  Same ballpark means our pipeline is right. Wildly off means a bug.")


if __name__ == "__main__":
    main()
