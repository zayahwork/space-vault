"""
roomserver.py - the war room, with faces.

room.py could hear you and answer. This adds the thing you actually asked for:
seeing them. Six teammates seated as stations on an orbit, the founder at the
focus, and every ring driven by REAL audio - not an animation that pretends.

    mic -> RealtimeSTT -> brain (+ each person's memory) -> Kokoro -> speakers
                             |
                             +---- events over SSE ----> the browser

WHAT IS REAL HERE, AND WHY THAT MATTERS
Every moving thing on that screen is measured, because a screen that invents
motion is how you end up trusting a demo instead of a system:
  * the ring around a speaker  = RMS of the actual audio chunks being played
  * the ring around YOU        = RMS of the actual microphone input
  * the words appearing as you talk = RealtimeSTT's live partial transcript
  * a still ring               = genuinely silent. Not "idle animation".
Nothing on the page animates without a number behind it.

Usage:
  python roomserver.py                 # opens http://127.0.0.1:8770
  python roomserver.py --brain claude  # sharper room (ANTHROPIC_API_KEY)
  python roomserver.py --no-open
"""

import argparse
import json
import math
import multiprocessing
import os
import queue
import re
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brain  # noqa: E402  - per-person memory
import room  # noqa: E402  - Ollama/Claude brains and the persona prompt live there
from worker import WorkQueue  # noqa: E402

TEAM = room.TEAM
WORK_RE = re.compile(r"\[WORK\]\s*(.+?)\s*$", re.I)
UI_DIR = HERE / "room_ui"
BRAINS = HERE / "brains"
MEETINGS = HERE / "meetings"
PORT = 8770

# Where each person sits. Angles run around an ellipse; the founder is at its
# FOCUS, not its centre - which is where a satellite's primary actually sits.
SEATS = ["Sable", "Rook", "Fitz", "Tim", "Nova", "Vega"]

# What makes this a room of colleagues rather than six chatbots taking turns.
ROOM_RULES = """

HOW THIS ROOM WORKS
- You are all senior and you all understand each other's jobs. Sable can read Rook's
  code, Rook can poke holes in Sable's method, Vega knows what a stale catalog entry
  is, Tim will check anyone's citation. Never explain your own field as though the
  others were outsiders.
- ARGUE when you disagree. The point of six people is that the answer nobody had
  alone beats the answer one person defends. Say "I think that's wrong, because..."
  and mean it. Then converge - the room does not end split.
- You work together around the clock and you like each other. Warmth and jokes are
  welcome. They never come at the cost of a real risk going unsaid.
- Get to know Zayah. Ask him something occasionally. Remember what he tells you.

CLAIMING A JOB
When the room agrees something should actually get built, exactly ONE person claims
it and ends their line with a job tag:

    Rook: I'll take that one. [WORK] add gap detection and retry to supgp_archive.py

- ONE job tag per turn, from ONE person. Never two. If two things are needed, claim
  the first and say the second is next.
- Only tag real work on files, code or data. Never for thinking, opinions, or
  anything you can answer out loud.
- Write it as one imperative sentence naming the file or thing to change.
- If nothing needs building, tag nothing. Most turns should tag nothing."""


# ---------------------------------------------------------------- event bus

class Bus:
    """Fan-out to every connected browser. Slow clients get dropped, not queued."""

    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()
        self.history = []

    def subscribe(self):
        q = queue.Queue(maxsize=200)
        with self.lock:
            self.clients.append(q)
        return q

    def drop(self, q):
        with self.lock:
            if q in self.clients:
                self.clients.remove(q)

    def emit(self, **event):
        event.setdefault("ts", time.time())
        if event["t"] in ("said", "you"):
            self.history.append(event)
            del self.history[:-200]
        data = json.dumps(event)
        with self.lock:
            for q in list(self.clients):
                try:
                    q.put_nowait(data)
                except queue.Full:
                    self.clients.remove(q)


BUS = Bus()


SHUTDOWN = threading.Event()

# --- keeping the room from talking to itself ------------------------------
#
# A soundbar plus an open mic is a feedback loop: they speak, the mic hears it,
# the room treats its own voice as the founder, answers itself, and never stops.
# Headphones fix it perfectly and nobody wants to wear headphones in their own
# office, so this is defended twice instead:
#
#   1. TEXT  - anything recognised that closely matches something we just said
#              is thrown away. This is the one that actually breaks the loop,
#              because it does not care how loud the room is.
#   2. LEVEL - while they are talking, the mic has to be clearly louder than the
#              bleed coming back off the speakers before it counts as you. You
#              are a foot from the mic; the soundbar is across the room.
#
# The founder always wins. The moment level+text agree that it is really him,
# whoever is speaking gets cut off mid-word.

RECENT_SAID = []          # (normalised text, when we said it)
ECHO_WINDOW_S = 25.0
ECHO_OVERLAP = 0.45
_word = re.compile(r"[a-z0-9']+")


def _norm(text):
    return set(_word.findall((text or "").lower()))


def remember_said(text):
    RECENT_SAID.append((_norm(text), time.time()))
    del RECENT_SAID[:-14]


def is_echo(text):
    """True if this is almost certainly our own voice coming back round."""
    words = _norm(text)
    if len(words) < 2:
        return True                       # a stray syllable is never a sentence
    now = time.time()
    for said, when in RECENT_SAID:
        if now - when > ECHO_WINDOW_S or not said:
            continue
        shared = len(words & said) / max(1, min(len(words), len(said)))
        if shared >= ECHO_OVERLAP:
            return True
    return False


def rms_of(pcm_bytes):
    """0..1 loudness of a raw int16 chunk. The number the rings are drawn from."""
    if not pcm_bytes:
        return 0.0
    import numpy as np
    a = np.frombuffer(pcm_bytes, dtype=np.int16)
    if a.size == 0:
        return 0.0
    val = float(np.sqrt(np.mean(a.astype(np.float32) ** 2))) / 32768.0
    # Speech RMS lives in a narrow band near the bottom; a log curve makes the
    # ring track what you HEAR rather than hugging zero.
    return max(0.0, min(1.0, math.log10(1 + 40 * val) / math.log10(41)))


# ---------------------------------------------------------------- the mouth

class Mouth:
    """Kokoro, one line at a time, reporting real amplitude as it plays."""

    def __init__(self):
        import warnings
        warnings.filterwarnings("ignore")
        from RealtimeTTS import KokoroEngine, TextToAudioStream
        t0 = time.time()
        self.engine = KokoroEngine()
        self.stream = TextToAudioStream(self.engine, level=50)
        for voice in dict.fromkeys(room.KOKORO_VOICE.values()):
            self.engine.set_voice(voice)
            self.stream.feed("ready").play(muted=True)
        print(f"  voices warm ({time.time() - t0:.1f}s)")

        self.q = queue.Queue()
        self.stop_flag = threading.Event()
        self.idle = threading.Event()
        self.idle.set()
        self._pending = 0
        self._lock = threading.Lock()
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
            last = [0.0]

            def on_chunk(chunk):
                # Throttle to ~30fps; the browser can't use more and the queue can.
                now = time.time()
                if now - last[0] < 0.033:
                    return
                last[0] = now
                BUS.emit(t="level", who=persona, rms=round(rms_of(chunk), 3))

            try:
                BUS.emit(t="speak_start", who=persona)
                self.engine.set_voice(room.KOKORO_VOICE.get(persona, "af_heart"))
                self.stream.feed(text)
                self.stream.play(on_audio_chunk=on_chunk)
            except Exception as exc:
                print(f"    [voice failed: {exc}]")
            finally:
                BUS.emit(t="speak_end", who=persona)
                BUS.emit(t="level", who=persona, rms=0.0)
                self._done()

    def interrupt(self):
        self.stop_flag.set()
        try:
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
        BUS.emit(t="cut")

    def wait(self):
        self.idle.wait()


# ---------------------------------------------------------------- the brains

def brain_context():
    """Each person's banked memory, so the room is smarter than it was yesterday."""
    if not BRAINS.exists():
        return ""
    out = []
    for name in TEAM:
        f = BRAINS / f"{name}.md"
        if not f.exists():
            continue
        lessons = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines()
                   if ln.strip().startswith("- [") and "[retired]" not in ln]
        if lessons:
            out.append(f"{name} has previously learned:\n" + "\n".join(lessons))
    if not out:
        return ""
    return ("\n\nWhat each person already knows from earlier sessions. Use it, and "
            "keep the proven/hypothesis distinction when you refer to it:\n\n"
            + "\n\n".join(out))


# ---------------------------------------------------------------- http

class Handler(BaseHTTPRequestHandler):
    server_version = "room/1.0"

    def log_message(self, *a):
        pass                                    # the console belongs to the meeting

    def _send(self, code, body, ctype="application/json"):
        body = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.path = self.path.split("?", 1)[0] or "/"    # query strings are the UI's
        if self.path.startswith("/events"):
            return self._events()
        if self.path in ("/", "/index.html"):
            return self._file("index.html", "text/html; charset=utf-8")
        if self.path == "/app.css":
            return self._file("app.css", "text/css")
        if self.path == "/app.js":
            return self._file("app.js", "text/javascript")
        if self.path == "/roster":
            return self._send(200, json.dumps(roster()))
        if self.path == "/history":
            # Plain polling snapshot of the room. Screenshot QA can't hold an SSE
            # stream open - a browser never finishes loading while one is live.
            return self._send(200, json.dumps({"roster": roster(), "board": board(),
                                               "events": BUS.history[-60:]}))
        self._send(404, "{}")

    def _file(self, name, ctype):
        p = UI_DIR / name
        if not p.exists():
            return self._send(404, f"missing {name}")
        self._send(200, p.read_bytes(), ctype)

    def _events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        q = BUS.subscribe()
        try:
            self.wfile.write(f"data: {json.dumps(roster())}\n\n".encode())
            for ev in BUS.history[-40:]:
                self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode())
            self.wfile.flush()
            while True:
                try:
                    data = q.get(timeout=15)
                    self.wfile.write(f"data: {data}\n\n".encode())
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")     # keep the pipe warm
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            BUS.drop(q)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or "{}") if n else {}
        if self.path == "/say" and body.get("text"):
            TURNS.put(body["text"].strip())
            return self._send(200, '{"ok":true}')
        if self.path == "/cut":
            MOUTH.interrupt()
            return self._send(200, '{"ok":true}')
        if self.path == "/end":
            # Ending the call has to actually end it. The old build left a python
            # process holding the microphone after the tab was closed.
            self._send(200, '{"ok":true}')
            BUS.emit(t="state", room="closed")
            threading.Thread(target=end_call, daemon=True).start()
            return
        self._send(404, "{}")


def calibrate(mouth, device_index):
    """Measure the actual bleed from your speakers into your mic, then your voice.

    A soundbar in the same room as an open mic is the whole problem. This says
    plainly whether you can be told apart from it, and what --gate to use.
    """
    import numpy as np
    import sounddevice as sd

    levels = {"peak": 0.0}

    def watch(seconds, label):
        levels["peak"] = 0.0
        end = time.time() + seconds

        def cb(indata, frames, t, status):
            levels["peak"] = max(levels["peak"], rms_of(bytes(indata)))

        with sd.RawInputStream(samplerate=16000, blocksize=480, dtype="int16",
                               channels=1, device=device_index, callback=cb):
            while time.time() < end:
                time.sleep(0.05)
        print(f"  {label:<34} {levels['peak']:.3f}")
        return levels["peak"]

    print("\n  CALIBRATION - stay quiet for the first two steps.\n")
    time.sleep(0.5)
    quiet = watch(2.0, "room with nobody talking")

    mouth.say("Rook", "Testing one two. This is what the speakers sound like to "
                      "your microphone when nobody else is talking.")
    time.sleep(0.4)
    bleed = watch(5.0, "speakers bleeding into the mic")
    mouth.wait()

    print("\n  Now TALK NORMALLY for five seconds, at your usual distance.\n")
    time.sleep(0.7)
    voice = watch(5.0, "you talking")

    print(f"\n  quiet {quiet:.3f}   speakers {bleed:.3f}   you {voice:.3f}")
    if voice <= bleed * 1.25:
        print("\n  ⚠ Your voice is not clearly louder than your speakers.")
        print("    Nothing in software can reliably separate them at this ratio.")
        print("    Turn the soundbar down, move the mic closer, or use headphones.")
        return 1
    gate = round(bleed + (voice - bleed) * 0.45, 2)
    print(f"\n  Use:  jarvis --gate {gate}")
    print(f"  (above the speakers at {bleed:.2f}, below you at {voice:.2f})")
    return 0


def end_call():
    """Hang up for real: stop the voices, release the mic, exit the process."""
    time.sleep(0.3)                       # let the browser get the last event
    try:
        MOUTH.interrupt()
    except Exception:
        pass
    SHUTDOWN.set()
    save_transcript()
    print("\n  call ended.")
    os._exit(0)                           # threads hold the mic; exit decisively


TRANSCRIPT = []
STARTED = datetime.now()


def save_transcript():
    if not TRANSCRIPT:
        return
    MEETINGS.mkdir(exist_ok=True)
    out = MEETINGS / f"room-{STARTED:%Y-%m-%d-%H%M}.md"
    out.write_text(f"# Room - {STARTED:%Y-%m-%d %H:%M}\n\n" +
                   "\n\n".join(TRANSCRIPT) + "\n", encoding="utf-8")
    print(f"  transcript -> {out}")


def board():
    """What goes on the screen at the head of the table.

    Every row is read off a real file at the moment it is asked for. If a number
    cannot be read, its row is left out rather than guessed - a board that
    invents a figure is worse than a board with a gap in it.
    """
    rows = []

    try:
        b = json.loads((HERE / "budget.json").read_text(encoding="utf-8"))
        spent = sum(e["hours"] * TEAM[e["who"]]["salary"] / 2080 for e in b["ledger"])
        rows.append({"k": "budget used",
                     "v": f"${spent:,.0f} / ${b['labor_pool']:,.0f}"})
    except Exception:
        pass

    try:
        log = (HERE / "supgp_archive" / "health.jsonl").read_text(encoding="utf-8")
        last = json.loads(log.strip().splitlines()[-1])
        rows.append({"k": "archive",
                     "v": f"{last['total_rows']:,} rows"
                          + ("" if last["ok"] else "  GAP"),
                     "hot": not last["ok"]})
    except Exception:
        pass

    lessons = 0
    if BRAINS.exists():
        for f in BRAINS.glob("*.md"):
            lessons += sum(1 for ln in f.read_text(encoding="utf-8").splitlines()
                           if ln.strip().startswith("- [") and "[retired]" not in ln)
    rows.append({"k": "lessons banked", "v": str(lessons)})

    try:
        tasks = TASKS_FILE.read_text(encoding="utf-8")
        pain = re.search(r"unprompted:\s*\*\*(\d+)\s*/\s*(\d+)\*\*", tasks)
        ask = re.search(r"asks:\s*\*\*(\d+)\s*/\s*(\d+)\*\*", tasks)
        if pain:
            rows.append({"k": "pain described", "v": f"{pain.group(1)} / {pain.group(2)}",
                         "hot": pain.group(1) == "0"})
        if ask:
            rows.append({"k": "can I try it?", "v": f"{ask.group(1)} / {ask.group(2)}",
                         "hot": ask.group(1) == "0"})
    except Exception:
        pass

    return {"t": "board", "title": "ON THE BOARD", "rows": rows[:5]}


def roster():
    people = []
    for i, name in enumerate(SEATS):
        p = TEAM[name]
        lessons = 0
        f = BRAINS / f"{name}.md"
        if f.exists():
            lessons = sum(1 for ln in f.read_text(encoding="utf-8").splitlines()
                          if ln.strip().startswith("- [") and "[retired]" not in ln)
        people.append({"name": name, "role": p["role"], "seat": i,
                       "salary": p["salary"], "lessons": lessons})
    return {"t": "roster", "people": people, "brain": BRAIN_LABEL}


# ---------------------------------------------------------------- the loop

TURNS = queue.Queue()
MOUTH = None
BRAIN_LABEL = ""


def meeting_loop(brain, recorder):
    history = []
    transcript = TRANSCRIPT
    while not SHUTDOWN.is_set():
        if recorder is not None:
            # Blocks until you stop talking. Typed input jumps the queue.
            def listen():
                try:
                    TURNS.put(("voice", recorder.text()))
                except Exception:
                    pass
            threading.Thread(target=listen, daemon=True).start()
        item = TURNS.get()
        typed = not isinstance(item, tuple)
        you = (item if typed else item[1] or "").strip()
        if not you:
            continue

        # Typed input is unambiguously you. Heard input might be the soundbar.
        if not typed and is_echo(you):
            print(f"  (ignored our own voice: {you[:60]})")
            continue

        BUS.emit(t="you", text=you)
        transcript.append(f"**Zayah** (founder): {you}")
        if any(w in you.lower() for w in room.WRAP):
            BUS.emit(t="state", room="closed")
            break

        BUS.emit(t="state", room="thinking")
        history.append({"role": "user", "content": you})
        system = room.system_prompt() + ROOM_RULES + brain_context()

        buf, said = "", []
        try:
            for piece in brain.stream(system, history):
                buf += piece
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    got = emit_line(line, transcript)
                    if got:
                        said.append(got)
            got = emit_line(buf, transcript)
            if got:
                said.append(got)
        except Exception as exc:
            BUS.emit(t="error", text=str(exc)[:200])

        history.append({"role": "assistant",
                        "content": "\n".join(said) or "(silence)"})
        history[:] = history[-16:]
        MOUTH.wait()
        BUS.emit(**board())          # numbers may have moved while they talked
        BUS.emit(t="state", room="listening")

    save_transcript()


def emit_line(line, transcript):
    line = line.strip()
    if not line:
        return None
    m = room.LINE.match(line)
    persona, text = (m.group(1), m.group(2).strip()) if m else ("Nova", line)
    if persona not in TEAM:
        persona, text = "Nova", line
    print(f"  {TEAM[persona].get('emoji','')} {persona}  {text}")
    transcript.append(f"**{persona}** ({TEAM[persona]['role']}): {text}")
    BUS.emit(t="said", who=persona, role=TEAM[persona]["role"], text=text)
    remember_said(text)          # so we recognise this coming back off the wall
    MOUTH.say(persona, text)
    return f"{persona}: {text}"


def main():
    global MOUTH, BRAIN_LABEL
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain", choices=["ollama", "claude"], default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--whisper", default="base.en")
    ap.add_argument("--mic", type=int, default=None)
    # How long you have to stop talking before they answer. This is the single
    # biggest lever on whether the room feels like a person or a walkie-talkie -
    # much below 0.35 and it starts interrupting your mid-sentence pauses.
    ap.add_argument("--silence", type=float, default=0.35)
    ap.add_argument("--gate", type=float, default=0.42,
                    help="how loud you must be to cut them off (0-1). Lower it if "
                         "they ignore you, raise it if the speakers cut them off.")
    ap.add_argument("--calibrate", action="store_true",
                    help="play a line and print what the mic hears back, to set --gate")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-mic", action="store_true", help="type-only, no listening")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    kind = args.brain or ("claude" if os.environ.get("ANTHROPIC_API_KEY") else "ollama")
    print("\n  opening the room")
    brain = (room.Claude(args.model or "claude-haiku-4-5-20251001") if kind == "claude"
             else room.Ollama(args.model or "llama3:latest"))
    BRAIN_LABEL = f"{brain.name} · {brain.model}"
    print(f"  brain: {BRAIN_LABEL}")
    if brain.name == "ollama":
        print("  ⚠  a local model invents details. Thinking out loud, not fact.")

    MOUTH = Mouth()

    if args.calibrate:
        return calibrate(MOUTH, args.mic)

    recorder = None
    if not args.no_mic:
        from RealtimeSTT import AudioToTextRecorder
        last = [0.0]

        loud_run = [0]

        def mic_chunk(chunk):
            level = rms_of(chunk)
            now = time.time()
            if now - last[0] >= 0.05:
                last[0] = now
                BUS.emit(t="mic", rms=round(level, 3))

            # You are the boss: the moment you speak, they stop mid-word. Three
            # consecutive loud chunks (~90ms) so a door slam doesn't do it, and
            # the bar is set above what the speakers bleed back into the mic.
            if MOUTH.idle.is_set():
                loud_run[0] = 0
                return
            if level >= args.gate:
                loud_run[0] += 1
                if loud_run[0] >= 3:
                    loud_run[0] = 0
                    print("  (you cut in - stopping)")
                    MOUTH.interrupt()
            else:
                loud_run[0] = 0

        t0 = time.time()
        recorder = AudioToTextRecorder(
            model=args.whisper, language="en", device="cpu", compute_type="int8",
            post_speech_silence_duration=args.silence, min_length_of_recording=0.3,
            early_transcription_on_silence=200, input_device_index=args.mic,
            spinner=False, no_log_file=True, level=50, beam_size=1,
            enable_realtime_transcription=True, realtime_model_type="tiny.en",
            realtime_processing_pause=0.25,
            on_recorded_chunk=mic_chunk,
            on_recording_start=lambda: BUS.emit(t="state", room="hearing"),
            on_recording_stop=lambda: BUS.emit(t="state", room="thinking"),
            on_realtime_transcription_update=lambda txt: BUS.emit(t="partial", text=txt),
        )
        print(f"  ears ready ({time.time() - t0:.1f}s)")

    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{args.port}/"
    print(f"\n  the room is at {url}\n")
    if not args.no_open:
        webbrowser.open(url)

    BUS.emit(t="state", room="listening")
    try:
        meeting_loop(brain, recorder)
    except KeyboardInterrupt:
        print("\n  (closed)")
    finally:
        if recorder:
            try:
                recorder.shutdown()
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main())
