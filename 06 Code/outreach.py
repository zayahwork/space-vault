"""
outreach.py - the daily outreach batch, drafted and tracked.

Fifteen emails a day only works if writing them isn't the bottleneck. This pulls
the next N untouched targets, fills the right template for their segment, and
keeps the sent/replied ledger in one CSV so nobody gets emailed twice.

It does NOT send anything. No mail account is connected, and a bad send can't be
unsent - you paste, you eyeball, you send.

Usage:
  python outreach.py                      # today's 15 drafts
  python outreach.py -n 5 --segment insurer
  python outreach.py --sent 3 7 11        # log what actually went out
  python outreach.py --replied 7 --note "wants a call"
  python outreach.py --status             # the ledger
"""

import argparse
import csv
import datetime
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CSV_PATH = Path(__file__).resolve().parent / "outreach_targets.csv"
FIELDS = ["id", "segment", "company", "why_them", "contact_route", "email",
          "status", "sent_on", "notes"]

SIGN = """Zayah Nelson
425-409-8684"""

# One template per segment. All of them ask a question and sell nothing - the
# scoreboard is people describing their pain unprompted, not pitches delivered.
TEMPLATES = {
    "operator": (
        "how do you handle a neighbour that changes its behaviour?",
        """Hi,

I'm working on detecting when a satellite breaks its own routine - a maneuver, a
drift, anything off its normal pattern - using only public tracking data.

I'm trying to understand the operator side before I build any further. When
something near one of your satellites starts behaving differently, how do you
find out today, and how much of that is someone watching screens versus a tool
telling you?

Genuinely just trying to learn how this works in practice - not selling anything.
Fifteen minutes would help me a lot.

Thanks,"""),
    "insurer": (
        "question about how orbital behavior figures into space underwriting",
        """Hi,

I'm an ML engineer working on detecting satellite behavior - when objects
maneuver or act outside their normal pattern - from public tracking data.

I'm trying to understand the insurance side: when a LEO mission gets priced, how
much does the actual behavior of the objects around it factor in, and where does
that information come from today?

Would someone on your space team have 15 minutes for a couple of questions? Not
selling anything - genuinely trying to learn how underwriters see this.

Thanks,"""),
    "partner": (
        "public-data maneuver detection - comparing notes",
        """Hi,

I'm building maneuver detection and pattern-of-life from free public orbit data
(GP history / OMM), and I'd rather learn from people already doing this than
guess.

Two things I keep hitting: public GP data is smoothed around maneuvers by design,
and the labelled datasets available are partly simulated. How do you handle
either of those - or do you consider them solved?

Happy to share what I've measured, including where my own approach falls over.

Thanks,"""),
    "academic": (
        "question from someone working on maneuver detection from public data",
        """Hi,

I'm working on maneuver detection and pattern-of-life using only free public
orbit data, and I've run into a question your work speaks to directly.

[ONE specific question about their paper or dataset - replace this line. A
generic email to a researcher is a wasted email.]

I'd rather ask than assume. Thanks for any steer.

Thanks,"""),
    "gov": (
        "question about public orbit data availability",
        """Hi,

I'm building maneuver detection from free public orbit data and I'm trying to
understand where that data is heading - what's expected to stay public, and what
changes are planned.

Is there someone who handles questions like this? Happy to be pointed at a
document rather than take anyone's time.

Thanks,"""),
}


def load():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(rows):
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def draft(row):
    subject, body = TEMPLATES.get(row["segment"], TEMPLATES["operator"])
    to = row["email"] or f"(find a contact: {row['contact_route']})"
    return (
        f"{'─' * 74}\n"
        f"#{row['id']}  {row['company']}   [{row['segment']}]\n"
        f"why them : {row['why_them']}\n"
        f"to       : {to}\n"
        f"subject  : {subject}\n\n"
        f"{body}\n{SIGN}\n"
        + (f"\n⚠ {row['notes']}\n" if row["notes"] else "")
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=15, help="how many drafts today")
    ap.add_argument("--segment", default=None)
    ap.add_argument("--sent", nargs="+", default=None, metavar="ID")
    ap.add_argument("--replied", nargs="+", default=None, metavar="ID")
    ap.add_argument("--dead", nargs="+", default=None, metavar="ID")
    ap.add_argument("--note", default=None)
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    rows = load()
    today = datetime.date.today().isoformat()

    for flag, state in (("sent", "sent"), ("replied", "replied"), ("dead", "dead")):
        ids = getattr(args, flag)
        if not ids:
            continue
        for r in rows:
            if r["id"] in ids:
                r["status"] = state
                if state == "sent":
                    r["sent_on"] = today
                if args.note:
                    r["notes"] = (r["notes"] + " | " if r["notes"] else "") + args.note
                print(f"  #{r['id']:<3} {r['company']:<28} -> {state}")
        save(rows)
        return 0

    if args.status:
        counts = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print("\n  " + "  ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
        for r in rows:
            if r["status"] != "todo":
                print(f"  #{r['id']:<3} {r['status']:<8} {r['sent_on'] or '':<11} "
                      f"{r['company']:<28} {r['notes'][:40]}")
        print()
        return 0

    batch = [r for r in rows
             if r["status"] == "todo"
             and (not args.segment or r["segment"] == args.segment)][:args.n]
    if not batch:
        print("\n  nothing left in the list. add rows to outreach_targets.csv.\n")
        return 0

    print(f"\n  {len(batch)} drafts for {today}. Nothing is sent automatically.")
    print("  Find a real human at each contact route first - 'info@' converts at ~zero.")
    print("  Then: python outreach.py --sent " + " ".join(r["id"] for r in batch) + "\n")
    for r in batch:
        print(draft(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
