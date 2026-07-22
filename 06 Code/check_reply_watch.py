"""Lint the reply-watch drafts (issue 017). Draft-only guard — checks language rules,
never sends anything.

Rules enforced (from NEXT - Marketing.md language orders):
  * BANNED everywhere: the retired 11.3x multiple and 72%-vs-11% phrasing, LinkedIn,
    and over-claiming GEO validation.
  * Every reply draft must lead with the dated verified number
    (~68-72% vs ~10% of matched controls) and the honest caveat verbatim.
  * Every nudge draft must carry the date its window hits (2026-07-...).
  * STATUS.md must exist and cover every in-flight contact.

Exit 0 = clean, exit 1 = violations (printed).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent / "reply_watch"

BANNED = [
    "11.3",            # retired multiple, in any spelling that matters
    "11% of controls",
    "vs 11%",
    "versus 11%",
    "72%-vs-11",
    "linkedin",
    "validated in geo",
    "confirmed in geo",
    "geo-validated",
    "works in geo",
]

# the approved number language, and the honest caveat (verbatim core)
REQUIRED_IN_REPLIES = [
    "68",                     # ~68-72%
    "72%",
    "~10%",
    "matched controls",
    "own methods agreeing, not operator ground truth",
]

# every contact currently in flight must appear in STATUS.md
STATUS_MUST_MENTION = [
    "Heldreth", "Jah", "Kelso", "TraCSS", "Morgansen", "Starfish", "Kayhan",
    "Xplore", "Space Grant", "AMOS", "Williams", "Miga", "Linares", "Digantara",
    "LeoLabs", "COMSPOC", "Vyoma", "Neuraspace", "Stoke",
]

REPLY_COUNT_MIN = 10
NUDGE_COUNT_MIN = 15


def main() -> int:
    errors = []

    if not ROOT.is_dir():
        print(f"FAIL: {ROOT} does not exist")
        return 1

    replies = sorted((ROOT / "replies").glob("*.md")) if (ROOT / "replies").is_dir() else []
    nudges = sorted((ROOT / "nudges").glob("*.md")) if (ROOT / "nudges").is_dir() else []
    status = ROOT / "STATUS.md"

    if len(replies) < REPLY_COUNT_MIN:
        errors.append(f"replies/: found {len(replies)} drafts, need >= {REPLY_COUNT_MIN}")
    if len(nudges) < NUDGE_COUNT_MIN:
        errors.append(f"nudges/: found {len(nudges)} drafts, need >= {NUDGE_COUNT_MIN}")
    if not status.is_file():
        errors.append("STATUS.md missing")

    for path in [*replies, *nudges] + ([status] if status.is_file() else []):
        text = path.read_text(encoding="utf-8")
        low = text.lower()
        for bad in BANNED:
            if bad in low:
                errors.append(f"{path.name}: BANNED phrase present: {bad!r}")

    for path in replies:
        text = path.read_text(encoding="utf-8")
        for req in REQUIRED_IN_REPLIES:
            if req not in text:
                errors.append(f"{path.name}: missing required language: {req!r}")

    for path in nudges:
        text = path.read_text(encoding="utf-8")
        if not re.search(r"2026-07-\d\d", text):
            errors.append(f"{path.name}: no dated send-window (2026-07-..)")

    if status.is_file():
        stext = status.read_text(encoding="utf-8")
        for name in STATUS_MUST_MENTION:
            if name not in stext:
                errors.append(f"STATUS.md: in-flight contact not covered: {name}")

    if errors:
        print(f"FAIL ({len(errors)} problems):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(replies)} reply drafts, {len(nudges)} nudge drafts, STATUS.md covers all in-flight contacts. Nothing sent (nothing to send with).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
