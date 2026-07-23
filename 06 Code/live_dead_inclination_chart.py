"""Issue 027: the one-picture "live vs dead satellite" chart for the broker.

Overlays ~60 days of inclination history for one healthy, actively station-kept
GEO satellite against one abandoned one, both from Space-Track GP_HISTORY and
both classified by McDowell's geotab:

  INTELSAT 10-02  (NORAD 28358)  geotab GEO/S   - alive, N-S station-kept at 1W
  INTELSAT 601    (NORAD 21765)  geotab GEO/ID  - abandoned 1990s bird, plane
                                                  fallen over to ~13.4 deg

The point a non-technical reader should get in one glance: the live satellite's
orbit plane is being actively pinned flat (inclination held near zero); the dead
one stopped fighting and gravity tipped its plane over. Nothing subtle - the
separation is ~200x.

Writes:
  output/live_dead_inclination_<end>.csv   the plotted data, reproducible
  output/live_dead_inclination.png         the figure

The window is pinned (not "last 60 days from today") so the cached Space-Track
pull and the figure stay reproducible run-to-run.

Usage: python live_dead_inclination_chart.py
"""
import csv
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "groundtruth"))
import gt_sources as gt  # noqa: E402  (needs the path shim above)

START, END = "2026-05-24", "2026-07-23"          # ~60 days
LIVE = ("28358", "INTELSAT 10-02", "GEO/S")
DEAD = ("21765", "INTELSAT 601", "GEO/ID")

# dataviz reference palette, categorical slots 1 + 2
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED = "#1a1a19", "#6b6a63"


def pull(norad):
    rows = gt.history(norad, START, END)
    t = [datetime.fromisoformat(r["epoch"]) for r in rows]
    inc = [r["inc"] for r in rows]
    return t, inc


def main():
    t_live, inc_live = pull(LIVE[0])
    t_dead, inc_dead = pull(DEAD[0])

    # Feedback loop: the chart's claim, asserted before it is drawn.
    assert len(inc_live) >= 20, f"live: only {len(inc_live)} epochs"
    assert len(inc_dead) >= 20, f"dead: only {len(inc_dead)} epochs"
    assert max(inc_live) < 0.5, f"live not flat: max {max(inc_live)}"
    assert min(inc_dead) > 10.0, f"dead not tipped: min {min(inc_dead)}"
    print(f"live {LIVE[1]}: {len(inc_live)} epochs, "
          f"inc {min(inc_live):.3f}-{max(inc_live):.3f} deg")
    print(f"dead {DEAD[1]}: {len(inc_dead)} epochs, "
          f"inc {min(inc_dead):.3f}-{max(inc_dead):.3f} deg")

    out = HERE / "output"
    out.mkdir(exist_ok=True)
    data_csv = out / f"live_dead_inclination_{END}.csv"
    with open(data_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["norad", "object", "geotab_class", "epoch", "inclination_deg"])
        for (norad, name, cls), ts, incs in (
                (LIVE, t_live, inc_live), (DEAD, t_dead, inc_dead)):
            for ts_i, inc_i in zip(ts, incs):
                w.writerow([norad, name, cls, ts_i.isoformat(), f"{inc_i:.4f}"])
    print(f"wrote {data_csv.name} ({len(inc_live) + len(inc_dead)} rows)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=150)
    ax.plot(t_dead, inc_dead, color=ORANGE, lw=2,
            label=f"{DEAD[1]} — abandoned (NORAD {DEAD[0]})")
    ax.plot(t_live, inc_live, color=BLUE, lw=2,
            label=f"{LIVE[1]} — alive (NORAD {LIVE[0]})")

    ax.annotate("DEAD: nobody is steering.\n"
                "Gravity has tipped its orbit plane 13° over,\n"
                "rising ~1° every year since the 1990s.",
                xy=(t_dead[len(t_dead) // 2], inc_dead[len(inc_dead) // 2]),
                xytext=(0, -58), textcoords="offset points",
                ha="center", fontsize=9.5, color=INK)
    ax.annotate("ALIVE: thrusters pin the plane flat, ~0°.\n"
                "The moment they stop, this line starts climbing.",
                xy=(t_live[len(t_live) // 2], inc_live[len(inc_live) // 2]),
                xytext=(0, 14), textcoords="offset points",
                ha="center", fontsize=9.5, color=INK)

    ax.set_title("A live satellite holds its orbit flat. A dead one lets it fall over.",
                 fontsize=13, color=INK, pad=12)
    ax.set_ylabel("orbit tilt (inclination, degrees)", color=MUTED)
    ax.set_ylim(-0.8, 16)
    ax.legend(loc="center right", frameon=False, fontsize=9.5)
    ax.grid(axis="y", color="#e6e5df", lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.text(0.99, 0.01,
             "60 days of US Space Force catalog data (Space-Track GP_HISTORY), "
             f"{START} to {END}. Status per McDowell geotab: GEO/S vs GEO/ID.",
             ha="right", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    png = out / "live_dead_inclination.png"
    fig.savefig(png, facecolor="white")
    print(f"wrote {png.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
