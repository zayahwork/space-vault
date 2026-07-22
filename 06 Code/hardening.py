"""hardening.py - does the verified separation survive at larger n? (issue 003)

WHY THIS EXISTS
The number we put in front of people is "~68-72% of top suspects clear a bar only ~10% of
matched controls clear". That was measured on the top 75. A rate measured on the top 75 is
a rate for the top 75: the suspects are ranked, so the ones further down the list are by
construction weaker candidates, and the separation SHOULD sag as n grows. The question is
how fast, and whether it is still a separation at n=300.

Better we find the sag ourselves than have Kelso or a broker find it.

MEASURED ONCE, UNDER THE PRODUCTION WINDOW
Run after issue 018, so every rate here comes from the window the live pipeline actually
uses (verify.window_for_regime), not a harness constant. And the groups are chosen by
verify.select_groups - the same function verify.py calls - so a bigger n is the same
measurement with more objects in it, not a different measurement.

THE CONTROL RATE IS PRINTED BESIDE THE SUSPECT RATE, ALWAYS
"72% of suspects moved" means nothing without "and 11% of ordinary objects also moved".
The bar is the controls' own 90th percentile, so their rate is ~10% BY CONSTRUCTION, not
by measurement - it is printed anyway, because the day it stops being ~10% something is
broken and we want to see it.

Usage:
  python hardening.py                                  # starlink, both published snapshots
  python hardening.py --group oneweb --n 10 25 50
  python hardening.py --snapshots 2026-07-22/0200Z 2026-07-22/0800Z
"""
import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402
import verify  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# The two snapshots the published 72%/68% headline was replicated on. Kept as the default
# so the hardened table extends that result rather than quietly re-basing it on newer data.
PUBLISHED_SNAPSHOTS = ("2026-07-22/0200Z", "2026-07-22/0800Z")
MIN_POINTS = 5


def score(session, rows, centre, regime, top, days):
    """One (snapshot, n) cell: suspects vs controls under the production window."""
    before, after, _ = verify.window_for_regime(regime)
    suspects, controls = verify.select_groups(rows, top)
    if not suspects or not controls:
        return None

    hist = verify.get_history(session, [r["norad"] for r in suspects + controls], days)

    def steps(group):
        out, thin = [], 0
        for r in group:
            pts = hist.get(r["norad"], [])
            if len(pts) < MIN_POINTS:
                thin += 1
                continue
            out.append(verify.biggest_step_km(pts, centre, before, after))
        return out, thin

    s_steps, s_thin = steps(suspects)
    c_steps, c_thin = steps(controls)
    if not s_steps or not c_steps:
        return None

    bar = sorted(c_steps)[int(0.9 * (len(c_steps) - 1))]
    over_s = sum(1 for v in s_steps if v > bar)
    over_c = sum(1 for v in c_steps if v > bar)
    med_s, med_c = statistics.median(s_steps), statistics.median(c_steps)
    return {"n_asked": top, "n_suspects": len(s_steps), "n_controls": len(c_steps),
            "thin_suspects": s_thin, "thin_controls": c_thin,
            "bar_km": bar, "median_suspect_km": med_s, "median_control_km": med_c,
            "median_ratio": med_s / max(med_c, 1e-12),
            "suspect_rate": over_s / len(s_steps),
            "control_rate": over_c / len(c_steps),
            "over_s": over_s, "over_c": over_c,
            "window": (before, after)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--group", default="starlink")
    ap.add_argument("--n", type=int, nargs="+", default=[25, 75, 150, 300])
    ap.add_argument("--snapshots", nargs="+", default=list(PUBLISHED_SNAPSHOTS))
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--pct", type=float, default=95.0)
    ap.add_argument("--min-km", type=float, default=None)
    args = ap.parse_args()

    session = verify.login()
    print(f"  group      {args.group}")
    print(f"  space-track login ok")

    results = {}
    for snap_name in args.snapshots:
        snap = detect.ARCHIVE / snap_name
        if not snap.exists():
            print(f"\n  !! {snap_name} not in the archive - skipped, not silently dropped")
            continue
        res = detect.analyze(snap, args.group, args.pct, args.min_km,
                             detect.MAX_PLAUSIBLE_KM, allow_live=False)
        if not res or res.get("skipped") or not res["rows"]:
            print(f"\n  !! {snap_name} could not be scored - skipped")
            continue
        centre = verify.snapshot_moment(snap)
        regime = res.get("regime", "LEO")
        before, after, basis = verify.window_for_regime(regime)
        obs = verify.observable_window(centre, after)

        print(f"\n  == {snap_name} ==  {len(res['rows'])} objects, regime {regime}")
        print(f"     window -{before:g}/+{after:g} d   {basis}")
        if obs["provisional"]:
            print(f"     PROVISIONAL: {obs['observable_after_days']:.2f} d of the "
                  f"+{after:g} d forward reach published; settles in "
                  f"{obs['settles_in_days']:.1f} d")
        for n in args.n:
            cell = score(session, res["rows"], centre, regime, n, args.days)
            if cell:
                results[(snap_name, n)] = cell

    if not results:
        print("\n  nothing scoreable.")
        return 1

    print(f"\n\n  {'snapshot':<20}{'n':>5}{'suspects':>10}{'bar km':>9}"
          f"{'median x':>10}{'SUSPECTS over':>15}{'CONTROLS over':>15}")
    for (snap_name, n), c in sorted(results.items()):
        print(f"  {snap_name:<20}{n:>5}{c['n_suspects']:>10}{c['bar_km']:>9.3f}"
              f"{c['median_ratio']:>10.1f}"
              f"{f'{c['over_s']}/{c['n_suspects']} ({100 * c['suspect_rate']:.0f}%)':>15}"
              f"{f'{c['over_c']}/{c['n_controls']} ({100 * c['control_rate']:.0f}%)':>15}")

    print("\n  CONTROLS' rate is ~10% BY CONSTRUCTION (the bar is their own 90th")
    print("  percentile), so it is a sanity check, not a second measurement.")
    thin = sum(c["thin_suspects"] for c in results.values())
    if thin:
        print(f"\n  {thin} suspect-slots across the sweep had too little GP_HISTORY to "
              f"score\n  and are excluded from their denominators, not counted as misses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
