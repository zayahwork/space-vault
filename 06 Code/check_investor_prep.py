"""Linter for card 030 (investor warm outreach prep).

Checks the two artifacts the card requires:

  1. `Investor Target List.md` (vault root) —
       * 20+ investor rows, each carrying: fund, named person, stage/check,
         warm-path options, cold-path quality
       * a YC row with the application deadline documented
       * no LinkedIn anywhere (permanent rule)
  2. `drafts/INVESTOR_DRAFTS.md` —
       * the 3 draft artifacts: a company one-liner, a warm intro-request
         email, and a cold intro email
       * each email carries the DATED approved number and the honest caveat
       * the retired 11.3x multiple appears nowhere; the unruled 96% figure
         appears nowhere (external language stays at ~68-72% until the CTO
         language ruling lands)
       * GEO only via the external-safe sentence
       * no named external people in the drafts (they could become public)

Run: python check_investor_prep.py   (exit 0 = clean, 1 = problems, printed)
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
LIST = HERE.parent / "Investor Target List.md"
DRAFTS = HERE / "drafts" / "INVESTOR_DRAFTS.md"

GEO_SAFE = "under active validation"

# People from our threads must not be named in draft emails that could
# become public. (The target LIST is internal and may name investors.)
BANNED_NAMES_IN_DRAFTS = [
    "Heldreth", "Kelso", "Jah", "Mason", "Gehant", "Curry", "Testore",
    "Therien", "Miga", "Skinner", "Kunstadter", "Wade", "Linares",
]

REQUIRED_PER_EMAIL = {
    "dated number": re.compile(r"2026-07-22|July 22|22 July"),
    "verified rate": re.compile(r"68[–—-]\s?72\s?%|two[- ]thirds"),
    "control rate": re.compile(r"~?10\s?%"),
    "honest caveat": re.compile(r"not operator ground truth"),
}


def problems_in_list(problems):
    if not LIST.exists():
        problems.append(f"MISSING: {LIST}")
        return
    text = LIST.read_text(encoding="utf-8")

    # Investor rows are markdown table rows tagged with a segment-style
    # marker in the first cell: "| INV |" (investor) — YC gets "| YC |".
    inv_rows = re.findall(r"^\|\s*INV\s*\|.*$", text, re.M)
    if len(inv_rows) < 20:
        problems.append(
            f"target list has {len(inv_rows)} investor rows tagged 'INV' — card needs 20+")
    for row in inv_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        # tag | fund | person | stage/check | why-them | warm path | cold path | confidence
        if len(cells) < 8 or any(not c for c in cells[1:8]):
            problems.append(f"incomplete investor row: {row[:80]!r}")

    if not re.search(r"^\|\s*YC\s*\|", text, re.M):
        problems.append("no YC row (tag 'YC') in the target list")
    if "July 27" not in text:
        problems.append("YC application deadline (July 27) not documented")

    if re.search(r"linkedin", text, re.I):
        problems.append("LinkedIn appears in the target list — banned route")
    if "11.3" in text:
        problems.append("retired 11.3x multiple appears in the target list")


def sections(text):
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"##\s+(.*)", line)
        if m:
            current = m.group(1).strip().lower()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def problems_in_drafts(problems):
    if not DRAFTS.exists():
        problems.append(f"MISSING: {DRAFTS}")
        return
    text = DRAFTS.read_text(encoding="utf-8")

    if "11.3" in text:
        problems.append("retired 11.3x multiple appears in the drafts")
    if re.search(r"96\s?%", text):
        problems.append("unruled 96% figure appears in the drafts — external "
                        "language stays at ~68-72% until the CTO ruling")
    if re.search(r"linkedin", text, re.I):
        problems.append("LinkedIn appears in the drafts — banned route")
    for i, line in enumerate(text.splitlines(), 1):
        if "GEO" in line and GEO_SAFE not in line:
            problems.append(f"drafts line {i}: GEO without the external-safe "
                            f"sentence: {line.strip()[:70]!r}")
    for name in BANNED_NAMES_IN_DRAFTS:
        if re.search(rf"\b{name}\b", text):
            problems.append(f"named person {name!r} appears in the drafts")

    secs = sections(text)
    needed = {
        "one-liner": [s for s in secs if "one-liner" in s],
        "warm intro-request email": [s for s in secs if "warm" in s],
        "cold intro email": [s for s in secs if "cold" in s],
    }
    for label, found in needed.items():
        if not found:
            problems.append(f"drafts missing the {label} section")

    for label in ("warm", "cold"):
        bodies = [b for s, b in secs.items() if label in s]
        if not bodies:
            continue
        # prose wraps at ~80 cols, so phrase checks run on ws-normalized text
        body = re.sub(r"\s+", " ", "\n".join(bodies))
        for req, rx in REQUIRED_PER_EMAIL.items():
            if not rx.search(body):
                problems.append(f"{label} intro email is missing its {req}")


def main():
    problems = []
    problems_in_list(problems)
    problems_in_drafts(problems)
    if problems:
        print(f"INVESTOR PREP: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("INVESTOR PREP: clean (target list + 3 draft artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
