"""Proves the persistence filter works, without waiting for the archive to grow.

The live archive can't exercise this yet - only one snapshot has a public catalog
saved beside it, so there is nothing to be persistent ACROSS. These cases feed the
two functions hand-built histories where the right answer is known by construction,
including the one that matters most: a candidate that looks corroborated but isn't,
because both element sets sat still between snapshots.

  python _test_detect.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402


def look(norad, sup, gp, gap, verdict="MANEUVER SUSPECT"):
    return {"norad": norad, "sup_epoch": sup, "gp_epoch": gp, "gap_km": gap,
            "verdict": verdict, "flagged": verdict == "MANEUVER SUSPECT",
            "band_cut_km": 20.0, "band_median_km": 4.0, "gp_age_h": 12.0}


def run(rows_per_snapshot, min_looks=2):
    runs = [{"rows": rows, "dir": None} for rows in rows_per_snapshot]
    looks = detect.independent_looks(runs)
    newest = rows_per_snapshot[-1]
    detect.apply_persistence(newest, looks, min_looks)
    return {r["norad"]: r for r in newest}, looks


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
    return ok


passed = True

# 1. Flagged three snapshots running, and the operator refreshed its orbit each time.
#    Three real looks, three flags - this is what a maneuver the catalog hasn't caught
#    up on should look like.
rows, looks = run([[look(1, sup=100.0, gp=99.0, gap=40)],
                   [look(1, sup=100.3, gp=99.0, gap=38)],
                   [look(1, sup=100.6, gp=99.0, gap=41)]])
passed &= check("real maneuver -> PERSISTENT SUSPECT",
                rows[1]["verdict"], "PERSISTENT SUSPECT")
passed &= check("  counted 3 independent looks", looks[1]["looks"], 3)

# 2. THE TRAP. Flagged three snapshots running, but neither element set ever changed -
#    CelesTrak simply republished the same file. That is one measurement seen three
#    times, and it must not be allowed to corroborate itself.
rows, looks = run([[look(2, sup=100.0, gp=99.0, gap=40)],
                   [look(2, sup=100.0, gp=99.0, gap=40)],
                   [look(2, sup=100.0, gp=99.0, gap=40)]])
passed &= check("republished identical data -> only 1 look", looks[2]["looks"], 1)
passed &= check("  and so cannot be called persistent",
                rows[2]["verdict"].startswith("SUSPECT (single look"), True)

# 3. A one-off. Clean across two real looks, then a big gap appears. Might be a burn
#    that just happened, might be a bad fit - the next snapshot decides, and until
#    then it does not get to sit beside the corroborated ones.
rows, _ = run([[look(3, sup=100.0, gp=99.0, gap=3, verdict="agrees")],
               [look(3, sup=100.3, gp=99.0, gap=3, verdict="agrees")],
               [look(3, sup=100.6, gp=99.0, gap=45)]])
passed &= check("first-look spike -> unconfirmed, not persistent",
                rows[3]["verdict"], "SUSPECT (new this look - unconfirmed)")

# 4. Cleared. Flagged twice, then the catalog caught up and the gap collapsed. Still
#    two flags on the record, but it is not a current candidate.
rows, looks = run([[look(4, sup=100.0, gp=99.0, gap=40)],
                   [look(4, sup=100.3, gp=99.0, gap=40)],
                   [look(4, sup=100.6, gp=100.5, gap=2, verdict="agrees")]])
passed &= check("catalog caught up -> not flagged now", looks[4]["flagged_now"], False)
passed &= check("  but the two earlier flags are kept", looks[4]["flags"], 2)

# 5. Only the catalog moved. Still a new comparison, so it still counts as a look.
_, looks = run([[look(5, sup=100.0, gp=99.0, gap=40)],
                [look(5, sup=100.0, gp=99.4, gap=40)]])
passed &= check("catalog-only refresh counts as an independent look",
                looks[5]["looks"], 2)

# 6. An object that only appears in the newest snapshot has nothing to compare against.
rows, _ = run([[look(6, sup=100.0, gp=99.0, gap=40)]])
passed &= check("single snapshot -> says so instead of implying support",
                rows[6]["verdict"].startswith("SUSPECT (single look"), True)

print("\n  all passed" if passed else "\n  FAILURES ABOVE")
sys.exit(0 if passed else 1)
