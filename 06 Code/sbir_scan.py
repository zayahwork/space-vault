"""
sbir_scan.py - what's actually open on the DoD SBIR portal today, without
clicking through DSIP.

Hits the same public API the topics portal uses, keeps everything that is
pre-release or open, and flags the ones that touch our field. Writes a dated
markdown report into the vault so the answer is on paper, not in a browser tab.

The column that matters is TPOC-Q: during pre-release you may email the topic
author directly. Once the topic opens, that door shuts and questions go through
the anonymous public Q&A instead.

Usage:
  python sbir_scan.py                 # space-relevant topics
  python sbir_scan.py --all           # every open/pre-release topic
  python sbir_scan.py --grep laser    # your own keyword
"""

import argparse
import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

API = "https://www.dodsbirsttr.mil/topics/api/public/topics/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.dodsbirsttr.mil/topics-app/",
}
PRE_RELEASE, OPEN = 591, 592
SPACE = re.compile(
    r"space|orbit|satellit|domain awareness|\bsda\b|maneuver|custody|astro|"
    r"debris|collision|catalog|constellation|gps|pnt|launch",
    re.I,
)
REPORT = Path(r"C:\Space\02 Task Guides")


def fetch(size=300):
    param = json.dumps({
        "searchText": "", "components": None, "programYear": None,
        "cycleNames": [], "topicReleaseStatus": [PRE_RELEASE, OPEN],
        "modernizationPriorities": [], "sortBy": "finalTopicCode,asc",
        "technologyAreaIds": [], "component": None, "program": None,
    })
    url = f"{API}?searchParam={urllib.parse.quote(param)}&size={size}&page=0"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def day(ms):
    if not ms:
        return "-"
    return datetime.datetime.utcfromtimestamp(ms / 1000).strftime("%Y-%m-%d")


WATCH_LOG = Path(__file__).resolve().parent / "sbir_watch.jsonl"
ALERT = REPORT / "🚨 SBIR ALERT - un-park SAM.gov.md"
# The two conditions the founder set on 2026-07-21 for un-parking SAM.gov.
UNPARK = re.compile(r"space domain awareness|\bSDA\b|maneuver|space situational|"
                    r"orbit determination|satellite track|catalog custody", re.I)


def watch():
    """Run unattended. Silent unless a topic appears that ends the SAM.gov park.

    SAM.gov registration was parked because there was nothing to apply for: 72 open
    topics, zero from USSF, zero on our field. Rather than re-check by hand forever,
    this runs weekly and only makes noise when that stops being true.
    """
    try:
        data = fetch()
    except Exception as exc:
        entry = {"date": datetime.date.today().isoformat(), "error": str(exc)[:200]}
        with WATCH_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
        print(f"  scan failed: {exc}")
        return 1

    hits = []
    for t in data["data"]:
        hay = f"{t.get('topicTitle','')} {t.get('topicCode','')}"
        if t.get("component", "").upper() in ("USSF", "SPACEWERX") or UNPARK.search(hay):
            hits.append({"code": t.get("topicCode"), "component": t.get("component"),
                         "title": t.get("topicTitle"), "status": t.get("topicStatus"),
                         "close": day(t.get("topicEndDate")),
                         "id": t.get("topicId", "")})

    entry = {"date": datetime.date.today().isoformat(), "total": data["total"],
             "hits": len(hits), "codes": [h["code"] for h in hits]}
    with WATCH_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    if not hits:
        print(f"  {data['total']} topics open, nothing for us. Park holds.")
        if ALERT.exists():
            ALERT.unlink()          # the previous alert is stale; don't cry wolf
        return 0

    REPORT.mkdir(parents=True, exist_ok=True)
    lines = [f"# 🚨 Un-park SAM.gov — {datetime.date.today()}", "",
             "A topic in our field is open. The condition the founder set on 2026-07-21",
             "has been met, so SAM.gov registration is no longer pointless paperwork.",
             "", "Registration takes 4–6 weeks. If a close date below is inside that,",
             "we cannot apply to *this* one — register anyway so we can apply to the next.", ""]
    for h in hits:
        lines += [f"## {h['code']} — {h['title']}",
                  f"- **{h['component']}** · {h['status']} · closes **{h['close']}**",
                  f"- https://www.dodsbirsttr.mil/topics-app/details/{h['id']}", ""]
    ALERT.write_text("\n".join(lines), encoding="utf-8")
    print(f"  🚨 {len(hits)} matching topic(s). Alert written to {ALERT}")
    return 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--grep", default=None)
    ap.add_argument("--no-report", action="store_true")
    ap.add_argument("--watch", action="store_true",
                    help="unattended: log the scan, and shout only if the park ends")
    args = ap.parse_args()

    if args.watch:
        return watch()

    pat = re.compile(args.grep, re.I) if args.grep else SPACE
    data = fetch()
    topics = data["data"]
    today = datetime.date.today()

    rows = []
    for t in topics:
        hay = f"{t['topicTitle']} {t.get('topicCode','')} {t.get('component','')}"
        if not args.all and not pat.search(hay):
            continue
        rows.append({
            "code": t.get("topicCode", "?"),
            "component": t.get("component", "?"),
            "status": t.get("topicStatus", "?"),
            "title": t.get("topicTitle", "").strip(),
            "open": day(t.get("topicStartDate")),
            "close": day(t.get("topicEndDate")),
            "tpoc_until": day(t.get("topicQATpocEndDate")),
            "managers": [
                f"{m.get('name')} <{m.get('email')}>"
                for m in (t.get("topicManagers") or [])
                if t.get("showTpoc") and m.get("emailDisplay") == "Y"
            ],
            "id": t.get("topicId", ""),
        })

    print(f"\n  {data['total']} topics pre-release or open · "
          f"{len(rows)} match{'' if args.all else ' our field'}\n")
    for r in rows:
        print(f"  {r['code']:<20} {r['component']:<7} {r['status']:<12} "
              f"opens {r['open']}  closes {r['close']}")
        print(f"     {r['title'][:92]}")
        if r["status"] == "Pre-Release" and r["managers"]:
            print(f"     ✉ topic author reachable until {r['tpoc_until']}: "
                  f"{'; '.join(r['managers'])}")
        print()

    if args.no_report or not rows:
        return 0

    REPORT.mkdir(parents=True, exist_ok=True)
    out = REPORT / f"SBIR Scan - {today}.md"
    lines = [
        f"# 🏛️ SBIR scan — {today}",
        "",
        f"Pulled live from the DSIP public topic API by `06 Code/sbir_scan.py`. "
        f"{data['total']} topics were pre-release or open; {len(rows)} touch our field.",
        "",
        "> [!warning] Pre-release is the only window where you can email the topic author.",
        "> Once a topic opens, questions go through the anonymous public Q&A instead.",
        "",
    ]
    for r in rows:
        lines += [
            f"## {r['code']} — {r['title']}",
            f"- **{r['component']}** · {r['status']} · opens **{r['open']}** · "
            f"closes **{r['close']}**",
            f"- Topic page: https://www.dodsbirsttr.mil/topics-app/details/{r['id']}",
        ]
        if r["managers"]:
            lines.append(f"- Topic author (reachable until {r['tpoc_until']}): "
                         f"{'; '.join(r['managers'])}")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  report -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
