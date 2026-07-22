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

THE SECOND FILTER: TEMPORAL PERSISTENCE
The age filter fixes "old data looks like movement". It does nothing about the other
way to fool yourself: a single snapshot is a single measurement, and one measurement
of 10,000 objects at the 95th percentile hands you ~540 "suspects" by construction.
Some of those are one-off garbage - a bad element set, a fit that went wrong once.

A real maneuver does not go away when you look again. The operator's orbit keeps
disagreeing with that catalog entry, through refresh after refresh of the operator's
own ephemeris, until the catalog finally catches up and the gap collapses. Noise does
not do that. So we look at the same object across several snapshots and ask: is it
still flagged?

The trap here is fake corroboration. CelesTrak republishes SupGP every ~30 min, but the
element sets only actually change a few times a day - two of our six snapshots are
byte-identical to the one before them. "Flagged in 6 of 6 snapshots" would mean nothing
if 4 of those looks were the same two element sets compared twice. So persistence is
counted in INDEPENDENT LOOKS only: a look counts for an object only if at least one of
its two element sets (operator or catalog) actually changed epoch since the last one
counted. Everything below reports looks, not snapshots.

WHAT THIS IS NOT
This is not ground truth. It is a ranked list of candidates with a stated reason.
Anything claimed publicly gets checked against an actual maneuver record first.

Usage:
  python detect.py                          # newest snapshot + persistence
  python detect.py --group oneweb --chart
  python detect.py --pct 95 --min-km 5
  python detect.py --history 1              # single snapshot, no persistence
  python detect.py --snapshot 2026-07-21/2025Z
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

# How many snapshots back to look, and how many INDEPENDENT looks must agree before a
# candidate is called persistent. Two is the minimum that means anything: one look is
# a measurement, two is a measurement that repeated.
HISTORY_SNAPSHOTS = 4
MIN_LOOKS = 2


# ------------------------------------------------------------------ loading

def snapshot_dirs():
    """Every archived snapshot, oldest first."""
    hits = sorted(ARCHIVE.glob("*/*/manifest.json"))
    if not hits:
        sys.exit("no archived snapshots - run supgp_archive.py first")
    return [h.parent for h in hits]


def newest_snapshot_dir():
    return snapshot_dirs()[-1]


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


_GP_CACHE = {}


def load_gp(snap_dir, group, now_jd, allow_live=True):
    """Archived public catalog for this snapshot, or the nearest EARLIER one.

    Archived-in-place is strongly preferred: it was captured at the same instant as
    the SupGP file, so the comparison is of the same moment rather than of now-vs-then.

    When a snapshot has no GP of its own we borrow one, but only ever from the past.
    Borrowing forwards would be a time-travel bug that quietly poisons everything
    downstream: a catalog entry issued AFTER the snapshot gets a negative age, lands
    in the wrong age bin, and drags that bin's threshold with it. It also manufactures
    fake persistence - every historical snapshot would be scored against one identical
    future catalog, so "still flagged three looks running" would just mean "we compared
    the same two files three times".

    Returns (sats, label, gp_capture_jd) - or (None, reason, None) if nothing usable.
    """
    local = snap_dir / "gp_active.csv.gz"
    if local.exists():
        return _cached_gp(local), "archived here", capture_jd(snap_dir)

    for cand in sorted(ARCHIVE.glob("*/*/gp_active.csv.gz"), reverse=True):
        when = capture_jd(cand.parent)
        if when > now_jd:
            continue                      # from the future - not ours to use
        label = f"borrowed {cand.parent.parent.name}/{cand.parent.name}"
        lag_h = (now_jd - when) * 24.0
        return _cached_gp(cand), f"{label}, {lag_h:.1f}h earlier", when

    if not allow_live:
        return None, "no archived catalog at or before this snapshot", None

    resp = requests.get(GP_URL, params={"GROUP": group, "FORMAT": "csv"},
                        headers=HEADERS, timeout=180)
    resp.raise_for_status()
    return load_omm(resp.text), "live", now_jd


def _cached_gp(path):
    """The same GP file gets borrowed by several snapshots - parse it once."""
    key = str(path)
    if key not in _GP_CACHE:
        _GP_CACHE[key] = load_omm(gzip.open(path, "rt", encoding="utf-8").read())
    return _GP_CACHE[key]


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


def analyze(snap_dir, group, pct, min_km, max_km, allow_live=True):
    """One snapshot end to end: measure every object, judge it against its age bin.

    Returns None if the snapshot can't be scored - no file for this group, or no
    catalog captured at or before it (see load_gp on why we never borrow forwards).
    """
    sup_file = snap_dir / f"{group}.csv.gz"
    if not sup_file.exists():
        return None
    now_jd = capture_jd(snap_dir)
    gp, gp_src, _ = load_gp(snap_dir, group, now_jd, allow_live)
    if gp is None:
        return {"dir": snap_dir, "rows": [], "bands": [], "skipped": gp_src}

    sup = load_omm(gzip.open(sup_file, "rt", encoding="utf-8").read())
    rows, failed = [], 0
    for norad in sorted(set(sup) & set(gp)):
        gap = rms_difference(sup[norad], gp[norad])
        if gap is None:
            failed += 1
            continue
        rows.append({
            "norad": norad,
            "gap_km": gap,
            "gp_age_h": (now_jd - epoch_jd(gp[norad])) * 24.0,
            "sup_age_h": (now_jd - epoch_jd(sup[norad])) * 24.0,
            "sup_epoch": epoch_jd(sup[norad]),
            "gp_epoch": epoch_jd(gp[norad]),
            "verdict": "agrees",
        })
    bands = classify(rows, pct, min_km, max_km)
    return {"dir": snap_dir, "rows": rows, "bands": bands, "failed": failed,
            "gp_src": gp_src, "n_sup": len(sup), "n_gp": len(gp), "skipped": None}


# --------------------------------------------------------- temporal persistence

def independent_looks(runs):
    """Per object, the history of looks that actually told us something new.

    A look only counts if at least one of the two element sets changed epoch since
    the last counted look. CelesTrak republishes on a fixed cadence whether or not
    the underlying fit moved, so consecutive snapshots are often the identical pair
    of element sets - comparing those twice is one measurement, not two.
    """
    history = {}
    for run in runs:                                   # oldest first
        for r in run["rows"]:
            history.setdefault(r["norad"], []).append(r)

    out = {}
    for norad, seq in history.items():
        kept = []
        for r in seq:
            fingerprint = (round(r["sup_epoch"], 9), round(r["gp_epoch"], 9))
            if kept and fingerprint == kept[-1][0]:
                continue                               # same two element sets again
            kept.append((fingerprint, r))
        looks = [r for _, r in kept]
        out[norad] = {
            "looks": len(looks),
            "flags": sum(1 for r in looks if r["verdict"] == "MANEUVER SUSPECT"),
            "gaps": [r["gap_km"] for r in looks],
            "flagged_now": looks[-1]["verdict"] == "MANEUVER SUSPECT",
        }
    return out


def apply_persistence(rows, looks, min_looks=MIN_LOOKS):
    """Split this snapshot's suspects by whether the evidence repeated.

    Nothing is thrown away - a first-look suspect may well be a burn that just
    happened. It is separated because it has not yet earned the same confidence.
    """
    for r in rows:
        h = looks.get(r["norad"])
        if not h:
            continue
        r["looks"] = h["looks"]
        r["flagged_looks"] = h["flags"]
        if r["verdict"] != "MANEUVER SUSPECT":
            continue
        if h["looks"] < 2:
            r["verdict"] = "SUSPECT (single look - nothing to corroborate against)"
        elif h["flags"] >= min_looks:
            r["verdict"] = "PERSISTENT SUSPECT"
        else:
            r["verdict"] = "SUSPECT (new this look - unconfirmed)"


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
    ap.add_argument("--history", type=int, default=HISTORY_SNAPSHOTS,
                    help="how many snapshots back to check for persistence; 1 disables")
    ap.add_argument("--min-looks", type=int, default=MIN_LOOKS,
                    help="independent looks that must agree before a candidate is "
                         "called persistent")
    ap.add_argument("--snapshot", default=None,
                    help="score this snapshot instead of the newest, e.g. 2026-07-21/2025Z")
    ap.add_argument("--chart", action="store_true")
    ap.add_argument("--csv", action="store_true", help="write the full table")
    args = ap.parse_args()

    every = snapshot_dirs()
    if args.snapshot:
        wanted = [d for d in every if str(d.relative_to(ARCHIVE)).replace("\\", "/")
                  == args.snapshot.replace("\\", "/")]
        if not wanted:
            sys.exit(f"no snapshot {args.snapshot} in {ARCHIVE}")
        every = every[: every.index(wanted[0]) + 1]
    snap_dir = every[-1]

    # Fetching the catalog live is only honest for the newest snapshot. For any
    # earlier one it would compare a past operator orbit against today's catalog -
    # the same time-travel mistake load_gp exists to prevent.
    replaying = snap_dir != snapshot_dirs()[-1]

    print(f"  snapshot   {snap_dir.relative_to(ARCHIVE)}"
          f"{'  (replay - live fetch disabled)' if replaying else ''}")
    latest = analyze(snap_dir, args.group, args.pct, args.min_km, args.max_km,
                     allow_live=not replaying)
    if latest is None:
        sys.exit(f"{args.group} not in {snap_dir.relative_to(ARCHIVE)}")
    if latest["skipped"]:
        sys.exit(f"cannot score this snapshot: {latest['skipped']}")
    rows, bands = latest["rows"], latest["bands"]
    print(f"  supgp      {latest['n_sup']} objects")
    print(f"  gp         {latest['n_gp']} objects ({latest['gp_src']})")
    print(f"  comparable {len(rows) + latest['failed']} objects\n")
    if not rows:
        sys.exit("no overlap - nothing to compare")
    failed = latest["failed"]

    # ---- second filter: did the same objects look wrong last time too? --------
    looks, runs, unusable = {}, [latest], []
    if args.history > 1:
        for older in every[-args.history:-1]:
            run = analyze(older, args.group, args.pct, args.min_km, args.max_km,
                          allow_live=False)
            if run and not run["skipped"] and run["rows"]:
                runs.insert(-1, run)
            elif run and run["skipped"]:
                unusable.append((older, run["skipped"]))
        for older, why in unusable:
            print(f"  unusable   {older.relative_to(ARCHIVE)} - {why}")
        if len(runs) > 1:
            looks = independent_looks(runs)
            apply_persistence(rows, looks, args.min_looks)
        else:
            print("\n  !! NO PERSISTENCE CHECK - only one scoreable snapshot exists.\n"
                  "     Every candidate below rests on a single measurement. A maneuver\n"
                  "     repeats; a bad element set does not, and right now we cannot tell\n"
                  "     them apart. Fix: archive gp_active.csv.gz alongside every SupGP\n"
                  "     snapshot, then re-run - two scoreable snapshots is all it needs.")

    print("  what a NORMAL gap looks like, by how old the catalog entry is:")
    print(f"  {'age (h)':>12}  {'objects':>8}  {'median km':>10}  {'flag above':>11}")
    for b in bands:
        hi = "inf" if b["hi"] > 1e8 else f"{b['hi']:g}"
        star = "" if b["basis"] == "bin" else "  (too few - used whole population)"
        print(f"  {b['lo']:>5g}-{hi:<6}  {b['n']:>8}  {b['median_km']:>10.2f}"
              f"  {b['cut_km']:>11.2f}{star}")

    by_strength = lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9)
    persistent = sorted([r for r in rows if r["verdict"] == "PERSISTENT SUSPECT"],
                        key=by_strength, reverse=True)
    unconfirmed = sorted([r for r in rows if r["verdict"].startswith("SUSPECT (")],
                         key=by_strength, reverse=True)
    single = sorted([r for r in rows if r["verdict"] == "MANEUVER SUSPECT"],
                    key=by_strength, reverse=True)
    suspects = persistent + unconfirmed + single
    stale = [r for r in rows if r["verdict"].startswith("stale")]
    flagged = sorted([r for r in rows if r["verdict"].startswith("DATA QUALITY")],
                     key=lambda r: r["gap_km"], reverse=True)

    if runs and len(runs) > 1:
        span_h = (capture_jd(runs[-1]["dir"]) - capture_jd(runs[0]["dir"])) * 24.0
        counted = [looks[r["norad"]]["looks"] for r in rows if r["norad"] in looks]
        print(f"\n  persistence over {len(runs)} snapshots ({span_h:.1f}h): "
              f"{'/'.join(str(r['dir'].name) for r in runs)}")
        print(f"  independent looks per object: median "
              f"{int(np.median(counted)) if counted else 0} "
              f"(a snapshot only counts if an element set actually changed)")

    head = "  {:>7}  {:>9}  {:>9}  {:>14}  {:>5}  {}".format(
        "NORAD", "gap km", "gp age h", "normal for age", "ratio", "looks")
    print(f"\n{head}")
    for r in suspects[: args.top]:
        mark = {"PERSISTENT SUSPECT": "persisted"}.get(
            r["verdict"], "new" if "new this look" in r["verdict"] else "-")
        seen = (f"{r['flagged_looks']}/{r['looks']} {mark}"
                if "looks" in r else "not checked")
        print(f"  {r['norad']:>7}  {r['gap_km']:>9.1f}  {r['gp_age_h']:>9.1f}"
              f"  {r['band_median_km']:>14.2f}"
              f"  {r['gap_km']/max(r['band_median_km'],1e-9):>4.0f}x  {seen}")

    print()
    if runs and len(runs) > 1:
        print(f"  PERSISTENT SUSPECTS{len(persistent):>5}  of {len(rows)} "
              f"({100*len(persistent)/len(rows):.1f}%) - flagged in >= {args.min_looks} "
              f"independent looks")
        new = [r for r in unconfirmed if "new this look" in r["verdict"]]
        lone = [r for r in unconfirmed if "single look" in r["verdict"]]
        print(f"  unconfirmed        {len(new):>5}  - flagged only in the newest look; "
              f"a fresh burn or a one-off. The next snapshot decides.")
        if lone:
            print(f"  uncorroborated     {len(lone):>5}  - no earlier independent look "
                  f"exists for these objects")
        cleared = sum(1 for n, h in looks.items()
                      if h["flags"] and not h["flagged_now"])
        print(f"  cleared            {cleared:>5}  - flagged in an earlier look, normal "
              f"now (catalog caught up, or it was noise)")
    else:
        print(f"  MANEUVER SUSPECTS  {len(single):>5}  of {len(rows)} "
              f"({100*len(single)/len(rows):.1f}%)  - UNCORROBORATED, one snapshot only")
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
        if len(runs) > 1 and suspects:
            print(f"  Demanding the flag repeat cuts that again to {len(persistent)} "
                  f"- {100*(len(suspects)-len(persistent))/len(suspects):.0f}% of the "
                  f"age-aware list did not survive a second look.")

    if args.csv or args.chart:
        OUT.mkdir(exist_ok=True)
    if args.csv:
        import csv as _csv
        path = OUT / f"detect_{args.group}_{snap_dir.parent.name}_{snap_dir.name}.csv"
        # Not every row carries every key - only graded rows get band stats, and only
        # objects present in an earlier snapshot get look counts. Take the union so a
        # row with extra keys can't blow up the writer.
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = _csv.DictWriter(fh, fieldnames=fields, restval="")
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
    is_suspect = lambda r: r["verdict"] == "PERSISTENT SUSPECT" \
        or r["verdict"] == "MANEUVER SUSPECT" or r["verdict"].startswith("SUSPECT (")
    persisted = [r for r in rows if r["verdict"] in
                 ("PERSISTENT SUSPECT", "MANEUVER SUSPECT")]
    once = [r for r in rows if r["verdict"].startswith("SUSPECT (")]
    other = [r for r in rows if not is_suspect(r)]
    ax.scatter([r["gp_age_h"] for r in other], [r["gap_km"] for r in other],
               s=6, alpha=0.25, c="#888", label="normal for its age")
    if once:
        ax.scatter([r["gp_age_h"] for r in once], [r["gap_km"] for r in once],
                   s=14, alpha=0.6, c="#ff7f0e", label="flagged once - unconfirmed")
    checked = any("looks" in r for r in rows)
    ax.scatter([r["gp_age_h"] for r in persisted], [r["gap_km"] for r in persisted],
               s=18, alpha=0.9, c="#d62728",
               label="suspect, flag repeated" if checked
                     else "maneuver suspect (single snapshot)")
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
