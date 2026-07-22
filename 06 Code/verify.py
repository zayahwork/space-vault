"""
verify.py - check detect.py's candidates against the catalog's own history.

WHY THIS EXISTS
Everything detect.py produces is self-graded. It ranks objects by how far the
operator's orbit sits from the public catalog RIGHT NOW, and nothing in it has ever
been compared to whether the object actually moved. A ranked guess with a good story
is still a guess.

This checks the candidates with a DIFFERENT method on DIFFERENTLY-SHAPED data: months
of altitude history from Space-Track's GP_HISTORY, looking for the step change a burn
leaves behind. That is the v0.1/v0.2 detector that went 3/3 on ISS reboosts. It shares
nothing with detect.py's instantaneous SupGP-vs-catalog comparison except the object.

THE CONTROL GROUP IS THE WHOLE POINT
"38% of our suspects show a burn" means nothing on its own - maybe 38% of ALL Starlinks
show a burn in any given week, in which case we have detected nothing whatsoever. So
every run also pulls a matched set of objects detect.py called ORDINARY, and puts them
through identical logic. The number that matters is the DIFFERENCE between the two.

If suspects and controls score the same, the detector is not working, and we would
rather find that out here than in front of Kelso.

WHAT THIS IS NOT
GP_HISTORY is the public catalog's own history, so it shares the catalog side with
detect.py. It is independent of the operator (SupGP) side, of the age-binning, and of
the persistence logic - but it is NOT operator ground truth. Real ground truth means
operator maneuver logs, which are not public for Starlink. Treat a "corroborated" here
as two different methods agreeing, not as proof.

Usage:
  python verify.py --flags          # the data-quality flags: are they really decaying?
  python verify.py --top 25         # top suspects vs matched controls
  python verify.py --top 25 --days 45
"""

import argparse
import json
import math
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
CACHE = HERE / "verify_cache"
BASE = "https://www.space-track.org"
EARTH_RADIUS = 6371.0
MU = 398600.4418

BATCH = 40            # NORADs per GP_HISTORY request - the API takes a comma list
POLITE_SEC = 3.0      # Space-Track allows ~30/min; we stay well under it
WINDOW_DAYS = 3.0     # how close to the snapshot a step has to be to count


# ------------------------------------------------------------------ space-track

def login():
    creds = json.loads((HERE / "spacetrack_auth.json").read_text(encoding="utf-8"))
    s = requests.Session()
    r = s.post(BASE + "/ajaxauth/login", data=creds, timeout=30)
    r.raise_for_status()
    if "failed" in r.text.lower():
        sys.exit("Space-Track login failed - check spacetrack_auth.json")
    return s


def altitude_km(row):
    """Mean altitude from a GP_HISTORY row, however it chooses to report the orbit."""
    sma = row.get("SEMIMAJOR_AXIS")
    if sma:
        return float(sma) - EARTH_RADIUS
    n = float(row["MEAN_MOTION"]) * 2 * math.pi / 86400.0
    return (MU / n ** 2) ** (1.0 / 3.0) - EARTH_RADIUS


def get_history(session, norads, days):
    """Altitude history per NORAD, batched and cached.

    Cached on disk because these runs get repeated while the analysis is being
    argued with, and Space-Track should not be asked the same question twice.
    """
    CACHE.mkdir(exist_ok=True)
    out, missing = {}, []
    for n in norads:
        f = CACHE / f"{n}_{days}d.json"
        if f.exists():
            out[n] = [(datetime.fromisoformat(t), a)
                      for t, a in json.loads(f.read_text(encoding="utf-8"))]
        else:
            missing.append(n)

    for i in range(0, len(missing), BATCH):
        chunk = missing[i:i + BATCH]
        url = (BASE + "/basicspacedata/query/class/gp_history/NORAD_CAT_ID/"
               + ",".join(str(c) for c in chunk)
               + f"/EPOCH/%3Enow-{days}/orderby/EPOCH%20asc/format/json")
        print(f"  fetching {len(chunk)} objects ({i + len(chunk)}/{len(missing)})...")
        resp = session.get(url, timeout=180)
        resp.raise_for_status()
        rows = resp.json()

        grouped = {}
        for row in rows:
            try:
                n = int(row["NORAD_CAT_ID"])
                grouped.setdefault(n, []).append(
                    (datetime.fromisoformat(row["EPOCH"]).replace(tzinfo=timezone.utc),
                     altitude_km(row)))
            except (KeyError, ValueError, TypeError):
                continue
        for n in chunk:
            pts = sorted(set(grouped.get(n, [])))
            out[n] = pts
            (CACHE / f"{n}_{days}d.json").write_text(
                json.dumps([[t.isoformat(), a] for t, a in pts]), encoding="utf-8")
        if i + BATCH < len(missing):
            time.sleep(POLITE_SEC)
    return out


# ------------------------------------------------------------------ the measures

def biggest_step_km(points, centre, window_days=WINDOW_DAYS):
    """Largest altitude change between consecutive records near `centre`.

    A burn shows up in the catalog as a step: the orbit was one thing, then it was
    another. Restricted to a window around the snapshot so we measure what the
    detector was reacting to, not something that happened last month.
    """
    lo, hi = centre - timedelta(days=window_days), centre + timedelta(days=window_days)
    best = 0.0
    for (t0, a0), (t1, a1) in zip(points, points[1:]):
        if lo <= t1 <= hi:
            best = max(best, abs(a1 - a0))
    return best


def descent_km_per_day(points, window_days=7):
    """Average altitude change per day over the last `window_days`. Negative = falling."""
    if len(points) < 2:
        return 0.0
    end_t, end_a = points[-1]
    for t, a in reversed(points):
        if (end_t - t) >= timedelta(days=window_days):
            return (end_a - a) / ((end_t - t).total_seconds() / 86400.0)
    span = (end_t - points[0][0]).total_seconds() / 86400.0
    return (end_a - points[0][1]) / span if span > 0.5 else 0.0


def summarise(name, values):
    if not values:
        return f"  {name:<26} no data"
    return (f"  {name:<26} n={len(values):<4} median {statistics.median(values):6.3f} km"
            f"   90th {sorted(values)[int(0.9 * (len(values) - 1))]:6.3f} km")


# ------------------------------------------------------------------ the runs

def snapshot_moment(snap_dir):
    man = json.loads((snap_dir / "manifest.json").read_text(encoding="utf-8"))
    when = datetime.fromisoformat(man["captured_utc"])
    return when if when.tzinfo else when.replace(tzinfo=timezone.utc)


def run_flags(session, rows, centre, days):
    """2a - the data-quality flags. We PUBLISHED that these are decay or bad data."""
    flags = sorted([r for r in rows if r["verdict"].startswith("DATA QUALITY")],
                   key=lambda r: -r["gap_km"])
    print(f"\n  {len(flags)} objects were gated out as 'likely decay or bad TLE'.")
    print(f"  RESULTS - Maneuver vs Stale says that in writing. Checking it.\n")

    hist = get_history(session, [r["norad"] for r in flags], days)
    decaying = flat = nodata = 0
    print(f"\n  {'NORAD':>7}  {'gap km':>9}  {'records':>7}  {'km/day':>8}  verdict")
    for r in flags:
        pts = hist.get(r["norad"], [])
        if len(pts) < 5:
            nodata += 1
            print(f"  {r['norad']:>7}  {r['gap_km']:>9.0f}  {len(pts):>7}  "
                  f"{'-':>8}  no usable history (often already reentered)")
            continue
        rate = descent_km_per_day(pts)
        if rate < detect.FALLING_KM_PER_DAY:
            decaying += 1
            verdict = "DECAYING - gate confirmed"
        else:
            flat += 1
            verdict = "NOT decaying - the published guess was wrong"
        print(f"  {r['norad']:>7}  {r['gap_km']:>9.0f}  {len(pts):>7}  "
              f"{rate:>8.2f}  {verdict}")

    print(f"\n  decaying, gate confirmed   {decaying:>4}")
    print(f"  not decaying               {flat:>4}"
          f"{'   <-- we published something wrong' if flat else ''}")
    print(f"  no usable history          {nodata:>4}")
    checked = decaying + flat
    if checked:
        print(f"\n  {100 * decaying / checked:.0f}% of the checkable flags are genuinely "
              f"falling out of the sky.")
    return {"decaying": decaying, "flat": flat, "nodata": nodata}


def run_top(session, rows, centre, days, top):
    """2b - suspects vs a matched control group of objects we called ordinary."""
    suspects = sorted([r for r in rows if not r["falling"] and r.get("flagged")],
                      key=lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9),
                      reverse=True)[:top]
    # Controls: same regime, called ordinary, drawn across the same catalog-age range
    # so the two groups differ in what detect.py SAID, not in what they are.
    ages = [r["gp_age_h"] for r in suspects]
    lo, hi = min(ages), max(ages)
    pool = [r for r in rows if not r["falling"] and not r.get("flagged")
            and r["verdict"] == "agrees" and lo <= r["gp_age_h"] <= hi]
    step = max(1, len(pool) // top)
    controls = pool[::step][:top]

    print(f"\n  {len(suspects)} top suspects vs {len(controls)} matched controls")
    print(f"  controls: same regime, catalog age {lo:.1f}-{hi:.1f}h, detect.py said "
          f"'agrees'")

    hist = get_history(session, [r["norad"] for r in suspects + controls], days)

    def measure(group):
        steps, rates, skipped = [], [], 0
        for r in group:
            pts = hist.get(r["norad"], [])
            if len(pts) < 5:
                skipped += 1
                continue
            steps.append(biggest_step_km(pts, centre))
            rates.append(descent_km_per_day(pts))
        return steps, rates, skipped

    s_steps, s_rates, s_skip = measure(suspects)
    c_steps, c_rates, c_skip = measure(controls)

    print(f"\n  biggest altitude step within +/-{WINDOW_DAYS:g} days of the snapshot:")
    print(summarise("SUSPECTS", s_steps))
    print(summarise("CONTROLS", c_steps))
    if s_skip or c_skip:
        print(f"  (skipped for thin history: {s_skip} suspects, {c_skip} controls)")

    if not s_steps or not c_steps:
        print("\n  not enough history on one side to compare - no verdict.")
        return {}

    # The bar is set by the controls, not by us. An object clears it only if it moved
    # more than 90% of the objects detect.py called ordinary.
    bar = sorted(c_steps)[int(0.9 * (len(c_steps) - 1))]
    over_s = sum(1 for v in s_steps if v > bar)
    over_c = sum(1 for v in c_steps if v > bar)
    print(f"\n  bar = 90th percentile of the CONTROLS = {bar:.3f} km")
    print(f"  suspects over the bar   {over_s:>4} / {len(s_steps)} "
          f"({100 * over_s / len(s_steps):.0f}%)")
    print(f"  controls over the bar   {over_c:>4} / {len(c_steps)} "
          f"({100 * over_c / len(c_steps):.0f}%)  <- 10% by construction")

    ratio = (over_s / len(s_steps)) / max(over_c / len(c_steps), 1e-9)
    med_ratio = statistics.median(s_steps) / max(statistics.median(c_steps), 1e-9)
    print(f"\n  suspects move {med_ratio:.1f}x more than controls (median step)")
    print(f"  and clear the bar {ratio:.1f}x as often")
    if med_ratio < 1.2 and ratio < 1.5:
        print("\n  ** NO SIGNAL. The suspects look like everything else. **\n"
              "     detect.py's ranking is not tracking real movement, or this\n"
              "     verifier cannot see the kind of movement it finds.")
    else:
        print(f"\n  The two methods agree more often than chance. That is the first\n"
              f"  number here that detect.py did not grade itself.")
    return {"bar_km": bar, "over_suspects": over_s, "n_suspects": len(s_steps),
            "over_controls": over_c, "n_controls": len(c_steps),
            "median_ratio": med_ratio}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="starlink")
    ap.add_argument("--flags", action="store_true", help="check the data-quality flags")
    ap.add_argument("--top", type=int, default=0, help="check the top N suspects")
    ap.add_argument("--days", type=int, default=30, help="days of history to pull")
    ap.add_argument("--pct", type=float, default=95.0)
    ap.add_argument("--min-km", type=float, default=5.0)
    args = ap.parse_args()
    if not args.flags and not args.top:
        ap.error("give --flags or --top N")

    snap = detect.newest_snapshot_dir()
    centre = snapshot_moment(snap)
    print(f"  snapshot   {snap.relative_to(detect.ARCHIVE)}  ({centre:%Y-%m-%d %H:%MZ})")
    res = detect.analyze(snap, args.group, args.pct, args.min_km,
                         detect.MAX_PLAUSIBLE_KM)
    if not res or res.get("skipped"):
        sys.exit("cannot score the newest snapshot")
    rows = res["rows"]
    print(f"  scored     {len(rows)} objects")

    session = login()
    print("  space-track login ok")
    if args.flags:
        run_flags(session, rows, centre, args.days)
    if args.top:
        run_top(session, rows, centre, args.days, args.top)

    print("\n  CAVEAT: GP_HISTORY is the public catalog's own history, so this shares "
          "the\n  catalog side with detect.py. It is independent of the operator data, "
          "the\n  age-binning and the persistence logic - but it is NOT operator ground "
          "truth.\n  Two methods agreeing is not proof that a satellite burned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
