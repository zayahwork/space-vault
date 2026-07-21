"""
team_voice.py - the standup team, in real voices.

Upgrade over team_voice.ps1: instead of Windows' two robot voices, this uses
edge-tts (free, no API key, no account) to reach Microsoft's neural voices.
47 English ones, so everybody gets their own voice AND their own accent.

Needs internet - these are generated server-side. The PowerShell version stays
around as the offline fallback.

Usage:
  python team_voice.py batch_update.txt              # build + play
  python team_voice.py standup.txt --no-play         # just build the mp3
  python team_voice.py --say Fitz "we shipped a bug" # one-off line
  python team_voice.py --cast                        # who's who
"""

import argparse
import asyncio
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

FFMPEG = "ffmpeg"
FFPLAY = "ffplay"

# The cast lives in team.json, not here - it's also read by brain.py and payroll.py,
# and a hire that only exists in one of them gets silently voiced as somebody else.
# (That is exactly what happened to Tim on his first day.)
import json

CAST = json.loads(
    (Path(__file__).resolve().parent / "team.json").read_text(encoding="utf-8")
)["cast"]

LINE = re.compile(r"^\s*(\w+)\s*:\s*(.+)$")


def parse(path):
    """Yield (persona, text) from a script file, skipping blanks and comments."""
    out = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = LINE.match(raw)
        if m and m.group(1) in CAST:
            out.append((m.group(1), m.group(2).strip()))
        else:
            out.append(("Nova", raw.strip()))
    return out


async def render(persona, text, dest):
    part = CAST[persona]
    tts = edge_tts.Communicate(
        text, part["voice"], rate=part["rate"], pitch=part["pitch"]
    )
    await tts.save(str(dest))


async def build(lines, out_path):
    tmp = Path(tempfile.mkdtemp(prefix="teamvoice_"))
    pieces = []

    for i, (persona, text) in enumerate(lines):
        piece = tmp / f"{i:03d}_{persona}.mp3"
        print(f"  {persona:<6} [{CAST[persona]['role']}]  {text[:58]}")
        await render(persona, text, piece)
        pieces.append(piece)

    # Concat via ffmpeg's demuxer. Paths are quoted because the vault path has a
    # space in it, and the list file wants forward slashes even on Windows.
    listing = tmp / "concat.txt"
    listing.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in pieces), encoding="utf-8"
    )

    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", str(out_path)],
        check=True,
    )
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?", help="a standup .txt file")
    ap.add_argument("--say", nargs=2, metavar=("PERSONA", "TEXT"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-play", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-render even if built")
    ap.add_argument("--cast", action="store_true")
    args = ap.parse_args()

    if args.cast:
        for name, part in CAST.items():
            print(f"  {name:<6} [{part['role']:<18}] {part['voice']}")
        return 0

    if args.say:
        persona, text = args.say
        if persona not in CAST:
            sys.exit(f"unknown persona {persona!r} - try --cast")
        lines = [(persona, text)]
        out = Path(args.out or Path(tempfile.gettempdir()) / "one_line.mp3")
    elif args.script:
        lines = parse(args.script)
        out = Path(args.out or Path(args.script).with_suffix(".mp3"))
    else:
        sys.exit("give me a script file, or --say PERSONA TEXT")

    if not lines:
        sys.exit("nothing to say - the script parsed to zero lines")

    # Don't re-render what's already built. Rendering is ~30 network calls and a
    # minute of silence, which reads exactly like a hang - so only do it when the
    # text is actually newer than the audio.
    fresh = (
        out.exists()
        and args.script
        and out.stat().st_mtime >= Path(args.script).stat().st_mtime
    )
    if fresh and not args.force:
        print(f"already built: {out}  (--force to re-render)")
    else:
        print(f"rendering {len(lines)} lines")
        asyncio.run(build(lines, out))
        print(f"\n  -> {out}  ({out.stat().st_size/1024:.0f} KB)")

    if not args.no_play:
        play(out)
    return 0


def play(path):
    """ffplay if we have it, otherwise hand the file to Windows."""
    try:
        subprocess.run(
            [FFPLAY, "-nodisp", "-autoexit", "-loglevel", "error", str(path)],
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("  ffplay unavailable - opening in the default player")
        import os

        os.startfile(str(path))  # noqa: S606 - Windows-only, intentional


if __name__ == "__main__":
    sys.exit(main())
