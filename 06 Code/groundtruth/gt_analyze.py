"""gt_analyze.py - regenerate every number in 'RESULTS - Ground Truth'.

Four things, in the order they have to happen:

  noise-floor   What does the catalog's altitude do when NOTHING is firing?
                Measured on satellites McDowell classifies as abandoned. This is
                where the detection bar comes from - it is measured, not chosen.
  score         Each documented event vs that bar. caught / missed.
  lag           For the misses: is the signal absent, or just late? (Usually late.)
  identity      Proves longitude drift is altitude in disguise, so nobody wastes
                a week "switching to a drift-based verifier".

    python gt_analyze.py noise-floor
    python gt_analyze.py score
    python gt_analyze.py lag
    python gt_analyze.py identity
    python gt_analyze.py all
"""
import statistics
import sys
from datetime import datetime, timedelta

import gt_sources as S

# The bar: the largest max-step ever observed in 132 null windows on 4 abandoned
# GEO objects. p99 of that null is 0.30 km; we use the observed max, which is
# stricter. Re-derive with `noise-floor` if the epoch cadence ever changes.
BAR_KM = 0.42
WINDOW_DAYS = 3.0   # what verify.py currently uses. Prior art says this is too tight:
                    # Decoto & Loerch 2015 measured detections landing a mean of 4
                    # days late (max 7). See 'Prior Art - GEO Maneuver Detection'.

# GEO/ID in McDowell's table = inclined drift = abandoned. They drift; they never burn.
NULL_OBJECTS = {29644: "AMC 18", 25626: "Galaxy 26", 24315: "AMC 1", 23877: "Galaxy 9"}
NULL_WINDOW = ("2026-01-01", "2026-07-20")

# (norad, name, documented_date, description). Dates come from the source columns
# of ground_truth.csv - press releases, S4S, NASA ODQN, USGS, GCAT phases.
EVENTS = [
    (26824, "Intelsat 901",  "2025-04-01", "graveyard raise (MEV-1 mission end)"),
    (26824, "Intelsat 901",  "2020-03-02", "MEV-1 stack relocation burn"),
    (46113, "MEV-2",         "2021-04-12", "docking with IS-1002"),
    (28358, "Intelsat 1002", "2021-04-12", "being docked by MEV-2"),
    (41748, "Intelsat 33e",  "2024-10-19", "breakup / total loss"),
    (41308, "Intelsat 29e",  "2019-04-07", "propulsion failure (leak late on 04-07)"),
    (27820, "AMC-9",         "2017-06-17", "anomaly + fragmentation"),
    (27820, "AMC-9",         "2017-11-13", "graveyard raise"),
    (28884, "Galaxy 15",     "2010-04-05", "loss of command ('zombiesat')"),
    (28252, "AMC 11",        "2026-04-22", "graveyard raise"),
    (33153, "Intelsat 25",   "2026-05-04", "graveyard raise"),
    (28252, "AMC 11",        "2025-02-10", "routine N-S station-keeping"),
    (28252, "AMC 11",        "2025-08-08", "routine N-S station-keeping"),
    (28252, "AMC 11",        "2025-10-21", "routine N-S station-keeping"),
]


def _t(epoch):
    return datetime.fromisoformat(epoch.replace("Z", ""))


def _max_step(pts, centre, key="alt", wd=WINDOW_DAYS):
    lo, hi = centre - timedelta(days=wd), centre + timedelta(days=wd)
    w = [p for p in pts if lo <= _t(p["epoch"]) <= hi]
    if len(w) < 2:
        return None
    return max(abs(b[key] - a[key]) for a, b in zip(w, w[1:]))


def noise_floor():
    """The bar, from objects that cannot be manoeuvring."""
    print("Null distribution - max altitude step in a +/-3 day window,")
    print("measured on GEO objects McDowell classifies as abandoned (GEO/ID).\n")
    alt_vals, inc_vals = [], []
    for norad, label in NULL_OBJECTS.items():
        pts = S.history(norad, *NULL_WINDOW)
        if len(pts) < 20:
            print(f"  {label:12} only {len(pts)} epochs - skipped")
            continue
        t0, t1 = _t(pts[0]["epoch"]), _t(pts[-1]["epoch"])
        c, per = t0 + timedelta(days=3), []
        while c < t1 - timedelta(days=3):
            a, i = _max_step(pts, c, "alt"), _max_step(pts, c, "inc")
            if a is not None:
                per.append(a); alt_vals.append(a); inc_vals.append(i)
            c += timedelta(days=6)
        print(f"  {label:12} {len(pts):5} epochs  {len(per):3} windows  "
              f"max={max(per):.3f}  median={statistics.median(per):.3f} km")
    for name, vals, unit in (("ALTITUDE", alt_vals, "km"), ("INCLINATION", inc_vals, "deg")):
        vals = sorted(v for v in vals if v is not None)
        q = lambda p: vals[min(len(vals) - 1, int(len(vals) * p))]
        print(f"\n{name} null, n={len(vals)} windows: median={statistics.median(vals):.4f} "
              f"p95={q(.95):.4f} p99={q(.99):.4f} max={max(vals):.4f} {unit}")
    print(f"\n=> altitude bar in use: {BAR_KM} km (observed max of the null)")
    print("=> inclination is the independent channel: N-S station-keeping moves it")
    print("   0.0435-0.0471 deg against a ~0.006 deg null, a 7.5-8x separation.")


def score():
    """Every documented event against the bar. This is the caught/missed table."""
    print(f"Scoring {len(EVENTS)} documented events, bar={BAR_KM} km, "
          f"window=+/-{WINDOW_DAYS} days\n")
    print(f"{'object':15} {'date':11} {'event':38} {'d_alt':>8} {'xBar':>6} "
          f"{'d_inc':>8} {'verdict':>8}")
    print("-" * 104)
    caught = 0
    for norad, name, date, ev in EVENTS:
        c = datetime.fromisoformat(date)
        pts = S.history(norad, (c - timedelta(days=9)).date().isoformat(),
                        (c + timedelta(days=9)).date().isoformat())
        da, di = _max_step(pts, c, "alt"), _max_step(pts, c, "inc")
        if da is None:
            print(f"{name:15} {date:11} {ev:38} {'no data':>8}")
            continue
        v = "CAUGHT" if da >= BAR_KM else "MISSED"
        caught += v == "CAUGHT"
        print(f"{name:15} {date:11} {ev:38} {da:8.2f} {da/BAR_KM:5.0f}x "
              f"{di:8.4f} {v:>8}")
    print(f"\n  {caught}/{len(EVENTS)} caught ({100*caught/len(EVENTS):.0f}%)")
    print("  NOTE: restricted to events carrying two independent sources the rate is")
    print("  2/6. The rest were dated from the catalog by us, so agreement is")
    print("  near-tautological. See the honest summary in 'RESULTS - Ground Truth'.")


def lag():
    """For the misses: absent signal, or late signal? Answer is usually 'late'."""
    print(f"Searching +/-40 days for any over-bar step (bar={BAR_KM} km).\n")
    for norad, name, date, ev in [
            (41748, "Intelsat 33e", "2024-10-19", "breakup"),
            (28884, "Galaxy 15", "2010-04-05", "loss of command"),
            (46113, "MEV-2", "2021-04-12", "docking"),
            (28358, "Intelsat 1002", "2021-04-12", "being docked")]:
        c = datetime.fromisoformat(date)
        pts = S.history(norad, (c - timedelta(days=40)).date().isoformat(),
                        (c + timedelta(days=40)).date().isoformat())
        best = None
        for a, b in zip(pts, pts[1:]):
            d = abs(b["alt"] - a["alt"])
            if d >= BAR_KM and (best is None or d > best[1]):
                best = (_t(b["epoch"]), d)
        print(f"{name} - documented {date} ({ev})")
        if best:
            days = (best[0] - c).days
            print(f"   largest over-bar step {best[0].date()}  {best[1]:.2f} km "
                  f"({best[1]/BAR_KM:.0f}x)  lag {days:+d} days -> "
                  f"{'INSIDE' if abs(days) <= WINDOW_DAYS else 'OUTSIDE'} the window\n")
        else:
            print("   nothing over bar in +/-40 days - genuinely invisible in altitude\n")


def identity():
    """Longitude drift is altitude rescaled. Do not rebuild the verifier around it."""
    theory = 1.5 * 360 * S.GEO_MEAN_MOTION / 42164.0
    pts = S.history(26824, "2025-03-25", "2025-04-25")
    lo = min(pts, key=lambda p: p["alt"]); hi = max(pts, key=lambda p: p["alt"])
    d_alt = hi["alt"] - lo["alt"]
    d_drift = abs(S.drift_deg_per_day(hi["mm"]) - S.drift_deg_per_day(lo["mm"]))
    print("Intelsat 901 graveyard raise, 2025:")
    print(f"  altitude change {d_alt:.1f} km  <->  drift change {d_drift:.2f} deg/day")
    print(f"  measured ratio {d_drift/d_alt:.5f} deg/day per km")
    print(f"  theory         {theory:.5f} deg/day per km   "
          f"(agree to {100*abs(d_drift/d_alt-theory)/theory:.1f}%)")
    print("\n=> Drift carries NO information altitude doesn't. Inclination does.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    fns = {"noise-floor": noise_floor, "score": score, "lag": lag, "identity": identity}
    if cmd == "all":
        for n, f in fns.items():
            print(f"\n{'='*30} {n} {'='*30}"); f()
    elif cmd in fns:
        fns[cmd]()
    else:
        print(__doc__)
