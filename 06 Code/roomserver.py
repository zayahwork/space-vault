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
            return self._send(200, json.dumps({"roster": roster(),
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
        self._send(404, "{}")


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
    history, transcript = [], []
    started = datetime.now()
    while True:
        you = None
        if recorder is not None:
            # Blocks until you stop talking. Typed input jumps the queue.
            def listen():
                try:
                    TURNS.put(("voice", recorder.text()))
                except Exception:
                    pass
            threading.Thread(target=listen, daemon=True).start()
        item = TURNS.get()
        you = item[1] if isinstance(item, tuple) else item
        you = (you or "").strip()
        if not you:
            continue

        BUS.emit(t="you", text=you)
        transcript.append(f"**Zayah** (founder): {you}")
        if any(w in you.lower() for w in room.WRAP):
            BUS.emit(t="state", room="closed")
            break

        BUS.emit(t="state", room="thinking")
        history.append({"role": "user", "content": you})
        system = room.system_prompt() + brain_context()

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
        BUS.emit(t="state", room="listening")

    if transcript:
        MEETINGS.mkdir(exist_ok=True)
        out = MEETINGS / f"room-{started:%Y-%m-%d-%H%M}.md"
        out.write_text(f"# Room - {started:%Y-%m-%d %H:%M}\n\n" +
                       "\n\n".join(transcript) + "\n", encoding="utf-8")
        print(f"  transcript -> {out}")


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
    MOUTH.say(persona, text)
    return f"{persona}: {text}"


def main():
    global MOUTH, BRAIN_LABEL
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain", choices=["ollama", "claude"], default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--whisper", default="base.en")
    ap.add_argument("--mic", type=int, default=None)
    ap.add_argument("--silence", type=float, default=0.5)
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

    recorder = None
    if not args.no_mic:
        from RealtimeSTT import AudioToTextRecorder
        last = [0.0]

        def mic_chunk(chunk):
            now = time.time()
            if now - last[0] < 0.05:
                return
            last[0] = now
            BUS.emit(t="mic", rms=round(rms_of(chunk), 3))

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
