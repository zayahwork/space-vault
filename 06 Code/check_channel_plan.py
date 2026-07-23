"""Linter for card 032 (traffic channel strategy).

Checks `Channel Plan - Traffic Beyond Cold Email.md` (vault root):

  * 3-4 chosen channels (`## CHANNEL: ...`), each with: what we post,
    cadence, effort cost, a first-2-weeks concrete content list, and a
    drafted first post inside a ```post fenced block
  * at least one killed channel (`## KILLED: ...`) with a stated reason
  * the founder-approval gate stated (nothing posts without approval)
  * the launch-delay X thread's Kelso-reply gate still stated
  * language rules on anything that could become public (the post blocks):
      - no named external people
      - no retired 11.3x, no unruled 96% figure (external language stays
        at the dated ~68-72% sentence until the CTO ruling lands)
      - if a post quotes the rate it must carry the date AND the honest
        caveat ("not operator ground truth")
      - GEO only via the external-safe sentence
  * no LinkedIn anywhere (permanent rule)

Run: python check_channel_plan.py   (exit 0 = clean, 1 = problems, printed)
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PLAN = HERE.parent / "Channel Plan - Traffic Beyond Cold Email.md"

GEO_SAFE = "under active validation"

# People from our threads must not be named in anything that could become
# public. (Plan prose is internal and may reference the Kelso-reply gate;
# the drafted posts may not name anyone.)
BANNED_NAMES_IN_POSTS = [
    "Heldreth", "Kelso", "Jah", "Mason", "Gehant", "Curry", "Testore",
    "Therien", "Miga", "Skinner", "Kunstadter", "Wade", "Linares",
]

REQUIRED_PER_CHANNEL = {
    "what we post": re.compile(r"\*\*What we post:\*\*", re.I),
    "cadence": re.compile(r"\*\*Cadence:\*\*", re.I),
    "effort cost": re.compile(r"\*\*Effort:\*\*", re.I),
    "first-2-weeks list": re.compile(r"###\s*First 2 weeks", re.I),
    "drafted first post": re.compile(r"###\s*First post", re.I),
}

RATE_HINT = re.compile(r"68\s?[–—-]\s?72|two[- ]thirds")
RATE_NEEDS = {
    "dated number": re.compile(r"2026-07-22|July 22|22 July"),
    "honest caveat": re.compile(r"not operator ground truth"),
}


def split_sections(text, tag):
    """Bodies of every `## {tag}: ...` section, keyed by heading rest."""
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"##\s+(.*)", line)
        if m:
            head = m.group(1).strip()
            if head.upper().startswith(tag + ":"):
                current = head[len(tag) + 1:].strip()
                out[current] = []
            else:
                current = None
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def post_blocks(text):
    return re.findall(r"```post\n(.*?)```", text, re.S)


def main():
    problems = []
    if not PLAN.exists():
        problems.append(f"MISSING: {PLAN}")
    else:
        text = PLAN.read_text(encoding="utf-8")

        # ---- global rules -------------------------------------------------
        if re.search(r"linkedin", text, re.I):
            problems.append("LinkedIn appears in the plan — banned route")
        if "11.3" in text:
            problems.append("retired 11.3x multiple appears in the plan")

        # ---- channels -----------------------------------------------------
        channels = split_sections(text, "CHANNEL")
        if not 3 <= len(channels) <= 4:
            problems.append(
                f"{len(channels)} chosen channels — card says pick 3-4")
        for name, body in channels.items():
            for label, rx in REQUIRED_PER_CHANNEL.items():
                if not rx.search(body):
                    problems.append(f"channel {name!r} is missing its {label}")
            weeks = re.search(r"###\s*First 2 weeks(.*?)(?=###|\Z)", body,
                              re.S | re.I)
            if weeks and len(re.findall(r"^\s*[-*]\s+\S", weeks.group(1),
                                        re.M)) < 4:
                problems.append(
                    f"channel {name!r}: first-2-weeks list has <4 concrete items")
            if not post_blocks(body):
                problems.append(
                    f"channel {name!r}: no ```post fenced draft in it")

        killed = split_sections(text, "KILLED")
        if not killed:
            problems.append("no killed channel (`## KILLED: ...`) — card says "
                            "kill the rest with reasons")
        for name, body in killed.items():
            if len(body.strip()) < 80:
                problems.append(f"killed channel {name!r} has no real reason")

        # ---- gates --------------------------------------------------------
        flat = re.sub(r"\s+", " ", text)
        if not re.search(r"nothing posts without founder approval", flat, re.I):
            problems.append("founder-approval gate not stated verbatim")
        if not re.search(r"gated on the Kelso reply", flat, re.I):
            problems.append("launch-delay thread's Kelso-reply gate not stated")

        # ---- language rules inside the drafted posts ----------------------
        for i, post in enumerate(post_blocks(text), 1):
            # prose wraps at ~80 cols, so phrase checks run ws-normalized
            body = re.sub(r"\s+", " ", post)
            for name in BANNED_NAMES_IN_POSTS:
                if re.search(rf"\b{name}\b", body):
                    problems.append(f"post {i}: named person {name!r} in a "
                                    "draft that could become public")
            if re.search(r"96\s?%", body):
                problems.append(f"post {i}: unruled 96% figure — external "
                                "language stays at ~68-72% until the ruling")
            if "GEO" in body and GEO_SAFE not in body:
                problems.append(f"post {i}: GEO without the external-safe "
                                "sentence")
            if RATE_HINT.search(body):
                for req, rx in RATE_NEEDS.items():
                    if not rx.search(body):
                        problems.append(f"post {i}: quotes the rate but is "
                                        f"missing its {req}")

    if problems:
        print(f"CHANNEL PLAN: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("CHANNEL PLAN: clean (3-4 channels, kills reasoned, posts drafted, "
          "gates stated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
