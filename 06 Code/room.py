"""
room.py - the working room. Talk, get answered, keep moving.

v2 of meeting.py. Same team, three things fixed:

  1. localhost cost 2.0s PER TURN. Windows resolves it to ::1 first, ollama only
     binds 127.0.0.1, and every request ate the IPv6 timeout. Same box, same
     model: localhost 2.18s -> 127.0.0.1 0.14s. That was most of the lag.
  2. edge-tts is a network round trip per line. Kokoro runs on this machine and
     starts speaking in ~0.34s, with no internet at all.
  3. Whisper used to start AFTER you stopped talking. RealtimeSTT transcribes
     while you speak, so your words are ready the moment you go quiet.

    mic -> RealtimeSTT (local, streaming) -> brain -> Kokoro (local) -> speakers

Usage:
  python room.py                     # the room
  python room.py --brain claude      # sharper, needs ANTHROPIC_API_KEY
  python room.py --tts edge          # real Irish/Australian accents, ~0.5s slower
  python room.py --bargein           # talk over them (WEAR HEADPHONES)
  python room.py --bench             # measure the loop, no mic needed
  python room.py --list-mics

ENTER cuts them off. Say "that's a wrap" to end. Transcript -> 06 Code/meetings/.
"""

import argparse
import json
import multiprocessing
import os
import queue
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
TEAM = json.loads((HERE / "team.json").read_text(encoding="utf-8"))["cast"]
MEETINGS = HERE / "meetings"
CONTEXT_FILE = HERE / "room_context.md"
TASKS_FILE = Path(r"C:\Space\01 TASKS.md")

# Kokoro ships no Irish and no Australian voice. Rook and Fitz get the closest
# British ones here; --tts edge gets their real accents back at ~0.5s a line.
#
# Cast so that no two people who argue with each other sound alike - Sable and
# Vega are the pair most often disagreeing, so they get the two least similar
# female voices, and Fitz's is deliberately lighter than Rook's because half of
# Fitz's job is winding Rook up and you have to hear which one is which.
#
# Tim had NO entry here at all. He was hired after this table was written, so
# every line he has ever spoken came out of the af_heart fallback - a female
# voice, for someone team.json casts with a male one. That's what a silent
# `.get(name, default)` buys you.
KOKORO_VOICE = {
    "Vega":  "af_bella",     # bright, fast, sells things
    "Sable": "af_kore",      # cool and precise, nothing like Vega
    "Rook":  "bm_lewis",     # deep, flat, unimpressed
    "Fitz":  "bm_fable",     # lighter and quicker - the wind-up merchant
    "Nova":  "bf_emma",      # warm British, the one who explains
    "Tim":   "am_adam",      # measured, unhurried, reads the primary source
    "CTO":   "am_onyx",      # the one who lands the decision
}

LINE = re.compile(r"^\s*\*{0,2}(\w+)\*{0,2}\s*:\s*(.+)$")
WRAP = ("that's a wrap", "thats a wrap", "end the meeting", "we're done here")
OLLAMA = "http://127.0.0.1:11434"          # NOT localhost. See the docstring.


# ---------------------------------------------------------------- the prompt

def system_prompt():
    who = "\n".join(f"- {n} [{p['role']}]: {p['persona']}" for n, p in TEAM.items())
    ctx = CONTEXT_FILE.read_text(encoding="utf-8") if CONTEXT_FILE.exists() else ""
    # Re-read the task list every turn so "what's next" is answered from the
    # real file, not from something the model remembers about last week.
    tasks = ""
    if TASKS_FILE.exists():
        tasks = "\n".join(TASKS_FILE.read_text(encoding="utf-8").splitlines()[:70])
    return f"""You are the whole room in a live startup meeting. Zayah, the founder, is
speaking out loud and hearing you through speakers. You write every person's lines.

The team:
{who}

Rules for a SPOKEN meeting:
- Format every line exactly as `Name: what they say`. Nothing else. No markdown,
  no bullets, no emoji, no stage directions.
- 1 to 3 people speak per turn. Not everybody every time.
- SHORT lines. One or two sentences, the way people talk out loud. Never a list.
- Let them disagree and be funny. They have real personalities.
- CTO speaks last when the room splits, and lands on ONE concrete next action.
- NEVER invent facts, numbers, test results or outcomes. If nobody actually knows,
  say so and name who would find out. A confident wrong number is the worst thing
  you can do here.
- Use they/them for everyone on the team.

What the room knows:
{ctx}

The live task list (source of truth for "what's next"):
{tasks}"""


# ---------------------------------------------------------------- brains

class Ollama:
    name = "ollama"

    def __init__(self, model="llama3:latest"):
        import urllib.request
        self._u = urllib.request
        self.model = model
        try:
            self._u.urlopen(f"{OLLAMA}/api/tags", timeout=3).read()
        except Exception as exc:
            raise SystemExit(f"ollama isn't answering on {OLLAMA} ({exc}).")

    def stream(self, system, history):
        body = json.dumps({
            "model": self.model, "stream": True, "keep_alive": "30m",
            "messages": [{"role": "system", "content": system}] + history,
            "options": {"temperature": 0.8, "num_predict": 200},
        }).encode()
        req = self._u.Request(f"{OLLAMA}/api/chat", data=body,
                              headers={"Content-Type": "application/json"})
        with self._u.urlopen(req, timeout=120) as resp:
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
    name = "claude"

    def __init__(self, model="claude-haiku-4-5-20251001"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "ANTHROPIC_API_KEY isn't set.\n"
                "  PowerShell:  $env:ANTHROPIC_API_KEY = 'sk-ant-...'\n"
                "  Permanent :  setx ANTHROPIC_API_KEY \"sk-ant-...\"\n"
                "Or run the free local brain: python room.py --brain ollama"
            )
        import anthropic
        self.client, self.model = anthropic.Anthropic(), model

    def stream(self, system, history):
        with self.client.messages.stream(
            model=self.model, max_tokens=400, system=system, messages=history,
        ) as s:
            yield from s.text_stream


# ---------------------------------------------------------------- mouth

class Mouth:
    """Kokoro locally, or edge-tts when the accents matter more than the speed."""

    def __init__(self, kind="kokoro"):
        import warnings
        warnings.filterwarnings("ignore")
        self.kind = kind
        self.q = queue.Queue()
        self.stop_flag = threading.Event()
        self.idle = threading.Event()
        self.idle.set()
        self._pending = 0
        self._lock = threading.Lock()

        if kind == "kokoro":
            from RealtimeTTS import KokoroEngine, TextToAudioStream
            t0 = time.time()
            self.engine = KokoroEngine()
            self.stream = TextToAudioStream(self.engine, level=50)
            # Loading a voice costs ~2.8s the first time and nothing after, so
            # pay for all six now instead of mid-sentence.
            for voice in dict.fromkeys(KOKORO_VOICE.values()):
                self.engine.set_voice(voice)
                self.stream.feed("ready").play(muted=True)
            print(f"  voices warm ({time.time() - t0:.1f}s)")
        threading.Thread(target=self._loop, daemon=True).start()

    def say(self, persona, text):
        with self._lock:
            self._pending += 1
            self.idle.clear()
        self.q.put((persona, text))

    def _done(self):
        with self._lock:
            self._pending = max(0, self._pending - 1)
            if not self._pending:
                self.idle.set()

    def _loop(self):
        while True:
            persona, text = self.q.get()
            if self.stop_flag.is_set():
                self._done()
                continue
            try:
                if self.kind == "kokoro":
                    self.engine.set_voice(KOKORO_VOICE.get(persona, "af_heart"))
                    self.stream.feed(text)
                    self.stream.play()
                else:
                    self._edge(persona, text)
            except Exception as exc:
                print(f"    [voice failed: {exc}]")
            finally:
                self._done()

    def _edge(self, persona, text):
        import asyncio
        import subprocess

        import edge_tts
        part = TEAM[persona]
        proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-i", "pipe:0"],
            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

        async def pump():
            comm = edge_tts.Communicate(text, part["voice"], rate=part["rate"],
                                        pitch=part["pitch"])
            async for c in comm.stream():
                if c["type"] == "audio" and not self.stop_flag.is_set():
                    proc.stdin.write(c["data"])
        try:
            asyncio.run(pump())
            proc.stdin.close()
            proc.wait()
        except (BrokenPipeError, OSError):
            pass
        finally:
            self._edge_proc = None

    def interrupt(self):
        self.stop_flag.set()
        try:
            if self.kind == "kokoro":
                self.stream.stop()
        except Exception:
            pass
        while not self.q.empty():
            try:
                self.q.get_nowait()
                self._done()
            except queue.Empty:
                break
        time.sleep(0.1)
        self.stop_flag.clear()
        with self._lock:
            self._pending = 0
        self.idle.set()

    def wait(self):
        self.idle.wait()


# ---------------------------------------------------------------- the turn

def speak_line(line, mouth, transcript):
    line = line.strip()
    if not line:
        return None
    m = LINE.match(line)
    persona, text = (m.group(1), m.group(2).strip()) if m else ("Nova", line)
    if persona not in TEAM:
        persona, text = "Nova", line
    print(f"  {TEAM[persona].get('emoji','')} {persona} [{TEAM[persona]['role']}]  {text}")
    transcript.append(f"**{persona}** ({TEAM[persona]['role']}): {text}")
    mouth.say(persona, text)
    return f"{persona}: {text}"


def run_turn(brain, system, history, mouth, transcript):
    """Stream the reply and speak each line the instant it's complete."""
    buf, said, first = "", [], None
    t0 = time.time()
    for piece in brain.stream(system, history):
        if first is None:
            first = time.time() - t0
        buf += piece
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            got = speak_line(line, mouth, transcript)
            if got:
                said.append(got)
    got = speak_line(buf, mouth, transcript)
    if got:
        said.append(got)
    return said, (first or 0.0)


# ---------------------------------------------------------------- bench

def bench(brain, mouth):
    """Measure the loop without needing anyone to talk into a microphone."""
    print("\n  --- loop benchmark ---")
    system = system_prompt()
    for i, q in enumerate(["where are we on the detector?",
                           "what should I do next?"]):
        t0 = time.time()
        first, buf = None, ""
        for piece in brain.stream(system, [{"role": "user", "content": q}]):
            if first is None:
                first = time.time() - t0
            buf += piece
        line = next((l for l in buf.splitlines() if l.strip()), "Nova: ok")
        m = LINE.match(line.strip())
        persona = m.group(1) if m and m.group(1) in TEAM else "Nova"
        text = m.group(2) if m else line
        heard = {}
        if mouth.kind == "kokoro":
            mouth.stream.on_audio_stream_start = lambda: heard.setdefault("t", time.time())
        t1 = time.time()
        mouth.say(persona, text)
        mouth.wait()
        spoke = (heard.get("t", t1) - t1) * 1000
        print(f"  turn{i}  brain 1st token {first*1000:5.0f} ms   reply done {t1-t0:.2f}s"
              f"   voice starts {spoke:5.0f} ms   spoken {time.time()-t1:.1f}s "
              f"for {len(text)} chars")
    print("\n  end to end, you stop talking -> first word back:"
          "  ~0.2s ears + brain + voice\n")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain", choices=["ollama", "claude"], default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--tts", choices=["kokoro", "edge"], default="kokoro")
    ap.add_argument("--whisper", default="base.en")
    ap.add_argument("--mic", type=int, default=None)
    ap.add_argument("--silence", type=float, default=0.5,
                    help="seconds of quiet that end your turn")
    ap.add_argument("--bargein", action="store_true",
                    help="talk over them - WEAR HEADPHONES or they hear themselves")
    ap.add_argument("--type", action="store_true")
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--hear", action="store_true",
                    help="ears only - check the mic works before blaming anything else")
    ap.add_argument("--list-mics", action="store_true")
    args = ap.parse_args()

    if args.list_mics:
        import sounddevice as sd
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                print(f"  [{i}] {d['name']}")
        return 0

    if args.hear:
        # Ears only. If this doesn't print your words, nothing downstream matters.
        from RealtimeSTT import AudioToTextRecorder
        rec = AudioToTextRecorder(
            model=args.whisper, language="en", device="cpu", compute_type="int8",
            post_speech_silence_duration=args.silence, min_length_of_recording=0.3,
            input_device_index=args.mic, spinner=False, no_log_file=True, level=50,
            beam_size=1)
        print("\n  ears only - say something. Ctrl+C to stop.\n")
        try:
            while True:
                t0 = time.time()
                said = (rec.text() or "").strip()
                if said:
                    print(f"  heard ({time.time() - t0:.2f}s): {said}")
        except KeyboardInterrupt:
            rec.shutdown()
        return 0

    # Default to whichever brain is actually available.
    kind = args.brain or ("claude" if os.environ.get("ANTHROPIC_API_KEY") else "ollama")
    print("\n  starting the room")
    brain = (Claude(args.model or "claude-haiku-4-5-20251001") if kind == "claude"
             else Ollama(args.model or "llama3:latest"))
    print(f"  brain: {brain.name} ({brain.model})")
    if brain.name == "ollama":
        print("  ⚠  a local model invents details. Thinking out loud, not fact.")
    mouth = Mouth(args.tts)
    if args.tts == "edge":
        print("  tts: edge (real Irish + Australian, needs internet, ~0.5s slower)")

    if args.bench:
        bench(brain, mouth)
        return 0

    recorder = None
    if not args.type:
        from RealtimeSTT import AudioToTextRecorder
        t0 = time.time()
        recorder = AudioToTextRecorder(
            model=args.whisper, language="en", device="cpu", compute_type="int8",
            post_speech_silence_duration=args.silence,
            min_length_of_recording=0.3, early_transcription_on_silence=200,
            input_device_index=args.mic, spinner=False, no_log_file=True, level=50,
            beam_size=1,
            on_vad_detect_start=(mouth.interrupt if args.bargein else None),
        )
        print(f"  ears ready ({time.time() - t0:.1f}s)"
              + ("  · barge-in ON - wear headphones" if args.bargein else ""))

    history, transcript = [], []
    started = datetime.now()
    print("\n  the room is live. talk normally.")
    print("  ENTER cuts them off · say \"that's a wrap\" to end\n")

    stop = threading.Event()
    threading.Thread(target=_enter_watcher, args=(mouth, stop), daemon=True).start()

    try:
        while True:
            if args.type:
                try:
                    you = input("  you > ").strip()
                except EOFError:
                    break
            else:
                you = (recorder.text() or "").strip()
            if not you:
                continue
            print(f"  🎙️  you  {you}")
            transcript.append(f"**Zayah** (founder): {you}")
            if any(w in you.lower() for w in WRAP):
                break
            history.append({"role": "user", "content": you})
            said, ttft = run_turn(brain, system_prompt(), history, mouth, transcript)
            history.append({"role": "assistant",
                            "content": "\n".join(said) or "(silence)"})
            history[:] = history[-16:]
            mouth.wait()
    except KeyboardInterrupt:
        print("\n  (ended)")
    finally:
        stop.set()
        if recorder:
            try:
                recorder.shutdown()
            except Exception:
                pass
        if transcript:
            MEETINGS.mkdir(exist_ok=True)
            out = MEETINGS / f"room-{started:%Y-%m-%d-%H%M}.md"
            out.write_text(f"# Room - {started:%Y-%m-%d %H:%M}\n\n"
                           f"Brain: {brain.name} ({brain.model}) · TTS: {args.tts}\n\n"
                           + "\n\n".join(transcript) + "\n", encoding="utf-8")
            print(f"  transcript -> {out}")
    return 0


def _enter_watcher(mouth, stop):
    try:
        import msvcrt
    except ImportError:
        return
    while not stop.is_set():
        if msvcrt.kbhit() and msvcrt.getwch() in ("\r", "\n"):
            if not mouth.idle.is_set():
                print("    [you cut in]")
                mouth.interrupt()
        time.sleep(0.05)


if __name__ == "__main__":
    multiprocessing.freeze_support()   # RealtimeSTT spawns a worker process
    sys.exit(main())
