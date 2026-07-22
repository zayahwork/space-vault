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
EVENT_PAD_DAYS = 25    # history pulled either side of an event date
NULL_STRIDE_DAYS = 5   # spacing of null window centres - deterministic, no sampling


# ------------------------------------------------------------------ the step math

def step_in_window(points, centre, comp, window_days):
    """Largest change in component `comp` between consecutive records near `centre`.

    Returns (size, offset_days, n_pairs): the step, how far after the event the catalog
    recorded it, and how many consecutive pairs the window actually contained. The last
    number is what stops a silent 0.0 from a row with no history reading as "no movement".

    Identical rule to verify.biggest_step_km and verify_geo.biggest_step: a pair counts if
    the LATER of its two epochs falls inside the window. _test_referee.py asserts that
    agreement against the shipped functions rather than trusting this comment.
    """
    lo, hi = centre - timedelta(days=window_days), centre + timedelta(days=window_days)
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

def measure_null(hist, widths, stride_days=NULL_STRIDE_DAYS):
    """Null step distribution per (component, width), from non-maneuvering objects.

    Window centres march across each object's history at a fixed stride, so the number of
    windows is a property of the data rather than of a random draw. Both components are
    measured through the same code path as the events, which is the only way the altitude
    and inclination columns can be compared to each other at all.
    """
    out = {}
    for comp, name in ((1, "alt"), (2, "inc")):
        for w in widths:
            out[f"{name}_{w:g}"] = []
    for pts in hist.values():
        if len(pts) < 10:
            continue
        t0, t1 = pts[0][0], pts[-1][0]
        centre = t0 + timedelta(days=max(widths))
        while centre <= t1 - timedelta(days=max(widths)):
            for comp, name in ((1, "alt"), (2, "inc")):
                for w in widths:
                    size, _, pairs = step_in_window(pts, centre, comp, w)
                    if pairs:
                        out[f"{name}_{w:g}"].append(size)
            centre += timedelta(days=stride_days)
    return out


# ------------------------------------------------------------------ scoring

def score_event(ev, pts, bars, widths=(NARROW_DAYS, WIDE_DAYS)):
    """One event through all four measurements. Never drops a row for thin history."""
    res = {"records": len(pts), "cols": {}}
    if pts:
        res["history_from"] = pts[0][0].isoformat()
        res["history_to"] = pts[-1][0].isoformat()
    for comp, name in ((1, "alt"), (2, "inc")):
        for w in widths:
            key = f"{name}_{w:g}"
            size, off, pairs = step_in_window(pts, ev["date"], comp, w)
            bar = bars.get(key, {})
            if pairs == 0:
                verdict = "NO DATA"
            elif bar.get("max") is None:
                verdict = "NO BAR"
            else:
                verdict = "caught" if size > bar["max"] else "missed"
            res["cols"][key] = {"step": size, "offset_days": off, "pairs": pairs,
                                "verdict": verdict,
                                "over_p99": (bar.get("p99") is not None
                                             and size > bar["p99"])}
    return res


def rate(rows, key):
    scored = [r for r in rows if r["cols"][key]["verdict"] in ("caught", "missed")]
    caught = [r for r in scored if r["cols"][key]["verdict"] == "caught"]
    return len(caught), len(scored)


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", default=str(HERE / "ground_truth.csv"))
    ap.add_argument("--nulls", type=int, default=8,
                    help="abandoned GEO/ID objects used to measure the bar")
    ap.add_argument("--null-start", default="2025-07-01")
    ap.add_argument("--null-end", default="2026-07-15")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    widths = (NARROW_DAYS, WIDE_DAYS)
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

    # --- the bar -----------------------------------------------------------
    exclude = {e["norad"] for e in events}
    nulls = abandoned_norads(parse_geotab(geotab_text()), exclude, args.nulls)
    print(f"\n  null objects (GCAT GEO/ID, abandoned): {nulls}")
    n_start = datetime.fromisoformat(args.null_start).replace(tzinfo=timezone.utc)
    n_end = datetime.fromisoformat(args.null_end).replace(tzinfo=timezone.utc)
    null_hist = fetch_range(session, nulls, n_start, n_end)
    bars = bars_from_null(measure_null(null_hist, widths))

    print(f"\n  NOISE FLOOR  {args.null_start}..{args.null_end}, "
          f"{sum(len(v) for v in null_hist.values())} catalog records")
    print(f"  {'window':<16}{'n windows':>10}{'median':>12}{'99th':>12}{'largest':>12}")
    for comp, unit in (("alt", "km"), ("inc", "deg")):
        for w in widths:
            b = bars[f"{comp}_{w:g}"]
            if not b["n"]:
                continue
            print(f"  {comp} +/-{w:g}d{'':<7}{b['n']:>10}"
                  f"{b['median']:>12.5f}{b['p99']:>12.5f}{b['max']:>12.5f}  {unit}")

    # --- the events --------------------------------------------------------
    print(f"\n  scoring {len(events)} GEO events")
    scored = []
    for ev in events:
        hist = fetch_range(session, [ev["norad"]],
                           ev["date"] - timedelta(days=EVENT_PAD_DAYS),
                           ev["date"] + timedelta(days=EVENT_PAD_DAYS))
        res = score_event(ev, hist.get(ev["norad"], []), bars, widths)
        res.update(ev)
        res["date"] = ev["date"].isoformat()[:10]
        scored.append(res)

    hdr = (f"\n  {'object':<16}{'date':<12}{'src':<5}{'rec':>5}"
           f"{'alt+/-3':>12}{'alt+/-10':>12}{'inc+/-3':>12}{'inc+/-10':>12}")
    for role, title in (("scoreable", "THE 14 SCOREABLE EVENTS"),
                        ("excluded", "EXCLUDED"), ("null", "NULL OBJECT")):
        rows = [r for r in scored if r["role"] == role]
        if not rows:
            continue
        print(f"\n  == {title} ==")
        print(hdr)
        for r in sorted(rows, key=lambda x: (not x["double_sourced"], x["date"])):
            cells = ""
            for key in ("alt_3", "alt_10", "inc_3", "inc_10"):
                c = r["cols"][key]
                mark = {"caught": "Y", "missed": "n", "NO DATA": "?", "NO BAR": "-"}[
                    c["verdict"]]
                cells += f"{mark} {c['step']:>9.4f}" if c["pairs"] else f"{'? no data':>12}"
            print(f"  {r['object']:<16}{r['date']:<12}"
                  f"{'2src' if r['double_sourced'] else '1src':<5}{r['records']:>5}{cells}")

    # --- the verdict -------------------------------------------------------
    sc = [r for r in scored if r["role"] == "scoreable"]
    dbl = [r for r in sc if r["double_sourced"]]
    print(f"\n  == SCOREBOARD ==")
    print(f"  {'measurement':<22}{'all scoreable':>16}{'double-sourced':>18}")
    for key, label in (("alt_3", "altitude +/-3d"), ("alt_10", "altitude +/-10d"),
                       ("inc_3", "inclination +/-3d"), ("inc_10", "inclination +/-10d")):
        a, an = rate(sc, key)
        d, dn = rate(dbl, key)
        print(f"  {label:<22}{f'{a}/{an}':>16}{f'{d}/{dn}':>18}")

    nulls_row = [r for r in scored if r["role"] == "null"]
    if nulls_row:
        fa = {k: nulls_row[0]["cols"][k]["verdict"] for k in
              ("alt_3", "alt_10", "inc_3", "inc_10")}
        print(f"\n  false-alarm check on the documented null "
              f"({nulls_row[0]['object']}): {fa}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"bars": bars, "nulls": nulls, "events": scored}, indent=2, default=str),
            encoding="utf-8")
        print(f"\n  wrote {args.json}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
