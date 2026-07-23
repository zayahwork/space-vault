"""Proves alert mode's stored-bar path - the code behind "zero is a possible answer".

Alert mode is the difference between a ranking tool and an alerting one. Rank mode
hands back the top (100-pct)% of today's crowd whatever happened up there; alert mode
judges today against a bar learned from PAST snapshots and held fixed, so a quiet day
can honestly return nothing.

That claim is published. Until now the code carrying it had no tests - the 9 cases in
_test_detect.py are all persistence, and none of them touch stored_cuts. The failure
mode that matters is silent: if alert mode ever falls back to a percentile of today's
population, it still prints a plausible-looking list and nobody can tell from the output
that "zero" stopped being possible.

  python _test_alert.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

TEST_GROUP = "_alerttest"       # never a real constellation - keeps real baselines safe


def rows(n, age_h, gap_km):
    return [{"gap_km": gap_km, "gp_age_h": age_h, "verdict": "agrees", "flagged": False}
            for _ in range(n)]


def flagged(rs):
    return sum(1 for r in rs if r["flagged"])


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
    return ok


passed = True
print("\n  the claim: zero is a possible answer\n")

# A whole population sitting quietly under a bar learned from past days.
quiet_day = rows(40, 15.0, 6.0)
bands = detect.classify(quiet_day, 95.0, 5.0, stored_cuts={(12, 24): 50.0})
passed &= check("40 objects, all under the stored bar -> ZERO flagged",
                flagged(quiet_day), 0)
passed &= check("  and the band says the bar was stored, not computed today",
                bands[0]["basis"], "stored")

# The same population in rank mode. This contrast IS the feature: identical data,
# and a percentile of today's crowd still has to hand back somebody.
same_day = rows(40, 15.0, 6.0)
same_day[0]["gap_km"] = 9.0          # one object marginally above the rest
detect.classify(same_day, 95.0, 5.0)
passed &= check("same quiet population in RANK mode -> still flags somebody",
                flagged(same_day) > 0, True)

print("\n  the stored bar actually decides\n")

busy = rows(30, 15.0, 4.0) + rows(1, 15.0, 60.0)
detect.classify(busy, 95.0, 5.0, stored_cuts={(12, 24): 50.0})
passed &= check("one object over the stored bar -> exactly 1 flagged",
                flagged(busy), 1)
passed &= check("  and it is the 60 km one",
                [r["gap_km"] for r in busy if r["flagged"]], [60.0])

# Floor still applies: unusual for its band is not enough on its own.
tiny = rows(30, 15.0, 4.0)
detect.classify(tiny, 95.0, 5.0, stored_cuts={(12, 24): 3.0})
passed &= check("over the stored bar but under --min-km -> not flagged",
                flagged(tiny), 0)

# The plausibility gate runs BEFORE the stored bar, in alert mode too.
junk = rows(30, 15.0, 4.0) + rows(1, 15.0, 5000.0)
detect.classify(junk, 95.0, 5.0, stored_cuts={(12, 24): 50.0})
passed &= check("a 5,000 km gap in alert mode -> data-quality, never a detection",
                flagged(junk), 0)
passed &= check("  and it is labelled as such",
                junk[-1]["verdict"].startswith("DATA QUALITY"), True)

print("\n  refusing to invent a bar it was never taught\n")

# An age band with no stored bar must NOT borrow today's percentile. Doing so would
# silently turn alert mode back into rank mode for those rows - the exact regression
# that would make "zero is possible" quietly untrue.
unseen = rows(30, 15.0, 4.0) + rows(1, 15.0, 400.0)
bands = detect.classify(unseen, 95.0, 5.0, stored_cuts={(24, 48): 50.0})
passed &= check("band with no stored bar -> nothing flagged, even a 400 km gap",
                flagged(unseen), 0)
passed &= check("  and it says so rather than inventing one",
                bands[0]["basis"], "no stored baseline")

# Rank mode is allowed the fallback alert mode is denied - proving the two paths differ.
thin = rows(5, 15.0, 4.0) + rows(30, 30.0, 4.0)
bands = detect.classify(thin, 95.0, 5.0)
thin_band = [b for b in bands if b["lo"] == 12][0]
passed &= check("rank mode, thin bin -> falls back to whole population",
                thin_band["basis"], "population")

print("\n  the stored file: provenance and the wrong-group guard\n")

path = detect.baseline_file(TEST_GROUP)
try:
    path.write_text(json.dumps({
        "group": TEST_GROUP, "learned_utc": "2026-07-22T00:00:00+00:00",
        "pct": 99.0, "min_km": 5.0, "snapshots": ["2026-07-22/0200Z"],
        "regimes": {"station": [{"lo": 12, "hi": 24, "n": 900, "cut_km": 43.9,
                                 "basis": "bin"}],
                    "falling": [{"lo": 12, "hi": 24, "n": 400, "cut_km": 282.8,
                                 "basis": "bin"}]},
    }), encoding="utf-8")

    got = detect.load_baselines(TEST_GROUP)
    passed &= check("cuts come back keyed by age band",
                    got["cuts"]["station"][(12, 24)], 43.9)
    passed &= check("  both regimes are carried", sorted(got["cuts"]), ["falling", "station"])
    passed &= check("  provenance survives the round trip",
                    got["snapshots"], ["2026-07-22/0200Z"])

    # A baseline learned for one constellation must never be applied to another -
    # Starlink's normal band says nothing about a GEO bird's. The guard is on the
    # group stamped INSIDE the file, so point a wrong-group file at this name.
    path.write_text(json.dumps({
        "group": "starlink", "learned_utc": "2026-07-22T00:00:00+00:00",
        "pct": 99.0, "min_km": 5.0, "snapshots": ["2026-07-22/0200Z"],
        "regimes": {"station": [{"lo": 12, "hi": 24, "n": 900, "cut_km": 43.9,
                                 "basis": "bin"}], "falling": []},
    }), encoding="utf-8")
    passed &= check("file stamped for another constellation -> refused, not applied",
                    detect.load_baselines(TEST_GROUP), None)

    # An empty regime list is NOT the same as a missing one: it yields {}, which is
    # not None, so classify() takes the refuse branch. baselines_oneweb.json is
    # actually shaped this way (nothing up there is decaying), so this path is live.
    path.write_text(json.dumps({
        "group": TEST_GROUP, "learned_utc": "2026-07-22T00:00:00+00:00",
        "pct": 99.0, "min_km": 5.0, "snapshots": ["2026-07-22/0200Z"],
        "regimes": {"station": [{"lo": 12, "hi": 24, "n": 900, "cut_km": 43.9,
                                 "basis": "bin"}], "falling": []},
    }), encoding="utf-8")
    empty = detect.load_baselines(TEST_GROUP)
    passed &= check("empty 'falling' regime -> {} not None", empty["cuts"]["falling"], {})
    empty_rows = rows(30, 15.0, 4.0) + rows(1, 15.0, 400.0)
    detect.classify(empty_rows, 95.0, 5.0, stored_cuts=empty["cuts"]["falling"])
    passed &= check("  so it still REFUSES rather than ranking",
                    flagged(empty_rows), 0)

    # A file missing a regime entirely. analyze() does cuts.get(regime), so a missing
    # key yields None - which classify() reads as "rank mode". Alert mode would then
    # silently rank that whole regime while still calling itself alert mode.
    path.write_text(json.dumps({
        "group": TEST_GROUP, "learned_utc": "2026-07-22T00:00:00+00:00",
        "pct": 99.0, "min_km": 5.0, "snapshots": ["2026-07-22/0200Z"],
        "regimes": {"station": [{"lo": 12, "hi": 24, "n": 900, "cut_km": 43.9,
                                 "basis": "bin"}]},
    }), encoding="utf-8")
    half = detect.load_baselines(TEST_GROUP)
    passed &= check("baseline file missing the 'falling' regime -> filled with {}, not None",
                    half["cuts"]["falling"], {})
    # Why that matters: None means "rank mode" to classify(). A truncated file would
    # otherwise rank a whole regime while still calling itself alert mode.
    fall_rows = rows(30, 15.0, 4.0) + rows(1, 15.0, 400.0)
    detect.classify(fall_rows, 95.0, 5.0, stored_cuts=half["cuts"]["falling"])
    passed &= check("  -> that regime refuses instead of silently ranking",
                    flagged(fall_rows), 0)
    # A mixed fleet's learned floor is stamped as a LIST ([1.0, 2.0] for SES's
    # GEO+MEO halves). That list is provenance; analyze() takes one float or None.
    # load_baselines must hand back None (= each object's own regime floor, which
    # is exactly what the learn run applied) - forwarding the list crashed the
    # scheduled alert run the evening SES re-learned as mixed.
    path.write_text(json.dumps({
        "group": TEST_GROUP, "learned_utc": "2026-07-22T00:00:00+00:00",
        "pct": 99.0, "min_km": [1.0, 2.0], "snapshots": ["2026-07-22/0200Z"],
        "regimes": {"station": [{"lo": 12, "hi": 24, "n": 900, "cut_km": 43.9,
                                 "basis": "bin"}], "falling": []},
    }), encoding="utf-8")
    mixed = detect.load_baselines(TEST_GROUP)
    passed &= check("mixed-fleet list floor -> read back as None (per-object regime floor)",
                    mixed["min_km"], None)
finally:
    if path.exists():
        path.unlink()

print()
print("  all passed" if passed else "  SOMETHING FAILED")
sys.exit(0 if passed else 1)
