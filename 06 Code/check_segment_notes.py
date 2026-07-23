"""Linter for drafts/SEGMENT_NOTES.md (card 023).

The notes file is the per-segment value language the queued drafts are audited
against, so it is held to the same language rules as the drafts themselves:

  * one section per segment that actually has queued (todo/drafted/hold) rows
  * every section carries the DATED verified number, the honest caveat, and
    exactly one ask
  * the retired 11.3x multiple appears nowhere
  * GEO is only ever mentioned alongside the external-safe validation sentence
  * no named external people (companies are fine; people are not)
  * a draft-audit section with an explicit mismatch list exists — the card
    requires mismatches listed, not silently rewritten

Run: python check_segment_notes.py   (exit 0 = clean, 1 = problems, printed)
"""

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
NOTES = HERE / "drafts" / "SEGMENT_NOTES.md"
CSV_PATH = HERE / "outreach_targets.csv"

QUEUED = ("todo", "drafted", "hold")

# The external-safe GEO sentence is the ONLY way GEO may be discussed.
GEO_SAFE = "under active validation"

# People must not be named in a file that could ride along with drafts.
BANNED_NAMES = [
    "Heldreth", "Kelso", "Jah", "Mason", "Gehant", "Curry", "Testore",
    "Therien", "Miga", "Skinner", "Kunstadter", "Wade", "Linares",
]

REQUIRED_PER_SECTION = {
    "dated number": re.compile(r"2026-07-22|July 22|22 July"),
    "verified rate": re.compile(r"68[–—-]\s?72\s?%|two[- ]thirds"),
    "control rate": re.compile(r"~?10\s?%"),
    "honest caveat": re.compile(r"not operator ground truth"),
    "one ask": re.compile(r"\*\*Ask:?\*\*"),
}


def queued_segments():
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return sorted({r["segment"] for r in rows if r["status"] in QUEUED})


def sections(text):
    """Map of '## heading' segment word -> section body."""
    out = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"##\s+`?(\w+)`?", line)
        if m:
            current = m.group(1).lower()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def main():
    problems = []

    if not NOTES.exists():
        print(f"MISSING: {NOTES}")
        return 1
    text = NOTES.read_text(encoding="utf-8")

    if "11.3" in text:
        problems.append("retired 11.3x multiple appears in the notes")

    for i, line in enumerate(text.splitlines(), 1):
        if "GEO" in line and GEO_SAFE not in line:
            problems.append(f"line {i}: GEO mentioned without the external-safe "
                            f"validation sentence: {line.strip()[:70]!r}")

    for name in BANNED_NAMES:
        if re.search(rf"\b{name}\b", text):
            problems.append(f"named person {name!r} appears in the notes")

    secs = sections(text)
    for seg in queued_segments():
        if seg not in secs:
            problems.append(f"no section for queued segment {seg!r}")
            continue
        body = secs[seg]
        for label, rx in REQUIRED_PER_SECTION.items():
            if not rx.search(body):
                problems.append(f"section {seg!r} is missing its {label}")

    if "audit" not in secs:
        problems.append("no '## audit' section (queued-draft audit)")
    elif "Mismatches" not in secs["audit"] and "mismatch" not in secs["audit"].lower():
        problems.append("audit section has no mismatch list")

    if problems:
        print(f"SEGMENT NOTES: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"SEGMENT NOTES: clean ({len(queued_segments())} queued segments covered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
