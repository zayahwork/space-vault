"""
brain.py - give each person their own memory, so they actually learn as we go.

THE QUESTION: "is there any way to give each agent their own brain?"

WHAT DOESN'T WORK
Fine-tuning a model per persona. You'd need thousands of examples per person, a
training run each time anyone learns anything, and you'd still get a model that
sounds like them rather than one that KNOWS more than yesterday. Wrong tool.

WHAT DOES WORK - AND YOU ALREADY BUILT IT
This is exactly Remend's playbook: proven outcomes get distilled into reusable
lessons, stored, and retrieved next time the same situation appears. Same design
here. Each person owns a markdown file of things they have personally learned on
this project. Before they speak, their file is read. That IS the brain: not
weights, but an accumulating, inspectable memory that survives every session.

THE ONE RULE THAT KEEPS IT HONEST (also borrowed from the playbook)
A lesson is banked as `proven` only when something actually demonstrated it.
Everything else is `hypothesis` and says so out loud. A brain full of confident
guesses is worse than no brain, because it launders yesterday's guess into
today's fact. Demote freely; being wrong in writing is the point.

Usage:
  python brain.py                              # who knows what, at a glance
  python brain.py Sable                        # read one brain
  python brain.py --learn Sable "lesson text" --evidence "how we know" --proven
  python brain.py --demote Sable 3             # that one didn't hold up
  python brain.py --context Sable Rook         # brains as prompt text
"""

import argparse
import json
import re
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
BRAINS = HERE / "brains"
ENTRY = re.compile(r"^- \[(proven|hypothesis|retired)\] (\d{4}-\d{2}-\d{2}) — (.+)$")


def path_for(name):
    return BRAINS / f"{name}.md"


def read(name):
    p = path_for(name)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = ENTRY.match(line.strip())
        if m:
            out.append({"status": m.group(1), "date": m.group(2), "text": m.group(3)})
    return out


def write(name, entries):
    BRAINS.mkdir(exist_ok=True)
    person = TEAM.get(name, {})
    head = (f"# {person.get('emoji','')} {name} — {person.get('role','')}\n\n"
            f"What {name} has learned on this project. Written by `brain.py`; read back\n"
            f"before {name} speaks. `proven` means something demonstrated it. `hypothesis`\n"
            f"means we think so and haven't shown it yet — say so out loud.\n\n")
    body = "\n".join(f"- [{e['status']}] {e['date']} — {e['text']}" for e in entries)
    path_for(name).write_text(head + body + "\n", encoding="utf-8")


def learn(name, text, evidence, proven):
    entries = read(name)
    status = "proven" if proven else "hypothesis"
    full = text if not evidence else f"{text}  **How we know:** {evidence}"
    # Don't bank the same lesson twice - the playbook's anti-collapse rule.
    for e in entries:
        if e["text"].split("**How we know:**")[0].strip().lower() == text.strip().lower():
            e["status"], e["date"] = status, date.today().isoformat()
            e["text"] = full
            write(name, entries)
            print(f"  updated {name}'s existing lesson -> {status}")
            return
    entries.append({"status": status, "date": date.today().isoformat(), "text": full})
    write(name, entries)
    print(f"  {name} learned something ({status}). {len(entries)} lessons banked.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("who", nargs="*", help="whose brain to read")
    ap.add_argument("--learn", nargs=2, metavar=("WHO", "LESSON"))
    ap.add_argument("--evidence", default="")
    ap.add_argument("--proven", action="store_true")
    ap.add_argument("--demote", nargs=2, metavar=("WHO", "INDEX"))
    ap.add_argument("--context", nargs="+", metavar="WHO",
                    help="print brains as prompt text for a meeting")
    args = ap.parse_args()

    if args.learn:
        who, lesson = args.learn
        if who not in TEAM:
            sys.exit(f"no such person: {who}")
        learn(who, lesson, args.evidence, args.proven)
        return 0

    if args.demote:
        who, idx = args.demote[0], int(args.demote[1])
        entries = read(who)
        if not 1 <= idx <= len(entries):
            sys.exit(f"{who} has {len(entries)} lessons; no #{idx}")
        entries[idx - 1]["status"] = "retired"
        write(who, entries)
        print(f"  retired {who}'s lesson #{idx} — being wrong in writing is the point")
        return 0

    if args.context:
        for who in args.context:
            entries = [e for e in read(who) if e["status"] != "retired"]
            if not entries:
                continue
            print(f"{who} has previously learned:")
            for e in entries:
                print(f"  - ({e['status']}) {e['text']}")
            print()
        return 0

    if args.who:
        for who in args.who:
            entries = read(who)
            print(f"\n  {TEAM.get(who,{}).get('emoji','')} {who} — "
                  f"{TEAM.get(who,{}).get('role','')}  ({len(entries)} lessons)")
            for i, e in enumerate(entries, 1):
                mark = {"proven": "✓", "hypothesis": "?", "retired": "✗"}[e["status"]]
                print(f"   {i:>2}. {mark} {e['date']}  {e['text']}")
        print()
        return 0

    print(f"\n  brains in {BRAINS}\n")
    for name in TEAM:
        entries = read(name)
        if not entries:
            print(f"  {TEAM[name].get('emoji','')} {name:<6} — empty")
            continue
        counts = {}
        for e in entries:
            counts[e["status"]] = counts.get(e["status"], 0) + 1
        summary = "  ".join(f"{v} {k}" for k, v in sorted(counts.items()))
        print(f"  {TEAM[name].get('emoji','')} {name:<6} {len(entries):>2} lessons   {summary}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
