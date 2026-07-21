"""
meeting.py - the standup team, live and out loud.

You talk. They answer, in their own voices, in real time. No API account needed
for the default path: speech recognition runs locally on this machine and the
voices come from edge-tts, same as team_voice.py.

    mic --> faster-whisper (local, offline) --> brain --> edge-tts --> speakers
                                                 |
                                                 +-- ollama  (free, local, default)
                                                 +-- claude  (sharper, ANTHROPIC_API_KEY)

Usage:
    python meeting.py                    # just talk - it listens for you to stop
    python meeting.py --brain claude     # sharper room, needs the key
    python meeting.py --type             # keyboard in, voices out
    python meeting.py --ptt              # push-to-talk: ENTER starts, ENTER stops
    python meeting.py --list-mics
    python meeting.py --cast

While they are talking, press ENTER to cut them off - same as interrupting a
person mid-sentence. Say "that's a wrap" (or Ctrl+C) to end the meeting; the
transcript is written to 06 Code/meetings/.
"""

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

# The console here is cp1252 by default, which can't print the team's emoji.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
TEAM = json.loads((HERE / "team.json").read_text(encoding="utf-8"))["cast"]
MEETINGS = HERE / "meetings"
CONTEXT_FILE = HERE / "room_context.md"

SAMPLE_RATE = 16000
BLOCK = 480                 # 30 ms at 16 kHz
SILENCE_TAIL = 0.9          # seconds of quiet that means "they're done"
MIN_SPEECH = 0.35           # shorter than this is a cough, not a sentence
NOISE_MARGIN = 3.0          # speech must be this many times the room's noise floor

LINE = re.compile(r"^\s*\*{0,2}(\w+)\*{0,2}\s*:\s*(.+)$")
WRAP_WORDS = ("that's a wrap", "thats a wrap", "end the meeting", "we're done here")


# ---------------------------------------------------------------- the prompt

def system_prompt(context: str) -> str:
    who = "\n".join(
        f"- {name} [{p['role']}]: {p['persona']}"
        for name, p in TEAM.items()
    )
    prompt = f"""You are the whole room in a live startup meeting. Zayah, the founder, is
speaking out loud and hearing your replies through speakers. You write every
person's lines.

The team:
{who}

Rules for a SPOKEN meeting:
- Format every line exactly as `Name: what they say`. Nothing else. No markdown,
  no bullets, no emoji, no stage directions.
- 1 to 3 people speak per turn. Not everybody every time - a real meeting has
  quiet people.
- Keep lines short. One or two sentences, the way people actually talk out loud.
  No lists. No headings. This is being read aloud.
- Let them disagree with each other, and be funny. They have real personalities.
- CTO speaks last when the room splits, and lands on ONE concrete next action.
- NEVER invent facts, numbers, test results, or outcomes. If nobody in the room
  actually knows something, have them say they don't know and name who would
  find out. A confident wrong number is the worst thing you can do here.
- Use they/them for everyone on the team.
- If Zayah asks something factual you can't verify, say so out loud rather than
  guessing."""
    if context:
        prompt += f"\n\nWhat the room already knows about the work:\n{context}"
    return prompt


# ---------------------------------------------------------------- brains

class Ollama:
    """Local model over http://localhost:11434 - free, offline, no account."""

    name = "ollama"

    def __init__(self, model="llama3:latest"):
        self.model = model
        import urllib.request  # stdlib; ollama's REST API is plain JSON lines
        self._urllib = urllib.request
        try:
            self._urllib.urlopen("http://localhost:11434/api/tags", timeout=3).read()
        except Exception as exc:
            raise SystemExit(
                f"ollama isn't answering on localhost:11434 ({exc}).\n"
                "Start it (it usually runs as a service) or use --brain claude."
            )

    def stream(self, system, history):
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system}] + history,
            "stream": True,
            "options": {"temperature": 0.8, "num_predict": 220},
        }).encode()
        req = self._urllib.Request(
            "http://localhost:11434/api/chat", data=body,
            headers={"Content-Type": "application/json"},
        )
        with self._urllib.urlopen(req, timeout=120) as resp:
            for raw in resp:
                if not raw.strip():
                    continue
                chunk = json.loads(raw)
                piece = chunk.get("message", {}).get("content", "")
                if piece:
                    yield piece
                if chunk.get("done"):
                    return


class Claude:
    """Anthropic API - sharper personas, needs ANTHROPIC_API_KEY in the env."""

    name = "claude"

    def __init__(self, model="claude-sonnet-5"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "ANTHROPIC_API_KEY isn't set, so --brain claude can't run.\n"
                "Either set it, or use the default local brain (--brain ollama)."
            )
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model

    def stream(self, system, history):
        with self.client.messages.stream(
            model=self.model, max_tokens=400, system=system, messages=history,
        ) as s:
            for piece in s.text_stream:
                yield piece


# ---------------------------------------------------------------- ears

class Ears:
    """Local speech recognition. The model downloads once, then works offline."""

    def __init__(self, model_size="base.en", device_index=None):
        import numpy as np
        import sounddevice as sd
        from faster_whisper import WhisperModel

        self.np, self.sd = np, sd
        print(f"  loading whisper ({model_size}, cpu)...", end="", flush=True)
        t0 = time.time()
        self.model = WhisperModel(
            model_size, device="cpu", compute_type="int8", cpu_threads=8
        )
        print(f" {time.time() - t0:.1f}s")
        self.device_index = device_index
        self.q = queue.Queue()

    def _callback(self, indata, frames, t, status):
        self.q.put(bytes(indata))

    def _rms(self, buf):
        a = self.np.frombuffer(buf, dtype=self.np.int16).astype(self.np.float32)
        return float(self.np.sqrt(self.np.mean(a * a)) + 1e-9)

    def listen(self):
        """Block until a full utterance lands, then return it as text."""
        np = self.np
        with self.sd.RawInputStream(
            samplerate=SAMPLE_RATE, blocksize=BLOCK, dtype="int16", channels=1,
            device=self.device_index, callback=self._callback,
        ):
            while not self.q.empty():
                self.q.get()

            # Learn this room's noise floor first - a desk fan is not speech.
            floor_blocks = [self._rms(self.q.get()) for _ in range(20)]
            floor = max(sorted(floor_blocks)[len(floor_blocks) // 2], 25.0)
            threshold = floor * NOISE_MARGIN

            frames, speaking, quiet_for = [], False, 0.0
            block_secs = BLOCK / SAMPLE_RATE
            while True:
                buf = self.q.get()
                loud = self._rms(buf) > threshold
                if not speaking:
                    if loud:
                        speaking = True
                        frames.append(buf)
                    continue
                frames.append(buf)
                quiet_for = 0.0 if loud else quiet_for + block_secs
                if quiet_for >= SILENCE_TAIL:
                    break

        audio = np.frombuffer(b"".join(frames), dtype=np.int16)
        if len(audio) / SAMPLE_RATE < MIN_SPEECH:
            return ""
        return self.transcribe(audio.astype(np.float32) / 32768.0)

    def transcribe(self, audio_f32):
        segments, _ = self.model.transcribe(
            audio_f32, language="en", beam_size=1, vad_filter=True,
        )
        return " ".join(s.text.strip() for s in segments).strip()


# ---------------------------------------------------------------- mouths

class Voices:
    """Renders lines to speech and plays them, one pipeline stage ahead.

    Line 2 is being rendered by edge-tts while line 1 is still playing, so the
    room doesn't pause between speakers.
    """

    def __init__(self):
        self.to_render = queue.Queue()
        self.to_play = queue.Queue()
        self.tmp = Path(tempfile.mkdtemp(prefix="meeting_"))
        self.cut = threading.Event()
        self.proc = None
        self.idle = threading.Event()
        self.idle.set()
        self._pending = 0
        self._lock = threading.Lock()
        threading.Thread(target=self._render_loop, daemon=True).start()
        threading.Thread(target=self._play_loop, daemon=True).start()

    def say(self, persona, text):
        with self._lock:
            self._pending += 1
            self.idle.clear()
        self.to_render.put((persona, text))

    def _done_one(self):
        with self._lock:
            self._pending -= 1
            if self._pending <= 0:
                self._pending = 0
                self.idle.set()

    def _render_loop(self):
        """Fetch each line's audio in chunks, handing them to the player as they
        land. Waiting for the whole file first added about a second and a half to
        every reply, which is exactly the pause that makes a room feel dead."""
        import asyncio

        import edge_tts
        while True:
            persona, text = self.to_render.get()
            if self.cut.is_set():
                self._done_one()
                continue
            part = TEAM.get(persona, TEAM["Nova"])
            chunks = queue.Queue()
            self.to_play.put(chunks)

            async def pump():
                comm = edge_tts.Communicate(
                    text, part["voice"], rate=part["rate"], pitch=part["pitch"]
                )
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        chunks.put(chunk["data"])
            try:
                asyncio.run(pump())
            except Exception as exc:      # offline, or edge-tts hiccup
                print(f"    [voice unavailable: {exc}]")
            finally:
                chunks.put(None)          # end of this speaker

    def _play_loop(self):
        while True:
            chunks = self.to_play.get()
            if self.cut.is_set():
                self._drain(chunks)
                self._done_one()
                continue
            try:
                self.proc = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                     "-hide_banner", "-i", "pipe:0"],
                    stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
                )
                while True:
                    data = chunks.get()
                    if data is None or self.cut.is_set():
                        break
                    self.proc.stdin.write(data)
                    self.proc.stdin.flush()
                try:
                    self.proc.stdin.close()
                except Exception:
                    pass
                self.proc.wait()
            except (FileNotFoundError, BrokenPipeError, OSError):
                pass                      # cut off mid-sentence, or no ffplay
            finally:
                self._drain(chunks)
                self.proc = None
                self._done_one()

    @staticmethod
    def _drain(chunks):
        while True:
            try:
                if chunks.get_nowait() is None:
                    return
            except queue.Empty:
                return

    def interrupt(self):
        """Stop them mid-sentence and drop whatever was queued behind it."""
        self.cut.set()
        if self.proc:
            try:
                self.proc.kill()
            except Exception:
                pass
        for q in (self.to_render, self.to_play):
            while not q.empty():
                try:
                    q.get_nowait()
                    self._done_one()
                except queue.Empty:
                    break
        time.sleep(0.15)
        self.cut.clear()
        with self._lock:
            self._pending = 0
        self.idle.set()

    def wait(self):
        self.idle.wait()


# ---------------------------------------------------------------- the room

def watch_for_interrupt(voices, stop):
    """ENTER while they're talking = you cutting in. Windows console only."""
    try:
        import msvcrt
    except ImportError:
        return
    while not stop.is_set():
        if msvcrt.kbhit() and msvcrt.getwch() in ("\r", "\n"):
            if not voices.idle.is_set():
                print("    [you cut in]")
                voices.interrupt()
        time.sleep(0.05)


def run_turn(brain, system, history, voices, transcript):
    """Stream one reply, speaking each line the moment it's complete."""
    buffer, said = "", []
    for piece in brain.stream(system, history):
        buffer += piece
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            said += speak_line(line, voices, transcript)
    said += speak_line(buffer, voices, transcript)
    return said


def speak_line(line, voices, transcript):
    line = line.strip()
    if not line:
        return []
    m = LINE.match(line)
    persona, text = (m.group(1), m.group(2).strip()) if m else ("Nova", line)
    if persona not in TEAM:
        persona, text = "Nova", line
    emoji = TEAM[persona].get("emoji", "")
    print(f"  {emoji} {persona} [{TEAM[persona]['role']}]  {text}")
    transcript.append(f"**{persona}** ({TEAM[persona]['role']}): {text}")
    voices.say(persona, text)
    return [f"{persona}: {text}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain", choices=["ollama", "claude"], default="ollama")
    ap.add_argument("--model", default=None, help="override the brain's model")
    ap.add_argument("--whisper", default="base.en",
                    help="tiny.en / base.en / small.en - bigger is slower, sharper")
    ap.add_argument("--type", action="store_true", help="type instead of talking")
    ap.add_argument("--ptt", action="store_true", help="push-to-talk (ENTER to start/stop)")
    ap.add_argument("--mic", type=int, default=None, help="input device index")
    ap.add_argument("--context", default=None, help="a file the room should know about")
    ap.add_argument("--list-mics", action="store_true")
    ap.add_argument("--cast", action="store_true")
    args = ap.parse_args()

    if args.cast:
        for name, p in TEAM.items():
            pay = f"${p['salary']:,}" if p["salary"] else "-"
            print(f"  {p.get('emoji','')} {name:<6} {p['role']:<18} {pay:>10}  {p['voice']}")
        return 0

    if args.list_mics:
        import sounddevice as sd
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                print(f"  [{i}] {d['name']}")
        return 0

    ctx_path = Path(args.context) if args.context else CONTEXT_FILE
    context = ctx_path.read_text(encoding="utf-8") if ctx_path.exists() else ""
    system = system_prompt(context)

    print("\n  starting the room")
    brain = (Claude(args.model or "claude-sonnet-5") if args.brain == "claude"
             else Ollama(args.model or "llama3:latest"))
    print(f"  brain: {brain.name} ({brain.model})")
    if brain.name == "ollama":
        print("  ⚠  a local 8B model WILL confidently invent details. Treat this room")
        print("     as thinking-out-loud, not as fact. Use --brain claude to decide things.")

    ears = None
    if not args.type:
        ears = Ears(args.whisper, args.mic)

    voices = Voices()
    stop = threading.Event()
    if not args.type:
        threading.Thread(target=watch_for_interrupt, args=(voices, stop), daemon=True).start()

    history, transcript = [], []
    started = datetime.now()
    print("\n  the room is live. talk normally - it waits for you to stop.")
    print("  ENTER cuts them off. say \"that's a wrap\" to end.\n")

    try:
        while True:
            if args.type:
                try:
                    you = input("  you > ").strip()
                except EOFError:
                    break
            elif args.ptt:
                input("  [ENTER to talk] ")
                print("  listening...", end="\r")
                you = ears.listen()
            else:
                you = ears.listen()
            if not you:
                continue
            print(f"  🎙️  you  {you}")
            transcript.append(f"**Zayah** (founder): {you}")
            if any(w in you.lower() for w in WRAP_WORDS):
                break

            history.append({"role": "user", "content": you})
            said = run_turn(brain, system, history, voices, transcript)
            history.append({"role": "assistant", "content": "\n".join(said) or "(silence)"})
            history[:] = history[-16:]
            voices.wait()
    except KeyboardInterrupt:
        print("\n  (meeting ended)")
    finally:
        stop.set()
        if transcript:
            MEETINGS.mkdir(exist_ok=True)
            out = MEETINGS / f"meeting-{started:%Y-%m-%d-%H%M}.md"
            out.write_text(
                f"# Meeting - {started:%Y-%m-%d %H:%M}\n\n"
                f"Brain: {brain.name} ({brain.model})\n\n"
                + "\n\n".join(transcript) + "\n",
                encoding="utf-8",
            )
            print(f"  transcript -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
