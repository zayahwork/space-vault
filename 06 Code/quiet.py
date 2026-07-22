"""
quiet.py - notice a satellite that has STOPPED maneuvering.

WHY THIS EXISTS
Every tool so far detects presence: a gap, a burn, a candidate. The insurer signal
is an absence. A working satellite station-keeps on a rhythm - burn, catalog falls
behind, gap spikes, catalog catches up, gap collapses, repeat. A satellite that
stops doing that has usually lost something: thruster, fuel, attitude control, or
the whole bus. That is the "abnormal before the claim" capability the pricing pitch
depends on, and detecting it means judging each object against ITS OWN PAST, not
against today's crowd.

HOW IT WORKS
Walk every scoreable snapshot in the archive, oldest to newest. For each object,
keep its independent looks (same dedup rule as detect.py's persistence: a look only
counts if an element set actually changed). A "spike" is a look where the object sat
over its cohort's stored baseline - the same fixed bar alert mode uses. The rhythm
is the typical time between spikes. An object has GONE QUIET when the time since its
last spike stretches well past its own rhythm.

THE HONEST BLOCKER
Rhythm needs history. Starlink station-keeps on a timescale of days-to-weeks, so
calling an object quiet needs (a) enough archive to have seen several of its spikes,
and (b) enough silence afterwards to mean something. With a day of archive, neither
exists. This tool REFUSES rather than substituting a shorter window - a cadence
claim from one day of data is exactly the kind of self-deception this project keeps
catching itself in. It prints how far along the archive is and unblocks itself as
snapshots accumulate, the same way persistence did.

Usage:
  python quiet.py                     # status + verdicts if the archive allows
  python quiet.py --min-days 14       # stricter history requirement
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# An object needs at least this many spikes on record before it HAS a rhythm to
# lose. Below that, "no recent spike" is indistinguishable from "we barely looked".
MIN_SPIKES = 3

# The archive must span at least this many days before any cadence claim is made.
# Starlink station-keeping cadence is measured in days; seeing less than a week
# means most healthy objects will not have shown even one full cycle.
MIN_ARCHIVE_DAYS = 7.0

# "Went quiet" = silence lasting this many times the object's own typical
# spike-to-spike interval.
QUIET_FACTOR = 2.5

# A rhythm cannot be measured finer than we sample, and station-keeping cadence is
# measured in days. Without this floor the check inverts on exactly the objects that
# matter most: a suspect flagged on three consecutive 6-hourly snapshots gets a
# "typical interval" of 0.25 days, so the next ordinary overnight gap (0.7 days) reads
# as 2.8x its rhythm and the satellite is reported as having stopped station-keeping.
# Measured: judge() called that object WENT QUIET with silent_days=0.70. The objects
# most likely to spike on consecutive looks are the persistent suspects - the ones the
# product exists to watch - so the false positive lands precisely on the paying case.
MIN_TYPICAL_DAYS = 1.0


def object_histories(group, pct, min_km, max_km, stored):
    """Per-object independent-look history across every scoreable snapshot.

    Returns (histories, used) where histories[norad] is a list of
    (capture_jd, gap_km, over_bar) in time order.
    """
    histories, used = {}, []
    last_fp = {}
    for snap in detect.snapshot_dirs():
        run = detect.analyze(snap, group, pct, min_km, max_km,
                             allow_live=False, stored=stored)
        if not run or run.get("skipped") or not run["rows"]:
            continue
        t = detect.capture_jd(snap)
        used.append(snap)
        for r in run["rows"]:
            fp = (round(r["sup_epoch"], 9), round(r["gp_epoch"], 9))
            if last_fp.get(r["norad"]) == fp:
                continue                      # same element sets - not a new look
            last_fp[r["norad"]] = fp
            histories.setdefault(r["norad"], []).append(
                (t, r["gap_km"], bool(r.get("flagged")) and not r["falling"]))
    return histories, used


def judge(history, now_jd):
    """One object's cadence verdict from its look history."""
    spikes = [t for t, _, over in history if over]
    if len(spikes) < MIN_SPIKES:
        return {"status": "no rhythm yet", "spikes": len(spikes)}
    intervals = np.diff(spikes)
    # Floored: see MIN_TYPICAL_DAYS. A burst of spikes inside one day describes our
    # sampling, not the satellite's rhythm, and must not become the bar it is judged by.
    typical = max(float(np.median(intervals)), MIN_TYPICAL_DAYS)
    silence = now_jd - spikes[-1]
    verdict = "WENT QUIET" if silence > QUIET_FACTOR * typical else "on rhythm"
    return {"status": verdict, "spikes": len(spikes),
            "typical_days": typical, "silent_days": float(silence)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="starlink")
    ap.add_argument("--pct", type=float, default=95.0)
    ap.add_argument("--min-km", type=float, default=5.0)
    ap.add_argument("--min-days", type=float, default=MIN_ARCHIVE_DAYS)
    args = ap.parse_args()

    stored = detect.load_baselines(args.group)
    if stored is None:
        sys.exit("cadence needs the stored baseline - run "
                 "'python detect.py --learn-baseline' first")

    print(f"  building per-object histories from the archive...")
    histories, used = object_histories(args.group, args.pct, args.min_km,
                                       detect.MAX_PLAUSIBLE_KM, stored)
    if not used:
        sys.exit("no scoreable snapshots")
    span_days = detect.capture_jd(used[-1]) - detect.capture_jd(used[0])
    looks = [len(h) for h in histories.values()]
    spike_counts = [sum(1 for _, _, over in h if over) for h in histories.values()]
    ready = sum(1 for c in spike_counts if c >= MIN_SPIKES)

    print(f"  scoreable snapshots  {len(used)}")
    print(f"  archive span         {span_days:.2f} days")
    print(f"  objects tracked      {len(histories)}")
    print(f"  independent looks    median {int(np.median(looks))} per object")
    print(f"  objects with >= {MIN_SPIKES} spikes on record: {ready} "
          f"(a rhythm needs {MIN_SPIKES}+)")

    if span_days < args.min_days:
        print(f"\n  !! NO CADENCE VERDICTS - the archive spans {span_days:.2f} days "
              f"and a rhythm\n     claim needs {args.min_days:g}. A station-keeper "
              f"burns every few days; with less\n     archive than that, 'this object "
              f"went quiet' and 'we only just started\n     watching' look identical, "
              f"and we will not pretend otherwise.\n"
              f"\n     Nothing to fix. The archiver banks ~4 scoreable snapshots/day; "
              f"this\n     unblocks itself around "
              f"{args.min_days:g} days after 2026-07-22. Re-run then.")
        return 0

    now_jd = detect.capture_jd(used[-1])
    quiet, on_rhythm, no_rhythm = [], 0, 0
    for norad, h in histories.items():
        v = judge(h, now_jd)
        if v["status"] == "WENT QUIET":
            quiet.append((norad, v))
        elif v["status"] == "on rhythm":
            on_rhythm += 1
        else:
            no_rhythm += 1

    print(f"\n  WENT QUIET      {len(quiet):>6}  - had a rhythm, stopped spiking")
    print(f"  on rhythm       {on_rhythm:>6}")
    print(f"  no rhythm yet   {no_rhythm:>6}  - fewer than {MIN_SPIKES} spikes on "
          f"record, not judgeable")
    for norad, v in sorted(quiet, key=lambda x: -x[1]["silent_days"])[:20]:
        print(f"    {norad:>7}  typical spike every {v['typical_days']:.1f}d, "
              f"silent {v['silent_days']:.1f}d")
    return 0


if __name__ == "__main__":
    sys.exit(main())
