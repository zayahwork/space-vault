"""verify_geo.py - check GEO candidates against the observables GEO burns actually move.

WHY A SECOND VERIFIER
verify.py watches ALTITUDE for the step a burn leaves behind. That works in LEO, where a
reboost is a change in orbital energy and shows up directly. At GEO it is close to
half-blind, and the reason is physics, not tuning:

  North-south station-keeping is roughly 95% of a GEO bird's station-keeping budget
  (~45-50 m/s per year against ~2 m/s for east-west). N-S burns fight the Sun and Moon
  pulling the orbit plane over, and what they change is INCLINATION - not altitude.

So the dominant maneuver at GEO is invisible to an altitude-only verifier by construction.
[[RESULTS - Beyond Starlink]] said the fix was "a GEO-shaped verifier (longitude drift,
inclination)". This is that.

WHAT IT WATCHES INSTEAD
  1. INCLINATION step        - the north-south burn. The big one.
  2. LONGITUDE DRIFT step    - the east-west burn. A GEO satellite parked over a longitude
                               holds a mean motion within a hair of synchronous; the
                               residual is its drift rate, in degrees per day. An E-W burn
                               is a STEP in that rate. Derived from mean motion, so it
                               needs no ephemeris beyond what the catalog already gives.

THE CONTROL GROUP IS STILL THE WHOLE POINT
Same discipline as verify.py: every run also measures objects detect.py called ORDINARY,
drawn from the same catalog-age range, through identical logic. "60% of suspects moved"
means nothing until you know what share of ordinary objects also moved.

WHAT THIS IS NOT
GP_HISTORY is the public catalog's own history, so this shares the catalog side with
detect.py. It is independent of the operator (SupGP) side, of the age binning and of the
persistence logic - but it is NOT operator ground truth. No GEO operator publishes a
maneuver log. Two methods agreeing is not proof.

THE TWO OBSERVABLES ARE NOT EQUALLY INDEPENDENT - READ THIS BEFORE QUOTING A NUMBER
detect.py ranks on RMS position difference over 6 hours, and that difference is dominated
by ALONG-TRACK error, which is essentially a disagreement about mean motion. The drift
rate below is *derived from mean motion*. So a big drift step and a big detect.py gap are
partly two views of the same quantity, and the drift column will tend to agree with the
detector by construction.

Inclination does not share that axis. A plane change barely touches along-track position
over six hours, so an inclination step is much closer to genuinely independent evidence.

When these two disagree, believe inclination. When drift alone is dramatic, treat it as
the weaker claim, however good the ratio looks.

Usage:
  python verify_geo.py --group intelsat --top 15
  python verify_geo.py --group ses --top 15 --days 60
"""
import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402
import verify  # noqa: E402  - login, BASE, BATCH and politeness are shared, not copied

CACHE = Path(__file__).resolve().parent / "verify_geo_cache"

# Sidereal day = 86,164.0905 s, so a satellite holding station over one longitude turns
# 86400/86164.0905 = 1.00273791 revolutions per solar day. Everything below is the
# residual from that number.
GEO_SYNC_REV_DAY = 86400.0 / 86164.0905

WINDOW_DAYS = 3.0     # how close to the snapshot a step has to be to count
MIN_POINTS = 5        # below this an object has no history worth stepping through


def drift_deg_per_day(mean_motion_rev_day):
    """Longitude drift rate implied by a mean motion, degrees/day. East is positive.

    A satellite turning faster than the Earth pulls ahead of its slot and drifts east;
    slower and it falls behind and drifts west. Exactly synchronous is zero. This is the
    quantity an east-west station-keeping burn exists to reset, which is why a STEP in it
    is the burn's signature.
    """
    return (mean_motion_rev_day - GEO_SYNC_REV_DAY) * 360.0


def get_geo_history(session, norads, days):
    """Per NORAD: [(epoch, inclination_deg, drift_deg_per_day)], batched and cached.

    verify.get_history keeps altitude only, so this asks for the two fields that matter
    up here. Cached on its own path so the two verifiers cannot read each other's files.
    """
    CACHE.mkdir(exist_ok=True)
    out, missing = {}, []
    for n in norads:
        f = CACHE / f"{n}_{days}d.json"
        if f.exists():
            out[n] = [(datetime.fromisoformat(t), inc, dr)
                      for t, inc, dr in json.loads(f.read_text(encoding="utf-8"))]
        else:
            missing.append(n)

    for i in range(0, len(missing), verify.BATCH):
        chunk = missing[i:i + verify.BATCH]
        url = (verify.BASE + "/basicspacedata/query/class/gp_history/NORAD_CAT_ID/"
               + ",".join(str(c) for c in chunk)
               + f"/EPOCH/%3Enow-{days}/orderby/EPOCH%20asc/format/json")
        print(f"  fetching {len(chunk)} objects ({i + len(chunk)}/{len(missing)})...")
        resp = session.get(url, timeout=180)
        resp.raise_for_status()

        grouped = {}
        for row in resp.json():
            try:
                n = int(row["NORAD_CAT_ID"])
                grouped.setdefault(n, []).append((
                    datetime.fromisoformat(row["EPOCH"]).replace(tzinfo=timezone.utc),
                    float(row["INCLINATION"]),
                    drift_deg_per_day(float(row["MEAN_MOTION"]))))
            except (KeyError, ValueError, TypeError):
                continue
        for n in chunk:
            pts = sorted(set(grouped.get(n, [])))
            out[n] = pts
            (CACHE / f"{n}_{days}d.json").write_text(
                json.dumps([[t.isoformat(), inc, dr] for t, inc, dr in pts]),
                encoding="utf-8")
        if i + verify.BATCH < len(missing):
            time.sleep(verify.POLITE_SEC)
    return out


# ------------------------------------------------------------------ the measures

def biggest_step(points, centre, component, window_days=WINDOW_DAYS):
    """Largest change in one component between consecutive records near `centre`.

    component: 1 = inclination (deg), 2 = longitude drift rate (deg/day).

    A burn shows in the catalog as a step - the orbit was one thing, then another.
    Restricted to a window around the snapshot so we measure what the detector was
    reacting to rather than something that happened last month.
    """
    lo, hi = centre - timedelta(days=window_days), centre + timedelta(days=window_days)
    best = 0.0
    for a, b in zip(points, points[1:]):
        if lo <= b[0] <= hi:
            best = max(best, abs(b[component] - a[component]))
    return best


def summarise(name, values, unit):
    if not values:
        return f"  {name:<26} no data"
    return (f"  {name:<26} n={len(values):<4} median {statistics.median(values):9.6f} {unit}"
            f"   90th {sorted(values)[int(0.9 * (len(values) - 1))]:9.6f} {unit}")


def compare(label, unit, s_vals, c_vals):
    """Suspects against controls on one observable. Returns a verdict dict, or {}."""
    print(f"\n  {label}")
    print(summarise("SUSPECTS", s_vals, unit))
    print(summarise("CONTROLS", c_vals, unit))
    if not s_vals or not c_vals:
        print("    not enough history on one side - no verdict on this observable.")
        return {}

    # The bar is set by the controls, never by us. An object clears it only by moving
    # more than 90% of the objects detect.py called ordinary.
    bar = sorted(c_vals)[int(0.9 * (len(c_vals) - 1))]
    over_s = sum(1 for v in s_vals if v > bar)
    over_c = sum(1 for v in c_vals if v > bar)
    med_s, med_c = statistics.median(s_vals), statistics.median(c_vals)
    med_ratio = med_s / max(med_c, 1e-12)
    rate_ratio = (over_s / len(s_vals)) / max(over_c / len(c_vals), 1e-12)
    print(f"    bar (90th pct of CONTROLS) = {bar:.6f} {unit}")
    print(f"    suspects over the bar  {over_s:>3}/{len(s_vals)} "
          f"({100 * over_s / len(s_vals):.0f}%)   "
          f"controls {over_c:>3}/{len(c_vals)} ({100 * over_c / len(c_vals):.0f}%)")
    print(f"    suspects move {med_ratio:.2f}x the controls' median, and clear the bar "
          f"{rate_ratio:.2f}x as often")
    # A signal has to survive BOTH readings. A median ratio on its own is easy to get
    # from four objects, and it means nothing if those objects clear the controls' bar
    # LESS often than the controls do - that is evidence against separation being read
    # as evidence for it. Requiring both is the difference between a result and a story.
    signal = med_ratio >= 1.2 and rate_ratio >= 1.5
    if not signal:
        if med_ratio >= 1.2 > rate_ratio:
            print(f"    -> NO SIGNAL: suspects' median is {med_ratio:.2f}x, but they "
                  f"clear the controls' bar\n       LESS often than the controls "
                  f"({100 * over_s / len(s_vals):.0f}% vs "
                  f"{100 * over_c / len(c_vals):.0f}%). The two disagree, so neither "
                  f"counts.")
        else:
            print("    -> NO SIGNAL on this observable. Say so.")
    return {"bar": bar, "med_ratio": med_ratio, "rate_ratio": rate_ratio, "signal": signal,
            "over_s": over_s, "n_s": len(s_vals), "over_c": over_c, "n_c": len(c_vals)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--group", default="intelsat")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--days", type=int, default=60,
                    help="how much GP_HISTORY to pull. GEO station-keeping cycles run "
                         "weeks, so a LEO-sized window sees nothing")
    ap.add_argument("--pct", type=float, default=95.0)
    ap.add_argument("--max-km", type=float, default=detect.MAX_PLAUSIBLE_KM)
    args = ap.parse_args()

    snap = detect.newest_snapshot_dir()
    run = detect.analyze(snap, args.group, args.pct, None, args.max_km, allow_live=False)
    if not run or run.get("skipped") or not run["rows"]:
        sys.exit(f"cannot score {args.group} at {snap}")
    rows = run["rows"]

    print(f"\n  group      {args.group}")
    print(f"  snapshot   {snap.relative_to(detect.ARCHIVE)}")
    print(f"  regime     {run['regime']} (median altitude "
          f"{statistics.median([r['altitude_km'] for r in rows]):,.0f} km)")
    if run["regime"] not in ("GEO", "mixed"):
        print(f"\n  WARNING: {args.group} is {run['regime']}, not GEO. The observables "
              f"below\n  are the right ones for a geostationary belt and may mean little "
              f"here.\n  verify.py's altitude step is the LEO tool.")

    suspects = sorted([r for r in rows if r.get("flagged")],
                      key=lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9),
                      reverse=True)[:args.top]
    if not suspects:
        print("\n  no suspects in this snapshot - nothing to verify.")
        return 0

    # Controls: called ordinary, drawn across the same catalog-age range, so the two
    # groups differ in what detect.py SAID about them, not in what they are.
    ages = [r["gp_age_h"] for r in suspects]
    lo, hi = min(ages), max(ages)
    pool = [r for r in rows if not r.get("flagged") and r["verdict"] == "agrees"
            and lo <= r["gp_age_h"] <= hi]
    if not pool:                      # GEO fleets are small; widen rather than give up
        pool = [r for r in rows if not r.get("flagged")]
        print("  (no 'agrees' object shares the suspects' age range - controls widened "
              "to all unflagged)")
    step = max(1, len(pool) // max(args.top, 1))
    controls = pool[::step][:args.top]

    print(f"\n  {len(suspects)} suspects vs {len(controls)} matched controls")
    print(f"  controls: detect.py said ordinary, catalog age {lo:.1f}-{hi:.1f}h")

    centre = datetime.fromisoformat(
        json.loads((snap / "manifest.json").read_text(encoding="utf-8"))["captured_utc"])
    if centre.tzinfo is None:
        centre = centre.replace(tzinfo=timezone.utc)

    session = verify.login()
    hist = get_geo_history(session, [r["norad"] for r in suspects + controls], args.days)

    def measure(group):
        inc, drift, skipped = [], [], 0
        for r in group:
            pts = hist.get(r["norad"], [])
            if len(pts) < MIN_POINTS:
                skipped += 1
                continue
            inc.append(biggest_step(pts, centre, 1))
            drift.append(biggest_step(pts, centre, 2))
        return inc, drift, skipped

    s_inc, s_drift, s_skip = measure(suspects)
    c_inc, c_drift, c_skip = measure(controls)
    if s_skip or c_skip:
        print(f"  (skipped for thin history: {s_skip} suspects, {c_skip} controls)")

    print(f"\n  biggest step within +/-{WINDOW_DAYS:g} days of the snapshot, "
          f"over {args.days} days of history")
    inc_v = compare("INCLINATION - the north-south burn (~95% of GEO station-keeping)",
                    "deg", s_inc, c_inc)
    dr_v = compare("LONGITUDE DRIFT RATE - the east-west burn  [WEAKER EVIDENCE: derived "
                   "from mean motion,\n  which is also what detect.py's along-track gap "
                   "mostly measures]",
                   "deg/day", s_drift, c_drift)

    print("\n  " + "-" * 66)
    named = [("inclination", inc_v), ("longitude drift", dr_v)]
    verdicts = [v for _, v in named if v]
    hits = [name for name, v in named if v and v["signal"]]
    if not verdicts:
        print("  NO VERDICT - not enough history on one side.")
    elif hits:
        print(f"  Suspects separate from controls on: {', '.join(hits)}.")
        print("  Two methods agreeing on the same objects. NOT operator ground truth -")
        print("  no GEO operator publishes a maneuver log.")
    else:
        print("  NO SIGNAL on either observable. On today's data these GEO candidates")
        print("  are not corroborated, and we should say so before anyone else does.")

    # Say the sample size out loud next to the verdict, not in a footnote. GEO fleets are
    # small and a 95th-percentile ranking of 44 objects can only ever yield a handful, so
    # every ratio here is computed off single figures.
    smallest = min(v["n_s"] for v in verdicts) if verdicts else 0
    if verdicts and smallest < 10:
        print(f"\n  n={smallest} suspects. That is an anecdote with a table around it,")
        print(f"  whichever way it points. Re-run as the GEO archive grows.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
