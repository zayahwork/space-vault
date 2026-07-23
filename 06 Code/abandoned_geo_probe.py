"""Issue 025 probe: do documented-abandoned objects appear in the public catalog,
and is their catalog-side behaviour separable from documented-healthy ones?

Reads the status populations from quiet_exam.csv, then makes exactly two
network pulls:
  1. Celestrak GROUP=active (the same upstream source the archiver's
     gp_active capture reads) -> membership per object.
  2. One batched Space-Track gp query for every object across all status
     groups -> EPOCH, INCLINATION, MEAN_MOTION, ECCENTRICITY, DECAYED.

Prints a per-group summary (membership counts, epoch-age median/IQR,
inclination median) and a per-object table for the abandoned + degraded
rows, and writes the merged per-object data to
output/abandoned_geo_probe_<date>.csv so the separability analysis is
reproducible without re-pulling. The note in 03 Reference/ is written
from this output by hand.

Usage: python abandoned_geo_probe.py
"""

import csv
import io
import json
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAM_CSV = HERE / "quiet_exam.csv"
AUTH_JSON = HERE / "spacetrack_auth.json"

CELESTRAK_ACTIVE = (
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"
)
SPACETRACK_LOGIN = "https://www.space-track.org/ajaxauth/login"
SPACETRACK_GP = (
    "https://www.space-track.org/basicspacedata/query/class/gp/"
    "NORAD_CAT_ID/{ids}/format/csv"
)

GROUPS = ("abandoned", "degraded", "active-stationkept")


def load_populations():
    with open(EXAM_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    pops = {g: [r for r in rows if r["status"] == g] for g in GROUPS}
    # Sanity pins: these counts are what the 2026-07-22 rebuild of
    # quiet_exam.csv contains. If they drift, the note's numbers are stale.
    assert len(pops["abandoned"]) == 27, len(pops["abandoned"])
    assert len(pops["degraded"]) == 8, len(pops["degraded"])
    assert len(pops["active-stationkept"]) == 71, len(pops["active-stationkept"])
    return pops


def fetch(url, data=None, opener=None):
    op = opener or urllib.request.build_opener()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "urllib"})
    with op.open(req, timeout=120) as resp:
        return resp.read()


def celestrak_active_norads():
    raw = fetch(CELESTRAK_ACTIVE).decode("utf-8", "replace")
    rows = list(csv.DictReader(io.StringIO(raw)))
    return {r["NORAD_CAT_ID"].strip() for r in rows}, len(rows)


def spacetrack_gp(norads):
    auth = json.loads(AUTH_JSON.read_text())
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor()
    )
    fetch(
        SPACETRACK_LOGIN,
        data=urllib.parse.urlencode(auth).encode(),
        opener=opener,
    )
    url = SPACETRACK_GP.format(ids=",".join(sorted(norads)))
    raw = fetch(url, opener=opener).decode("utf-8", "replace")
    rows = list(csv.DictReader(io.StringIO(raw)))
    return {r["NORAD_CAT_ID"].strip(): r for r in rows}


def epoch_age_hours(gp_row, now):
    epoch = datetime.fromisoformat(gp_row["EPOCH"]).replace(tzinfo=timezone.utc)
    return (now - epoch).total_seconds() / 3600.0


def quartiles(vals):
    if not vals:
        return None
    q = statistics.quantiles(vals, n=4) if len(vals) > 1 else [vals[0]] * 3
    return statistics.median(vals), q[0], q[2]


def main():
    now = datetime.now(timezone.utc)
    pops = load_populations()

    # Celestrak throttles repeated identical GROUP queries (HTTP 403) —
    # degrade to membership-unknown rather than dying, so the Space-Track
    # side still lands.
    try:
        active_set, n_active = celestrak_active_norads()
        print(f"Celestrak GROUP=active pulled {now:%Y-%m-%d %H%MZ}: {n_active} objects")
    except Exception as e:
        active_set = None
        print(f"Celestrak GROUP=active unavailable ({e}); membership marked unknown")

    all_norads = {r["norad"] for rows in pops.values() for r in rows}
    gp = spacetrack_gp(all_norads)
    print(f"Space-Track gp returned {len(gp)}/{len(all_norads)} queried objects\n")

    for g in GROUPS:
        rows = pops[g]
        in_active = (
            [r for r in rows if r["norad"] in active_set]
            if active_set is not None else None
        )
        have_gp = [r for r in rows if r["norad"] in gp]
        ages = [epoch_age_hours(gp[r["norad"]], now) for r in have_gp]
        incs = [float(gp[r["norad"]]["INCLINATION"]) for r in have_gp]
        med = quartiles(ages)
        print(f"== {g} (n={len(rows)}) ==")
        mem = f"{len(in_active)}/{len(rows)}" if in_active is not None else "unknown"
        print(f"  in Celestrak 'active' group : {mem}")
        print(f"  in current GP catalog       : {len(have_gp)}/{len(rows)}")
        if med:
            print(
                f"  epoch age h  median {med[0]:7.1f}  IQR {med[1]:.1f}-{med[2]:.1f}"
            )
            print(f"  inclination  median {statistics.median(incs):7.2f} deg")
        print()

    out = HERE / "output" / f"abandoned_geo_probe_{now:%Y-%m-%d}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["norad", "object", "fleet", "status", "in_celestrak_active",
             "epoch_age_h", "inclination_deg", "mean_motion", "eccentricity",
             "pulled_utc"]
        )
        for g in GROUPS:
            for r in pops[g]:
                n = r["norad"]
                row = gp.get(n)
                w.writerow(
                    [n, r["object"], r["fleet"], g,
                     ("yes" if n in active_set else "no")
                     if active_set is not None else "unknown",
                     f"{epoch_age_hours(row, now):.1f}" if row else "",
                     row["INCLINATION"] if row else "",
                     row["MEAN_MOTION"] if row else "",
                     row["ECCENTRICITY"] if row else "",
                     f"{now:%Y-%m-%dT%H:%MZ}"]
                )
    print(f"wrote {out.name} ({sum(len(v) for v in pops.values())} rows)\n")

    print("Per-object detail (abandoned + degraded):")
    hdr = f"{'norad':>6} {'object':<16} {'grp':<9} {'act?':<4} {'age_h':>7} {'inc':>6} {'n':>9} {'ecc':>9}"
    print(hdr)
    for g in ("abandoned", "degraded"):
        for r in sorted(pops[g], key=lambda r: r["object"]):
            n = r["norad"]
            if active_set is None:
                act = "?"
            else:
                act = "yes" if n in active_set else "NO"
            if n in gp:
                row = gp[n]
                print(
                    f"{n:>6} {r['object']:<16} {g:<9} {act:<4} "
                    f"{epoch_age_hours(row, now):>7.1f} "
                    f"{float(row['INCLINATION']):>6.2f} "
                    f"{float(row['MEAN_MOTION']):>9.5f} "
                    f"{float(row['ECCENTRICITY']):>9.6f}"
                )
            else:
                print(f"{n:>6} {r['object']:<16} {g:<9} {act:<4}   -- not in GP --")
    return 0


if __name__ == "__main__":
    sys.exit(main())
