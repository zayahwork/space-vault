"""
Maneuver detector v0.2 — multiple satellites, same idea:
physics only changes orbits smoothly; a jump = a burn.
Targets: a live Starlink (auto-picked), GOES-18 (GEO), for comparison with the ISS.
"""
import json
import math
import os
from datetime import datetime

import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")
os.makedirs(OUT_DIR, exist_ok=True)

BASE = "https://www.space-track.org"
MU = 398600.4418
EARTH_RADIUS = 6371.0


def login():
    creds = json.load(open(os.path.join(HERE, "spacetrack_auth.json")))
    s = requests.Session()
    r = s.post(BASE + "/ajaxauth/login", data=creds, timeout=30)
    r.raise_for_status()
    if "failed" in r.text.lower():
        raise SystemExit("Space-Track login failed")
    return s


def find_active_starlink(s):
    """Ask the catalog for one currently-active Starlink (fresh data, not decayed)."""
    url = (BASE + "/basicspacedata/query/class/gp/OBJECT_NAME/~~STARLINK/"
           "DECAY_DATE/null-val/orderby/EPOCH%20desc/limit/1/format/json")
    row = s.get(url, timeout=60).json()[0]
    return row["OBJECT_NAME"].strip(), row["NORAD_CAT_ID"]


def pull_history(s, norad):
    url = (BASE + f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{norad}/"
           "EPOCH/%3Enow-120/orderby/EPOCH%20asc/format/json")
    rows = s.get(url, timeout=120).json()
    seen, points = set(), []
    for row in rows:
        ep = row["EPOCH"]
        if ep in seen:
            continue
        seen.add(ep)
        sma = row.get("SEMIMAJOR_AXIS")
        if sma:
            alt = float(sma) - EARTH_RADIUS
        else:
            n = float(row["MEAN_MOTION"]) * 2 * math.pi / 86400.0
            alt = (MU / n**2) ** (1 / 3) - EARTH_RADIUS
        points.append((datetime.fromisoformat(ep), alt))
    points.sort()
    return points


def detect(points, threshold_km):
    """v0.1 rule: upward altitude jump bigger than threshold = maneuver (12h grouping)."""
    hits = []
    for i in range(1, len(points)):
        if points[i][1] - points[i - 1][1] > threshold_km:
            if not hits or (points[i][0] - hits[-1]).total_seconds() > 12 * 3600:
                hits.append(points[i][0])
    return hits


def chart(name, norad, points, hits, note, fname):
    times = [p[0] for p in points]
    alts = [p[1] for p in points]
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(times, alts, lw=1.3, color="#2f81f7")
    for j, m in enumerate(hits):
        ax.axvline(m, color="#e5534b", ls="--", lw=1.1,
                   label="detected maneuver" if j == 0 else None)
    ax.set_title(f"{name} (#{norad}) mean altitude, last 120 days — "
                 f"{len(hits)} maneuvers detected  |  {note}", fontsize=12)
    ax.set_ylabel("mean altitude (km)")
    ax.grid(alpha=0.3)
    if hits:
        ax.legend(loc="best")
    fig.autofmt_xdate()
    out = os.path.join(OUT_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"{name}: {len(points)} records, {len(hits)} maneuvers -> {out}")
    for m in hits[:12]:
        print(f"   - {m:%Y-%m-%d %H:%M} UTC")


def main():
    s = login()

    sl_name, sl_id = find_active_starlink(s)
    print(f"Auto-picked active Starlink: {sl_name} (#{sl_id})")
    targets = [
        (sl_name, sl_id, 0.25, "LEO, electric thrusters", "starlink_maneuvers.png"),
        ("GOES-18", 51850, 0.15, "GEO, station-keeping", "goes18_maneuvers.png"),
    ]
    for name, norad, thr, note, fname in targets:
        points = pull_history(s, norad)
        if len(points) < 10:
            print(f"{name}: only {len(points)} records, skipping")
            continue
        hits = detect(points, thr)
        chart(name, norad, points, hits, note, fname)


if __name__ == "__main__":
    main()
