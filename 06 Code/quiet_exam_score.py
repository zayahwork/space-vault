"""quiet_exam_score.py — grade quiet.py's Jul 29 verdicts against the pre-registered exam.

The exam (`quiet_exam.csv`, `in_exam_set == yes`) was pre-registered on 2026-07-22, before
quiet.py could produce any cadence verdict. This script joins that pre-registration to a real
run and prints the false-alarm rate, the (expected-empty) catch rate, and gate coverage — each
WITH its denominator, because "0 of 4" and "0 of 55" are different claims.

It does not re-run quiet.py (that needs the tech-lane detect.py + the archive). Feed it
quiet.py's own output:

    cd "C:/Space/06 Code"
    python quiet.py --group starlink > quiet_starlink.txt
    python quiet.py --group oneweb  > quiet_oneweb.txt
    python quiet_exam_score.py quiet_starlink.txt quiet_oneweb.txt

If quiet.py grows a machine-readable (--json) mode, prefer that; this parser only needs each
line to contain a NORAD id and one of the three verdict strings, so it is deliberately loose.

Pre-registered expectation (see '03 Reference/Quiet Detector Exam - pre-registered.md'):
every exam object is documented Active, so every one should return 'on rhythm'. Any 'WENT
QUIET' among them is a FALSE ALARM — the _test_quiet.py failure mode this exam exists to catch
on real data. Catch rate is expected to be not-measurable (no known-dead object has spikes).
"""
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAM = HERE / "quiet_exam.csv"

VERDICTS = ["WENT QUIET", "no rhythm yet", "on rhythm"]   # order matters: longest/first match wins


def load_exam():
    with EXAM.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["in_exam_set"] == "yes"]
    return {r["norad"]: r for r in rows}


def parse_verdicts(paths):
    """Pull (norad -> verdict) from quiet.py console output. Loose by design."""
    got = {}
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"\b(\d{5,6})\b", line)
            if not m:
                continue
            for v in VERDICTS:
                if v in line:
                    got[m.group(1)] = v
                    break
    return got


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    exam = load_exam()
    got = parse_verdicts(sys.argv[1:])

    healthy = {n: r for n, r in exam.items() if r["status"] in ("active", "active-stationkept")}
    dead = {n: r for n, r in exam.items() if "abandoned" in r["status"] or "dead" in r["status"]}

    graded_healthy = {n: got[n] for n in healthy if n in got}
    graded_dead = {n: got[n] for n in dead if n in got}
    false_alarms = [n for n, v in graded_healthy.items() if v == "WENT QUIET"]
    catches = [n for n, v in graded_dead.items() if v == "WENT QUIET"]

    print(f"\nExam set: {len(exam)} objects "
          f"({len(healthy)} documented-healthy, {len(dead)} documented-dead)")
    print(f"Verdicts parsed from run: {len(got)}")
    print(f"Exam objects that reached a verdict (gate coverage): "
          f"{len(graded_healthy) + len(graded_dead)} of {len(exam)}")

    print("\n--- FALSE-ALARM RATE (the number we can actually report) ---")
    if graded_healthy:
        print(f"  WENT QUIET among documented-healthy: {len(false_alarms)} of {len(graded_healthy)} "
              f"= {100*len(false_alarms)/len(graded_healthy):.1f}%")
        if false_alarms:
            print(f"  ⚠️  FALSE ALARMS — healthy satellites declared quiet: {sorted(false_alarms)}")
            print("      This is the _test_quiet.py regression. Do NOT show a broker unscored.")
        else:
            print("  ✅ zero false alarms on documented-healthy objects")
    else:
        print("  no documented-healthy exam objects reached a verdict — report gate coverage")

    print("\n--- CATCH RATE (expected: not measurable) ---")
    if graded_dead:
        print(f"  WENT QUIET among documented-dead: {len(catches)} of {len(graded_dead)}")
    else:
        print("  denominator = 0 — NOT MEASURABLE. Report as such, never as 0%.")
        print("  (structural: MIN_SPIKES=3 needs station-keeping evidence a dead object never gives)")

    print()


if __name__ == "__main__":
    main()
