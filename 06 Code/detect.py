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
import re
import sys
from collections import Counter
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

# An object losing altitude faster than this is on its way down, not holding station.
# The number is deorbit_check.py's, kept deliberately identical so the two tools cannot
# drift into disagreeing about what "falling" means.
#
# This matters more than it sounds. Objects falling this fast are ~9.5% of the Starlink
# population but were producing ~79% of the maneuver candidates - a median gap of 19.7 km
# against 4.0 km for everything else. A satellite being deliberately deorbited fights the
# catalog every single day; that is decay doing its job, not a maneuver worth anyone's
# attention. Judged against the general population it looks extraordinary. Judged against
# other deorbiting hardware it looks like exactly what it is.
FALLING_KM_PER_DAY = -0.4

# How many snapshots back to look, and how many INDEPENDENT looks must agree before a
# candidate is called persistent. Two is the minimum that means anything: one look is
# a measurement, two is a measurement that repeated.
HISTORY_SNAPSHOTS = 4
MIN_LOOKS = 2


# ------------------------------------------------------------------ orbital regime
#
# Every constant above was calibrated on Starlink, at 475 km, in thick air. Point the
# same code at a GEO bird 75x higher and it still runs, still prints a table, and still
# sounds confident - while two of its three filters quietly do nothing at all. Measured
# on 2026-07-22:
#
#                         median alt      km/day range        median gap    "falling"
#   starlink (LEO)          475.2 km   -55.44 .. +24.18         9.68 km    1021 objects
#   intelsat (GEO)       35,786.6 km    -0.077 .. +0.160        7.44 km       0 objects
#   ses      (GEO)       35,786.0 km    -0.085 .. +0.192        0.97 km       0 objects
#
# The decay filter needs an object to lose 0.4 km/day. Nothing at GEO comes within a
# factor of two of that, because there is no atmosphere up there to lose it to. The
# filter is not broken, it is INAPPLICABLE - and a detector that reports "on the way
# down: 0" as though it had looked and found none is lying by omission.
#
# So the regime is named out loud, and each profile says which filters can actually
# fire. Naming it is the point: silence about an inert filter is how a LEO number ends
# up quoted as a GEO result.
LEO_CEILING_KM = 2000.0
GEO_BAND_KM = (34000.0, 37000.0)      # 35,786 nominal, plus room for drift and graveyard

# The floor below which nothing is flagged however unusual it looks for its age bin.
# 5 km on Starlink is about half that population's median gap. The same 5 km at GEO is
# five times SES's median - the same nominal number is ~10x more restrictive relative to
# the population it is judging, and it silently excludes most of the constellation from
# ever being flagged at all.
#
# GEO gets 1.0 km instead. Be clear about what that number is: it is a JUDGEMENT, not a
# measurement. There is no drag up there so the catalog tracks a GEO bird far more
# closely, and 1 km sits above the sub-km noise while leaving normal station-keeping
# reachable. It has not been validated against a real GEO maneuver record, and until it
# has, it is the least defensible constant in this file.
REGIME_PROFILES = {
    "LEO": {"min_km": 5.0, "decay_filter": True,
            "note": "drag is real here; the decay split does work"},
    "GEO": {"min_km": 1.0, "decay_filter": False,
            "note": "no drag: the decay split cannot fire and is reported as inert"},
    "MEO": {"min_km": 2.0, "decay_filter": False,
            "note": "little drag; decay split treated as inert pending evidence"},
}


def orbital_regime(altitudes):
    """Name the regime a constellation lives in, or 'mixed' if it does not live in one.

    Judged on the median so a couple of graveyard or transfer orbits cannot rename the
    whole constellation, and refuses to answer when the population genuinely straddles
    regimes - a single profile would be wrong for most of it.
    """
    alts = [a for a in altitudes if a == a]          # drop NaN (no mean motion on file)
    if not alts:
        return "unknown"
    med = float(np.median(alts))
    if med <= LEO_CEILING_KM:
        regime = "LEO"
    elif GEO_BAND_KM[0] <= med <= GEO_BAND_KM[1]:
        regime = "GEO"
    elif med < GEO_BAND_KM[0]:
        regime = "MEO"
    else:
        return "unknown"
    # A constellation spread across regimes gets no profile at all. Better to say so
    # than to judge half a population by the other half's physics.
    share = sum(1 for a in alts if _regime_of_one(a) == regime) / len(alts)
    return regime if share >= 0.8 else "mixed"


def _regime_of_one(alt):
    if alt <= LEO_CEILING_KM:
        return "LEO"
    if GEO_BAND_KM[0] <= alt <= GEO_BAND_KM[1]:
        return "GEO"
    if alt < GEO_BAND_KM[0]:
        return "MEO"
    return "unknown"


def regime_profile(regime):
    """Constants appropriate to a regime. Unknown regimes fall back to LEO, loudly."""
    return REGIME_PROFILES.get(regime, dict(REGIME_PROFILES["LEO"],
                                            note="UNRECOGNISED REGIME - using LEO "
                                                 "constants, which are probably wrong"))


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
    """Parse OMM CSV into {norad: Satrec}, plus the raw fields we reason about.

    Returns (sats, meta) where meta[norad] = (mean_motion, mean_motion_dot). Those
    two don't come back off a Satrec in a form that's pleasant to read, and both are
    needed to tell a satellite holding station from one on its way down.
    Later duplicates win.
    """
    sats, meta = {}, {}
    for fields in omm.parse_csv(io.StringIO(text)):
        sat = Satrec()
        try:
            omm.initialize(sat, fields)
        except (ValueError, KeyError):
            continue
        sats[sat.satnum] = sat
        try:
            meta[sat.satnum] = (float(fields["MEAN_MOTION"]),
                                float(fields["MEAN_MOTION_DOT"]))
        except (KeyError, TypeError, ValueError):
            pass
    return sats, meta


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


MU_KM3_S2 = 398600.4418
EARTH_RADIUS_KM = 6378.14


def altitude_km(mean_motion_rev_day):
    """Circular altitude implied by a mean motion, in km."""
    period_s = 86400.0 / mean_motion_rev_day
    semi_major = (MU_KM3_S2 * (period_s / (2 * np.pi)) ** 2) ** (1.0 / 3.0)
    return semi_major - EARTH_RADIUS_KM


def descent_km_per_day(mean_motion, mean_motion_dot):
    """How fast this object is losing altitude, in km/day. Negative = falling.

    MEAN_MOTION_DOT in an OMM is n-dot/2 in rev/day^2, so the mean motion changes by
    twice it over a day. Convert both to altitudes and take the difference - no drag
    model, just the element set's own statement about where it is going.
    """
    return altitude_km(mean_motion + 2.0 * mean_motion_dot) - altitude_km(mean_motion)


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

# The two things a flagged object can be. Kept as constants because persistence
# rewrites verdict strings and string-matching on them was already getting fragile.
SUSPECT = "MANEUVER SUSPECT"
FALLING_SUSPECT = "DESCENDING (extreme even for hardware on the way down)"


def classify(rows, pct, min_km, max_km=MAX_PLAUSIBLE_KM, flag=SUSPECT,
             stored_cuts=None):
    """Attach a verdict to every row, using its own age bin as the yardstick.

    Call this once per orbital regime. Objects holding station and objects being
    deorbited disagree with the catalog for completely different reasons and at
    completely different scales, so mixing them means the deorbiting ones set a
    threshold the station-keepers can never reach - and sail over it themselves.

    Two ways to set the bar, and they answer different questions:
      stored_cuts=None  - RANK: the bar is a percentile of today's population.
                          Always returns ~(100-pct)% of objects. Can never say
                          "nothing happened", because someone is always most unusual.
      stored_cuts given - ALERT: the bar was learned from past snapshots and held
                          fixed ({(lo,hi): cut_km} per age band). Today's population
                          can all sit under it, so zero is a possible answer - which
                          is the entire point.

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
        if stored_cuts is not None and (lo, hi) in stored_cuts:
            cut, basis, n = stored_cuts[(lo, hi)], "stored", int(sel.sum())
        elif stored_cuts is not None:
            # No stored bar for this band - refuse to invent one from today's crowd,
            # that would silently turn alert mode back into rank mode for these rows.
            cut, basis, n = float("inf"), "no stored baseline", int(sel.sum())
        elif sel.sum() < MIN_PER_BIN:
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
            # The floor is the object's own where analyze stamped one (regimes differ
            # inside a single operator's fleet); the scalar is the fallback.
            floor = r.get("min_km", min_km)
            if r["gap_km"] >= cut and r["gap_km"] >= floor:
                r["verdict"] = flag
                r["flagged"] = True
            elif r["gap_km"] >= floor:
                r["verdict"] = "stale (big gap, but normal for its age)"
            else:
                r["verdict"] = "agrees"
    return bands


# ------------------------------------------------------------------ baselines

BASELINE_FILE = HERE / "baselines.json"     # legacy single-group file, read-only now


def baseline_file(group):
    """One baseline file per group. A stored bar is a per-constellation fact -
    Starlink's normal band says nothing about a GEO bird's, and a single shared
    file meant learning OneWeb silently destroyed the Starlink baseline."""
    return HERE / f"baselines_{group}.json"


def learn_baselines(group, pct, min_km, max_km):
    """Learn each cohort's normal band from EVERY scoreable snapshot, and persist it.

    This is what makes "nothing happened" a possible answer. A percentile of today's
    population always hands back the top (100-pct)% - someone is always most unusual.
    A bar learned from past days and held fixed can sit above the whole of a quiet
    day, so alert mode can honestly return zero.

    The file carries its own provenance - which snapshots, when, what percentile -
    because a threshold nobody can audit is a tuned number wearing a lab coat.
    """
    pools = {"station": {}, "falling": {}}     # (lo,hi) -> [gaps]
    used, floors, regimes_seen = [], set(), set()
    for snap in snapshot_dirs():
        run = analyze(snap, group, pct, min_km, max_km, allow_live=False)
        if not run or run.get("skipped") or not run["rows"]:
            continue
        used.append(str(snap.relative_to(ARCHIVE)).replace("\\", "/"))
        # Record the floors actually applied, not the None that asked for a regime
        # default. A baseline stamped "min_km: null" is provenance nobody can audit -
        # and for a straddling fleet like SES a single scalar would be a lie, since its
        # GEO half was judged at 1 km and its MEO half at 2 km.
        floors.update(r["min_km"] for r in run["rows"])
        regimes_seen.add(run["regime"])
        for r in run["rows"]:
            if r["gap_km"] >= max_km:
                continue                        # data-quality rows poison baselines
            regime = "falling" if r["falling"] else "station"
            for lo, hi in zip(AGE_BINS, AGE_BINS[1:]):
                if lo <= r["gp_age_h"] < hi:
                    pools[regime].setdefault((lo, hi), []).append(r["gap_km"])
                    break
    if not used:
        sys.exit("no scoreable snapshots to learn from")

    applied = sorted(floors)
    out = {"group": group, "learned_utc": datetime.now(timezone.utc).isoformat(),
           "pct": pct,
           "min_km": applied[0] if len(applied) == 1 else applied,
           "orbital_regime": sorted(regimes_seen)[0] if len(regimes_seen) == 1
                             else sorted(regimes_seen),
           "snapshots": used, "regimes": {}}
    for regime, bands in pools.items():
        every = [g for v in bands.values() for g in v]
        entries = []
        for (lo, hi), gaps in sorted(bands.items()):
            # Same small-sample rule as ranking: a bar off 4 objects is not a bar.
            src = gaps if len(gaps) >= MIN_PER_BIN else every
            entries.append({"lo": lo, "hi": hi, "n": len(gaps),
                            "cut_km": float(np.percentile(src, pct)),
                            "basis": "bin" if len(gaps) >= MIN_PER_BIN else "regime"})
        out["regimes"][regime] = entries
    baseline_file(group).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def load_baselines(group):
    """Stored cuts as {(lo,hi): cut_km} per regime, or None if never learned."""
    path = baseline_file(group)
    if not path.exists():
        path = BASELINE_FILE                 # fall back to the legacy shared file
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("group") != group:
        return None
    raw["cuts"] = {reg: {(b["lo"], b["hi"]): b["cut_km"] for b in bands}
                   for reg, bands in raw["regimes"].items()}
    # Guarantee a key per regime, so a baseline file that is missing one entirely
    # cannot hand analyze() a None. None means "rank mode" to classify(), so a
    # truncated or hand-edited file would silently rank that whole regime while the
    # run still called itself alert mode - the one failure here that leaves no trace
    # in the output. An empty dict refuses loudly instead, which is the house rule.
    for regime in ("station", "falling"):
        raw["cuts"].setdefault(regime, {})
    # learn_baselines stamps the floor(s) it APPLIED - one number, or a list when
    # the fleet straddles regimes (SES: [1.0, 2.0]). The list is provenance, not a
    # parameter: analyze() takes one float or None, and None reproduces exactly
    # what the learn run did (each object judged by its own regime's floor). Read
    # it back as None rather than handing every consumer a list that crashes the
    # first float comparison - daily_alert's scheduled run died on exactly this
    # the evening SES re-learned as a mixed fleet.
    if isinstance(raw.get("min_km"), list):
        raw["min_km"] = None
    return raw


def pooled_comparison(rows, pct, min_km, max_km):
    """What the list would look like if both regimes were ranked together.

    This is the claim the regime split has to earn, so it gets measured rather than
    asserted. Returns (pooled_total, how_many_were_falling, station_keepers_the
    _pooled_ranking_never_showed).
    """
    copy = [dict(r, verdict="agrees", flagged=False) for r in rows]
    classify(copy, pct, min_km, max_km)
    pooled = {r["norad"] for r in copy if r["flagged"]}
    falling_in_pooled = sum(1 for r in copy if r["flagged"] and r["falling"])
    now = {r["norad"] for r in rows if not r["falling"] and r.get("flagged")}
    return len(pooled), falling_in_pooled, len(now - pooled)


def analyze(snap_dir, group, pct, min_km, max_km, allow_live=True, stored=None):
    """One snapshot end to end: measure every object, judge it against its age bin.

    Returns None if the snapshot can't be scored - no file for this group, or no
    catalog captured at or before it (see load_gp on why we never borrow forwards).
    """
    sup_file = snap_dir / f"{group}.csv.gz"
    if not sup_file.exists():
        return None
    now_jd = capture_jd(snap_dir)
    gp_loaded, gp_src, _ = load_gp(snap_dir, group, now_jd, allow_live)
    if gp_loaded is None:
        return {"dir": snap_dir, "rows": [], "bands": [], "skipped": gp_src}
    gp, gp_meta = gp_loaded

    sup, _ = load_omm(gzip.open(sup_file, "rt", encoding="utf-8").read())
    rows, failed = [], 0
    for norad in sorted(set(sup) & set(gp)):
        gap = rms_difference(sup[norad], gp[norad])
        if gap is None:
            failed += 1
            continue
        # Is it holding station, or on its way down? Straight off the catalog's own
        # element set - the object tells us which population it belongs to.
        mm = gp_meta.get(norad)
        drop = descent_km_per_day(*mm) if mm else 0.0
        rows.append({
            "norad": norad,
            "gap_km": gap,
            "gp_age_h": (now_jd - epoch_jd(gp[norad])) * 24.0,
            "sup_age_h": (now_jd - epoch_jd(sup[norad])) * 24.0,
            "sup_epoch": epoch_jd(sup[norad]),
            "gp_epoch": epoch_jd(gp[norad]),
            "km_per_day": drop,
            "altitude_km": altitude_km(mm[0]) if mm else float("nan"),
            "falling": drop < FALLING_KM_PER_DAY,
            "verdict": "agrees",
            "flagged": False,
        })

    # Where does this constellation actually live? The floor below which nothing is
    # flagged has to come from the regime, not from Starlink. Passing min_km=None means
    # "use the regime's own"; an explicit --min-km still wins.
    #
    # The floor is stamped PER OBJECT, not per constellation, because operators do not
    # respect the boundary: SES flies 38 birds at GEO and 30 more at 8,066 km (O3b), and
    # measured on 2026-07-22 no single floor is right for both halves. A constellation
    # -wide number would judge one half by the other half's physics.
    regime = orbital_regime([r["altitude_km"] for r in rows])
    prof = regime_profile(regime)
    for r in rows:
        if min_km is not None:
            r["min_km"] = min_km                     # an explicit --min-km wins outright
        elif r["altitude_km"] == r["altitude_km"]:   # not NaN
            r["min_km"] = regime_profile(_regime_of_one(r["altitude_km"]))["min_km"]
        else:
            r["min_km"] = prof["min_km"]             # no mean motion on file - fall back
    if min_km is None:
        min_km = prof["min_km"]

    # Can the decay split fire for ANY object here? Asked of the objects themselves
    # rather than the constellation label, because "mixed" falls back to LEO constants
    # and would otherwise claim a working decay filter for a GEO+MEO fleet that has no
    # atmosphere to decay into.
    decay_applies = any(
        regime_profile(_regime_of_one(r["altitude_km"]))["decay_filter"]
        for r in rows if r["altitude_km"] == r["altitude_km"])

    # Each regime gets its own baseline. A deorbiting satellite is only interesting
    # if it is extreme among OTHER deorbiting satellites.
    on_station = [r for r in rows if not r["falling"]]
    falling = [r for r in rows if r["falling"]]
    cuts = stored["cuts"] if stored else {}
    bands = classify(on_station, pct, min_km, max_km, flag=SUSPECT,
                     stored_cuts=cuts.get("station") if stored else None)
    classify(falling, pct, min_km, max_km, flag=FALLING_SUSPECT,
             stored_cuts=cuts.get("falling") if stored else None)

    return {"dir": snap_dir, "rows": rows, "bands": bands, "failed": failed,
            "gp_src": gp_src, "n_sup": len(sup), "n_gp": len(gp), "skipped": None,
            "n_falling": len(falling), "n_station": len(on_station),
            "regime": regime, "profile": prof, "min_km": min_km,
            "decay_applies": decay_applies}


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
            "flags": sum(1 for r in looks if r.get("flagged")),
            "gaps": [r["gap_km"] for r in looks],
            "flagged_now": bool(looks[-1].get("flagged")),
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
        if not r.get("flagged"):
            continue
        if h["looks"] < 2:
            r["verdict"] = "SUSPECT (single look - nothing to corroborate against)"
        elif h["flags"] >= min_looks:
            r["verdict"] = "PERSISTENT SUSPECT"
        else:
            r["verdict"] = "SUSPECT (new this look - unconfirmed)"


# --------------------------------------------------------- one-command daily run
#
# The whole morning verdict as `python detect.py --all`: every fleet scored in
# ALERT mode against its stored bar, one combined block on stdout, the same block
# appended to the vault's alert log. daily_alert.py stays the every-snapshot
# ledger the scheduled task fills; this is the command a human (or the scheduled
# task, once switched) runs to get today's answer in one go.

ALL_GROUPS = ["starlink", "oneweb", "intelsat", "ses"]
ALERT_LOG = HERE.parent / "RESULTS - Alert Log.md"


def score_fleet(group, every, history=HISTORY_SNAPSHOTS, min_looks=MIN_LOOKS):
    """One fleet's verdict on the newest snapshot: alert mode, persistence applied.

    Returns a plain dict for run_all to format. Deliberately does NOT catch its
    own exceptions - run_all does, per fleet, so one broken fleet reports and the
    rest still score.
    """
    stored = load_baselines(group)
    if stored is None:
        return {"group": group,
                "unscored": "no stored baseline - run --learn-baseline first"}
    latest = analyze(every[-1], group, stored["pct"], stored["min_km"],
                     MAX_PLAUSIBLE_KM, allow_live=True, stored=stored)
    if latest is None:
        return {"group": group, "unscored": "no SupGP file in this snapshot"}
    if latest["skipped"]:
        return {"group": group, "unscored": latest["skipped"]}
    rows = latest["rows"]

    runs = [latest]
    for older in every[-history:-1]:
        run = analyze(older, group, stored["pct"], stored["min_km"],
                      MAX_PLAUSIBLE_KM, allow_live=False, stored=stored)
        if run and not run["skipped"] and run["rows"]:
            runs.insert(-1, run)
    if len(runs) > 1:
        apply_persistence(rows, independent_looks(runs), min_looks)

    over = sorted([r for r in rows if not r["falling"] and r.get("flagged")],
                  key=lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9),
                  reverse=True)
    return {
        "group": group, "n": len(rows), "over": over,
        "persistent": sum(1 for r in over
                          if r["verdict"] == "PERSISTENT SUSPECT"),
        "descending": sum(1 for r in rows if r["falling"] and r.get("flagged")),
        "dq": sum(1 for r in rows if r["verdict"].startswith("DATA QUALITY")),
    }


def fleet_line(s):
    """One log line per fleet - same shape daily_alert.py established, plus the
    persistent count the morning reader actually acts on."""
    if "unscored" in s:
        return f"- **{s['group']}**: not scored - {s['unscored']}"
    if not s["over"] and not s["descending"]:
        return (f"- **{s['group']}**: 🔇 quiet — all {s['n']} objects inside "
                f"the stored bar")
    line = (f"- **{s['group']}**: {len(s['over'])} over the bar of {s['n']} scored, "
            f"{s['persistent']} persistent ({s['descending']} more among deorbiting "
            f"hardware, {s['dq']} data-quality)")
    if s["over"]:
        top = s["over"][0]
        line += (f" — top: {top['norad']} at {top['gap_km']:.1f} km, "
                 f"{top['gap_km'] / max(top['band_cut_km'], 1e-9):.1f}x its bar")
    return line


def run_all(groups=None, log_path=None, history=HISTORY_SNAPSHOTS,
            min_looks=MIN_LOOKS):
    """Score every fleet, print one block, append it to the alert log.

    Exit code is 0 as long as ANY fleet scored; 1 only when every fleet failed.
    The log is a ledger: a snapshot that already has a heading there is printed
    but never appended twice (same rule daily_alert.py keys on).
    """
    groups = groups or ALL_GROUPS
    log_path = Path(log_path) if log_path else ALERT_LOG
    every = snapshot_dirs()
    sid = f"{every[-1].parent.name}/{every[-1].name}"

    lines, failed = [], 0
    for g in groups:
        try:
            s = score_fleet(g, every, history, min_looks)
        except Exception as e:            # one fleet must not kill the others
            failed += 1
            lines.append(f"- **{g}**: FAILED - {type(e).__name__}: {e}")
            continue
        lines.append(fleet_line(s))

    print(f"\n  daily run - alert mode, stored bars - snapshot {sid}\n")
    for ln in lines:
        print(f"  {ln}")

    if log_path.exists():
        text = log_path.read_text(encoding="utf-8")
    else:
        try:                              # reuse the ledger's own header, once
            import daily_alert
            text = daily_alert.LOG_HEADER
        except Exception:
            text = "# 🚨 Alert Log\n"
    if re.search(rf"^## {re.escape(sid)}\s*$", text, re.MULTILINE):
        print(f"\n  {log_path.name} already has an entry for {sid} - not appended")
    else:
        log_path.write_text(text + f"\n## {sid}\n\n" + "\n".join(lines) + "\n",
                            encoding="utf-8")
        print(f"\n  appended -> {log_path.name}")
    if failed:
        print(f"  {failed} fleet(s) FAILED above; the rest were still scored")
    return 1 if failed == len(groups) else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="score every fleet (alert mode, stored bars), print one "
                         "combined summary and append it to the alert log")
    ap.add_argument("--group", default="starlink")
    ap.add_argument("--pct", type=float, default=95.0,
                    help="a gap above this percentile FOR ITS AGE BIN is a suspect")
    ap.add_argument("--min-km", type=float, default=None,
                    help="never flag anything below this, however unusual for its bin. "
                         "Default: the orbital regime's own floor (LEO 5.0, MEO 2.0, "
                         "GEO 1.0) - 5 km is half Starlink's median gap but five times "
                         "SES's, so one number cannot serve both")
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
    ap.add_argument("--mode", choices=["rank", "alert"], default="rank",
                    help="rank: percentile of today's crowd, always returns ~5%%. "
                         "alert: fixed bar learned from past snapshots - can return zero")
    ap.add_argument("--learn-baseline", action="store_true",
                    help="learn each cohort's normal band from every scoreable "
                         "snapshot, write baselines.json, and exit")
    ap.add_argument("--chart", action="store_true")
    ap.add_argument("--csv", action="store_true", help="write the full table")
    args = ap.parse_args()

    if args.all:
        return run_all(history=args.history, min_looks=args.min_looks)

    if args.learn_baseline:
        base = learn_baselines(args.group, args.pct, args.min_km, args.max_km)
        print(f"  learned from {len(base['snapshots'])} snapshots: "
              f"{', '.join(base['snapshots'])}")
        for regime, bands in base["regimes"].items():
            print(f"\n  {regime}:")
            for b in bands:
                hi = "inf" if b["hi"] > 1e8 else f"{b['hi']:g}"
                note = "" if b["basis"] == "bin" else "  (thin bin - used whole regime)"
                print(f"    age {b['lo']:>4g}-{hi:<6} n={b['n']:<6} "
                      f"flag above {b['cut_km']:8.2f} km{note}")
        print(f"\n  -> {baseline_file(args.group).name}  (provenance stamped inside)")
        print(f"     WARNING: learned from {len(base['snapshots'])} snapshot(s). "
              f"A bar learned from one\n     day only knows one day's weather. "
              f"Re-learn as the archive grows.")
        return 0

    stored = None
    if args.mode == "alert":
        stored = load_baselines(args.group)
        if stored is None:
            sys.exit("alert mode needs a stored baseline - run "
                     "'python detect.py --learn-baseline' first")

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
    if stored:
        print(f"  mode       ALERT - fixed bar learned from "
              f"{len(stored['snapshots'])} snapshot(s), "
              f"{stored['pct']:g}th pct, {stored['learned_utc'][:16]}Z")
    latest = analyze(snap_dir, args.group, args.pct, args.min_km, args.max_km,
                     allow_live=not replaying, stored=stored)
    if latest is None:
        sys.exit(f"{args.group} not in {snap_dir.relative_to(ARCHIVE)}")
    if latest["skipped"]:
        sys.exit(f"cannot score this snapshot: {latest['skipped']}")
    rows, bands = latest["rows"], latest["bands"]
    print(f"  supgp      {latest['n_sup']} objects")
    print(f"  gp         {latest['n_gp']} objects ({latest['gp_src']})")
    print(f"  comparable {len(rows) + latest['failed']} objects")
    if not rows:
        sys.exit("no overlap - nothing to compare")
    failed = latest["failed"]

    # ---- which physics are we actually in? -----------------------------------
    # Say it out loud. The same code, the same table and the same confident tone
    # come out whether or not half the filters below can fire at all.
    med_alt = float(np.nanmedian([r["altitude_km"] for r in rows]))
    prof = latest["profile"]
    floors = sorted({r["min_km"] for r in rows})
    shown = (f"floor {floors[0]:g} km" if len(floors) == 1
             else "floor " + "/".join(f"{f:g}" for f in floors) + " km, per object")
    print(f"  regime     {latest['regime']} - median altitude {med_alt:,.0f} km, "
          f"{shown}"
          f"{' (--min-km given)' if args.min_km is not None else ' (regime default)'}")
    if latest["regime"] == "mixed":
        mix = Counter(_regime_of_one(r["altitude_km"]) for r in rows
                      if r["altitude_km"] == r["altitude_km"])
        parts = ", ".join(f"{n} {k}" for k, n in sorted(mix.items(), key=lambda kv: -kv[1]))
        print(f"             This operator straddles regimes ({parts}). No single floor "
              f"fits, so each\n             object is judged against its own; the "
              f"constellation-wide number would have\n             put one half under "
              f"the other half's physics.")
    if not latest["decay_applies"]:
        drops = [r["km_per_day"] for r in rows]
        print(f"             DECAY SPLIT INERT here: no drag at this altitude, so the "
              f"split cannot fire.")
        print(f"             Nothing can reach {FALLING_KM_PER_DAY} km/day - this "
              f"population spans {min(drops):+.3f} to {max(drops):+.3f}.")
        print(f"             'on the way down: 0' below means NOT APPLICABLE, "
              f"not 'looked and found none'.")
    print()

    # ---- second filter: did the same objects look wrong last time too? --------
    looks, runs, unusable = {}, [latest], []
    if args.history > 1:
        for older in every[-args.history:-1]:
            run = analyze(older, args.group, args.pct, args.min_km, args.max_km,
                          allow_live=False, stored=stored)
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

    print(f"  splitting the population by what it is DOING:")
    print(f"    holding station    {latest['n_station']:>6}"
          f"   - judged against each other")
    print(f"    on the way down    {latest['n_falling']:>6}"
          f"   - losing > {abs(FALLING_KM_PER_DAY):g} km/day, judged separately\n")

    if stored:
        print("  the STORED bar for a station-keeping object, by catalog age:")
    else:
        print("  what a NORMAL gap looks like for a STATION-KEEPING object, by catalog age:")
    print(f"  {'age (h)':>12}  {'objects':>8}  {'median km':>10}  {'flag above':>11}")
    for b in bands:
        hi = "inf" if b["hi"] > 1e8 else f"{b['hi']:g}"
        star = "" if b["basis"] in ("bin", "stored")             else "  (too few - used whole population)"
        print(f"  {b['lo']:>5g}-{hi:<6}  {b['n']:>8}  {b['median_km']:>10.2f}"
              f"  {b['cut_km']:>11.2f}{star}")

    by_strength = lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9)
    station = [r for r in rows if not r["falling"]]
    persistent = sorted([r for r in station if r["verdict"] == "PERSISTENT SUSPECT"],
                        key=by_strength, reverse=True)
    unconfirmed = sorted([r for r in station if r["verdict"].startswith("SUSPECT (")],
                         key=by_strength, reverse=True)
    single = sorted([r for r in station if r["verdict"] == SUSPECT],
                    key=by_strength, reverse=True)
    descending = sorted([r for r in rows if r["falling"] and r.get("flagged")],
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
        print(f"  MANEUVER SUSPECTS  {len(single):>5}  of {len(station)} station-keepers"
              f"  - UNCORROBORATED, one snapshot only")
    print(f"  on the way down    {len(descending):>5}  - extreme among deorbiting "
          f"hardware, but they are SUPPOSED to be moving")
    print(f"  big gap but stale  {len(stale):>5}  "
          f"- would have been false positives on gap alone")
    print(f"  agrees             "
          f"{len(rows)-len(suspects)-len(descending)-len(stale)-len(flagged):>5}")
    print(f"  DATA QUALITY FLAG  {len(flagged):>5}  "
          f"- gap >= {args.max_km:g} km, physically impossible; likely decay or bad TLE")
    if flagged:
        worst = ", ".join(f"{r['norad']} ({r['gap_km']:.0f} km)" for r in flagged[:3])
        print(f"                           excluded from candidates, e.g. {worst}")
    if failed:
        print(f"  propagation failed {failed:>5}  (usually reentering)")

    if stored:
        if not suspects and not descending:
            print(f"\n  ** NOTHING HAPPENED. **\n"
                  f"     Every one of {len(rows)} objects sits inside the normal band "
                  f"learned from\n     {len(stored['snapshots'])} earlier snapshot(s). "
                  f"A percentile could never say this -\n     it would have handed back "
                  f"the top {100-stored['pct']:g}% anyway. Zero is a real answer\n"
                  f"     now, which is what makes a nonzero day mean something.")
        else:
            print(f"\n  {len(suspects)} object(s) over a bar that was set BEFORE today. "
                  f"These are not\n  'today's most unusual' - they are outside what "
                  f"{len(stored['snapshots'])} past snapshot(s)\n  called normal. "
                  f"A quiet day would have returned zero.")

    caught = len(suspects) + len(descending) + len(stale)
    if not stored and caught:
        n_pooled, n_falling, n_new = pooled_comparison(rows, args.pct, args.min_km,
                                                       args.max_km)
        print(f"\n  Ranking on raw gap alone would have surfaced {caught} objects."
              f"\n  Age-aware ranking cuts that to {n_pooled} "
              f"- {100*len(stale)/caught:.0f}% of the naive list was just old data.")
        print(f"\n  Separating the regimes does NOT shorten the list. At the "
              f"{args.pct:g}th percentile about\n  {100-args.pct:g}% of each cohort gets "
              f"flagged whatever happens up there. What it changes\n  is WHO is on it:")
        print(f"    {n_falling:>5}  of those {n_pooled} "
              f"({100*n_falling/max(n_pooled,1):.0f}%) were hardware being deliberately "
              f"deorbited.\n           They move every day, on purpose. Judged against "
              f"their own kind,\n           only {len(descending)} are unusual.")
        print(f"    {n_new:>5}  station-keepers are on the list that the pooled ranking "
              f"never\n           showed at all - they were crowded out by falling hardware.")
        if len(runs) > 1 and suspects:
            print(f"    {len(persistent):>5}  of the {len(suspects)} survived a second "
                  f"independent look.")
        print(f"\n  A satellite holding station that moved when it shouldn't have is the "
              f"only\n  part anyone would pay for. Everything else now has a name.")

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
    station = [r for r in rows if not r["falling"]]
    falling = [r for r in rows if r["falling"]]
    hit = lambda r: r["verdict"] in ("PERSISTENT SUSPECT", SUSPECT)
    once = [r for r in station if r["verdict"].startswith("SUSPECT (")]
    persisted = [r for r in station if hit(r)]
    quiet = [r for r in station if not hit(r) and not r["verdict"].startswith("SUSPECT (")]

    ax.scatter([r["gp_age_h"] for r in quiet], [r["gap_km"] for r in quiet],
               s=6, alpha=0.25, c="#888", label="holding station - normal for its age")
    ax.scatter([r["gp_age_h"] for r in falling], [r["gap_km"] for r in falling],
               s=7, alpha=0.30, c="#9467bd",
               label=f"on the way down (>{abs(FALLING_KM_PER_DAY):g} km/day) - judged separately")
    if once:
        ax.scatter([r["gp_age_h"] for r in once], [r["gap_km"] for r in once],
                   s=14, alpha=0.6, c="#ff7f0e", label="flagged once - unconfirmed")
    checked = any("looks" in r for r in rows)
    ax.scatter([r["gp_age_h"] for r in persisted], [r["gap_km"] for r in persisted],
               s=20, alpha=0.95, c="#d62728",
               label="station-keeper that moved, flag repeated" if checked
                     else "station-keeper that moved (single snapshot)")
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
