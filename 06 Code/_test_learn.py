"""Proves learn_baselines - the step that turns an archive into the stored bar.

This is the last untested link in the alert-mode chain. _test_alert.py covers the bar
once it exists (loading it, applying it, refusing without it); this covers the code that
MANUFACTURES it. A bug here is the worst kind we have: it writes a plausible number into
a file stamped with real provenance, and every later run trusts it. Nothing downstream
can tell a poisoned bar from an honest one.

The archive is faked (snapshot_dirs and analyze are swapped out) so every expected
percentile is computable by hand. Percentile is set to 50 throughout, because a median
of a known list is checkable by eye and a 99th percentile of 30 values is not.

  python _test_learn.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

TEST_GROUP = "_learntest"        # never a real constellation - keeps real baselines safe

_real_snapshot_dirs = detect.snapshot_dirs
_real_analyze = detect.analyze


def row(gap, age_h, falling=False):
    return {"gap_km": gap, "gp_age_h": age_h, "falling": falling,
            "verdict": "agrees", "flagged": False}


def snap(name):
    return detect.ARCHIVE / "2026-07-22" / name


def install(by_snap):
    """Swap the archive for a hand-built one. by_snap: {snap_dir: run-or-None}."""
    detect.snapshot_dirs = lambda: list(by_snap)
    detect.analyze = lambda s, *a, **k: by_snap[s]


def restore():
    detect.snapshot_dirs = _real_snapshot_dirs
    detect.analyze = _real_analyze


def band(out, regime, lo):
    return [b for b in out["regimes"][regime] if b["lo"] == lo][0]


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
    return ok


passed = True
path = detect.baseline_file(TEST_GROUP)

try:
    print("\n  nonsense orbits must not poison the bar\n")

    # 30 honest station-keepers at 1..30 km -> median 15.5. Plus one 5,000 km row,
    # which is physically impossible and is exactly what the max_km gate exists for.
    # If it leaked into the pool the median would move to 16.0.
    rs = [row(g, 15.0) for g in range(1, 31)] + [row(5000.0, 15.0)]
    install({snap("0000Z"): {"rows": rs, "skipped": None}})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    passed &= check("a 5,000 km gap is excluded from the learned bar",
                    band(out, "station", 12)["cut_km"], 15.5)
    passed &= check("  and is not counted in the band's n",
                    band(out, "station", 12)["n"], 30)

    print("\n  the two regimes are learned apart\n")

    # Deorbiting hardware disagrees with the catalog by hundreds of km every day. If
    # it pooled with the station-keepers it would drag their bar far out of reach -
    # the same mistake the regime split exists to prevent, made one layer earlier.
    rs = ([row(g, 15.0) for g in range(1, 31)] +
          [row(g, 15.0, falling=True) for g in range(100, 130)])
    install({snap("0000Z"): {"rows": rs, "skipped": None}})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    passed &= check("station bar is unmoved by falling hardware",
                    band(out, "station", 12)["cut_km"], 15.5)
    passed &= check("falling hardware gets its own, much higher bar",
                    band(out, "falling", 12)["cut_km"], 114.5)

    print("\n  age binning\n")

    # A thin band must not produce a percentile off 5 objects. It falls back to the
    # whole regime: 1..30 plus 100..104 = 35 values, median = 18.
    rs = [row(g, 15.0) for g in range(1, 31)] + [row(g, 4.0) for g in range(100, 105)]
    install({snap("0000Z"): {"rows": rs, "skipped": None}})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    passed &= check("fat band (n=30) -> percentile of the band itself",
                    (band(out, "station", 12)["basis"], band(out, "station", 12)["cut_km"]),
                    ("bin", 15.5))
    passed &= check("thin band (n=5) -> falls back to the whole regime",
                    (band(out, "station", 3)["basis"], band(out, "station", 3)["cut_km"]),
                    ("regime", 18.0))

    # Bands are half-open [lo, hi). An age of exactly 24 h belongs to 24-48, not 12-24.
    rs = [row(4.0, 24.0)] + [row(4.0, 23.999)]
    install({snap("0000Z"): {"rows": rs, "skipped": None}})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    passed &= check("age exactly 24.0 h lands in 24-48, not 12-24",
                    (band(out, "station", 24)["n"], band(out, "station", 12)["n"]), (1, 1))

    # A negative age means a catalog entry issued AFTER the snapshot - the time-travel
    # bug load_gp exists to prevent. If one ever slipped through it must be dropped,
    # not silently folded into the lowest band.
    rs = [row(4.0, -1.0)] + [row(g, 15.0) for g in range(1, 31)]
    install({snap("0000Z"): {"rows": rs, "skipped": None}})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    total = sum(b["n"] for b in out["regimes"]["station"])
    passed &= check("a negative catalog age is dropped, not mis-binned", total, 30)

    print("\n  learning from the whole archive\n")

    # Every scoreable snapshot contributes. Two snapshots of 15 rows each pool into
    # one band of 30 - so the bar is learned from the archive, not from one day.
    install({snap("0000Z"): {"rows": [row(g, 15.0) for g in range(1, 16)],
                             "skipped": None},
             snap("0600Z"): {"rows": [row(g, 15.0) for g in range(16, 31)],
                             "skipped": None}})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    passed &= check("two snapshots pool into one band", band(out, "station", 12)["n"], 30)
    passed &= check("  and both are recorded as provenance",
                    out["snapshots"], ["2026-07-22/0000Z", "2026-07-22/0600Z"])

    # Unscoreable snapshots are skipped and must not be claimed as provenance.
    install({snap("0000Z"): {"rows": [row(g, 15.0) for g in range(1, 31)],
                             "skipped": None},
             snap("0600Z"): {"rows": [], "skipped": "no archived catalog"},
             snap("1200Z"): None})
    out = detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
    passed &= check("skipped and empty snapshots are not claimed as sources",
                    out["snapshots"], ["2026-07-22/0000Z"])

    print("\n  provenance, and the round trip back out\n")

    passed &= check("the settings it was learned under are stamped in",
                    (out["group"], out["pct"], out["min_km"]), (TEST_GROUP, 50.0, 5.0))
    passed &= check("  and it is written where load_baselines will find it",
                    path.exists(), True)
    back = detect.load_baselines(TEST_GROUP)
    passed &= check("  and reads back as a usable bar",
                    back["cuts"]["station"][(12, 24)], 15.5)

    print("\n  refusing an empty archive\n")

    # Nothing scoreable must be a loud exit, not a baseline file full of nothing.
    install({snap("0000Z"): None})
    try:
        detect.learn_baselines(TEST_GROUP, 50.0, 5.0, 500.0)
        passed &= check("no scoreable snapshots -> refuses", "returned normally", "SystemExit")
    except SystemExit as e:
        passed &= check("no scoreable snapshots -> refuses", "no scoreable" in str(e), True)

finally:
    restore()
    if path.exists():
        path.unlink()

print()
print("  all passed" if passed else "  SOMETHING FAILED")
sys.exit(0 if passed else 1)
