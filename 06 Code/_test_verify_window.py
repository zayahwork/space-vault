"""_test_verify_window.py - regression tests for the lag-aware verify window (issue 018).

WHAT THIS PROTECTS
The referee (issue 015) measured that the public catalog records GEO burns up to +11.0 days
after they happen, while `verify.py` shipped a +/-3 day window - so it threw away real
signal on 3 of 14 documented maneuvers. This file pins the fix:

  1. the window is REGIME-AWARE      - LEO's catalog is not late, GEO's is
  2. the window is ASYMMETRIC        - lateness runs one way; a symmetric window credits
                                       a burn with steps that happened BEFORE it
  3. the forward half is OBSERVABLE  - a +14 day reach means nothing when the snapshot is
                                       two hours old, and the run has to say so

Point 3 is the one that would otherwise ship as a silent lie: widening the window changes
no live number today, because the data it reaches for has not been published yet.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify  # noqa: E402
import verify_geo  # noqa: E402

PASS = FAIL = 0
T0 = datetime(2026, 7, 22, 20, 0, tzinfo=timezone.utc)


def check(name, got, want, tol=None):
    global PASS, FAIL
    ok = (abs(got - want) <= tol) if tol is not None else (got == want)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   got={got!r} want={want!r}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


# ---------------------------------------------------------------- regime -> window

def test_leo_window_is_unchanged():
    """LEO must not move. The catalog is not late in LEO, and a wider window there only
    feeds the control bar more noise - it would move the headline 68-72% for no reason."""
    before, after, _ = verify.window_for_regime("LEO")
    check("LEO looks back 3 days", before, 3.0, 1e-12)
    check("LEO looks forward 3 days (unchanged)", after, 3.0, 1e-12)


def test_geo_window_is_lag_aware():
    before, after, basis = verify.window_for_regime("GEO")
    check("GEO looks back only 3 days", before, 3.0, 1e-12)
    check("GEO looks forward 14 days", after, 14.0, 1e-12)
    check("GEO window cites the measurement it came from",
          "10.98" in basis and "015" in basis, True)


def test_geo_window_covers_the_worst_documented_lag():
    """Intelsat 33e's step landed at +10.98 days. +/-10 misses it by 24 hours; that is
    the whole reason this constant is 14 and not 10."""
    _, after, _ = verify.window_for_regime("GEO")
    check("GEO forward reach clears the +10.98d worst case", after > 10.98, True)


def test_window_is_never_symmetric_where_the_catalog_is_late():
    for regime in ("GEO", "MEO", "mixed"):
        before, after, _ = verify.window_for_regime(regime)
        check(f"{regime}: forward reach exceeds backward", after > before, True)


def test_mixed_and_meo_are_conservative_and_say_so():
    """No ground truth exists for MEO. Borrowing GEO's window is a judgement and has to be
    labelled as one - the same rule detect.py's GEO floor lives under."""
    for regime in ("MEO", "mixed"):
        _, _, basis = verify.window_for_regime(regime)
        check(f"{regime} window is flagged unvalidated",
              "UNVALIDATED" in basis.upper(), True)


def test_unknown_regime_falls_back_loudly():
    before, after, basis = verify.window_for_regime("banana")
    check("unknown regime still returns a usable window", (before, after), (3.0, 14.0))
    check("unknown regime says it is guessing", "UNRECOGNISED" in basis.upper(), True)


# ---------------------------------------------------------------- the step math

def pts(*rows):
    return [(T0 + timedelta(days=d), a) for d, a in rows]


def test_biggest_step_is_asymmetric():
    p = pts((-13, 100.0), (-12, 130.0), (0, 130.0), (1, 130.0))
    early = verify.biggest_step_km(p, T0, 3.0, 14.0)
    symmetric = verify.biggest_step_km(p, T0, 14.0, 14.0)
    check("a step 12 days BEFORE is not credited to the event", early, 0.0, 1e-9)
    check("a symmetric window would have credited it", symmetric, 30.0, 1e-9)


def test_biggest_step_still_defaults_to_symmetric():
    """Back-compat: one positional window argument keeps the old meaning, so every
    existing caller and the referee harness read the same thing they always did."""
    p = pts((-2, 100.0), (2, 105.0))
    check("single-arg call is symmetric",
          verify.biggest_step_km(p, T0, 3.0),
          verify.biggest_step_km(p, T0, 3.0, 3.0), 1e-12)


def test_late_step_is_caught_by_the_lag_aware_window():
    """The bug, in one assertion: Intelsat 33e-shaped signal at +11 days."""
    p = pts((-1, 100.0), (10.9, 100.0), (11.0, 129.87))
    check("+11d step invisible at +/-3d", verify.biggest_step_km(p, T0, 3.0), 0.0, 1e-9)
    check("+11d step visible at -3/+14d",
          verify.biggest_step_km(p, T0, 3.0, 14.0), 29.87, 1e-6)


# ---------------------------------------------------------------- measured catalog lag

def test_lag_profile_measures_update_cadence():
    hist = {1: [(T0 + timedelta(days=i * 0.5), 100.0) for i in range(11)]}
    prof = verify.lag_profile(hist)
    check("median catalog update interval, days", prof["median_days"], 0.5, 1e-9)
    check("counts the intervals it measured", prof["n"], 10)


def test_lag_profile_ignores_objects_with_no_intervals():
    prof = verify.lag_profile({1: [(T0, 100.0)], 2: []})
    check("no intervals -> no profile, not a zero", prof["n"], 0)
    check("no intervals -> median is None", prof["median_days"], None)


# ---------------------------------------------------------------- observability

def test_forward_half_is_unobservable_on_a_fresh_snapshot():
    """The finding that stops this change being a silent no-op: verifying a snapshot two
    hours old with a +14 day window reaches for data nobody has published yet."""
    now = T0 + timedelta(hours=2)
    obs = verify.observable_window(T0, 14.0, now)
    check("only 2 hours of the forward half exist", obs["observable_after_days"],
          2 / 24, 1e-6)
    check("so the verdict is provisional", obs["provisional"], True)
    check("and it says when it can be settled", obs["settles_in_days"], 14 - 2 / 24, 1e-6)


def test_an_old_snapshot_is_fully_observable():
    now = T0 + timedelta(days=20)
    obs = verify.observable_window(T0, 14.0, now)
    check("whole forward half available", obs["observable_after_days"], 14.0, 1e-9)
    check("verdict is final", obs["provisional"], False)
    check("nothing left to wait for", obs["settles_in_days"], 0.0, 1e-9)


def test_leo_is_not_provisional_for_the_usual_reason():
    """LEO's window is +/-3d, so a 3-day-old snapshot is already fully settled there -
    the provisional warning must not cry wolf on every LEO run."""
    obs = verify.observable_window(T0, 3.0, T0 + timedelta(days=3.1))
    check("LEO settles in 3 days", obs["provisional"], False)


# ---------------------------------------------------------------- both verifiers agree

def test_verify_geo_uses_the_same_window_table():
    """verify_geo.py must not keep a private copy of the constant - that is how the two
    verifiers drifted apart in the first place."""
    check("verify_geo delegates to verify.window_for_regime",
          verify_geo.window_for_regime("GEO"), verify.window_for_regime("GEO"))
    check("and its step finder takes the same asymmetric window",
          verify_geo.biggest_step(
              [(T0 + timedelta(days=d), i, 0.0) for d, i in
               ((-13, 1.00), (-12, 1.04), (0, 1.04))], T0, 1, 3.0, 14.0),
          0.0, 1e-9)


if __name__ == "__main__":
    for fn in sorted([f for n, f in list(globals().items()) if n.startswith("test_")],
                     key=lambda f: f.__code__.co_firstlineno):
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n  {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
