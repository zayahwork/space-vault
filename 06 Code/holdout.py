"""holdout.py - the headline number, scored on data it could not have been tuned on.

WHY THIS EXISTS (issue 033)
The first question technical diligence asks is "did you tune on what you tested?". Until
now the honest answer was "mostly no, but nothing proves it": every constant in the
pipeline was chosen while looking at the same July-22 snapshots the 96%-vs-11% headline
is measured on. This file makes the separation explicit, enforced, and reusable weekly.

THE CUTOFF
2026-07-23 00:00Z. Everything tunable was frozen at or before it:
  - detect.py's constants (age bins, pct 95, regime floors, decay threshold, 500 km gate)
    predate 2026-07-22 and were last touched that day;
  - the verify window table (issue 018) and the observability correction (issue 003)
    both closed 2026-07-22;
  - the stored alert bars were learned 2026-07-22T19:16Z from snapshots up to
    2026-07-22/1400Z - provenance is checked here, not assumed.
A snapshot counts as UNSEEN only if captured STRICTLY AFTER the cutoff. Nothing captured
after it has ever been used to pick a constant, a window, or a bar.

THE TWO SPLITS THE CARD DEMANDS
  1. SNAPSHOTS: suspects are selected and scored on post-cutoff snapshots only, with the
     exact production code path (detect.analyze rank mode -> verify.select_groups ->
     controls' own 90th-percentile bar). The tuned-set numbers are recomputed beside them.
  2. GROUND-TRUTH EVENTS: the -3/+14d GEO window was chosen on the 16 rows that existed
     at issue 015. Those rows may never score the window again. Every row added since -
     and every row added in the future - is holdout by default (frozen key list below).

MATCHED REACH, OR THE COMPARISON LIES
Issue 003 proved a same-day LEO verification under-reports: the forward half of the
window holds no published data yet (76% at zero reach, plateau 96% by ~0.5d). So a fresh
holdout run must be compared against the TUNED set at the SAME forward reach, not against
the settled 96% - and the reach is measured from the fetched history itself, never the
wall clock, because a cached file has no idea what "now" is.

Each scored snapshot gets its own cache directory (holdout_cache/<snapshot>/). The shared
verify_cache is keyed by object+days only: a file cached yesterday silently ends
yesterday, which for a fresh snapshot means zero forward reach wearing a full window's
label.

Usage:
  python holdout.py                    # starlink, top 75, every unseen snapshot
  python holdout.py --top 75 150
  python holdout.py --cutoff 2026-07-30T00:00:00  # next week's re-run, new freeze
"""
import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402
import verify  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
HOLDOUT_CACHE = HERE / "holdout_cache"
REFEREE_JSON = HERE / "output" / "referee_026.json"
OUT_JSON = HERE / "output" / "holdout_033.json"

CUTOFF_UTC = datetime(2026, 7, 23, 0, 0, tzinfo=timezone.utc)
CUTOFF_BASIS = ("all detector constants, the verify window table (issue 018), the "
                "observability correction (issue 003) and the stored bars (learned "
                "2026-07-22T19:16Z) were fixed on or before 2026-07-22")

# The published tuned-set snapshots and their settled headline, for the side-by-side.
TUNED_SNAPSHOTS = ("2026-07-22/0200Z", "2026-07-22/0800Z")
TUNED_SETTLED = "96% vs 11% at top-75, settled (plateau by ~0.5d reach; issue 003)"

# Forward reaches to sweep, matching the published observability table. Each run clamps
# this list to what the fetched history actually contains.
REACHES = (0.0, 0.25, 0.5, 1.5, 3.0)
MIN_POINTS = 5          # same scoreability rule as verify.py / hardening.py

# Every GEO ground-truth row that existed when the -3/+14d window was chosen (issue 015:
# 14 scoreable + MEV-1 excluded + AMC 18 null). FROZEN - these rows picked the window, so
# they may never be quoted as evidence for it again. Any row not in this list is holdout.
TUNING_EVENT_KEYS = frozenset({
    (44625, "2020-02-25"),      # MEV-1 (excluded then, excluded now)
    (46113, "2021-04-12"),      # MEV-2
    (28358, "2021-04-12"),      # Intelsat 1002 docking
    (41748, "2024-10-19"),      # Intelsat 33e
    (41308, "2019-04-07"),      # Intelsat 29e
    (27820, "2017-06-17"),      # AMC-9 anomaly
    (28884, "2010-04-05"),      # Galaxy 15
    (26824, "2025-03-31"),      # Intelsat 901 graveyard
    (26824, "2020-03-02"),      # Intelsat 901 relocation
    (27820, "2017-11-13"),      # AMC-9 graveyard
    (28252, "2026-04-22"),      # AMC 11 graveyard
    (33153, "2026-05-04"),      # Intelsat 25 graveyard
    (28252, "2025-02-10"),      # AMC 11 NS
    (28252, "2025-08-08"),      # AMC 11 NS
    (28252, "2025-10-21"),      # AMC 11 NS
    (29644, "2025-01-01"),      # AMC 18 (the null)
})


# ------------------------------------------------------------------ pure pieces

def snap_name_to_dt(name):
    """'2026-07-22/1400Z' -> its capture instant, UTC."""
    day, hm = name.split("/")
    return datetime.strptime(f"{day} {hm}", "%Y-%m-%d %H%MZ").replace(
        tzinfo=timezone.utc)


def split_snapshots(names, cutoff):
    """(tuned-side, unseen) - unseen means captured STRICTLY AFTER the cutoff. A
    snapshot captured at the cutoff instant was available to tuning and stays out."""
    pre = [n for n in names if snap_name_to_dt(n) <= cutoff]
    post = [n for n in names if snap_name_to_dt(n) > cutoff]
    return pre, post


def baseline_violations(baseline, cutoff):
    """Learn-set snapshots captured after the cutoff, by name. One of these and the
    zero-overlap claim is dead - the caller refuses, it does not warn-and-continue."""
    return [s for s in baseline.get("snapshots", [])
            if snap_name_to_dt(s) > cutoff]


def split_events(events):
    """(tuning, holdout) ground-truth rows by the FROZEN key list. Disjoint by
    construction; anything not in the frozen set - including rows added after this file
    was written - is holdout automatically."""
    tune = [e for e in events if (e["norad"], e["date"]) in TUNING_EVENT_KEYS]
    hold = [e for e in events if (e["norad"], e["date"]) not in TUNING_EVENT_KEYS]
    return tune, hold


def data_reach_days(history, centre):
    """How far past the snapshot the FETCHED history actually goes, in days.

    Measured from the data because that is what the steps are computed on. The wall
    clock says how much reach could exist; the points say how much does.
    """
    reaches = []
    for pts in history.values():
        if not pts:
            continue
        last = max(t for t, _ in pts)
        reaches.append(max(0.0, (last - centre).total_seconds() / 86400.0))
    if not reaches:
        return {"n": 0, "median": 0.0, "min": 0.0, "max": 0.0}
    return {"n": len(reaches), "median": statistics.median(reaches),
            "min": min(reaches), "max": max(reaches)}


def evict_unsettled_cache(cache_dir, centre, after_days, days):
    """Delete cached history files that do not yet span the snapshot's full forward
    window, so a re-run refetches instead of re-serving its own first fetch.

    Found on the second real run (2026-07-23): the 0200Z snapshot printed no fetches
    and returned the same 0.00d reach as the day before - its per-snapshot cache,
    written 5.8h after capture, was re-served whole, so the "re-run once aged ~0.5d"
    instruction could never settle the number. Per-snapshot dirs stop cross-snapshot
    truncation; this stops the same lie from a stale re-serve WITHIN one snapshot.
    Settled files are kept - refetching them could not add information.
    """
    evicted = 0
    for f in cache_dir.glob(f"*_{days}d.json"):
        try:
            pts = json.loads(f.read_text(encoding="utf-8"))
            keep = pts and max(
                (datetime.fromisoformat(t) - centre).total_seconds() / 86400.0
                for t, _ in pts) >= after_days - 1e-9
        except (ValueError, TypeError):
            keep = False          # corrupt cache teaches nothing; one refetch is cheap
        if not keep:
            f.unlink()
            evicted += 1
    return evicted


def score_at_reach(suspects, controls, history, centre, before_days, reach_days):
    """Suspect-vs-control rates with the forward window clamped to `reach_days`.

    Same step logic, same thin-history rule, same controls'-own-90th-percentile bar as
    verify.run_top - the bar is recomputed AT THIS REACH, because reusing a full-reach
    bar against clamped suspect steps would flatter the suspects.
    """
    def steps(group):
        out, thin = [], 0
        for r in group:
            pts = history.get(r["norad"], [])
            if len(pts) < MIN_POINTS:
                thin += 1
                continue
            out.append(verify.biggest_step_km(pts, centre, before_days, reach_days))
        return out, thin

    s_steps, s_thin = steps(suspects)
    c_steps, c_thin = steps(controls)
    if not s_steps or not c_steps:
        return None
    bar = sorted(c_steps)[int(0.9 * (len(c_steps) - 1))]
    over_s = sum(1 for v in s_steps if v > bar)
    over_c = sum(1 for v in c_steps if v > bar)
    return {"reach_days": reach_days, "bar_km": bar,
            "n_suspects": len(s_steps), "n_controls": len(c_steps),
            "thin_suspects": s_thin, "thin_controls": c_thin,
            "over_suspects": over_s, "over_controls": over_c,
            "suspect_rate": over_s / len(s_steps),
            "control_rate": over_c / len(c_steps)}


# ------------------------------------------------------------------ the runs

def sweep_snapshot(session, snap_name, top, days, cache_dir):
    """One snapshot: production selection, then rates across every observable reach.

    `cache_dir` isolates this snapshot's history fetches - see the module docstring for
    why sharing verify_cache here would silently truncate the forward window.
    """
    snap = detect.ARCHIVE / snap_name
    res = detect.analyze(snap, "starlink", 95.0, None, detect.MAX_PLAUSIBLE_KM,
                         allow_live=False)
    if not res or res.get("skipped") or not res["rows"]:
        print(f"  !! {snap_name} not scoreable - skipped, not silently dropped")
        return None
    centre = verify.snapshot_moment(snap)
    regime = res.get("regime", "LEO")
    before, after, _ = verify.window_for_regime(regime)
    suspects, controls = verify.select_groups(res["rows"], top)
    if not suspects or not controls:
        print(f"  !! {snap_name}: no suspects or no controls at top {top}")
        return None

    old_cache = verify.CACHE
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        if cache_dir != verify.CACHE:      # holdout's own caches only, never the shared one
            n_evicted = evict_unsettled_cache(cache_dir, centre, after, days)
            if n_evicted:
                print(f"     cache: {n_evicted} unsettled file(s) evicted - "
                      f"refetching fresher history")
        verify.CACHE = cache_dir
        hist = verify.get_history(session, [r["norad"] for r in suspects + controls],
                                  days)
    finally:
        verify.CACHE = old_cache

    reach = data_reach_days(hist, centre)
    usable = [r for r in REACHES if r <= reach["median"] + 1e-9]
    if reach["median"] > 0 and reach["median"] not in usable:
        usable.append(round(reach["median"], 2))
    cells = []
    for r in sorted(set(usable)):
        cell = score_at_reach(suspects, controls, hist, centre, before, min(r, after))
        if cell:
            cells.append(cell)
    return {"snapshot": snap_name, "top": top, "regime": regime,
            "window_before": before, "window_after": after,
            "data_reach": reach, "settled": reach["median"] >= after - 1e-9,
            "cells": cells}


def event_holdout():
    """The ground-truth split, read from the referee's own saved run - no refetch."""
    if not REFEREE_JSON.exists():
        return None
    events = json.loads(REFEREE_JSON.read_text(encoding="utf-8"))["events"]
    tune, hold = split_events(events)

    def tally(rows):
        scoreable = [e for e in rows if e.get("role") == "scoreable"]
        caught = [e for e in scoreable
                  if e["cols"]["alt_3_14"]["verdict"] == "caught"]
        return scoreable, caught

    t_all, t_caught = tally(tune)
    h_all, h_caught = tally(hold)
    return {"tuning": {"scoreable": len(t_all), "caught": len(t_caught)},
            "holdout": {"scoreable": len(h_all), "caught": len(h_caught),
                        "rows": [{"object": e["object"], "norad": e["norad"],
                                  "date": e["date"],
                                  "verdict": e["cols"]["alt_3_14"]["verdict"]}
                                 for e in h_all]}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--top", type=int, nargs="+", default=[75])
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--cutoff", default=None,
                    help="ISO instant; snapshots strictly after it are the holdout. "
                         "Default: the documented 2026-07-23T00:00Z freeze")
    args = ap.parse_args()
    cutoff = (datetime.fromisoformat(args.cutoff).replace(tzinfo=timezone.utc)
              if args.cutoff else CUTOFF_UTC)

    print(f"  cutoff     {cutoff:%Y-%m-%d %H:%MZ}")
    print(f"  basis      {CUTOFF_BASIS}")

    # 1. the bars' provenance - checked, not assumed
    base = detect.load_baselines("starlink")
    if base:
        bad = baseline_violations(base, cutoff)
        if bad:
            sys.exit(f"  REFUSING: stored bars were learned from post-cutoff "
                     f"snapshot(s) {bad} - there is no zero-overlap claim to make")
        print(f"  bars       learned {base['learned_utc'][:16]}Z from "
              f"{len(base['snapshots'])} snapshot(s), all at/before the cutoff - clean")

    # 2. which snapshots are actually unseen
    names = [str(d.relative_to(detect.ARCHIVE)).replace("\\", "/")
             for d in detect.snapshot_dirs()]
    pre, post = split_snapshots(names, cutoff)
    if not post:
        sys.exit("  REFUSING: no snapshot is strictly after the cutoff yet. The "
                 "protocol waits for unseen data; it does not shrink the requirement.")
    print(f"  unseen     {len(post)} snapshot(s) strictly after the cutoff: "
          f"{', '.join(post)}")
    print(f"\n  ZERO-OVERLAP STATEMENT: every constant, window and bar was fixed at or "
          f"before\n  {cutoff:%Y-%m-%d %H:%MZ}; nothing captured after it has ever been "
          f"used to tune anything.\n  The snapshots above are scored below for the "
          f"first time.")

    session = verify.login()
    print("  space-track login ok")

    results = {"cutoff": cutoff.isoformat(), "basis": CUTOFF_BASIS,
               "holdout": [], "tuned": [], "events": event_holdout()}

    # 3. the unseen snapshots, each in its own cache
    for snap_name in post:
        for top in args.top:
            print(f"\n  == HOLDOUT {snap_name}  top {top} ==")
            out = sweep_snapshot(session, snap_name, top, args.days,
                                 HOLDOUT_CACHE / snap_name.replace("/", "_"))
            if out:
                results["holdout"].append(out)
                _print_sweep(out)

    # 4. the tuned side at the same reaches, from its own (already aged) cache
    for snap_name in TUNED_SNAPSHOTS:
        for top in args.top:
            print(f"\n  == TUNED  {snap_name}  top {top} ==")
            out = sweep_snapshot(session, snap_name, top, args.days, verify.CACHE)
            if out:
                results["tuned"].append(out)
                _print_sweep(out)

    _print_side_by_side(results)
    if results["events"]:
        _print_events(results["events"])

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n  run saved -> {OUT_JSON.relative_to(HERE)}")
    return 0


def _print_sweep(out):
    r = out["data_reach"]
    print(f"     window -{out['window_before']:g}/+{out['window_after']:g}d   "
          f"data reach: median {r['median']:.2f}d, min {r['min']:.2f}d "
          f"(n={r['n']} objects)")
    if not out["settled"]:
        print(f"     ** PROVISIONAL: only {r['median']:.2f}d of the "
              f"+{out['window_after']:g}d forward reach exists in the data. A same-day "
              f"rate is a floor,\n        not the result (issue 003) - re-run once the "
              f"snapshot has aged ~0.5d. **")
    for c in out["cells"]:
        print(f"     reach {c['reach_days']:>5.2f}d  bar {c['bar_km']:.3f} km  "
              f"suspects {c['over_suspects']}/{c['n_suspects']} "
              f"({100 * c['suspect_rate']:.0f}%)  "
              f"controls {c['over_controls']}/{c['n_controls']} "
              f"({100 * c['control_rate']:.0f}%)")


def _print_side_by_side(results):
    print(f"\n\n  TUNED vs UNSEEN at MATCHED forward reach (top "
          f"{results['holdout'][0]['top'] if results['holdout'] else '?'}, "
          f"suspect-rate / control-rate):")
    print(f"  {'reach':>7}  {'tuned (jul 22)':>28}  {'UNSEEN (post-cutoff)':>28}")
    holdout_cells = {}
    for out in results["holdout"]:
        for c in out["cells"]:
            holdout_cells.setdefault(c["reach_days"], []).append(c)
    tuned_cells = {}
    for out in results["tuned"]:
        for c in out["cells"]:
            tuned_cells.setdefault(c["reach_days"], []).append(c)
    for r in sorted(set(holdout_cells) | set(tuned_cells)):
        def fmt(cells):
            if not cells:
                return "-"
            return " | ".join(f"{100 * c['suspect_rate']:.0f}%/"
                              f"{100 * c['control_rate']:.0f}%" for c in cells)
        print(f"  {r:>6.2f}d  {fmt(tuned_cells.get(r)):>28}  "
              f"{fmt(holdout_cells.get(r)):>28}")
    print(f"\n  tuned-set settled value for context: {TUNED_SETTLED}")


def _print_events(ev):
    t, h = ev["tuning"], ev["holdout"]
    print(f"\n  GROUND-TRUTH SPLIT (GEO, altitude -3/+14d):")
    print(f"    tuning set  {t['caught']}/{t['scoreable']} caught - these rows CHOSE "
          f"the window; never quote them as evidence for it")
    print(f"    HOLDOUT     {h['caught']}/{h['scoreable']} caught - added after the "
          f"window was frozen, never touched by tuning:")
    for row in h["rows"]:
        print(f"      {row['object']:<16} {row['date']}  {row['verdict']}")


if __name__ == "__main__":
    sys.exit(main())
