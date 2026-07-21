"""
Zayah's first maneuver detector — v0.1
Pulls ~120 days of ISS orbit history from Space-Track (free, public),
charts its altitude, and marks every jump = a real engine burn (maneuver).
"""
import json
import math
import os
from datetime import datetime

import requests
import matplotlib
matplotlib.use("Agg")  # draw to file, no window needed
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(HERE, "spacetrack_auth.json")
OUT_DIR = os.path.join(HERE, "output")
os.makedirs(OUT_DIR, exist_ok=True)

BASE = "https://www.space-track.org"
LOGIN_URL = BASE + "/ajaxauth/login"
# GP_HISTORY = the modern OMM-era API class. JSON out. Last 120 days, oldest first.
QUERY_URL = (BASE + "/basicspacedata/query/class/gp_history/"
             "NORAD_CAT_ID/25544/EPOCH/%3Enow-120/orderby/EPOCH%20asc/format/json")

MU = 398600.4418          # Earth's gravity constant, km^3/s^2
EARTH_RADIUS = 6371.0     # mean radius, km (fine for a chart)
JUMP_THRESHOLD_KM = 0.25  # altitude jump between records bigger than this = maneuver


def get_history():
    creds = json.load(open(AUTH_FILE))
    s = requests.Session()
    r = s.post(LOGIN_URL, data=creds, timeout=30)
    r.raise_for_status()
    if "failed" in r.text.lower():
        raise SystemExit("Space-Track login failed — check spacetrack_auth.json")
    r = s.get(QUERY_URL, timeout=120)
    r.raise_for_status()
    rows = r.json()
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"No data returned. Response starts: {str(rows)[:200]}")
    return rows


def altitude_km(row):
    """Turn one record into 'how high was it flying' (mean altitude, km)."""
    sma = row.get("SEMIMAJOR_AXIS")
    if sma:  # Space-Track pre-computes this for us
        return float(sma) - EARTH_RADIUS
    # fallback: derive from mean motion (revolutions per day)
    n_rad_s = float(row["MEAN_MOTION"]) * 2.0 * math.pi / 86400.0
    return (MU / n_rad_s**2) ** (1.0 / 3.0) - EARTH_RADIUS


def main():
    rows = get_history()
    # de-duplicate by epoch (catalog sometimes repeats entries)
    seen, points = set(), []
    for row in rows:
        ep = row["EPOCH"]
        if ep in seen:
            continue
        seen.add(ep)
        points.append((datetime.fromisoformat(ep), altitude_km(row)))
    points.sort()
    times = [p[0] for p in points]
    alts = [p[1] for p in points]
    print(f"Records: {len(points)}  ({times[0]:%Y-%m-%d} -> {times[-1]:%Y-%m-%d})")

    # THE DETECTOR (v0.1): a sudden upward jump between records = engine burn.
    maneuvers = []
    for i in range(1, len(alts)):
        if alts[i] - alts[i - 1] > JUMP_THRESHOLD_KM:
            # group multi-record burns: only count if not within 12h of the last one
            if not maneuvers or (times[i] - maneuvers[-1]).total_seconds() > 12 * 3600:
                maneuvers.append(times[i])

    print(f"Maneuvers detected: {len(maneuvers)}")
    for m in maneuvers:
        print(f"  - {m:%Y-%m-%d %H:%M} UTC")

    # the chart
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(times, alts, lw=1.4, color="#2f81f7")
    for j, m in enumerate(maneuvers):
        ax.axvline(m, color="#e5534b", ls="--", lw=1.2,
                   label="detected maneuver" if j == 0 else None)
    ax.set_title(f"ISS mean altitude, last 120 days — {len(maneuvers)} maneuvers "
                 f"detected from free public data", fontsize=13)
    ax.set_ylabel("mean altitude (km)")
    ax.set_xlabel("date")
    ax.grid(alpha=0.3)
    if maneuvers:
        ax.legend(loc="best")
    fig.autofmt_xdate()
    out = os.path.join(OUT_DIR, "iss_maneuvers.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Chart saved: {out}")


if __name__ == "__main__":
    main()
