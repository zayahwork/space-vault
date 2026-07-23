"""_test_holdout.py - tests for the unseen-data holdout protocol (issue 033).

WHAT THIS PROTECTS
The first question any technical diligence asks is "did you tune on what you tested?".
holdout.py exists to answer it in writing, so its splitting logic must itself be beyond
argument:

  1. a snapshot counts as UNSEEN only if captured STRICTLY AFTER the cutoff - a
     snapshot captured at the cutoff instant was available for tuning and stays tuned-side
  2. stored bars are only usable if every snapshot in their provenance is at/before the
     cutoff - one post-cutoff snapshot in the learn set poisons the whole claim
  3. ground-truth events split by a FROZEN key list - an event used to pick the -3/+14
     window can never score the window, and any event added later is holdout by default
  4. the measured reach comes from the DATA, not the wall clock - a cache written
     yesterday has no idea what "now" is, and clamping to wall-clock elapsed would
     silently credit forward reach the fetched history does not contain
  5. rates at a clamped reach are computed with the same one-sided step logic verify.py
     ships - a step landing beyond the clamp must not count yet

All on synthetic fixtures - no archive, no network.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import holdout  # noqa: E402

PASS = FAIL = 0
UTC = timezone.utc
CUTOFF = datetime(2026, 7, 23, 0, 0, tzinfo=UTC)
CENTRE = datetime(2026, 7, 23, 2, 0, tzinfo=UTC)


def check(name, got, want, tol=None):
    global PASS, FAIL
    ok = (abs(got - want) <= tol) if tol is not None else (got == want)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   got={got!r} want={want!r}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


# ---------------------------------------------------------------- snapshot split

def test_snapshot_name_parses():
    check("archive name parses to its capture instant",
          holdout.snap_name_to_dt("2026-07-22/1400Z"),
          datetime(2026, 7, 22, 14, 0, tzinfo=UTC))


def test_snapshot_split_is_strict():
    """A snapshot captured AT the cutoff was available to tuning. Only strictly-after
    counts as unseen - the boundary case is exactly where a soft split would cheat."""
    names = ["2026-07-22/1400Z", "2026-07-23/0000Z", "2026-07-23/0200Z"]
    pre, post = holdout.split_snapshots(names, CUTOFF)
    check("pre-cutoff side keeps the old snapshot", "2026-07-22/1400Z" in pre, True)
    check("a snapshot AT the cutoff instant is NOT unseen",
          "2026-07-23/0000Z" in pre, True)
    check("strictly-after snapshot is unseen", post, ["2026-07-23/0200Z"])


def test_empty_when_nothing_is_unseen():
    """No post-cutoff data means the protocol refuses, not improvises. The standing
    rule: never shrink the requirement to force output."""
    pre, post = holdout.split_snapshots(["2026-07-22/0200Z"], CUTOFF)
    check("no unseen snapshots -> empty list, caller must refuse", post, [])


# ---------------------------------------------------------------- baseline provenance

def _baseline(snaps):
    return {"group": "starlink", "learned_utc": "2026-07-22T19:16:25+00:00",
            "snapshots": snaps}


def test_clean_baseline_has_no_violations():
    b = _baseline(["2026-07-22/0200Z", "2026-07-22/1400Z"])
    check("bars learned wholly before the cutoff pass",
          holdout.baseline_violations(b, CUTOFF), [])


def test_poisoned_baseline_is_named():
    """One post-cutoff snapshot in the learn set and the zero-overlap claim is dead.
    The violation is returned BY NAME so the refusal can say exactly why."""
    b = _baseline(["2026-07-22/1400Z", "2026-07-23/0200Z"])
    check("a post-cutoff learn snapshot is flagged",
          holdout.baseline_violations(b, CUTOFF), ["2026-07-23/0200Z"])


def test_learn_snapshot_at_cutoff_is_fine():
    """Provenance may reach up TO the cutoff - the split is tuned-through-cutoff,
    scored-after. Only strictly-after learn data violates."""
    b = _baseline(["2026-07-23/0000Z"])
    check("learn data at the cutoff instant is allowed",
          holdout.baseline_violations(b, CUTOFF), [])


# ---------------------------------------------------------------- ground-truth split

def _ev(norad, date, role="scoreable", verdict="caught"):
    return {"norad": norad, "date": date, "object": f"obj{norad}", "role": role,
            "cols": {"alt_3_14": {"verdict": verdict}}}


def test_event_split_by_frozen_keys():
    events = [_ev(46113, "2021-04-12"),                 # in the 015 tuning set
              _ev(36581, "2025-09-08"),                 # added by 026 - holdout
              _ev(99999, "2026-08-01")]                 # future row - holdout by default
    tune, hold = holdout.split_events(events)
    check("015-era event stays tuning-side",
          any(e["norad"] == 46113 for e in tune), True)
    check("026's later row is holdout", any(e["norad"] == 36581 for e in hold), True)
    check("an event added in the future is holdout automatically",
          any(e["norad"] == 99999 for e in hold), True)
    check("the two sides are disjoint",
          {(e['norad'], e['date']) for e in tune}
          & {(e['norad'], e['date']) for e in hold}, set())


def test_frozen_tuning_keys_are_the_015_set():
    """16 GEO rows existed when the -3/+14 window was chosen (14 scoreable + MEV-1
    excluded + AMC 18 null). If this number moves, someone edited the frozen list -
    which is exactly the thing freezing exists to prevent."""
    check("frozen tuning key count", len(holdout.TUNING_EVENT_KEYS), 16)
    check("MEV-1 is tuning-side (excluded there, excluded here)",
          (44625, "2020-02-25") in holdout.TUNING_EVENT_KEYS, True)
    check("Astra 3B EW row is NOT in the frozen set",
          (36581, "2025-09-08") in holdout.TUNING_EVENT_KEYS, False)


# ---------------------------------------------------------------- reach from data

def _pts(*hours_and_alts):
    return [(CENTRE + timedelta(hours=h), a) for h, a in hours_and_alts]


def test_reach_measured_from_data_not_clock():
    hist = {1: _pts((-48, 500.0), (-24, 500.0), (0, 500.0), (6, 500.0)),
            2: _pts((-48, 500.0), (-24, 500.0), (0, 500.0), (3, 500.0))}
    r = holdout.data_reach_days(hist, CENTRE)
    check("median forward reach is what the points contain", r["median"], 0.1875, 1e-9)
    check("min reach reported too", r["min"], 0.125, 1e-9)


def test_reach_with_no_forward_data_is_zero():
    hist = {1: _pts((-24, 500.0), (-1, 500.0))}
    r = holdout.data_reach_days(hist, CENTRE)
    check("history ending before the centre = zero reach, not negative",
          r["median"], 0.0, 1e-12)


# ---------------------------------------------------------------- rates at a reach

def _row(norad):
    return {"norad": norad}


def test_step_beyond_the_clamp_does_not_count():
    """A suspect whose step lands +0.2d after the snapshot: invisible at reach 0.1,
    visible at reach 0.3. This is the observability correction, enforced per run."""
    flat = _pts((-30, 500.0), (-20, 500.0), (-10, 500.0), (0, 500.0), (10, 500.0))
    stepped = _pts((-30, 500.0), (-20, 500.0), (-10, 500.0), (0, 500.0), (4.8, 503.0))
    hist = {1: stepped, **{n: flat for n in range(2, 12)}}
    suspects = [_row(1)]
    controls = [_row(n) for n in range(2, 12)]
    early = holdout.score_at_reach(suspects, controls, hist, CENTRE, 3.0, 0.1)
    late = holdout.score_at_reach(suspects, controls, hist, CENTRE, 3.0, 0.3)
    check("step at +0.2d invisible at reach 0.1", early["over_suspects"], 0)
    check("same step counted at reach 0.3", late["over_suspects"], 1)
    check("controls' denominator is all ten", late["n_controls"], 10)


def test_thin_history_leaves_the_denominator():
    """Same rule as verify.py/hardening.py: <5 points is not scoreable and is excluded
    from the denominator, never counted as a miss."""
    flat = _pts((-30, 500.0), (-20, 500.0), (-10, 500.0), (0, 500.0), (1, 500.0))
    hist = {1: _pts((0, 500.0)), **{n: flat for n in range(2, 8)}}
    out = holdout.score_at_reach([_row(1), _row(2)], [_row(n) for n in range(3, 8)],
                                 hist, CENTRE, 3.0, 1.0)
    check("thin suspect excluded from denominator", out["n_suspects"], 1)
    check("thin count reported", out["thin_suspects"], 1)


def test_bar_is_the_controls_90th_percentile():
    """The bar must come from the controls at the SAME reach - reusing a full-reach bar
    against clamped suspect steps would flatter the suspects."""
    mk = lambda a: _pts((-30, 500.0), (-20, 500.0), (-10, 500.0), (0, 500.0),
                        (2.4, 500.0 + a))
    hist = {n: mk(0.01 * n) for n in range(1, 11)}          # controls step 0.01..0.10
    hist[99] = mk(5.0)                                       # suspect steps 5 km
    out = holdout.score_at_reach([_row(99)], [_row(n) for n in range(1, 11)],
                                 hist, CENTRE, 3.0, 3.0)
    check("bar is controls' own 90th pct", out["bar_km"], 0.09, 1e-9)
    check("suspect over it", out["over_suspects"], 1)
    check("exactly one control over its own bar", out["over_controls"], 1)


# ---------------------------------------------------------------- cache eviction

def _cache_file(d, norad, days, pts):
    import json
    f = d / f"{norad}_{days}d.json"
    f.write_text(json.dumps([[t.isoformat(), a] for t, a in pts]), encoding="utf-8")
    return f


def test_unsettled_cache_file_is_evicted():
    """The bug this guards against (found 2026-07-23, second real run): a snapshot's
    first fetch lands in its per-snapshot cache with 0.00d forward reach, and every
    re-run re-serves that file - so 're-run once aged ~0.5d' silently no-ops and the
    holdout figure can never settle. A cached file that does not yet span the full
    forward window must be evicted so the re-run refetches."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        f = _cache_file(d, 101, 30, _pts((-24, 500.0), (0, 500.0), (2, 500.0)))
        n = holdout.evict_unsettled_cache(d, CENTRE, 3.0, 30)
        check("short-reach file evicted", f.exists(), False)
        check("eviction counted", n, 1)


def test_settled_cache_file_is_kept():
    """Once the cached history spans the full forward window, refetching cannot add
    information - the file stays and Space-Track is not asked twice."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        f = _cache_file(d, 102, 30, _pts((-24, 500.0), (0, 500.0), (73, 500.0)))
        n = holdout.evict_unsettled_cache(d, CENTRE, 3.0, 30)
        check("settled file kept", f.exists(), True)
        check("nothing evicted", n, 0)


def test_empty_and_corrupt_cache_files_are_evicted():
    """An empty history teaches nothing and a corrupt file would crash the read -
    both are worth one refetch."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        empty = _cache_file(d, 103, 30, [])
        corrupt = d / "104_30d.json"
        corrupt.write_text("{not json", encoding="utf-8")
        n = holdout.evict_unsettled_cache(d, CENTRE, 3.0, 30)
        check("empty file evicted", empty.exists(), False)
        check("corrupt file evicted", corrupt.exists(), False)
        check("both counted", n, 2)


def test_other_days_suffix_untouched():
    """Eviction only reasons about files fetched at this run's --days; a file for a
    different span is someone else's and stays."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        other = _cache_file(d, 105, 60, _pts((0, 500.0)))
        n = holdout.evict_unsettled_cache(d, CENTRE, 3.0, 30)
        check("different-days file untouched", other.exists(), True)
        check("not counted", n, 0)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith("test_") and callable(v)}.items()):
        print(f"\n{name}")
        fn()
    print(f"\n{'=' * 60}\n  {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
