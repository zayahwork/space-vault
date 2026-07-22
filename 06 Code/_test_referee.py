"""_test_referee.py - tests for referee_geo.py.

The load-bearing test in here is not any single number: it is that referee_geo's step
finder returns EXACTLY what verify.biggest_step_km and verify_geo.biggest_step return on
the same points. If it drifted from them, the referee would be scoring a verifier nobody
ships, and the whole exercise would be theatre.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import referee_geo as R  # noqa: E402
import verify  # noqa: E402
import verify_geo  # noqa: E402

PASS = FAIL = 0
T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)


def check(name, got, want, tol=None):
    global PASS, FAIL
    ok = (abs(got - want) <= tol) if tol is not None else (got == want)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   got={got!r} want={want!r}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


def pts(*rows):
    """(day offset, altitude, inclination) -> the (epoch, alt, inc) tuples used by both."""
    return [(T0 + timedelta(days=d), a, i) for d, a, i in rows]


# ---------------------------------------------------------------- step math

def test_step_basic():
    p = pts((-5, 100.0, 1.0), (-1, 100.0, 1.0), (1, 103.0, 1.05), (6, 103.0, 1.05))
    size, off, pairs = R.step_in_window(p, T0, 1, 3.0)
    check("step size inside +/-3d", size, 3.0, 1e-9)
    check("step offset is the LATER epoch", off, 1.0, 1e-9)
    check("pairs counted in +/-3d", pairs, 2)


def test_step_window_excludes():
    """A step whose later epoch sits outside the window must not count. This is the whole
    Tim-vs-Randy timing argument in one assertion."""
    p = pts((0, 100.0, 1.0), (5, 130.0, 1.0))
    narrow, _, _ = R.step_in_window(p, T0, 1, 3.0)
    wide, off, _ = R.step_in_window(p, T0, 1, 10.0)
    check("+5d step invisible at +/-3d", narrow, 0.0, 1e-9)
    check("+5d step visible at +/-10d", wide, 30.0, 1e-9)
    check("+5d step reports its lag", off, 5.0, 1e-9)


def test_step_no_pairs_is_not_zero_movement():
    p = pts((-20, 100.0, 1.0), (-19, 100.0, 1.0))
    size, off, pairs = R.step_in_window(p, T0, 1, 3.0)
    check("empty window -> 0.0 size", size, 0.0, 1e-9)
    check("empty window -> no offset", off, None)
    check("empty window -> pairs 0 (so callers can say NO DATA)", pairs, 0)


def test_inclination_component():
    p = pts((-1, 100.0, 1.00), (1, 100.0, 1.05))
    size, _, _ = R.step_in_window(p, T0, 2, 3.0)
    check("inclination step reads component 2", size, 0.05, 1e-9)


def test_matches_shipped_verify():
    """referee vs verify.biggest_step_km on identical points."""
    p = pts((-6, 100.0, 1.0), (-2, 101.5, 1.0), (0, 101.5, 1.0), (2, 108.0, 1.0),
            (9, 108.4, 1.0))
    alt_pts = [(t, a) for t, a, _ in p]
    for w in (3.0, 10.0, 14.0):
        mine, _, _ = R.step_in_window(p, T0, 1, w)
        theirs = verify.biggest_step_km(alt_pts, T0, window_days=w)
        check(f"altitude step agrees with verify.py at +/-{w:g}d", mine, theirs, 1e-12)


def test_matches_shipped_verify_geo():
    """referee vs verify_geo.biggest_step on identical points, both components.

    verify_geo's tuples are (epoch, inclination, drift); ours are (epoch, altitude,
    inclination). Component 2 there is drift and here is inclination - the shapes differ,
    the windowing rule must not, so the comparison feeds each function its own layout.
    """
    p = pts((-6, 100.0, 1.00), (-2, 101.5, 1.02), (0, 101.5, 1.02), (2, 108.0, 1.09),
            (9, 108.4, 1.11))
    geo_pts = [(t, i, a) for t, a, i in p]      # (epoch, inclination, <other>)
    for w in (3.0, 10.0):
        mine, _, _ = R.step_in_window(p, T0, 2, w)
        theirs = verify_geo.biggest_step(geo_pts, T0, 1, window_days=w)
        check(f"inclination step agrees with verify_geo.py at +/-{w:g}d",
              mine, theirs, 1e-12)
    check("verify_geo's shipped default window is still 3 days",
          verify_geo.WINDOW_DAYS, 3.0, 1e-12)
    check("verify's shipped default window is still 3 days",
          verify.WINDOW_DAYS, 3.0, 1e-12)


# ---------------------------------------------------------------- the bar

def test_bars():
    b = R.bars_from_null({"alt_3": [0.1, 0.2, 0.3, 9.0], "inc_3": []})
    check("bar takes the largest null step", b["alt_3"]["max"], 9.0, 1e-9)
    check("bar reports n", b["alt_3"]["n"], 4)
    check("empty null -> no bar, not a zero bar", b["inc_3"]["max"], None)


def test_wider_window_cannot_lower_the_bar():
    """Monotonicity: every +/-3d window is contained in the +/-10d window with the same
    centre, so the wide null can only be >= the narrow one. If this ever fails, the
    windowing is broken and every 'lag-aware' catch below it is an artefact."""
    p = pts(*[(d, 100.0 + (0.4 if d % 7 == 0 else 0.0), 1.0) for d in range(-40, 41)])
    null = R.measure_null({1: p}, (3.0, 10.0), stride_days=5)
    n3, n10 = max(null["alt_3"]), max(null["alt_10"])
    check("wide-window null >= narrow-window null", n10 >= n3, True)


def test_measure_null_skips_thin_history():
    thin = pts((0, 100.0, 1.0), (1, 100.0, 1.0))
    null = R.measure_null({1: thin}, (3.0, 10.0))
    check("thin object contributes no null windows", len(null["alt_3"]), 0)


# ---------------------------------------------------------------- scoring

def test_score_event_verdicts():
    bars = {"alt_3": {"max": 0.5, "p99": 0.3}, "alt_10": {"max": 0.6, "p99": 0.35},
            "inc_3": {"max": 0.006, "p99": 0.004}, "inc_10": {"max": 0.007,
                                                              "p99": 0.005}}
    ev = {"date": T0}
    # -2 and -1 give the +/-3d window a pair of its own, so a "missed" there means the
    # window looked and saw nothing - not that it had nothing to look at.
    p = pts((-2, 100.0, 1.0), (-1, 100.0, 1.0), (5, 102.15, 1.0), (6, 102.15, 1.0))
    res = R.score_event(ev, p, bars)
    check("late altitude step missed at +/-3d", res["cols"]["alt_3"]["verdict"], "missed")
    check("late altitude step caught at +/-10d", res["cols"]["alt_10"]["verdict"],
          "caught")
    check("no inclination movement -> missed", res["cols"]["inc_10"]["verdict"], "missed")


def test_score_event_no_data_is_reported_not_dropped():
    bars = {k: {"max": 1.0, "p99": 0.5} for k in ("alt_3", "alt_10", "inc_3", "inc_10")}
    res = R.score_event({"date": T0}, [], bars)
    check("no history -> NO DATA verdict", res["cols"]["alt_3"]["verdict"], "NO DATA")
    check("no history -> record count 0", res["records"], 0)


def test_rate_ignores_unscoreable():
    rows = [{"cols": {"a": {"verdict": "caught"}}},
            {"cols": {"a": {"verdict": "missed"}}},
            {"cols": {"a": {"verdict": "NO DATA"}}}]
    c, n = R.rate(rows, "a")
    check("rate counts caught", c, 1)
    check("rate excludes NO DATA from the denominator", n, 2)


# ---------------------------------------------------------------- inputs

def test_load_geo_events():
    evs = R.load_geo_events(str(Path(__file__).resolve().parent / "ground_truth.csv"))
    roles = [e["role"] for e in evs]
    check("14 scoreable GEO events", roles.count("scoreable"), 14)
    check("1 excluded (MEV-1)", roles.count("excluded"), 1)
    check("1 documented null (AMC 18)", roles.count("null"), 1)
    dbl = [e for e in evs if e["double_sourced"]]
    check("7 double-sourced GEO rows in the CSV", len(dbl), 7)
    check("but only 6 of them are scoreable - MEV-1 is excluded",
          sum(1 for e in dbl if e["role"] == "scoreable"), 6)
    g15 = [e for e in evs if e["object"] == "Galaxy 15"][0]
    check("Galaxy 15 date parsed", g15["date"].isoformat()[:10], "2010-04-05")


def test_parse_and_select_geotab():
    text = ("#JCAT\tPiece\tName\tPerigee\tApogee\tOType\n"
            "S00001\t-\tActive\t35780\t35790\tGEO/S\n"
            "S00002\t-\tDrifter\t35770\t35800\tGEO/ID\n"
            "S00003\t-\tExcluded\t35770\t35800\tGEO/ID\n"
            "S00004\t-\tEccentric\t20000\t36000\tGEO/ID\n")
    rows = R.parse_geotab(text)
    check("geotab parsed", len(rows), 4)
    got = R.abandoned_norads(rows, exclude={3}, limit=10)
    check("only abandoned, near-belt, non-excluded objects set the bar", got, [2])


if __name__ == "__main__":
    for fn in sorted([f for n, f in list(globals().items()) if n.startswith("test_")],
                     key=lambda f: f.__code__.co_firstlineno):
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n  {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
