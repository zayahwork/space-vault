"""
payroll.py - the CTO actually managing the money.

THE QUESTION: "if we had $150,000, how would we pay our employees?"

THE HONEST ANSWER FIRST
The six notional salaries in team.json add up to $1,075,000 a year. $150,000 does
not pay that team. It does not pay ANY of them for a year. Pretending otherwise is
how startups die, so this tool refuses to pretend.

What $150,000 actually buys - and $150K is not a random number, it's the size of an
SBIR Phase I - is roughly SIX MONTHS of a small team working part-time. So we stop
thinking in salaries and start thinking in HOURS. Each person's salary becomes an
hourly rate (salary / 2080), and the budget buys a number of their hours. That is
also how a real Phase I budget is written, so the exercise isn't make-believe.

THE ALLOCATION RULE
Hours follow the phase we're actually in, not seniority and not fairness. Right now
the company's entire risk is "can we tell a maneuver from stale data" - so ML and
engineering get the hours, and marketing gets enough to keep talking to humans.
When the risk moves, the allocation moves.

Usage:
  python payroll.py                          # the plan
  python payroll.py --charge Sable 6 "age-binned detector v1"
  python payroll.py --report                 # spent vs remaining
  python payroll.py --reset 150000           # start a new budget
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
TEAM = json.loads((HERE / "team.json").read_text(encoding="utf-8"))["cast"]
BUDGET_FILE = HERE / "budget.json"

WORK_HOURS_YEAR = 2080          # 40h x 52w, the standard the government also uses
NONLABOR_SHARE = 0.15           # compute, data, conference travel, filing fees

# Hours bought per person for this phase. Chosen against the current risk, which is
# entirely "can we separate a maneuver from stale data" - not against seniority.
PHASE = "Phase I - prove maneuver-vs-stale on live public data (6 months)"
PLAN_HOURS = {
    "Sable": 400,   # owns the detector and the structure question
    "Rook": 350,    # archive, pipeline, anything that has to keep running
    "Tim": 300,     # prior art + verifying suspects against real maneuver records
    "Fitz": 150,    # adversarial checks; the reason we don't publish something wrong
    "Vega": 120,    # customer conversations, which is the only real scoreboard
    "Nova": 90,     # writing it down so a stranger can follow it
}


def hourly(name):
    return TEAM[name]["salary"] / WORK_HOURS_YEAR


def load_budget():
    if BUDGET_FILE.exists():
        return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    return None


def save_budget(b):
    BUDGET_FILE.write_text(json.dumps(b, indent=2), encoding="utf-8")


def new_budget(total):
    nonlabor = round(total * NONLABOR_SHARE, 2)
    return {
        "total": total,
        "phase": PHASE,
        "nonlabor_reserve": nonlabor,
        "labor_pool": round(total - nonlabor, 2),
        "plan_hours": dict(PLAN_HOURS),
        "ledger": [],
        "opened": date.today().isoformat(),
    }


def plan_table(b):
    print(f"\n  {b['phase']}")
    print(f"  budget ${b['total']:,.0f}   "
          f"non-labor reserve ${b['nonlabor_reserve']:,.0f} "
          f"({NONLABOR_SHARE:.0%}: compute, data, travel, filings)")
    print(f"  labor pool ${b['labor_pool']:,.0f}\n")

    print(f"  {'who':<7} {'role':<18} {'$/yr':>10} {'$/hr':>8} {'hours':>7} {'cost':>11}")
    total = 0.0
    for name, hours in b["plan_hours"].items():
        rate = hourly(name)
        cost = rate * hours
        total += cost
        print(f"  {TEAM[name].get('emoji','')} {name:<5} {TEAM[name]['role']:<18} "
              f"{TEAM[name]['salary']:>10,} {rate:>8.0f} {hours:>7} {cost:>11,.0f}")
    print(f"  {'CTO':<7} {'CTO':<18} {'—':>10} {'—':>8} {'—':>7} {0:>11,.0f}"
          "   founder, unpaid")
    pool = b["labor_pool"]
    # Nested same-type quotes inside an f-string need Python 3.12+, and the room's
    # venv is 3.11. Build the phrase first.
    gap = (f"OVER BY ${total - pool:,.0f}" if total > pool
           else f"${pool - total:,.0f} unallocated")
    print(f"\n  planned labor {total:>11,.0f}   of ${pool:,.0f} pool   ({gap})")

    year = sum(TEAM[n]["salary"] for n in b["plan_hours"])
    print(f"\n  reality check: these six at full salary cost ${year:,}/yr.")
    print(f"  ${b['total']:,.0f} buys {100*total/year:.0f}% of one team-year — "
          f"about {sum(b['plan_hours'].values())} hours total, "
          f"or {sum(b['plan_hours'].values())/6/26:.1f} h/person/week over 26 weeks.")
    return total


def report(b):
    spent = {}
    for e in b["ledger"]:
        spent[e["who"]] = spent.get(e["who"], 0.0) + e["hours"]
    plan_table(b)
    print(f"\n  {'who':<7} {'planned h':>10} {'used h':>8} {'left h':>8} {'$ used':>10}")
    total_used = 0.0
    for name, hours in b["plan_hours"].items():
        used = spent.get(name, 0.0)
        cost = used * hourly(name)
        total_used += cost
        bar = "█" * int(12 * min(used / hours, 1.0)) if hours else ""
        print(f"  {name:<7} {hours:>10} {used:>8.1f} {hours-used:>8.1f} "
              f"{cost:>10,.0f}  {bar}")
    print(f"\n  spent ${total_used:,.0f} of ${b['labor_pool']:,.0f} labor pool  "
          f"(${b['labor_pool']-total_used:,.0f} left)")
    if b["ledger"]:
        print("\n  recent work charged:")
        for e in b["ledger"][-8:]:
            print(f"    {e['date']}  {e['who']:<6} {e['hours']:>4.1f}h  "
                  f"${e['hours']*hourly(e['who']):>7,.0f}  {e['note']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--charge", nargs=3, metavar=("WHO", "HOURS", "NOTE"))
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--reset", type=float, default=None, metavar="TOTAL")
    args = ap.parse_args()

    b = load_budget()
    if args.reset is not None or b is None:
        b = new_budget(args.reset if args.reset is not None else 150000.0)
        save_budget(b)
        print(f"  opened a ${b['total']:,.0f} budget")

    if args.charge:
        who, hours, note = args.charge[0], float(args.charge[1]), args.charge[2]
        if who not in TEAM:
            sys.exit(f"no such person: {who}")
        b["ledger"].append({"date": date.today().isoformat(), "who": who,
                            "hours": hours, "note": note})
        save_budget(b)
        print(f"  charged {who} {hours}h (${hours*hourly(who):,.0f}) — {note}")
        return 0

    if args.report:
        report(b)
    else:
        plan_table(b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
