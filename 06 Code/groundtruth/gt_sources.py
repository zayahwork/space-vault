"""gt_sources.py - the outside-world data behind ground_truth.csv.

Two independent providers, deliberately kept separate:

  Space-Track  - the US government catalog. GP_HISTORY (every past version of an
                 orbit, going back years) and SATCAT (launch/decay records).
  GCAT         - Jonathan McDowell's General Catalog, curated by hand since 1985.
                 Used as the *second* source when scoring evidence, because his
                 judgements (is this thing abandoned? did it dock? was it renamed?)
                 are made independently of the raw catalog.

Everything is cached to disk. Space-Track is a free service run by people with
better things to do than serve the same query twice; be polite.

Credentials come from ../spacetrack_auth.json, which is gitignored. Never commit it.

    python gt_sources.py history 26824 2025-03-25 2025-04-25
    python gt_sources.py satcat 47404
    python gt_sources.py geotab            # McDowell's GEO table -> cache
"""
import csv
import http.cookiejar
import json
import math
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Space-Track presents a cert chain some Windows Python builds dislike; the data
# is public and read-only, so this is a convenience, not a security decision.
ssl._create_default_https_context = ssl._create_unverified_context

HERE = Path(__file__).resolve().parent
AUTH = HERE.parent / "spacetrack_auth.json"
CACHE = HERE / "cache"
ST = "https://www.space-track.org"
GCAT = "https://planet4589.org/space/gcat"

EARTH_EQ_KM = 6378.137          # equatorial radius, matches McDowell's convention
MU = 398600.4418                # km^3/s^2
GEO_MEAN_MOTION = 1.0027379     # rev/day, sidereal
POLITE_SEC = 3.0

_opener = None


# ----------------------------------------------------------------- space-track

def _login():
    global _opener
    if _opener:
        return _opener
    if not AUTH.exists():
        sys.exit(f"missing {AUTH} - see 06 Code/verify.py for the expected shape")
    creds = json.loads(AUTH.read_text(encoding="utf-8"))
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", "space-groundtruth-research")]
    op.open(ST + "/ajaxauth/login",
            urllib.parse.urlencode(creds).encode(), timeout=60).read()
    _opener = op
    return op


def st_query(path, tag):
    """Run a Space-Track query, cached on disk by `tag`."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{tag}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    rows = json.loads(_login().open(ST + path, timeout=300).read().decode("utf-8"))
    f.write_text(json.dumps(rows), encoding="utf-8")
    time.sleep(POLITE_SEC)
    return rows


def altitude_km(row):
    """Mean altitude from a GP_HISTORY row, however it reports the orbit."""
    sma = row.get("SEMIMAJOR_AXIS")
    if sma:
        return float(sma) - EARTH_EQ_KM
    n = float(row["MEAN_MOTION"]) * 2 * math.pi / 86400.0
    return (MU / n ** 2) ** (1.0 / 3.0) - EARTH_EQ_KM


def drift_deg_per_day(mean_motion):
    """Longitude drift at GEO. Negative = westward.

    Note for whoever builds the GEO verifier: this is NOT an independent
    observable. It is mean motion rescaled, so it carries exactly the same
    information as altitude - 1 km of altitude is 0.0128 deg/day of drift.
    Confirmed against the Intelsat 901 graveyard raise to 1.2%.
    Inclination IS independent. See 'RESULTS - Ground Truth'.
    """
    return (mean_motion - GEO_MEAN_MOTION) * 360.0


def history(norad, start, end):
    """Orbit history for one object over a date range (YYYY-MM-DD), de-duplicated."""
    path = (f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{norad}"
            f"/EPOCH/{start}--{end}/orderby/EPOCH%20asc/format/json")
    rows = st_query(path, f"h_{norad}_{start}_{end}")
    out = {}
    for r in rows:
        try:
            out[r["EPOCH"]] = dict(
                epoch=r["EPOCH"], alt=altitude_km(r),
                mm=float(r["MEAN_MOTION"]), inc=float(r["INCLINATION"]),
                raan=float(r["RA_OF_ASC_NODE"]), ecc=float(r["ECCENTRICITY"]))
        except (KeyError, ValueError, TypeError):
            continue
    return [out[k] for k in sorted(out)]


def satcat(norad):
    return st_query(f"/basicspacedata/query/class/satcat/NORAD_CAT_ID/{norad}/format/json",
                    f"sc_{norad}")


def decays(start, end):
    """Payload reentries in a window - authoritative, precisely dated."""
    return st_query(
        f"/basicspacedata/query/class/satcat/OBJECT_TYPE/PAYLOAD/DECAY/{start}--{end}"
        f"/orderby/DECAY%20desc/format/json", f"decay_{start}_{end}")


# ------------------------------------------------------------------------ gcat

def _gcat(relpath, name):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / name
    if not f.exists():
        req = urllib.request.Request(f"{GCAT}/{relpath}",
                                     headers={"User-Agent": "space-groundtruth-research"})
        f.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    return f


def geotab():
    """McDowell's GEO table: longitude, drift rate, and his orbit classification.

    OType codes that matter here (from GCAT's orbit-category definitions):
      GEO/S  stationary, actively station-kept
      GEO/D  drifting, low inclination - relocating, or freshly disposed
      GEO/I  inclined but longitude-held (N-S station-keeping stopped)
      GEO/ID inclined drift - abandoned. These are the null objects.
      GEO/NS near-synchronous - includes graveyard orbits
    """
    p = _gcat("tsv/derived/geotab.tsv", "geotab.tsv")
    with p.open(encoding="utf-8", errors="replace") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t")
                if not r["#JCAT"].startswith("#")]


def gcat_phases(norad, which="satcat"):
    """All GCAT phases for one object. `which` is 'satcat' (in orbit) or 'rcat' (reentered).

    CAREFUL - this bit me. GCAT rows are PHASES, not objects. DDate is the end of
    a phase and Status is the event that ended it, so the first row for an object
    is usually not its current state. Status codes:
      O in orbit | R reentered | N RENAMED | DK docked | UDK undocked | E exploded
    Reading a first-phase row as 'current' would report Galaxy 15 as decayed in
    2006, when it was merely renamed.
    """
    p = _gcat(f"tsv/cat/{which}.tsv", f"{which}.tsv")
    hits = []
    with p.open(encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if (r.get("Satcat") or "").strip() == str(norad):
                hits.append(r)
    return hits


def gcat_updated(which="rcat"):
    """When McDowell last refreshed a catalog - decides whether a non-match means
    'he disagrees' or just 'he hasn't got to it yet'. It was the latter for the
    five Starlink reentries in ground_truth.csv."""
    p = _gcat(f"tsv/cat/{which}.tsv", f"{which}.tsv")
    with p.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#") and "Updated" in line:
                return line.strip()
    return None


# ------------------------------------------------------------------------- cli

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "history":
        n, s, e = sys.argv[2], sys.argv[3], sys.argv[4]
        for p in history(n, s, e):
            print(f"  {p['epoch'][:16]}  alt={p['alt']:9.2f}  "
                  f"drift={drift_deg_per_day(p['mm']):+7.3f}  inc={p['inc']:6.3f}")
    elif cmd == "satcat":
        print(json.dumps(satcat(sys.argv[2]), indent=2)[:1500])
    elif cmd == "geotab":
        rows = geotab()
        print(f"{len(rows)} GEO objects cached -> {CACHE/'geotab.tsv'}")
    elif cmd == "phases":
        for r in gcat_phases(sys.argv[2]):
            print(f"  {r['Name'].strip():24} SDate={r['SDate'].strip():18} "
                  f"DDate={r['DDate'].strip():18} Status={r['Status'].strip()}")
    elif cmd == "updated":
        print(gcat_updated(sys.argv[2] if len(sys.argv) > 2 else "rcat"))
    else:
        print(__doc__)
