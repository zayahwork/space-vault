"""referee_geo.py - score BOTH GEO verifiers against the documented maneuver record.

WHY THIS EXISTS
Two of us built explanations for the same failure (SES shows no signal at GEO) and the
explanations contradict each other:

  Tim   (verify_geo.py):  the altitude verifier is blind to the dominant GEO maneuver by
                          construction - north-south station-keeping moves INCLINATION,
                          not altitude. Wrong OBSERVABLE.
  Randy (ground_truth.csv): N-S station-keeping DOES move fitted altitude, by 0.84-3.00 km
                          on documented events. The altitude verifier's real failure is
                          its +/-3 day window against a catalog that lags up to 10 days.
                          Wrong TIMING.

Mechanism arguments cannot settle that. Documented events can. This scores every GEO event
in ground_truth.csv three ways, with the SAME step-finding math the shipped verifiers use:

  (a) altitude step, +/-3 day window     - verify.py exactly as written (WINDOW_DAYS = 3.0)
  (b) altitude step, +/-10 day window    - the lag-aware fix Randy proposes
  (c) inclination step, +/-3 day window  - verify_geo.py's independent channel

and (d) inclination at +/-10 days too, because comparing (b) against (c) would otherwise
be comparing a widened window against a narrow one and calling the difference physics.

THE BAR IS RE-MEASURED PER WINDOW WIDTH, AND THAT IS THE POINT
A wider window is not free. It examines more consecutive-record pairs, so it gives catalog
noise more chances to throw a big step. Scoring a +/-10 day window against a bar measured
in +/-3 day windows would manufacture catches out of arithmetic. So the null distribution
is measured separately at each width, from objects McDowell's GCAT classifies GEO/ID -
inclined-drifting, i.e. abandoned, no engine - and the bar is the largest step those
objects ever produce, which is the rule Randy's 0.419 km bar was built on.

THE BAR IS ALSO MATCHED PER EVENT, ON ERA AND ON TRACKING CADENCE
A first pass measured one global bar from eight abandoned objects and got 1.51 km, nearly
4x Randy's 0.419 km. The whole difference was two objects: Syncom 3 and Early Bird, 1960s
spacecraft the size of a dustbin, updated 0.7 and 1.3 times a day against 2.5-3 for the
rest. Sparse tracking means looser fits means bigger apparent steps, so those two were not
measuring GEO catalog noise - they were measuring how badly a small target gets tracked.
The four well-tracked objects gave 0.26-0.39 km, which reproduces Randy's number from a
different sample.

That is a trap, not a curiosity: the events being scored are large GEO comsats tracked
1.1-3.4 times a day, and Galaxy 15 in 2010 is tracked less often than AMC 11 in 2026. So
the bar for each event is measured from abandoned objects over the SAME +/-120 days, kept
only if their catalog update rate is within 0.5x-2x of the event object's own. Every row
reports the bar it was judged against and how many objects set it.

WHAT THIS IS NOT
GP_HISTORY is the public catalog's own history, so every column here shares the catalog
side with detect.py. What makes this a referee is not independence from the catalog - it
is that the EVENT DATES come from press releases, a Space Force statement, a NASA debris
bulletin, a USGS space-weather study and McDowell's phase catalog, none of which either
author wrote. Rows whose date we read out of the catalog ourselves cannot referee
anything; they are reported separately and carry no weight in the verdict.

Usage:
  python referee_geo.py                 # score everything, print the table
  python referee_geo.py --json out.json # also dump machine-readable results
  python referee_geo.py --nulls 8       # how many abandoned objects set the bar
"""
import argparse
import csv
import json
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify  # noqa: E402  - login, BASE, BATCH, altitude_km and politeness are shared

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
CACHE = HERE / "referee_cache"
GEOTAB_URL = "https://planet4589.org/space/gcat/tsv/derived/geotab.tsv"

NARROW_DAYS = 3.0      # verify.py / verify_geo.py as shipped
WIDE_DAYS = 10.0       # the largest catalog lag documented in ground_truth.csv
# ...except the CSV rounds it. Intelsat 33e's step actually lands at +10.98 days, so a
# +/-10 window misses the best-evidenced late signal in the set by 24 hours. 14 is the
# width Randy's own write-up recommends and the one that survives the rounding.
WIDER_DAYS = 14.0
EVENT_PAD_DAYS = 25    # history pulled either side of an event date
NULL_SPAN_DAYS = 120   # history pulled either side of an event to measure ITS bar
NULL_STRIDE_DAYS = 5   # spacing of null window centres - deterministic, no sampling
CADENCE_LO, CADENCE_HI = 0.5, 2.0   # null must be tracked 0.5x-2x as often as the event


# Every window scored, as (days BEFORE the event, days AFTER, label).
#
# The lag-aware windows are ASYMMETRIC, and that is not a detail. Catalog lateness runs
# one way: an orbit determination can be published days after the burn, never days before
# it. A symmetric +/-14d window does not model lateness - it just looks at four weeks of
# history and takes the biggest thing in it. Measured here, that difference is the whole
# result on two rows: at +/-14d the MEV-2 and Intelsat 1002 dockings both "catch" on
# inclination steps landing 12.3 days BEFORE the docking. Those are unrelated events being
# credited to the docking by a window wide enough to swallow them.
WINDOWS = [
    (3.0, 3.0, "+/-3d"),        # verify.py / verify_geo.py exactly as shipped
    (3.0, 10.0, "-3/+10d"),     # lag-aware to the largest lag ground_truth.csv records
    (3.0, 14.0, "-3/+14d"),     # ...and to the width Randy's write-up actually recommends
    (14.0, 14.0, "+/-14d"),     # the naive symmetric widening, for comparison
]


def key_for(comp, before, after):
    return f"{comp}_{before:g}_{after:g}"


# ------------------------------------------------------------------ the step math

def step_in_window(points, centre, comp, before_days, after_days=None):
    """Largest change in component `comp` between consecutive records near `centre`.

    Returns (size, offset_days, n_pairs): the step, how far after the event the catalog
    recorded it, and how many consecutive pairs the window actually contained. The last
    number is what stops a silent 0.0 from a row with no history reading as "no movement".

    Identical rule to verify.biggest_step_km and verify_geo.biggest_step: a pair counts if
    the LATER of its two epochs falls inside the window. _test_referee.py asserts that
    agreement against the shipped functions rather than trusting this comment.
    """
    if after_days is None:
        after_days = before_days
    lo = centre - timedelta(days=before_days)
    hi = centre + timedelta(days=after_days)
    best, best_off, pairs = 0.0, None, 0
    for a, b in zip(points, points[1:]):
        if lo <= b[0] <= hi:
            pairs += 1
            size = abs(b[comp] - a[comp])
            if size > best:
                best = size
                best_off = (b[0] - centre).total_seconds() / 86400.0
    return best, best_off, pairs


def bars_from_null(null_steps):
    """Bar per window width: the largest step an abandoned object ever produced.

    Also returns the 99th percentile, because "largest ever observed" is not a stable
    statistic - it can only grow as more windows are measured, so a bar built that way
    gets stricter every time someone re-runs it with a bigger null. Both are reported and
    the verdicts are checked against both.
    """
    out = {}
    for key, vals in null_steps.items():
        if not vals:
            out[key] = {"n": 0, "max": None, "p99": None, "median": None}
            continue
        s = sorted(vals)
        out[key] = {"n": len(s), "max": s[-1],
                    "p99": s[min(len(s) - 1, int(0.99 * (len(s) - 1)))],
                    "median": statistics.median(s)}
    return out


# ------------------------------------------------------------------ inputs

def parse_geotab(text):
    """McDowell's GEO table into dicts. Header line is commented, so strip the '#'."""
    lines = [L for L in text.splitlines() if L.strip()]
    hdr = [h.strip() for h in lines[0].lstrip("#").split("\t")]
    rows = []
    for L in lines[1:]:
        if L.startswith("#"):
            continue
        parts = [p.strip() for p in L.split("\t")]
        if len(parts) < len(hdr):
            continue
        rows.append(dict(zip(hdr, parts)))
    return rows


def abandoned_norads(geotab_rows, exclude, limit):
    """Objects GCAT calls GEO/ID - inclined drifting, i.e. nobody is flying them.

    Deterministic: sorted by catalogue number, first `limit` that clear the filters. No
    sampling, so the bar this produces is reproducible by anyone running the same command.
    """
    out = []
    for r in geotab_rows:
        jcat = r.get("JCAT", "")
        if not jcat.startswith("S") or r.get("OType") != "GEO/ID":
            continue
        try:
            norad = int(jcat[1:])
            per, apo = float(r["Perigee"]), float(r["Apogee"])
        except (ValueError, KeyError):
            continue
        if norad in exclude:
            continue
        # Near the belt and roughly circular: a drifting object in a wild ellipse is not
        # measuring the same noise the station-kept population sits in.
        if not (34500 <= per <= 37500 and 34500 <= apo <= 37500):
            continue
        out.append(norad)
    return sorted(out)[:limit]


def load_geo_events(csv_path):
    """The GEO rows of ground_truth.csv, tagged with how they get treated.

    scoreable  - the 14 the referee test is about
    excluded   - MEV-1, whose own orbit-raising transit contaminates its window
    null       - AMC 18, the documented non-maneuvering object; scored as a false-alarm
                 check rather than as a catch/miss
    """
    events = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["regime"] != "GEO":
                continue
            if row["verdict"] == "excluded":
                role = "excluded"
            elif row["verdict"] == "true_negative":
                role = "null"
            else:
                role = "scoreable"
            events.append({
                "norad": int(row["norad"]),
                "object": row["object"],
                "date": datetime.fromisoformat(row["event_date_utc"]).replace(
                    tzinfo=timezone.utc),
                "type": row["event_type"],
                "double_sourced": row["independent"].strip().lower() == "yes",
                "randy_verdict": row["verdict"],
                "randy_alt_km": row["alt_step_km"],
                "randy_inc_deg": row["inc_step_deg"],
                "role": role,
            })
    return events


# ------------------------------------------------------------------ space-track

def fetch_range(session, norads, start, end):
    """GP_HISTORY between two dates: {norad: [(epoch, altitude_km, inclination_deg)]}.

    Cached per object per range. These are historical windows going back to 2010, so the
    answers never change; asking Space-Track twice would be rude and slow.
    """
    CACHE.mkdir(exist_ok=True)
    tag = f"{start:%Y%m%d}_{end:%Y%m%d}"
    out, missing = {}, []
    for n in norads:
        f = CACHE / f"{n}_{tag}.json"
        if f.exists():
            out[n] = [(datetime.fromisoformat(t), a, i)
                      for t, a, i in json.loads(f.read_text(encoding="utf-8"))]
        else:
            missing.append(n)

    for i in range(0, len(missing), verify.BATCH):
        chunk = missing[i:i + verify.BATCH]
        url = (verify.BASE + "/basicspacedata/query/class/gp_history/NORAD_CAT_ID/"
               + ",".join(str(c) for c in chunk)
               + f"/EPOCH/{start:%Y-%m-%d}--{end:%Y-%m-%d}"
               + "/orderby/EPOCH%20asc/format/json")
        print(f"    fetching {len(chunk)} objects {tag} "
              f"({i + len(chunk)}/{len(missing)})...")
        resp = session.get(url, timeout=180)
        resp.raise_for_status()

        grouped = {}
        for row in resp.json():
            try:
                n = int(row["NORAD_CAT_ID"])
                grouped.setdefault(n, []).append((
                    datetime.fromisoformat(row["EPOCH"]).replace(tzinfo=timezone.utc),
                    verify.altitude_km(row),
                    float(row["INCLINATION"])))
            except (KeyError, ValueError, TypeError):
                continue
        for n in chunk:
            pts = sorted(set(grouped.get(n, [])))
            out[n] = pts
            (CACHE / f"{n}_{tag}.json").write_text(
                json.dumps([[t.isoformat(), a, inc] for t, a, inc in pts]),
                encoding="utf-8")
        if i + verify.BATCH < len(missing):
            time.sleep(verify.POLITE_SEC)
    return out


def geotab_text():
    CACHE.mkdir(exist_ok=True)
    f = CACHE / "geotab.tsv"
    if not f.exists():
        f.write_bytes(urllib.request.urlopen(GEOTAB_URL, timeout=120).read())
    return f.read_text(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------ the null

def cadence(points, span_days):
    """Catalog updates per day. The single best predictor of how big a step noise alone
    can throw: a loosely-tracked object gets loosely-fitted orbits."""
    return len(points) / float(span_days) if span_days else 0.0


def cadence_matched(null_hist, event_cadence, span_days,
                    lo=CADENCE_LO, hi=CADENCE_HI):
    """Keep only null objects tracked at a rate comparable to the event object.

    Returns (kept_hist, [(norad, cadence, kept)]) so the caller can print who set the bar
    and who was thrown out - a bar nobody can audit is not a bar.
    """
    kept, audit = {}, []
    for n, pts in sorted(null_hist.items()):
        c = cadence(pts, span_days)
        ok = event_cadence > 0 and lo * event_cadence <= c <= hi * event_cadence
        if ok:
            kept[n] = pts
        audit.append((n, c, ok))
    return kept, audit


def measure_null(hist, windows, stride_days=NULL_STRIDE_DAYS):
    """Null step distribution per (component, width), from non-maneuvering objects.

    Window centres march across each object's history at a fixed stride, so the number of
    windows is a property of the data rather than of a random draw. Both components are
    measured through the same code path as the events, which is the only way the altitude
    and inclination columns can be compared to each other at all.
    """
    out = {}
    for comp, name in ((1, "alt"), (2, "inc")):
        for b, a, _ in windows:
            out[key_for(name, b, a)] = []
    pad = max(max(b, a) for b, a, _ in windows)
    for pts in hist.values():
        if len(pts) < 10:
            continue
        t0, t1 = pts[0][0], pts[-1][0]
        centre = t0 + timedelta(days=pad)
        while centre <= t1 - timedelta(days=pad):
            for comp, name in ((1, "alt"), (2, "inc")):
                for b, a, _ in windows:
                    size, _, pairs = step_in_window(pts, centre, comp, b, a)
                    if pairs:
                        out[key_for(name, b, a)].append(size)
            centre += timedelta(days=stride_days)
    return out


# ------------------------------------------------------------------ scoring

def score_event(ev, pts, bars, windows):
    """One event through every measurement. Never drops a row for thin history."""
    res = {"records": len(pts), "cols": {}}
    if pts:
        res["history_from"] = pts[0][0].isoformat()
        res["history_to"] = pts[-1][0].isoformat()
    for comp, name in ((1, "alt"), (2, "inc")):
        for b, a, _ in windows:
            key = key_for(name, b, a)
            size, off, pairs = step_in_window(pts, ev["date"], comp, b, a)
            bar = bars.get(key, {})
            if pairs == 0:
                verdict = verdict_p99 = "NO DATA"
            elif bar.get("max") is None:
                verdict = verdict_p99 = "NO BAR"
            else:
                # Two bars, because "largest step ever observed" is the strict rule Randy
                # used but is hostage to the single worst-fitted orbit in the null, while
                # the 99th percentile is stable but lets ~1 window in 100 through. A
                # result that flips between them is not a result; say which ones flip.
                verdict = "caught" if size > bar["max"] else "missed"
                verdict_p99 = "caught" if size > bar["p99"] else "missed"
            res["cols"][key] = {"step": size, "offset_days": off, "pairs": pairs,
                                "verdict": verdict, "verdict_p99": verdict_p99,
                                "bar_max": bar.get("max"), "bar_p99": bar.get("p99")}
    return res


def rate(rows, key, field="verdict"):
    scored = [r for r in rows if r["cols"][key][field] in ("caught", "missed")]
    caught = [r for r in scored if r["cols"][key][field] == "caught"]
    return len(caught), len(scored)


def matched_bar(null_hist, event_cadence, span_days, windows):
    """The bar for one event, relaxing the cadence match only as far as it has to.

    Nothing here silently falls back to "all objects": each relaxation is returned so the
    row can be marked. An unmatched bar is a weaker bar and the reader gets to know which
    rows have one.
    """
    for lo, hi, tag in ((CADENCE_LO, CADENCE_HI, "matched"),
                        (CADENCE_LO / 2, CADENCE_HI * 2, "widened"),
                        (0.0, 1e9, "unmatched")):
        kept, audit = cadence_matched(null_hist, event_cadence, span_days, lo, hi)
        bars = bars_from_null(measure_null(kept, windows))
        if any(b["n"] for b in bars.values()):
            return bars, kept, audit, tag
    return bars_from_null({}), {}, [], "none"


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", default=str(HERE / "ground_truth.csv"))
    ap.add_argument("--nulls", type=int, default=16,
                    help="candidate abandoned GEO/ID objects; each event keeps the ones "
                         "tracked at a comparable rate in its own era")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    windows = WINDOWS
    events = load_geo_events(args.csv)
    scoreable = [e for e in events if e["role"] == "scoreable"]
    print(f"\n  ground truth   {args.csv}")
    print(f"  GEO rows       {len(events)}  "
          f"({len(scoreable)} scoreable, "
          f"{sum(1 for e in events if e['role'] == 'excluded')} excluded, "
          f"{sum(1 for e in events if e['role'] == 'null')} null)")
    print(f"  double-sourced {sum(1 for e in scoreable if e['double_sourced'])} "
          f"of the {len(scoreable)} scoreable")

    session = verify.login()
    print("  space-track login ok")

    # --- candidate null pool ------------------------------------------------
    exclude = {e["norad"] for e in events}
    candidates = abandoned_norads(parse_geotab(geotab_text()), exclude, args.nulls)
    print(f"\n  candidate null objects (GCAT GEO/ID, abandoned, near-belt): {candidates}")
    print(f"  each event keeps those tracked {CADENCE_LO:g}x-{CADENCE_HI:g}x as often as "
          f"the event object, over the same +/-{NULL_SPAN_DAYS}d")

    # --- score each event against its own era- and cadence-matched bar ------
    print(f"\n  scoring {len(events)} GEO events")
    scored = []
    for ev in events:
        hist = fetch_range(session, [ev["norad"]],
                           ev["date"] - timedelta(days=EVENT_PAD_DAYS),
                           ev["date"] + timedelta(days=EVENT_PAD_DAYS))
        pts = hist.get(ev["norad"], [])
        ev_cad = cadence(pts, 2 * EVENT_PAD_DAYS)

        null_hist = fetch_range(session, candidates,
                                ev["date"] - timedelta(days=NULL_SPAN_DAYS),
                                ev["date"] + timedelta(days=NULL_SPAN_DAYS))
        bars, kept, audit, tag = matched_bar(null_hist, ev_cad, 2 * NULL_SPAN_DAYS,
                                             windows)

        res = score_event(ev, pts, bars, windows)
        res.update(ev)
        res["date"] = ev["date"].isoformat()[:10]
        res["cadence"] = ev_cad
        res["bars"] = bars
        res["bar_match"] = tag
        res["bar_objects"] = sorted(kept)
        res["bar_audit"] = [{"norad": n, "cadence": c, "kept": k} for n, c, k in audit]
        scored.append(res)

    for role, title in (("scoreable", "THE 14 SCOREABLE EVENTS"),
                        ("excluded", "EXCLUDED"), ("null", "NULL OBJECT")):
        rows = sorted([r for r in scored if r["role"] == role],
                      key=lambda x: (not x["double_sourced"], x["date"]))
        if not rows:
            continue
        for comp, unit in (("alt", "km"), ("inc", "deg")):
            keys = [key_for(comp, b, a) for b, a, _ in windows]
            print(f"\n  == {title} == {comp.upper()} step ({unit}) and how many times "
                  f"its own bar   Y = over, n = under")
            print(f"  {'object':<15}{'date':<12}{'src':<5}{'rec/d':>6}{'bar':>9}"
                  + "".join(f"{lab:>20}" for _, _, lab in windows)
                  + f"{'lag':>8}")
            for r in rows:
                cells = ""
                for key in keys:
                    c = r["cols"][key]
                    if not c["pairs"]:
                        cells += f"{'? no data':>20}"
                    elif c["bar_max"] is None:
                        cells += f"{'- no bar':>20}"
                    else:
                        cells += (f"{c['step']:>10.4f}"
                                  f"{c['step'] / max(c['bar_max'], 1e-12):>7.1f}x "
                                  f"{'Y' if c['verdict'] == 'caught' else 'n'}")
                off = r["cols"][keys[-1]]["offset_days"]
                print(f"  {r['object']:<15}{r['date']:<12}"
                      f"{'2src' if r['double_sourced'] else '1src':<5}"
                      f"{r['cadence']:>6.1f}{r['bar_match']:>9}{cells}"
                      + (f"{off:>+7.1f}d" if off is not None else f"{'-':>8}"))
            print(f"  {'':<38}{'bar used:':>9}"
                  + "".join(
                      f"{r0.get(k, {}).get('max'):>13.4f} [{r0[k]['p99']:.3f}]"
                      if (r0 := rows[0]['bars']).get(k, {}).get('max') is not None
                      else f"{'-':>20}" for k in keys)
                  + "   <- first row; per-row bars in --json")

    # --- the verdict -------------------------------------------------------
    sc = [r for r in scored if r["role"] == "scoreable"]
    dbl = [r for r in sc if r["double_sourced"]]
    print(f"\n  == SCOREBOARD ==   bar = largest null step  (99th-pct bar in brackets)")
    print(f"  {'measurement':<22}{'all scoreable':>22}{'double-sourced':>22}")
    labels = [(key_for(c, b, a),
               ("altitude" if c == "alt" else "inclination") + " " + lab)
              for c in ("alt", "inc") for b, a, lab in windows]
    for key, label in labels:
        got, n = rate(sc, key)
        got99, n99 = rate(sc, key, "verdict_p99")
        d, dn = rate(dbl, key)
        d99, dn99 = rate(dbl, key, "verdict_p99")
        print(f"  {label:<22}{f'{got}/{n} [{got99}/{n99}]':>22}"
              f"{f'{d}/{dn} [{d99}/{dn99}]':>22}")

    flips = [(r["object"], r["date"], k) for r in sc for k, _ in labels
             if r["cols"][k]["verdict"] != r["cols"][k]["verdict_p99"]]
    print(f"\n  rows whose verdict depends on which bar you pick ({len(flips)}): "
          f"{flips if flips else 'none'}")

    for role, label in (("null", "documented NULL (no maneuvers, must stay silent)"),
                        ("excluded", "EXCLUDED from scoring")):
        for r in [x for x in scored if x["role"] == role]:
            fa = {k: r["cols"][k]["verdict"] for k, _ in labels}
            print(f"  {label}: {r['object']} -> {fa}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"candidate_nulls": candidates, "events": scored}, indent=2, default=str),
            encoding="utf-8")
        print(f"\n  wrote {args.json}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
