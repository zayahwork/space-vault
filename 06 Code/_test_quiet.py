"""Proves quiet.py's cadence judgement, on hand-built rhythms.

quiet.py carries the claim the insurer pitch is priced on - "a satellite in your book
stopped station-keeping" - and until now had no tests at all. It cannot be exercised
against the real archive for another week, which is exactly why the logic needs pinning
down here: by the time there IS enough data to run it on, a regression in this file
would be invisible.

judge() is pure - a list of (capture_jd, gap_km, over_bar) and a "now" - so every case
below is a rhythm whose right answer is known by construction.

  python _test_quiet.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quiet  # noqa: E402

T0 = 2461000.0


def hist(spike_days, quiet_gap=2.0, spike_gap=40.0):
    """A look history whose spikes land on the given days after T0."""
    return [(T0 + d, spike_gap, True) for d in spike_days]


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"          got  {got!r}\n          want {want!r}")
    return ok


passed = True
print("\n  refusing to judge without a rhythm\n")

# Two spikes is not a rhythm - one interval, and no way to tell a long gap from
# the object simply not having been watched for long.
for n in (0, 1, 2):
    r = quiet.judge(hist(list(range(n))), T0 + 30)
    passed &= check(f"{n} spike(s) -> no rhythm yet", r["status"], "no rhythm yet")

r = quiet.judge(hist([0, 5, 10]), T0 + 12)
passed &= check("3 spikes -> now it will judge", r["status"] != "no rhythm yet", True)

print("\n  reading the rhythm\n")

# Spikes every 5 days, last one 6 days ago. Well inside 2.5x - still on rhythm.
r = quiet.judge(hist([0, 5, 10, 15]), T0 + 21)
passed &= check("regular 5d rhythm, silent 6d -> on rhythm", r["status"], "on rhythm")
passed &= check("  typical interval measured as 5d", r["typical_days"], 5.0)

# Same object, silent 15 days - that is 3x its own interval.
r = quiet.judge(hist([0, 5, 10, 15]), T0 + 30)
passed &= check("same object silent 15d -> WENT QUIET", r["status"], "WENT QUIET")
passed &= check("  and reports how long it has been silent", r["silent_days"], 15.0)

# The boundary is strictly greater-than: silence of exactly 2.5x is NOT quiet.
r = quiet.judge(hist([0, 5, 10, 15]), T0 + 15 + 12.5)
passed &= check("silence exactly 2.5x typical -> not yet quiet", r["status"], "on rhythm")
r = quiet.judge(hist([0, 5, 10, 15]), T0 + 15 + 12.6)
passed &= check("a fraction past 2.5x -> quiet", r["status"], "WENT QUIET")

# One irregular interval must not drag the verdict - that is why it is a median.
r = quiet.judge(hist([0, 5, 30, 35, 40]), T0 + 46)
passed &= check("one long outlier interval -> median holds at 5d",
                r["typical_days"], 5.0)
passed &= check("  so a 6d silence is still on rhythm", r["status"], "on rhythm")

print("\n  the degenerate rhythm (guards a divide-by-almost-zero)\n")

# Three spikes at the SAME instant is a typical interval of zero. Every silence is
# then infinitely many times the interval, so a healthy satellite would be reported
# as failed. This can happen for real: several snapshots in one archiving burst.
r = quiet.judge(hist([0, 0, 0]), T0 + 0.3)
passed &= check("zero-length typical interval -> refuses, not WENT QUIET",
                r["status"] == "WENT QUIET", False)

# Spikes clustered inside one day, then a normal overnight gap. The object is fine;
# the archive just sampled it in a burst.
r = quiet.judge(hist([0, 0.1, 0.2]), T0 + 1.0)
passed &= check("spikes clustered in one burst -> not called quiet overnight",
                r["status"] == "WENT QUIET", False)

print()
print("  all passed" if passed else "  SOMETHING FAILED")
sys.exit(0 if passed else 1)
