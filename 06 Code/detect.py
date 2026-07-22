"""
detect.py - is the catalog wrong because something MANEUVERED, or just because
the catalog is OLD?

THE PROBLEM THIS SOLVES
supgp_vs_gp.py proved the gap between operator orbits (SupGP) and the public
catalog (GP) is real and large: median 3.72 km, 90th percentile 16.6 km, 6.0% of
Starlink over 25 km. But a big gap on its own is not a finding. There are two
completely different reasons a gap appears:

  MANEUVERED - the object burned, the operator knows, the catalog hasn't caught up.
  STALE      - nobody burned anything; the catalog's element set is simply old, and
               any orbit propagated far enough drifts away from the truth.

Treat those as the same thing and your "maneuver detector" is mostly an age
detector wearing a hat. Telling them apart is what turns the archive into labels.

THE METHOD (deliberately assumption-light)
For every object we have both element sets for:
  1. RMS position difference between SupGP and GP over 6 hours (Kelso's comparison).
  2. GP age = how old the public catalog's element set was at capture time.
  3. Bin the population by age. Within each bin, find what a NORMAL gap looks like.
  4. Flag objects that are extreme FOR THEIR OWN AGE BIN.

Step 4 is the whole idea. We never say "20 km is a lot". We say "20 km is a lot for
an element set that is only 3 hours old, because its neighbours of the same age sit
at 2 km". A stale object with a huge gap looks perfectly normal next to other stale
objects, and is not flagged. The baseline is empirical - measured off the same
population, same day - so no drag model, no physics assumption, nothing to tune.

WHAT THIS IS NOT
This is not ground truth. It is a ranked list of candidates with a stated reason.
Anything claimed publicly gets checked against an actual maneuver record first.

Usage:
  python detect.py                          # newest snapshot, starlink
  python detect.py --group oneweb --chart
  python detect.py --pct 95 --min-km 5
"""

import argparse
import gzip
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from sgp4 import omm
from sgp4.api import Satrec, SatrecArray

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "supgp_archive"
OUT = HERE / "output"
GP_URL = "https://celestrak.org/NORAD/elements/gp.php"
HEADERS = {
    "User-Agent": (
        "SpaceProject-SupGP-Archiver/1.0 "
        "(research: maneuver detection from public data; contact zayahwork@gmail.com)"
    )
}

SPAN_HOURS = 6
STEP_MINUTES = 1
AGE_BINS = [0, 3, 6, 12, 24, 48, 96, 1e9]      # hours
MIN_PER_BIN = 25          # below this a percentile is noise, so we widen instead

# A hard physical sanity gate, applied BEFORE the age-aware statistics.
# No station-keeping burn - and no plausible orbit-raising a public catalog would
# lag on - moves an object hundreds of km RMS over a 6h span. A gap this size means
# the two element sets describe wholly different orbits: a decaying/reentering object
# or a bad TLE, not a maneuver. These get bucketed as data-quality flags, never as
# detections, so a nonsense 5,337 km "maneuver" can't reach a customer dashboard.
MAX_PLAUSIBLE_KM = 500.0


# ------------------------------------------------------------------ loading

def newest_snapshot_dir():
    hits = sorted(ARCHIVE.glob("*/*/manifest.json"))
    if not hits:
        sys.exit("no archived snapshots - run supgp_archive.py first")
    return hits[-1].parent


def load_omm(text):
    """Parse OMM CSV into {norad: Satrec}. Later duplicates win."""
    sats = {}
    for fields in omm.parse_csv(io.StringIO(text)):
        sat = Satrec()
        try:
            omm.initialize(sat, fields)
        except (ValueError, KeyError):
            continue
        sats[sat.satnum] = sat
    return sats


def load_gp(snap_dir, group):
    """Archived public catalog if this snapshot has one, else fetch it live.

    Archived is strongly preferred: it was captured at the same instant as the
    SupGP file, so the comparison is of the same moment rather than of now-vs-then.
    """
    local = snap_dir / "gp_active.csv.gz"
    if local.exists():
        return load_omm(gzip.open(local, "rt", encoding="utf-8").read()), "archived"

    # Walk back - a snapshot marked "unchanged" points at an earlier identical pull.
    for older in sorted(ARCHIVE.glob("*/*/gp_active.csv.gz"), reverse=True):
        return load_omm(gzip.open(older, "rt", encoding="utf-8").read()), \
            f"archived {older.parent.name}"

    resp = requests.get(GP_URL, params={"GROUP": group, "FORMAT": "csv"},
                        headers=HEADERS, timeout=180)
    resp.raise_for_status()
    return load_omm(resp.text), "live"


# ------------------------------------------------------------------ measuring

def epoch_jd(sat):
    return sat.jdsatepoch + sat.jdsatepochF


def rms_difference(sat_a, sat_b):
    """RMS position difference in km over the span, or None if propagation fails."""
    start = max(epoch_jd(sat_a), epoch_jd(sat_b))
    steps = int(SPAN_HOURS * 60 / STEP_MINUTES)
    offsets = np.arange(steps) * (STEP_MINUTES / 1440.0)
    jd = np.full(steps, start)
    err, pos, _ = SatrecArray([sat_a, sat_b]).sgp4(jd, offsets)
    if err.any():
        return None
    delta = pos[0] - pos[1]
    return float(np.sqrt((delta ** 2).sum(axis=1).mean()))


def capture_jd(snap_dir):
    """Julian date of the snapshot, from its manifest."""
    man = json.loads((snap_dir / "manifest.json").read_text(encoding="utf-8"))
    when = datetime.fromisoformat(man["captured_utc"])
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    # days since the J2000-independent JD epoch, matching sgp4's convention
    return when.timestamp() / 86400.0 + 2440587.5


# ------------------------------------------------------------------ the call

def classify(rows, pct, min_km, max_km=MAX_PLAUSIBLE_KM):
    """Attach a verdict to every row, using its own age bin as the yardstick.

    A hard plausibility gate runs first: any gap >= max_km is physically impossible
    for a real maneuver and is flagged as a data-quality issue, then excluded from
    the age-baseline statistics so a handful of nonsense orbits can't distort the
    per-band thresholds the honest candidates are judged against.
    """
    for r in rows:
        if r["gap_km"] >= max_km:
            r["verdict"] = "DATA QUALITY FLAG (likely decay or bad TLE, not a maneuver)"

    graded = [r for r in rows if not r["verdict"].startswith("DATA QUALITY")]
    if not graded:
        return []
    ages = np.array([r["gp_age_h"] for r in graded])
    gaps = np.array([r["gap_km"] for r in graded])

    bands = []
    for lo, hi in zip(AGE_BINS, AGE_BINS[1:]):
        sel = (ages >= lo) & (ages < hi)
        if sel.sum() == 0:
            continue
        # A percentile off 4 objects is not a baseline. Fall back to the whole
        # population rather than inventing a threshold from nothing.
        if sel.sum() < MIN_PER_BIN:
            cut, basis, n = float(np.percentile(gaps, pct)), "population", int(sel.sum())
        else:
            cut, basis, n = float(np.percentile(gaps[sel], pct)), "bin", int(sel.sum())
        bands.append({"lo": lo, "hi": hi, "n": n, "cut_km": cut, "basis": basis,
                      "median_km": float(np.median(gaps[sel]))})
        for r, is_in in zip(graded, sel):
            if not is_in:
                continue
            r["band_cut_km"] = cut
            r["band_median_km"] = float(np.median(gaps[sel]))
            if r["gap_km"] >= cut and r["gap_km"] >= min_km:
                r["verdict"] = "MANEUVER SUSPECT"
            elif r["gap_km"] >= min_km:
                r["verdict"] = "stale (big gap, but normal for its age)"
            else:
                r["verdict"] = "agrees"
    return bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="starlink")
    ap.add_argument("--pct", type=float, default=95.0,
                    help="a gap above this percentile FOR ITS AGE BIN is a suspect")
    ap.add_argument("--min-km", type=float, default=5.0,
                    help="never flag anything below this, however unusual for its bin")
    ap.add_argument("--max-km", type=float, default=MAX_PLAUSIBLE_KM,
                    help="gaps at/above this are physically impossible for a maneuver; "
                         "bucketed as data-quality flags, never as detections")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--chart", action="store_true")
    ap.add_argument("--csv", action="store_true", help="write the full table")
    args = ap.parse_args()

    snap_dir = newest_snapshot_dir()
    sup_file = snap_dir / f"{args.group}.csv.gz"
    if not sup_file.exists():
        sys.exit(f"{args.group} not in {snap_dir.relative_to(ARCHIVE)}")

    print(f"  snapshot   {snap_dir.relative_to(ARCHIVE)}")
    sup = load_omm(gzip.open(sup_file, "rt", encoding="utf-8").read())
    gp, gp_src = load_gp(snap_dir, args.group)
    now_jd = capture_jd(snap_dir)
    print(f"  supgp      {len(sup)} objects")
    print(f"  gp         {len(gp)} objects ({gp_src})")

    both = sorted(set(sup) & set(gp))
    print(f"  comparable {len(both)} objects\n")
    if not both:
        sys.exit("no overlap - nothing to compare")

    rows, failed = [], 0
    for norad in both:
        gap = rms_difference(sup[norad], gp[norad])
        if gap is None:
            failed += 1
            continue
        rows.append({
            "norad": norad,
            "gap_km": gap,
            "gp_age_h": (now_jd - epoch_jd(gp[norad])) * 24.0,
            "sup_age_h": (now_jd - epoch_jd(sup[norad])) * 24.0,
            "verdict": "agrees",
        })

    bands = classify(rows, args.pct, args.min_km, args.max_km)

    print("  what a NORMAL gap looks like, by how old the catalog entry is:")
    print(f"  {'age (h)':>12}  {'objects':>8}  {'median km':>10}  {'flag above':>11}")
    for b in bands:
        hi = "inf" if b["hi"] > 1e8 else f"{b['hi']:g}"
        star = "" if b["basis"] == "bin" else "  (too few - used whole population)"
        print(f"  {b['lo']:>5g}-{hi:<6}  {b['n']:>8}  {b['median_km']:>10.2f}"
              f"  {b['cut_km']:>11.2f}{star}")

    suspects = sorted([r for r in rows if r["verdict"] == "MANEUVER SUSPECT"],
                      key=lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9),
                      reverse=True)
    stale = [r for r in rows if r["verdict"].startswith("stale")]
    flagged = sorted([r for r in rows if r["verdict"].startswith("DATA QUALITY")],
                     key=lambda r: r["gap_km"], reverse=True)

    print(f"\n  {'NORAD':>7}  {'gap km':>9}  {'gp age h':>9}  {'normal for age':>14}  ratio")
    for r in suspects[: args.top]:
        print(f"  {r['norad']:>7}  {r['gap_km']:>9.1f}  {r['gp_age_h']:>9.1f}"
              f"  {r['band_median_km']:>14.2f}  {r['gap_km']/max(r['band_median_km'],1e-9):>5.0f}x")

    print(f"\n  MANEUVER SUSPECTS  {len(suspects):>5}  of {len(rows)} "
          f"({100*len(suspects)/len(rows):.1f}%)")
    print(f"  big gap but stale  {len(stale):>5}  "
          f"- would have been false positives on gap alone")
    print(f"  agrees             {len(rows)-len(suspects)-len(stale)-len(flagged):>5}")
    print(f"  DATA QUALITY FLAG  {len(flagged):>5}  "
          f"- gap >= {args.max_km:g} km, physically impossible; likely decay or bad TLE")
    if flagged:
        worst = ", ".join(f"{r['norad']} ({r['gap_km']:.0f} km)" for r in flagged[:3])
        print(f"                           excluded from candidates, e.g. {worst}")
    if failed:
        print(f"  propagation failed {failed:>5}  (usually reentering)")

    caught = len(suspects) + len(stale)
    if caught:
        print(f"\n  Ranking on raw gap alone would have surfaced {caught} objects."
              f"\n  Age-aware ranking cuts that to {len(suspects)} "
              f"- {100*len(stale)/caught:.0f}% of the naive list was just old data.")

    if args.csv or args.chart:
        OUT.mkdir(exist_ok=True)
    if args.csv:
        import csv as _csv
        path = OUT / f"detect_{args.group}_{snap_dir.parent.name}_{snap_dir.name}.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = _csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: -r["gap_km"]))
        print(f"\n  table -> {path}")
    if args.chart:
        chart(rows, bands, args.group, snap_dir)
    return 0


def chart(rows, bands, group, snap_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    sus = [r for r in rows if r["verdict"] == "MANEUVER SUSPECT"]
    other = [r for r in rows if r["verdict"] != "MANEUVER SUSPECT"]
    ax.scatter([r["gp_age_h"] for r in other], [r["gap_km"] for r in other],
               s=6, alpha=0.25, c="#888", label="normal for its age")
    ax.scatter([r["gp_age_h"] for r in sus], [r["gap_km"] for r in sus],
               s=18, alpha=0.9, c="#d62728", label="maneuver suspect")
    for b in bands:
        hi = min(b["hi"], max(r["gp_age_h"] for r in rows))
        ax.plot([b["lo"], hi], [b["cut_km"]] * 2, c="#1f77b4", lw=1.5)
    ax.set_yscale("log")
    ax.set_xlabel("age of the public catalog entry at capture (hours)")
    ax.set_ylabel("SupGP vs GP disagreement (km, RMS over 6h)")
    ax.set_title(f"{group} - a big gap only means something for a FRESH catalog entry\n"
                 f"{snap_dir.parent.name} {snap_dir.name}  ·  blue = flag threshold per age band")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.2)
    path = OUT / f"detect_{group}_{snap_dir.parent.name}_{snap_dir.name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    print(f"  chart -> {path}")


if __name__ == "__main__":
    sys.exit(main())
