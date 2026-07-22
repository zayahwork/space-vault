"""
daily_alert.py - score every new snapshot in ALERT mode and append the verdict.

WHY THIS EXISTS
The archiver banks a snapshot every 6 hours whether anyone is at the keyboard or
not. Until now, turning those snapshots into "did anything move today?" required a
human to remember to run detect.py. This closes the loop: a scheduled task runs
this script shortly after each archive cycle, it scores whatever snapshots have
not been scored yet, and appends one section per snapshot to the alert log in the
vault. The demo week builds itself.

HOW IT DECIDES WHAT IS NEW
The log itself is the ledger. Before scoring, this reads 'RESULTS - Alert Log.md'
and skips any snapshot that already has a heading there. No separate state file:
state files fall out of sync with the thing they describe, drift between git
worktrees, and die in clones. The log cannot disagree with itself.

WHAT IT RUNS
Alert mode only - each group is judged against its stored per-group baseline
(baselines_<group>.json), a bar learned from PAST snapshots and held fixed, so
"nothing happened" is a possible answer and gets logged as exactly that. Groups
without a stored baseline are skipped; learn one first:

  python detect.py --group <g> --learn-baseline --pct 99

Snapshots with no public catalog at or before them cannot be scored honestly
(see load_gp in detect.py on borrowed catalogs) and are left out of the log
entirely - they are re-checked each run, which costs milliseconds, rather than
logged as noise.

Usage:
  python daily_alert.py             # score everything new, append to the log
  python daily_alert.py --dry-run   # show what would be appended, write nothing
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect  # noqa: E402

# The scheduled task's console is cp1252; a stray glyph must not kill an alert run.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
LOG = HERE.parent / "RESULTS - Alert Log.md"

LOG_HEADER = """\
---
status: written by a scheduled task - do not hand-edit entries, add notes below them
code: "06 Code/daily_alert.py (scheduled: Maneuver Alert, every 6h)"
---

# 🚨 Alert Log — every snapshot, judged against a fixed bar

Each entry below is one archive snapshot scored in **alert mode**: objects are flagged
only if their operator-vs-catalog gap exceeds a bar **learned from past snapshots and
held fixed** (see `baselines_<group>.json` for provenance). That means **zero is a real
answer** — a quiet line is the detector saying "nothing happened", not saying nothing.

*Jargon: "gap" = how far the operator's own orbit (SupGP) sits from the public catalog
(GP), in km. "bar" = the 99th-percentile gap for objects of the same catalog age and
regime, from the baseline file. "quiet" = nothing over the bar.*
"""


def scored_groups():
    """Every group that has earned an alert baseline. The file IS the opt-in."""
    return sorted(p.stem.replace("baselines_", "")
                  for p in HERE.glob("baselines_*.json"))


def already_logged():
    """Snapshot ids ('2026-07-22/0800Z') that already have a heading in the log."""
    if not LOG.exists():
        return set()
    text = LOG.read_text(encoding="utf-8")
    return set(re.findall(r"^## (\d{4}-\d{2}-\d{2}/\d{4}Z)", text, re.MULTILINE))


def snap_id(snap_dir):
    return f"{snap_dir.parent.name}/{snap_dir.name}"


def score_group(snap_dir, group):
    """One group, one snapshot, alert mode. Returns a log line, or None to skip."""
    stored = detect.load_baselines(group)
    if stored is None:
        return None
    run = detect.analyze(snap_dir, group, stored["pct"], stored["min_km"],
                         detect.MAX_PLAUSIBLE_KM, allow_live=False, stored=stored)
    if run is None:
        return f"- **{group}**: no SupGP file in this snapshot"
    if run["skipped"]:
        return "UNSCOREABLE"
    rows = run["rows"]
    suspects = sorted([r for r in rows if not r["falling"] and r.get("flagged")],
                      key=lambda r: r["gap_km"] / max(r["band_cut_km"], 1e-9),
                      reverse=True)
    descending = [r for r in rows if r["falling"] and r.get("flagged")]
    dq = sum(1 for r in rows if r["verdict"].startswith("DATA QUALITY"))
    base = (f"- **{group}**: {len(suspects)} over the bar of {len(rows)} scored"
            f" ({len(descending)} more among deorbiting hardware, {dq} data-quality)")
    if not suspects and not descending:
        return f"- **{group}**: 🔇 quiet — all {len(rows)} objects inside the stored bar"
    if suspects:
        top = suspects[0]
        base += (f" — top: {top['norad']} at {top['gap_km']:.1f} km, "
                 f"{top['gap_km'] / max(top['band_cut_km'], 1e-9):.1f}x its bar")
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    args = ap.parse_args()

    groups = scored_groups()
    if not groups:
        sys.exit("no baselines_<group>.json anywhere - nothing is opted into alerting")
    done = already_logged()

    entries = []
    for snap_dir in detect.snapshot_dirs():                    # oldest first
        sid = snap_id(snap_dir)
        if sid in done:
            continue
        lines, unscoreable = [], False
        for g in groups:
            line = score_group(snap_dir, g)
            if line == "UNSCOREABLE":
                unscoreable = True
                break
            if line:
                lines.append(line)
        if unscoreable or not lines:
            print(f"  {sid}  unscoreable (no catalog at or before it) - not logged")
            continue
        entries.append((sid, lines))
        print(f"  {sid}")
        for ln in lines:
            print(f"    {ln}")

    if not entries:
        print("  nothing new to score - log already covers every scoreable snapshot")
        return 0
    if args.dry_run:
        print(f"\n  dry run - {len(entries)} entr{'y' if len(entries)==1 else 'ies'} "
              f"NOT written to {LOG.name}")
        return 0

    text = LOG.read_text(encoding="utf-8") if LOG.exists() else LOG_HEADER
    for sid, lines in entries:
        text += f"\n## {sid}\n\n" + "\n".join(lines) + "\n"
    LOG.write_text(text, encoding="utf-8")
    print(f"\n  appended {len(entries)} entr{'y' if len(entries)==1 else 'ies'} "
          f"-> {LOG.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
