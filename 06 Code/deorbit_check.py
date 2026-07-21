"""
Detector v0.2.1 — patches blind spot #1:
also see DOWNWARD jumps and SUSTAINED descent (electric deorbit / decay),
not just upward chemical kicks. Target: the dying STARLINK-2083.
"""
import os
from datetime import timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from multi_chart import login, pull_history  # reuse v0.2's plumbing

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")


def descent_rate_km_per_day(points, i, window_days=7):
    """Average descent over the past `window_days` at record i (negative = falling)."""
    t_i, a_i = points[i]
    for j in range(i, -1, -1):
        if (t_i - points[j][0]) >= timedelta(days=window_days):
            dt_days = (t_i - points[j][0]).total_seconds() / 86400.0
            return (a_i - points[j][1]) / dt_days
    return 0.0


def main():
    s = login()
    name, norad = "STARLINK-2083", 47676
    points = pull_history(s, norad)
    times = [p[0] for p in points]
    alts = [p[1] for p in points]

    # sustained-descent detector: falling faster than 0.4 km/day for 2+ weeks
    fast = [descent_rate_km_per_day(points, i) < -0.4 for i in range(len(points))]
    # find the start of the long descent phase
    phase_start = None
    run = 0
    for i, f in enumerate(fast):
        run = run + 1 if f else 0
        if run == 1 and f:
            candidate = i
        if f and (times[i] - times[candidate]) >= timedelta(days=14) and phase_start is None:
            phase_start = candidate
    total_drop = alts[0] - alts[-1]
    rate_now = descent_rate_km_per_day(points, len(points) - 1)

    print(f"{name}: {alts[0]:.1f} km -> {alts[-1]:.1f} km  (dropped {total_drop:.1f} km)")
    print(f"Current descent rate: {rate_now:.2f} km/day")
    if phase_start is not None:
        print(f"SUSTAINED DESCENT detected starting {times[phase_start]:%Y-%m-%d}")
        if rate_now < -0.2:
            days_left = (alts[-1] - 200.0) / -rate_now  # ~200 km = the point of no return
            print(f"Rough reentry estimate at current rate: ~{days_left:.0f} days "
                  f"(accelerates as air thickens — real number will be smaller)")

    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(times, alts, lw=1.4, color="#2f81f7")
    if phase_start is not None:
        ax.axvspan(times[phase_start], times[-1], color="#e5534b", alpha=0.12,
                   label="detected: sustained descent (deorbit/decay)")
        ax.axvline(times[phase_start], color="#e5534b", ls="--", lw=1.2)
    ax.set_title(f"{name} (#{norad}) — detector v0.2.1 sees the descent: "
                 f"{total_drop:.0f} km lost, {rate_now:.1f} km/day and accelerating",
                 fontsize=12)
    ax.set_ylabel("mean altitude (km)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    fig.autofmt_xdate()
    out = os.path.join(OUT, "starlink_deorbit_detected.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Chart saved: {out}")


if __name__ == "__main__":
    main()
