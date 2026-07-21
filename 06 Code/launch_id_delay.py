"""
launch_id_delay.py — how long does a newly-launched object take to get its first orbit?

Pulls CelesTrak's public "Launch Until First GP Data" table and measures the trend.
This is the analysis behind the numbers in the Kelso reply — anything we claimed in
that email must stay reproducible by running this.

Headline finding (2026-07-21): the MEDIAN delay has more than quadrupled since 2019,
rising every year since 2021. Rideshares are the tail — Transporter-17 took 12.62 days,
the worst of 156 launches in 2026, and is still catalogued as "OBJECT A / TBD".

Usage:  python launch_id_delay.py
Needs:  requests  (no API key — this page is free and public)
"""

import html
import re
import statistics
import sys
from collections import defaultdict

import requests

URL = "https://celestrak.org/satcat/first-gp-by-launch.php"

# Columns in the table, in order. Index 7 is the one we care about.
INTDES, NORAD, NAME, SOURCE, LAUNCH, SITE, FIRST_EPOCH, DAYS = range(8)


def fetch_rows(url=URL):
    """Return the table as a list of cell-lists, one per launch."""
    page = requests.get(url, timeout=90)
    page.raise_for_status()

    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page.text, re.S):
        cells = [
            html.unescape(re.sub("<[^>]+>", "", c)).strip()
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        ]
        # Real data rows start with an international designator like "2026-156".
        if len(cells) < 8 or not re.match(r"^20\d\d-", cells[INTDES]):
            continue
        try:
            cells[DAYS] = float(cells[DAYS])
        except ValueError:
            continue  # a few historic rows have no delay recorded
        rows.append(cells)
    return rows


def by_year(rows, name_filter=None):
    """Median/max delay per launch year, optionally filtered to one operator."""
    buckets = defaultdict(list)
    for r in rows:
        if name_filter and name_filter.upper() not in r[NAME].upper():
            continue
        buckets[r[INTDES][:4]].append(r[DAYS])
    return {
        year: (len(v), statistics.median(v), max(v))
        for year, v in sorted(buckets.items())
    }


def unidentified(rows, year):
    """Objects still carrying a placeholder name or an unattributed source."""
    return [
        r for r in rows
        if r[INTDES].startswith(year)
        and ("OBJECT" in r[NAME].upper() or r[SOURCE] == "TBD")
    ]


def main():
    rows = fetch_rows()
    print(f"{len(rows)} launches in the table\n")

    print("Median days from launch to first GP data")
    print(f"{'year':<6} {'all launches':<30} {'Starlink only':<30}")
    everything, starlink = by_year(rows), by_year(rows, "STARLINK")
    for year in sorted(everything):
        if year < "2019":
            continue
        n, med, mx = everything[year]
        line = f"n={n:<4} median {med:5.2f}  max {mx:7.2f}"
        if year in starlink:
            sn, smed, smx = starlink[year]
            line += f"   n={sn:<4} median {smed:5.2f}  max {smx:6.2f}"
        print(f"{year:<6} {line}")

    # The rideshare tail — Kelso's "identified for months (some never)" case.
    current = max(r[INTDES][:4] for r in rows)
    stragglers = unidentified(rows, current)
    print(f"\nStill unidentified or unattributed in {current}: {len(stragglers)}")
    for r in sorted(stragglers, key=lambda r: -r[DAYS]):
        print(
            f"  {r[INTDES]:<9} {r[NORAD]:<7} {r[NAME][:32]:<32} "
            f"src={r[SOURCE]:<4} launched {r[LAUNCH]}  {r[DAYS]:6.2f} d"
        )

    # The 5-digit catalog is overflowing — worth watching, breaks legacy TLE software.
    six_digit = [r for r in rows if len(r[NORAD]) > 5]
    if six_digit:
        print(f"\n6-digit NORAD catalog numbers now in the table: {len(six_digit)}")
        for r in six_digit[:5]:
            print(f"  {r[NORAD]}  {r[NAME][:40]}  ({r[INTDES]})")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        sys.exit(f"couldn't reach CelesTrak: {exc}")
