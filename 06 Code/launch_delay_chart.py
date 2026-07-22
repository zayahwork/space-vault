"""
launch_delay_chart.py - the one picture for publishing the launch-delay finding.

Reuses launch_id_delay.py's fetch and binning so the chart can never disagree
with the numbers we quote - same data, same code path, drawn instead of printed.

Two panels, one message:
  left   median days from launch to first public orbit, per year - the 4x climb
  right  the 2026 rideshare tail - Transporter-17 at 12.62 days, still "OBJECT A"

Credits CelesTrak on the image itself, not just in the caption, per the
sequencing rule in [[Publish - Launch Delay Finding]]: the data is Kelso's and
the credit travels with the picture wherever it gets reposted.

Usage:  python launch_delay_chart.py          # writes output/launch_delay.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from launch_id_delay import DAYS, INTDES, NAME, by_year, fetch_rows, unidentified

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output", "launch_delay.png")


def main():
    rows = fetch_rows()
    per_year = {y: v for y, v in by_year(rows).items() if y >= "2019"}
    years = sorted(per_year)
    medians = [per_year[y][1] for y in years]
    counts = [per_year[y][0] for y in years]

    current = max(years)
    stragglers = sorted(unidentified(rows, current), key=lambda r: -r[DAYS])[:8]

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(12, 5.5), gridspec_kw={"width_ratios": [3, 2]})

    # Left: the climb. Bars, annotated, no drama needed - the shape says it.
    bars = ax.bar(years, medians, color="#2b6cb0")
    bars[0].set_color("#718096")   # 2019 baseline in grey
    for x, m, n in zip(years, medians, counts):
        ax.text(x, m + 0.05, f"{m:.2f}", ha="center", fontsize=10, weight="bold")
        ax.text(x, -0.22, f"n={n}", ha="center", fontsize=8, color="#718096")
    ax.set_title(
        f"Median days from launch to first public orbit data\n"
        f"{medians[0]:.2f} d in 2019 → {medians[-1]:.2f} d in {current}  "
        f"({medians[-1]/medians[0]:.1f}×)",
        fontsize=13, weight="bold", loc="left")
    ax.set_ylabel("days (median)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(y=0.15)

    # Right: the tail. Where the median hides the real pain.
    names = [f"{r[NAME][:24]}  ({r[INTDES]})" for r in stragglers][::-1]
    days = [r[DAYS] for r in stragglers][::-1]
    ax2.barh(names, days, color="#c05621")
    for i, d in enumerate(days):
        ax2.text(d + 0.1, i, f"{d:.1f} d", va="center", fontsize=9)
    ax2.set_title(
        f"Still unidentified in {current}\n(placeholder name or unattributed)",
        fontsize=11, weight="bold", loc="left")
    ax2.set_xlabel("days to first orbit data")
    ax2.tick_params(axis="y", labelsize=8)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.margins(x=0.15)

    fig.text(0.99, 0.01,
             "data: CelesTrak “Launch Until First GP Data” (T.S. Kelso) "
             "· analysis: launch_id_delay.py, free public data",
             ha="right", fontsize=8, color="#718096")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
