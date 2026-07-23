"""Proves detect.py --all - the one-command morning verdict (issue 020).

The claim: `python detect.py --all` scores every fleet in ALERT mode against its
stored bar, prints one combined block anyone can read, appends the same block to
'RESULTS - Alert Log.md', and - the part this file exists to pin - a failure in
ONE fleet reports and continues instead of killing the whole run. The scheduled
task will lean on that: a morning where Starlink's file is corrupt must still
deliver the OneWeb/Intelsat/SES verdicts.

Everything here runs on fakes - no archive, no network, no real baselines.

  python _test_all.py
"""
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
    return ok


# --------------------------------------------------------------------- fixtures

def row(norad, gap, cut=10.0, falling=False, dq=False, epoch=1.0):
    """One synthetic scored object, shaped like analyze()'s output rows."""
    flagged = gap > cut and not dq
    verdict = ("DATA QUALITY FLAG (physically implausible)" if dq
               else detect.FALLING_SUSPECT if (flagged and falling)
               else detect.SUSPECT if flagged
               else "agrees")
    return {"norad": norad, "gap_km": gap, "band_cut_km": cut, "flagged": flagged,
            "falling": falling, "verdict": verdict,
            "sup_epoch": epoch, "gp_epoch": epoch}


def result(rows):
    return {"rows": rows, "bands": [], "skipped": None}


tmp = Path(tempfile.mkdtemp())
older = tmp / "2026-07-23" / "0200Z"
newest = tmp / "2026-07-23" / "0800Z"
for d in (older, newest):
    d.mkdir(parents=True)

BASELINE = {"pct": 99.0, "min_km": 5.0, "cuts": {"station": {}, "falling": {}},
            "snapshots": ["2026-07-22/0200Z"]}

# Per (group, snapshot name) synthetic runs. Object 1001 is flagged in BOTH
# snapshots at different epochs -> two independent looks -> PERSISTENT. 1002 is
# flagged only in the newest. 1005 is falling and flagged; 1004 is data-quality.
FAKE_RUNS = {
    ("starlink", "0200Z"): result([row(1001, 50.0, epoch=1.0),
                                   row(1003, 2.0, epoch=1.0)]),
    ("starlink", "0800Z"): result([row(1001, 50.0, epoch=2.0),
                                   row(1002, 30.0, epoch=2.0),
                                   row(1003, 2.0, epoch=2.0),
                                   row(1004, 5000.0, dq=True, epoch=2.0),
                                   row(1005, 40.0, falling=True, epoch=2.0)]),
    ("intelsat", "0200Z"): result([row(2001, 1.0), row(2002, 2.0)]),
    ("intelsat", "0800Z"): result([row(2001, 1.0), row(2002, 2.0)]),
}


def fake_analyze(snap_dir, group, pct, min_km, max_km, allow_live=True, stored=None):
    if group == "oneweb":
        raise RuntimeError("simulated corrupt snapshot")
    run = FAKE_RUNS.get((group, snap_dir.name))
    if run is None:
        return None
    return {**run, "rows": [dict(r) for r in run["rows"]]}


def fake_load_baselines(group):
    return None if group == "ses" else dict(BASELINE)


real = (detect.analyze, detect.load_baselines, detect.snapshot_dirs)
detect.analyze = fake_analyze
detect.load_baselines = fake_load_baselines
detect.snapshot_dirs = lambda: [older, newest]

log = tmp / "RESULTS - Alert Log.md"
passed = True

try:
    print("\n  one broken fleet must not kill the run\n")
    code = detect.run_all(groups=["starlink", "oneweb", "intelsat", "ses"],
                          log_path=log)
    passed &= check("exit code 0 - three of four fleets were still scored", code, 0)

    text = log.read_text(encoding="utf-8")
    passed &= check("log got the snapshot heading",
                    bool(re.search(r"^## 2026-07-23/0800Z\s*$", text, re.M)), True)
    star = next(ln for ln in text.splitlines() if ln.startswith("- **starlink**"))
    passed &= check("starlink: 2 over the bar (falling and DQ not among them)",
                    "2 over the bar of 5 scored" in star, True)
    passed &= check("starlink: exactly 1 persistent (two independent looks)",
                    "1 persistent" in star, True)
    passed &= check("starlink: deorbiting and data-quality counted separately",
                    "(1 more among deorbiting hardware, 1 data-quality)" in star, True)
    passed &= check("starlink: top suspect named with its ratio",
                    "top: 1001 at 50.0 km, 5.0x its bar" in star, True)
    oneweb = next(ln for ln in text.splitlines() if ln.startswith("- **oneweb**"))
    passed &= check("oneweb: failure reported in its line, run continued",
                    "FAILED" in oneweb and "simulated corrupt snapshot" in oneweb, True)
    passed &= check("intelsat: zero over the bar reads as quiet",
                    any(ln.startswith("- **intelsat**") and "quiet" in ln
                        for ln in text.splitlines()), True)
    passed &= check("ses: no stored baseline reported, not silently dropped",
                    any(ln.startswith("- **ses**") and "baseline" in ln
                        for ln in text.splitlines()), True)

    print("\n  the log is a ledger - same snapshot never appended twice\n")
    detect.run_all(groups=["starlink"], log_path=log)
    text = log.read_text(encoding="utf-8")
    passed &= check("second run, same snapshot -> still exactly one heading",
                    len(re.findall(r"^## 2026-07-23/0800Z\s*$", text, re.M)), 1)

    print("\n  every fleet failing is a failed run\n")
    code = detect.run_all(groups=["oneweb"], log_path=tmp / "other.md")
    passed &= check("all fleets FAILED -> nonzero exit code", code, 1)
finally:
    detect.analyze, detect.load_baselines, detect.snapshot_dirs = real

print()
sys.exit(0 if passed else 1)
