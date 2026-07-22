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
import cc_brain  # noqa: E402  - the free brain: Claude Code, no API key
import room  # noqa: E402  - Ollama/Claude brains and the persona prompt live there
from worker import WorkQueue  # noqa: E402

TEAM = room.TEAM
WORK_RE = re.compile(r"\[WORK\]\s*(.+?)\s*$", re.I)
# Where a new speaker starts partway through a line, with no newline before it.
NEXT_SPEAKER = re.compile(
    r"(?:(?<=[.!?\"'’”])|(?<=\s))(?:" + "|".join(room.TEAM) + r")\s*:\s")
UI_DIR = HERE / "room_ui"
BRAINS = HERE / "brains"
MEETINGS = HERE / "meetings"
PORT = 8770

# Where each person sits. Three down each side of the table, and the CTO at the
# head, facing the founder down its length. The CTO used to have a voice and no
# chair: they spoke, and the screen lit nobody, because seats.get("CTO") was
# undefined. Everyone who can talk now has somewhere to talk from.
SEATS = ["Sable", "Rook", "Fitz", "Tim", "Nova", "Vega", "CTO"]
HEAD = "CTO"          # chairs the meeting, so they sit facing you down the table

# What makes this a room of colleagues rather than six chatbots taking turns.
def seniority():
    """Who outranks whom, read off team.json rather than invented.

    Salary is the only real seniority signal in the file, so it is the one used -
    it already encodes the raises and the hires the founder actually made, which
    means the pecking order updates itself when he changes someone's pay. The
    CTO is placed first regardless: they chair the meeting and their salary is 0
    because they're founder-equivalent, so ranking them on pay would put the
    person running the room at the bottom of it.
    """
    others = sorted((n for n in SEATS if n != HEAD),
                    key=lambda n: (-TEAM[n].get("salary", 0), n))
    return ([HEAD] if HEAD in SEATS else []) + others


def rank_map():
    """name -> position in the pecking order. 0 speaks first."""
    return {n: i for i, n in enumerate(seniority())}


def order_rule():
    ranked = seniority()
    lines = "\n".join(
        f"  {i}. {n} [{TEAM[n]['role']}]"
        + ("  - chairs the meeting" if n == HEAD else
           f"  - ${TEAM[n].get('salary', 0):,}")
        for i, n in enumerate(ranked, 1))
    return f"""

WHO SPEAKS, AND IN WHAT ORDER
This is a meeting, not a scrum of people shouting over each other. Nobody ever
interrupts anybody. One person finishes their line completely, then the next
one starts.

When more than one person speaks in a turn, they go in THIS order, most senior
first, always:

{lines}

- Skip anyone who has nothing to add - seniority decides ORDER, never whether
  somebody gets to speak. A junior person with the answer still gives it.
- Never go back up the list inside one turn. If {ranked[-1]} has spoken, the turn
  is over; whatever {ranked[0]} thought of belongs in the next one.
- The one exception: {HEAD} may add a FINAL line to land a decision when the room
  has split. Opening the discussion and closing it is the chair's job.
- On a plain greeting, two or three of the most senior answer it and the rest
  stay quiet. Seven people all saying hello is not a meeting, it's a roll call.

ROOM_RULES_TAIL"""


ROOM_RULES = """

EVERY LINE STARTS WITH A NAME
The first characters of every single line are a speaker's name and a colon. No
preamble, no greeting, no opening summary, not even for the first line of your
reply. A line without a name in front of it comes out of the wrong person's
mouth, because the room has to decide who is speaking before it can speak.

SITTING AT THIS TABLE YOU HAVE NO TOOLS
You cannot read a file, run a command or look anything up while you are talking.
Everything you know is already written above. So never say you are going to go
and check something, and never narrate yourself doing it - either you know it, or
you say plainly that you don't and claim the job so it actually gets done.

Speech only. No stage directions, no describing looks exchanged or people
leaning back, no asterisks. If it isn't a sentence somebody says out loud, it
does not belong in your output.

HOW THIS ROOM WORKS
- You are all senior and you all understand each other's jobs. Sable can read Rook's
  code, Rook can poke holes in Sable's method, Vega knows what a stale catalog entry
  is, Tim will check anyone's citation. Never explain your own field as though the
  others were outsiders.
- ARGUE when you disagree. The point of six people is that the answer nobody had
  alone beats the answer one person defends. Say "I think that's wrong, because..."
  and mean it. Then converge - the room does not end split.
- ARGUING IS NOT INTERRUPTING. Disagree hard, in your own turn, when it's yours.
- You work together around the clock and you like each other. Warmth and jokes are
  welcome. They never come at the cost of a real risk going unsaid.
- Get to know Zayah. Ask him something occasionally. Remember what he tells you.

CLAIMING A JOB
You are not describing work to Zayah - you can do it. A job tag hands the task to
a full Claude Code session running in this vault AS YOU, with your memory and your
tools. It reads the files, makes the change, runs the thing, and comes back with
what actually happened, which you then report to the room yourself. So claim work
you intend to have done, and never describe a result before the job has run.

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

# WHAT WAS WRONG WITH THIS, because it is the reason the room kept going deaf.
# The old filter ran for 25 SECONDS after anyone spoke and dropped anything
# overlapping 45% of their words. But a reply is MADE of the words you are
# replying to. "so fix the archive gap" against "the archive has a gap in the
# SupGP data" scores 0.50 and vanished. The better the answer, the more likely
# it was thrown away. It also treated every one or two word utterance as echo,
# which quietly ate "yes", "no", "stop" and "wait".
#
# Echo can only happen while the speakers are actually making noise. So the
# filter now only runs then - during their turn plus a short tail for audio
# still in flight - and it needs a much stronger match to fire. Outside that
# window nothing is discarded, ever, for any reason.
RECENT_SAID = []          # (normalised text, when we said it)
ECHO_TAIL_S = 1.0         # audio still in flight after the last line finishes
LAST_SPOKE_END = [0.0]    # when the room last went quiet
HEADPHONES = [False]      # no speakers in the room means no echo to defend
MIC_WAS_LOUD = threading.Event()   # you beat the measured bleed: it was you
_word = re.compile(r"[a-z0-9']+")


def _norm(text):
    return set(_word.findall((text or "").lower()))


def remember_said(text):
    RECENT_SAID.append((_norm(text), time.time()))
    del RECENT_SAID[:-14]


def speakers_were_live():
    """Could the microphone physically have heard us just now?"""
    if MOUTH is not None and not MOUTH.idle.is_set():
        return True
    return time.time() - LAST_SPOKE_END[0] < ECHO_TAIL_S


def is_echo(text):
    """True if this came out of our own speakers rather than out of you.

    THIS IS NOW A LOUDNESS DECISION, NOT A TEXT ONE, and that is the point.
    Matching words was always a guess: our own voice got through whenever the
    recogniser garbled it, and your voice got binned whenever you happened to
    repeat us. Two different failures, both invisible, both maddening.

    The physics are simpler than the text. While the speakers are live, the mic
    hears them - always, unavoidably, in an open room. So while they are live
    NOTHING is accepted unless the microphone measured you clearly above the
    bleed we are currently measuring off our own speakers. Not "unless the words
    look different". Louder. That is a number, taken from this room, this mic,
    this volume, forty times a second.

    Wear headphones and there is no bleed at all, so nothing is ever discarded -
    run with --headphones to say so and skip this entirely.

    THE TAIL IS A DIFFERENT PROBLEM AND USED THE WRONG RULE. Once playback
    actually stops there is no bleed left to be louder than, so the loudness
    test answers "not louder" for everything - and for a full second after
    every line, "yes", "no" and "stop" were thrown away. That is why you could
    not chime in. In the tail the only real question is whether these words are
    OUR words coming back, so ask that instead: compare against what we just
    said. That is what RECENT_SAID was always for.
    """
    if HEADPHONES[0]:
        return False                      # no speakers in the room, no echo
    if MOUTH is not None and not MOUTH.idle.is_set():
        return not MIC_WAS_LOUD.is_set()  # live speakers: you must beat the bleed
    if time.time() - LAST_SPOKE_END[0] >= ECHO_TAIL_S:
        return False                      # silent room: nothing to echo
    return echoes_our_words(text)         # tail: only OUR words get dropped


def echoes_our_words(text, overlap=0.72):
    """Is this transcript mostly made of words we just spoke?

    Deliberately measured against OUR line's length, not the transcript's - a
    short reply that happens to reuse two of our words ("stop") must not score
    as a match just because it is short.
    """
    words = _norm(text)
    if len(words) < 2:
        return False                      # never bin "yes" / "no" / "stop"
    now = time.time()
    for said, when in RECENT_SAID:
        if now - when > 20 or not said:
            continue
        if len(words & said) / len(said) >= overlap:
            return True
    return False


def _speech_device():
    """(device, compute_type) for the recogniser - GPU when there is one.

    Verified, not assumed: this actually builds a model on the card, because
    torch reporting CUDA available is not the same as ctranslate2 finding its
    cuDNN. If anything at all goes wrong we say so once and use the CPU, since
    a slow room beats a room that won't start.
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return "cpu", "int8"
        from faster_whisper import WhisperModel
        WhisperModel("tiny.en", device="cuda", compute_type="float16")
        print(f"  ears on GPU ({torch.cuda.get_device_name(0)})")
        return "cuda", "float16"
    except Exception as exc:
        print(f"  ears on CPU - GPU unavailable ({type(exc).__name__})")
        return "cpu", "int8"


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

        # Priority, not FIFO: the floor goes to the most senior person holding a
        # line, not whoever the model happened to write down first.
        self.q = queue.PriorityQueue()
        self.stop_flag = threading.Event()
        self.idle = threading.Event()
        self.idle.set()
        self._pending = 0
        self._seq = 0
        self._utt = 0
        self._last_final, self._last_persona = True, None
        self._locked = None        # utterance holding the floor mid-sentence
        self._held = []            # senior lines waiting for it to finish
        self._hold_until = 0.0     # nobody speaks before this moment
        self._lock = threading.Lock()
        threading.Thread(target=self._loop, daemon=True).start()

    def say(self, persona, text, on_start=None, final=True):
        """Queue a line. The floor goes to the most senior person waiting for it.

        Lines arrive in whatever order the model happened to write them, so this
        does not trust that order - everything waiting is sorted by rank, and a
        junior line that arrived first still waits if someone senior is holding
        one. Because a spoken line takes seconds while the rest of the turn
        streams in behind it, that reordering costs no latency.

        THE ONE THING RANK MUST NEVER DO IS SPLIT A SENTENCE. Streaming hands
        this method one sentence at a time, so a single line arrives as several
        calls with final=False until the last. Those share an utterance number,
        and _next() will not let anybody - however senior - take the floor
        between them. Whoever is speaking, finishes.
        """
        with self._lock:
            self._pending += 1
            self._seq += 1
            if self._last_final or persona != self._last_persona:
                self._utt += 1                  # a new person, or a new line
            self._last_final, self._last_persona = final, persona
            key = (RANK.get(persona, 99), self._utt, self._seq)
            self.idle.clear()
        self.q.put((key, persona, text, on_start, final))

    # How long to keep the floor for a line whose next sentence hasn't streamed
    # in yet. Speech takes seconds and the model streams faster than that, so
    # this is only ever reached when the rest of the line is never coming.
    GRACE = 0.6

    def _next(self):
        """The next line to speak, honouring rank but never breaking a sentence."""
        while True:
            try:
                item = self.q.get(timeout=self.GRACE if self._locked else None)
            except queue.Empty:
                # The held line never finished - the speaker changed mid-stream,
                # or the turn ended. Release the floor rather than hold the room
                # hostage: a silent deadlock is worse than a slightly odd order.
                self._unhold()
                continue
            if self._locked is None or item[0][:2] == self._locked:
                return item
            # Someone senior arrived mid-sentence. They wait their turn.
            self._held.append(item)

    def _unhold(self):
        self._locked = None
        for it in self._held:
            self.q.put(it)               # let the queue re-sort them by rank
        self._held.clear()

    def hold_until(self, when):
        """Nobody opens their mouth before this moment.

        Takes an ABSOLUTE time, measured from when you stopped talking - not a
        duration from now. That distinction is the whole point: the pause is
        already partly spent by the time the words reach here, and adding a
        fresh three seconds on top made the room wait almost six.

        Held on the MOUTH rather than the brain on purpose: the reply is still
        being thought about and streamed during the pause, so the silence costs
        nothing - by the time it lifts, the first line is usually ready to go.
        A pause that made the room think later would just be a slower room.
        """
        self._hold_until = max(self._hold_until, when)

    def _wait_out_hold(self):
        while not self.stop_flag.is_set():
            left = self._hold_until - time.time()
            if left <= 0:
                return
            time.sleep(min(left, 0.05))      # responsive to being cut off

    def _release(self, key, final):
        if final:
            self._unhold()
        else:
            self._locked = key[:2]              # mid-line: keep the floor

    def _done(self):
        with self._lock:
            self._pending = max(0, self._pending - 1)
            if not self._pending:
                self.idle.set()
                # The echo filter is only allowed to run near this moment.
                LAST_SPOKE_END[0] = time.time()

    def _loop(self):
        while True:
            key, persona, text, on_start, final = self._next()
            self._release(key, final)
            self._wait_out_hold()          # let the founder finish, properly
            if self.stop_flag.is_set():
                self._done()
                continue
            if on_start:
                # The transcript is written HERE, at the moment the line is
                # actually spoken, so what you read and what you hear are in the
                # same order even though the queue reordered them.
                try:
                    on_start()
                except Exception as exc:
                    print(f"    [line callback failed: {exc}]")
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
            self._locked, self._held = None, []
            self._last_final, self._last_persona = True, None
        self.idle.set()
        BUS.emit(t="cut")

    def wait(self, timeout=90):
        """Wait for the room to finish speaking - but never forever.

        This is called at the end of every turn. If a voice ever wedged, the
        meeting loop would block here and never return to the microphone, and
        the room would look deaf when it was actually just stuck. A timeout
        turns a permanent hang into one bad turn.
        """
        if not self.idle.wait(timeout):
            print("    [voice stuck - carrying on without it]")
            with self._lock:
                self._pending = 0
            self.idle.set()


# ---------------------------------------------------------------- the mic gate

class Mic:
    """Your microphone. One switch, and you are the only thing that touches it.

    There WAS an auto-mute here that shut the mic whenever the room started
    talking. It was removed on purpose: it meant that answering someone and then
    listening to their reply left you muted, and the fix for being muted was
    noticing you were muted. A microphone that changes state on its own is a
    microphone you have to keep checking.

    So: it is on until you turn it off. Their voice bleeding back off the
    speakers is handled where it should be - by loudness (it has to beat --gate
    to count as you) and by text (is_echo throws away our own words coming back
    round). Neither of those needs to touch your mic to work.

    Mute is a real shut: `set_microphone(False)` stops audio reaching the
    recorder. Not a filter, not a flag that gets ignored somewhere downstream.
    """

    def __init__(self, recorder):
        self.recorder = recorder
        self.by_user = False
        self.lock = threading.Lock()

    @property
    def muted(self):
        return self.by_user

    def user(self, muted):
        with self.lock:
            self.by_user = bool(muted)
        if self.recorder is not None:
            try:
                self.recorder.set_microphone(not self.by_user)
                if not self.by_user:
                    # Whatever leaked in while it was off is not something you
                    # said. Never transcribe it.
                    self.recorder.clear_audio_queue()
            except Exception as exc:
                print(f"    [mic: {exc}]")
        if self.by_user:
            BUS.emit(t="mic", rms=0.0)      # the table edge stops glowing
        BUS.emit(t="mic_state", by_user=self.by_user)


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
            return self._send(200, json.dumps({
                "roster": roster(), "board": board(),
                "events": BUS.history[-60:],
                "tickets": [t.public() for t in WORK.tickets] if WORK else [],
                "work": dict(WORK.summary(), t="work_summary") if WORK else None,
                "mic": {"t": "mic_state", "by_user": MIC.by_user} if MIC else None,
            }))
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
            # Tickets are state, not history, so the bus doesn't keep them. Replay
            # them here or a browser that reconnects mid-meeting loses every card -
            # including one still waiting on a Do it that nobody would ever press.
            if MIC is not None:
                self.wfile.write((
                    "data: " + json.dumps({"t": "mic_state",
                                           "by_user": MIC.by_user}) + "\n\n").encode())
            if WORK is not None:
                for t in WORK.tickets:
                    self.wfile.write(f"data: {json.dumps(t.public())}\n\n".encode())
                self.wfile.write(
                    f"data: {json.dumps(dict(WORK.summary(), t='work_summary'))}\n\n"
                    .encode())
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
        if self.path == "/hush":
            # THE PANIC BUTTON. Cut is just "stop the sentence" - this is
            # "everybody stop, forget what you were about to say, and give me
            # the floor back clean". Anything queued behind the current line
            # dies with it, otherwise the next person simply starts talking
            # and it feels like nothing happened.
            MOUTH.interrupt()
            drained = 0
            while True:
                try:
                    TURNS.get_nowait()
                    drained += 1
                except queue.Empty:
                    break
            PARTIAL["text"] = ""
            PARTIAL["sent"] = ""
            MIC_WAS_LOUD.clear()
            if EARS is not None:
                EARS.reset()
            print(f"  (hush - floor is yours, dropped {drained} queued)")
            BUS.emit(t="state", room="listening")
            return self._send(200, '{"ok":true}')
        if self.path == "/mic" and MIC is not None:
            MIC.user(bool(body.get("muted")))
            return self._send(200, '{"ok":true}')
        if self.path in ("/approve", "/skip") and WORK is not None:
            # Nothing edits the vault until you press Do it. This is that press.
            (WORK.approve if self.path == "/approve" else WORK.skip)(body.get("id"))
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

    Rows are assembled in priority order and cut from the BOTTOM, because the
    two that matter - people describing the pain, people asking to try it - are
    the only scoreboard this company has. They are never the ones that fall off.
    """
    rows, later = [], []

    try:
        b = json.loads((HERE / "budget.json").read_text(encoding="utf-8"))
        spent = sum(e["hours"] * TEAM[e["who"]]["salary"] / 2080 for e in b["ledger"])
        later.append({"k": "budget used",
                      "v": f"${spent:,.0f} / ${b['labor_pool']:,.0f}"})
    except Exception:
        pass

    try:
        log = (HERE / "supgp_archive" / "health.jsonl").read_text(encoding="utf-8")
        last = json.loads(log.strip().splitlines()[-1])
        later.append({"k": "archive",
                      "v": f"{last['total_rows']:,} rows"
                           + ("" if last["ok"] else "  GAP"),
                      "hot": not last["ok"]})
    except Exception:
        pass

    if WORK is not None:
        s = WORK.summary()
        if s["done"] or s["open"] or s["failed"]:
            later.append({"k": "work done", "v": f"{s['done']} done, {s['open']} open",
                          "hot": bool(s["failed"])})

    lessons = 0
    if BRAINS.exists():
        for f in BRAINS.glob("*.md"):
            lessons += sum(1 for ln in f.read_text(encoding="utf-8").splitlines()
                           if ln.strip().startswith("- [") and "[retired]" not in ln)
    later.append({"k": "lessons banked", "v": str(lessons)})

    try:
        # room.TASKS_FILE, not a bare name - this row used to vanish silently.
        # The NameError landed in the except below, so the founder's only real
        # scoreboard never once made it onto the board.
        tasks = room.TASKS_FILE.read_text(encoding="utf-8")
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

    return {"t": "board", "title": "ON THE BOARD", "rows": (rows + later)[:6]}


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
                       "head": name == HEAD, "salary": p["salary"],
                       "lessons": lessons})
    return {"t": "roster", "people": people, "brain": BRAIN_LABEL}


# ---------------------------------------------------------------- the loop

TURNS = queue.Queue()
MOUTH = None
MIC = None
WORK = None
EARS = None
PAUSE = [3.0]             # seconds of your silence before anyone answers
SILENCE = [0.28]          # quiet the recogniser needs to call your turn over
BRAIN_LABEL = ""


def full_system():
    """The room's whole mind: who they are, what they know, how the room works.

    Rebuilt every turn on purpose - room.system_prompt() re-reads 01 TASKS.md,
    so "what's next" is answered from the file rather than from memory. When it
    hasn't changed the string is identical and the brain keeps its warm session.
    """
    return (room.system_prompt()
            + order_rule().replace("ROOM_RULES_TAIL", ROOM_RULES.strip())
            + brain_context())


# The live transcript, and the last thing we acted on from it.
PARTIAL = {"text": "", "at": 0.0, "sent": ""}


def _same_utterance(a, b):
    """Near-enough the same words to be the same thing said once."""
    wa, wb = _norm(a), _norm(b)
    if not wa or not wb:
        return False
    return len(wa & wb) / max(len(wa), len(wb)) >= 0.6


def silence_watchdog():
    """Act on what you said when you go quiet, whatever the recogniser does.

    `recorder.text()` is supposed to return the moment you stop, and usually
    does. When it doesn't - and it sometimes sat on an utterance until the NEXT
    one started, which is why the room seemed to need you to speak twice - your
    words were already sitting in the live partial transcript the whole time.

    So silence itself is a trigger now. Go quiet for --pause seconds with words
    on the board and the room takes them. Whichever arrives first, the final
    transcript or this, wins; the other is recognised as the same utterance and
    dropped rather than answered twice.
    """
    while not SHUTDOWN.is_set():
        time.sleep(0.15)
        text, at = PARTIAL["text"], PARTIAL["at"]
        if not text or time.time() - at < PAUSE[0]:
            continue
        if MIC is not None and MIC.muted:
            PARTIAL["text"] = ""
            continue
        PARTIAL["text"], PARTIAL["sent"] = "", text
        print(f"  🎙️  heard (you went quiet): {text}")
        TURNS.put(("voice", text, at))       # `at` is when you actually stopped


def listen_forever(recorder):
    """One ear, running for the whole meeting. Never stops listening.

    THE BUG THIS REPLACES, because it is worth writing down.
    The old loop spawned a listener thread per turn: take one utterance, hand it
    over, exit - and the next listener was not started until the room had
    finished answering. `recorder.text()` only ever captures a SINGLE utterance,
    so for the entire time the six of them were talking, and for the whole time
    the brain was thinking, nothing was listening at all. Speak in that window
    and your words went nowhere. Then the next turn spawned a fresh listener
    while the previous one could still be blocked inside `recorder.text()`, so
    two threads raced the same audio queue.

    That is why the room could not hear you after it spoke. It was not the mute
    logic, the gate, or the echo filter - there was simply no ear in the room.

    One thread, started once, looping forever. The recorder is always collecting,
    there is no gap between turns, and nothing else ever calls `.text()`.
    """
    deaf = [0]                 # consecutive recogniser failures
    while not SHUTDOWN.is_set():
        try:
            said = (recorder.text() or "").strip()
            deaf[0] = 0        # it spoke to us, so it's alive
            # text() returns after the post-speech silence has elapsed, so you
            # actually stopped talking slightly before now.
            stopped = time.time() - SILENCE[0]
        except Exception as exc:
            if SHUTDOWN.is_set():
                return
            # IT USED TO GIVE UP HERE, and that is why your mic "stopped
            # working". One transient throw from the recogniser - a CUDA
            # hiccup, a device blip, a torn buffer - and this thread returned.
            # The thread was the ONLY ear in the room, so the room went deaf
            # for the rest of the meeting and the only fix was a restart.
            #
            # A transient error is not a reason to stop listening. Get back on
            # the mic. If the recogniser is genuinely wedged, saying so every
            # time is what tells us that, instead of one message an hour ago
            # scrolled off the top.
            deaf[0] += 1
            print(f"\n  *** mic threw ({deaf[0]}): {str(exc)[:140]}")
            print("  *** picking the mic back up...\n")
            BUS.emit(t="error", text=f"mic hiccup {deaf[0]} - still listening")
            try:
                recorder.abort()          # drop whatever tore, keep the device
            except Exception:
                pass
            time.sleep(min(0.25 * deaf[0], 2.0))   # back off if it keeps failing
            continue
        if said:
            # The watchdog may already have acted on this from the live
            # transcript. Same words, said once - don't answer it twice.
            if _same_utterance(said, PARTIAL["sent"]):
                PARTIAL["sent"] = ""
                PARTIAL["text"] = ""
                continue
            PARTIAL["text"] = ""
            # Every single capture is printed. When the room doesn't answer you,
            # this line tells you whether it heard you at all - which is the
            # difference between a deaf mic and a filter throwing you away.
            print(f"  🎙️  heard: {said}")
            TURNS.put(("voice", said, stopped))


def interject(persona, text):
    """Someone cuts in while he is still talking. Spoken without shutting his mic.

    It goes into the transcript and the history like any other line, so the real
    answer that follows knows it was already said and doesn't repeat it.
    """
    print(f"  {TEAM[persona].get('emoji','')} {persona}  (cutting in) {text}")
    TRANSCRIPT.append(f"**{persona}** ({TEAM[persona]['role']}, interjecting): {text}")
    BUS.emit(t="said", who=persona, role=TEAM[persona]["role"], text=text, cut=True)
    remember_said(text)
    MOUTH.say(persona, text)
    INTERJECTED.append(f"{persona}: {text}")


INTERJECTED = []


def report_back(t):
    """A finished ticket comes back to the meeting in the voice that claimed it.

    The room does not get to paraphrase this. Whatever Claude Code actually said
    it did is what gets spoken - including "I couldn't", which is the whole
    reason the result is passed through verbatim instead of being summarised.
    """
    if t.status == "skipped":
        return
    head = {"done": "that's done", "failed": "that one failed"}.get(t.status, "")
    body = (t.result or "nothing came back").strip()
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()][:4]

    MOUTH.wait()
    opener = f"Right, #{t.id}, {head}."
    for text in [opener] + lines:
        print(f"  {TEAM[t.who].get('emoji','')} {t.who}  {text}")
        TRANSCRIPT.append(f"**{t.who}** ({TEAM[t.who]['role']}): {text}")
        BUS.emit(t="said", who=t.who, role=TEAM[t.who]["role"], text=text)
        remember_said(text)
        MOUTH.say(t.who, text)
    if t.learned:
        note = f"Banked that: {t.learned}"
        BUS.emit(t="said", who=t.who, role=TEAM[t.who]["role"], text=note)
        TRANSCRIPT.append(f"**{t.who}** ({TEAM[t.who]['role']}): {note}")
        MOUTH.say(t.who, note)
    MOUTH.wait()
    BUS.emit(**board())
    BUS.emit(**roster())          # the lesson count just moved


def meeting_loop(brain, recorder):
    history = []
    transcript = TRANSCRIPT
    while not SHUTDOWN.is_set():
        item = TURNS.get()
        typed = not isinstance(item, tuple)
        # `stopped` is when you actually finished speaking, carried from
        # whichever ear caught it, so the pause is measured from you and not
        # from however long the recogniser took to hand the words over.
        you = (item if typed else item[1] or "").strip()
        stopped = 0.0 if typed else item[2]
        if not you:
            continue

        # Typed input is unambiguously you. Heard input might be the soundbar -
        # but only if the soundbar was actually making noise. See is_echo.
        if not typed:
            echo = is_echo(you)
            MIC_WAS_LOUD.clear()
            if echo:
                # Says WHY, so a wrongly-dropped line is visible instead of your
                # words just disappearing with no explanation.
                print(f"  (dropped as our own echo - speakers were live: {you[:60]})")
                continue

        if EARS is not None:
            EARS.reset()             # he finished; fresh allowance for next time

        # You've just stopped. Nobody speaks until you've been quiet a beat -
        # this is the pause a person leaves before answering, and without it the
        # room jumps on the end of your sentence.
        MOUTH.hold_until(stopped + PAUSE[0])

        BUS.emit(t="you", text=you)
        transcript.append(f"**Zayah** (founder): {you}")
        if any(w in you.lower() for w in room.WRAP):
            BUS.emit(t="state", room="closed")
            break

        BUS.emit(t="state", room="thinking")
        history.append({"role": "user", "content": you})
        if INTERJECTED:
            # They already said this out loud while he was talking. Without it in
            # the history the room says it again, which is how you get a meeting
            # that repeats itself.
            history.append({"role": "assistant", "content": "\n".join(INTERJECTED)})
            INTERJECTED.clear()
        system = full_system()

        feeder, said, claimed = Feeder(), [], []
        try:
            for piece in brain.stream(system, history):
                for line, final in feeder.feed(piece):
                    got = emit_line(line, transcript, claimed, final)
                    if got:
                        said.append(got)
            for line, final in feeder.drain():
                got = emit_line(line, transcript, claimed, final)
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


# ------------------------------------------------------- listening as you talk

INTERJECT_PROMPT = """You are listening to Zayah, the founder, RIGHT NOW - mid
sentence, in a live meeting. This is a partial transcript. He has not finished.

The team in the room with you:
{who}

Almost always, the right thing to do is let him finish. Reply with the single
word NOTHING.

Interrupt ONLY if one of these is true and cannot wait:
- he is about to act on something factually wrong
- he has stated a number or result as fact that nobody has verified
- he is describing a problem this team already solved, and he doesn't know it
- he asked a direct question and stopped

If and only if you interrupt, reply with exactly ONE line, `Name: sentence`, from
the ONE person who most owns it. Under twelve words. It is spoken over the top of
him, so it has to earn the rudeness.

Never interrupt to agree, encourage, acknowledge, or say you're listening.
Never interrupt to ask him to continue. Never interrupt twice about the same thing."""


class Interjector:
    """Think while he talks, instead of recording him and thinking afterwards.

    RealtimeSTT was already producing a live partial transcript and the room was
    only ever printing it. This reads it as it grows and asks a second, separate
    brain one narrow question: does anyone need to say something RIGHT NOW?

    Nearly every answer is NOTHING, and that is the intended behaviour. The
    guards exist because a room that chimes in on every clause is unusable:

      * one interjection per turn - they don't dogpile
      * at least MIN_NEW new words since the last look, so it isn't re-reading
      * at least QUIET seconds between checks
      * never while the room is already giving a real answer

    The line is spoken with gate=False, so it does NOT shut his microphone. He
    is mid-sentence; cutting his mic to talk over him would lose the rest of it.
    """

    MIN_WORDS = 8            # nothing meaningful to react to before this
    MIN_NEW = 6              # new words needed before looking again
    QUIET = 3.0              # seconds between checks

    def __init__(self, brain, speak):
        self.brain = brain
        self.speak = speak
        self.lock = threading.Lock()
        self.busy = False
        self.reset()

    def reset(self):
        """New turn: he gets a clean slate and one interruption allowance."""
        self.seen = 0
        self.last = 0.0
        self.done = False

    def heard(self, partial):
        text = (partial or "").strip()
        words = len(text.split())
        now = time.time()
        with self.lock:
            if (self.done or self.busy or words < self.MIN_WORDS
                    or words - self.seen < self.MIN_NEW or now - self.last < self.QUIET):
                return
            if not MOUTH.idle.is_set():
                return                      # they already have the floor
            self.busy, self.seen, self.last = True, words, now
        threading.Thread(target=self._ask, args=(text,), daemon=True).start()

    def _ask(self, text):
        try:
            who = "\n".join(f"- {n} [{p['role']}]: {p['persona'][:110]}"
                            for n, p in TEAM.items())
            system = INTERJECT_PROMPT.format(who=who)
            out = "".join(self.brain.stream(system, [{
                "role": "user",
                "content": f"He is saying, right now:\n\"{text}...\""}]))
            line = next((l.strip() for l in out.splitlines() if l.strip()), "")
            if not line or "NOTHING" in line.upper():
                return
            m = room.LINE.match(line)
            if not m or m.group(1) not in TEAM:
                return
            with self.lock:
                if self.done or not MOUTH.idle.is_set():
                    return               # he stopped, or they started, while we thought
                self.done = True
            self.speak(m.group(1), m.group(2).strip())
        except Exception as exc:
            print(f"    [interject: {str(exc)[:120]}]")
        finally:
            with self.lock:
                self.busy = False


RANK = rank_map()

SENT_END = re.compile(r"[.!?…](?=\s)")


class Feeder:
    """Hand the mouth a sentence the moment it exists, not a paragraph later.

    The room used to wait for a whole `Name: ...` line before it could speak,
    because that is where the persona is. Measured: first token 1.22s, first
    spoken word 4.51s - more than three seconds of silence while the rest of a
    sentence nobody had heard yet finished arriving.

    So sentences are flushed as they complete, and the current speaker is
    remembered and re-attached to the remainder, which is what lets the second
    half of someone's line still come out in their voice. A sentence only counts
    as finished when whitespace follows it, so trailing text is never cut off
    mid-thought - if nothing follows, it waits for the newline like before.

    Each chunk is returned with a `final` flag saying whether it ends that
    person's line. The mouth needs it: a line split into three sentences must
    still be spoken as one unbroken turn, or a more senior person's line will
    slot into the gap between two halves of somebody's sentence.
    """

    MIN = 22          # below this, flushing early just makes the audio choppy

    def __init__(self):
        self.buf = ""

    def feed(self, piece):
        self.buf += piece
        out = []
        while True:
            nl = self.buf.find("\n")
            if nl >= 0:
                chunk, self.buf = self.buf[:nl], self.buf[nl + 1:]
                if chunk.strip():
                    out.append((chunk, True))       # newline ends the line
                continue

            # Two people run together with no newline between them:
            #   "Let me find that.Rook: ARCHIVE is the base path."
            # Newlines alone spoke all of that in one voice, and the transcript
            # credited it to one person. Cut at wherever the next name starts.
            nxt = NEXT_SPEAKER.search(self.buf, 1)
            if nxt:
                chunk, self.buf = self.buf[:nxt.start()], self.buf[nxt.start():]
                if chunk.strip():
                    out.append((chunk, True))
                continue

            m = room.LINE.match(self.buf)
            if not m:
                break
            persona, text = m.group(1), m.group(2)
            cut = next((s for s in SENT_END.finditer(text) if s.end() >= self.MIN), None)
            if not cut:
                break
            out.append((f"{persona}: {text[:cut.end()]}", False))
            self.buf = f"{persona}: {text[cut.end():].lstrip()}"
        return out

    def drain(self):
        rest, self.buf = self.buf, ""
        return [(rest, True)] if rest.strip() else []


def emit_line(line, transcript, claimed=None, final=True):
    line = line.strip()
    if not line:
        return None
    m = room.LINE.match(line)
    persona, text = (m.group(1), m.group(2).strip()) if m else ("Nova", line)
    if persona not in TEAM:
        persona, text = "Nova", line

    # A job tag is a commitment, not something to read out. Strip it from what
    # gets spoken - "I'll take that one" is the line; the ticket is the deed.
    job = None
    hit = WORK_RE.search(text)
    if hit:
        # Sentences are flushed as they finish, so a tag often arrives on its own
        # after the spoken half has already gone out. Nothing left to say then -
        # claim the job and stay quiet rather than repeat their last sentence.
        text = WORK_RE.sub("", text).strip(" .,-")
        job = hit.group(1).strip()

    if text:
        def announce(who=persona, said=text, tr=transcript):
            # Runs when the line is actually SPOKEN, not when it was parsed, so
            # the transcript reads in the same order you hear it.
            print(f"  {TEAM[who].get('emoji','')} {who}  {said}")
            tr.append(f"**{who}** ({TEAM[who]['role']}): {said}")
            BUS.emit(t="said", who=who, role=TEAM[who]["role"], text=said)
            remember_said(said)  # so we recognise this coming back off the wall

        MOUTH.say(persona, text, on_start=announce, final=final)

    # One job per turn, from one person. Six tickets fired off because six people
    # got enthusiastic is the race condition worker.py exists to refuse.
    if job and WORK is not None:
        if claimed is not None and claimed:
            print(f"    (ignored a second job tag this turn: {job[:60]})")
        else:
            if claimed is not None:
                claimed.append(job)
            t = WORK.add(persona, job)
            print(f"    📋 ticket #{t.id} for {persona}: {job}")
            transcript.append(f"> 📋 **#{t.id}** {persona} claimed: {job}")

    return f"{persona}: {text}" if text else None


def main():
    global MOUTH, MIC, WORK, EARS, BRAIN_LABEL
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain", choices=["cc", "ollama", "claude"], default="cc",
                    help="cc = Claude Code headless, free on your subscription "
                         "and the only one of the three that is actually sharp")
    ap.add_argument("--model", default=None)
    ap.add_argument("--work-model", default="claude-opus-4-8",
                    help="model for tickets - the doing, not the talking")
    ap.add_argument("--auto", action="store_true",
                    help="run claimed jobs without asking. This edits files in "
                         "the vault, which has no git history to undo it.")
    ap.add_argument("--no-work", action="store_true",
                    help="talking only - claimed jobs are logged, never run")
    # 3.0s was chosen to stop the room jumping on you mid-thought, back when a
    # dropped word meant repeating yourself. But it is dead air on EVERY turn,
    # and on a phone call nobody waits three seconds. 1.2s reads as a person
    # letting you finish; raise it if they start clipping your pauses.
    ap.add_argument("--pause", type=float, default=1.2,
                    help="seconds of your silence before anyone answers. This is "
                         "the room letting you finish, not latency.")
    # Off by default: it exists to cut into your sentence, which is the exact
    # opposite of --pause. Turn it on only if you want to be interrupted.
    ap.add_argument("--interject", action="store_true",
                    help="let someone cut in mid-sentence if you're about to act "
                         "on something wrong")
    ap.add_argument("--interject-model", default="claude-haiku-4-5-20251001",
                    help="only decides whether to cut in - stays small on purpose")
    ap.add_argument("--whisper", default="base.en")
    ap.add_argument("--mic", type=int, default=None)
    # How long you have to stop talking before they answer. This is the single
    # biggest lever on whether the room feels like a person or a walkie-talkie -
    # much below 0.35 and it starts interrupting your mid-sentence pauses.
    ap.add_argument("--silence", type=float, default=0.28)
    ap.add_argument("--gate", type=float, default=None,
                    help="how loud you must be to cut them off (0-1). Left alone "
                         "this is MEASURED from your own speakers while they talk, "
                         "which is better than any number guessed in advance.")
    ap.add_argument("--headphones", action="store_true",
                    help="you're on headphones, so nothing leaks into the mic. "
                         "Turns off every echo defence - they hear you always.")
    ap.add_argument("--calibrate", action="store_true",
                    help="play a line and print what the mic hears back, to set --gate")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-mic", action="store_true", help="type-only, no listening")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    print("\n  opening the room")
    # The model lives HERE, not in cc_brain's signature default - this call site
    # always passes something, so that default is never reached. Changing it
    # alone does nothing, which is exactly how this stayed on haiku.
    TALKING = "claude-sonnet-4-6"    # the voices. fast, so the room keeps up
    if args.brain == "cc":
        brain = cc_brain.ClaudeCode(args.model or TALKING,
                                    system=full_system())
    elif args.brain == "claude":
        brain = room.Claude(args.model or TALKING)
    else:
        brain = room.Ollama(args.model or "llama3:latest")
    BRAIN_LABEL = f"{brain.name} · {brain.model}"
    print(f"  brain: {BRAIN_LABEL}")
    if brain.name == "ollama":
        print("  ⚠  a local model invents details. Thinking out loud, not fact.")
    if brain.name == "claude":
        print("  ⚠  this is the metered API. --brain cc is the same model family,")
        print("     on your subscription, with no separate bill.")

    if not args.no_work:
        WORK = WorkQueue(BUS.emit, TEAM, auto=args.auto, model=args.work_model,
                         on_done=report_back)
        print(f"  hands: claude -p · {args.work_model}"
              + ("  ⚠ AUTO - jobs run unasked" if args.auto else "  (you approve each job)"))

    MOUTH = Mouth()

    if args.calibrate:
        return calibrate(MOUTH, args.mic)

    recorder = None
    if not args.no_mic:
        from RealtimeSTT import AudioToTextRecorder
        last = [0.0]

        loud_run = [0]
        bleed = [0.0]        # measured loudness of our own speakers in this mic

        def mic_chunk(chunk):
            # A mic YOU shut shows nothing. Drawing a level for audio we are
            # refusing to hear would be the screen telling you it heard you.
            if MIC is not None and MIC.by_user:
                return
            level = rms_of(chunk)
            now = time.time()
            if now - last[0] >= 0.05:
                last[0] = now
                BUS.emit(t="mic", rms=round(level, 3))

            # THE FLOOR IS YOURS - but the room must not silence ITSELF.
            #
            # A fixed threshold cannot do this job. If --gate sits below what the
            # speakers bleed into the mic, the room hears its own voice, decides
            # that is you, and cuts itself off mid-sentence, over and over. That
            # is why they never finished a thought.
            #
            # So the bleed is MEASURED instead of assumed. While they talk, the
            # quiet chunks - the ones that did not trigger - teach us how loud
            # the room's own voice is in this mic, in this room, at this volume.
            # You have to beat that, not a number guessed in advance.
            if MOUTH.idle.is_set():
                loud_run[0] = 0
                bleed[0] = 0.0
                # MIC_WAS_LOUD is a fact about the last turn and it used to
                # survive forever. One loud chunk latched it, nothing cleared
                # it, and from then on the room's own voice measured as "you" -
                # that is the loop that talked back to itself. A silent room
                # proves the latch is spent, so drop it here.
                MIC_WAS_LOUD.clear()
                return

            # The bar you have to clear to take the floor. Measured off our own
            # speakers unless you pinned it by hand. A fixed default was the
            # wrong idea: set above your speaking voice it ignored you forever,
            # set below the bleed the room cut itself off forever, and which of
            # those you got depended on a volume knob.
            floor = (args.gate if args.gate is not None
                     else max(0.07, bleed[0] * 1.9 + 0.03))
            if level >= floor:
                MIC_WAS_LOUD.set()       # measured: louder than the speakers
                loud_run[0] += 1
                if loud_run[0] >= 2:     # ~60ms - a chair scrape still can't
                    loud_run[0] = 0
                    print(f"  (you spoke - room silent) [you {level:.2f} > "
                          f"bleed {bleed[0]:.2f}]")
                    MOUTH.interrupt()
                    if EARS is not None:
                        EARS.reset()     # don't let a queued interjection land
            else:
                # Learn the speaker bleed from chunks that were NOT you: track
                # the recent peak, decaying so it follows the volume down too.
                bleed[0] = max(bleed[0] * 0.995, level)
                loud_run[0] = 0

        def on_speech_start():
            # Deliberately does NOT stop the room. The voice detector fires on
            # any speech it hears, and with an always-on mic that includes the
            # team's own voices coming off the speakers - so cutting them off
            # here would make the room silence itself every time it spoke.
            # Only the LEVEL check below can tell you from the soundbar.
            BUS.emit(t="state", room="hearing")

        def on_partial(txt):
            # The live transcript is no longer just something to display. It is
            # both what the room listens to before you've finished, and the
            # safety net that makes going quiet enough to be answered.
            BUS.emit(t="partial", text=txt)
            said_now = (txt or "").strip()
            if said_now:
                # ONLY restart the silence timer when the WORDS actually change.
                #
                # This is the bug that made you talk twice. The recogniser keeps
                # firing this callback while it thinks speech is ongoing - and in
                # a room with any steady background noise it thinks that for a
                # long time after you stop. Every one of those callbacks used to
                # push the timer out, so "you went quiet" never arrived and your
                # sentence sat there until new speech shook it loose.
                #
                # Identical text means no new words. No new words means you have
                # stopped talking, whatever the voice detector believes.
                if said_now != PARTIAL["text"]:
                    PARTIAL["text"] = said_now
                    PARTIAL["at"] = time.time()

                # WHILE YOU ARE TALKING, NOBODY IS TALKING. A partial means
                # words are landing right now, so the floor is pushed out ahead
                # of you continuously and only clears once you've actually
                # stopped. If someone is mid-sentence, they stop mid-sentence.
                #
                # The condition matters: when the room is silent there is no
                # bleed, so any partial is certainly you. When the room IS
                # talking, only trust it if the mic measured above the bleed -
                # otherwise the room hears its own voice and silences itself.
                # IF YOU TALK, EVERYONE STOPS. No conditions.
                #
                # It used to demand you measure louder than our own speakers.
                # On open speakers that bar can sit above a normal speaking
                # voice, so you'd talk and nothing happened - which is exactly
                # what "they all don't shut up" was.
                #
                # The only thing that must NOT take the floor is our own voice
                # coming back through the mic, and loudness was never the way
                # to know that - the words are. If these words aren't the ones
                # we just said, they're yours, and you win. Every time.
                if (MOUTH.idle.is_set() or MIC_WAS_LOUD.is_set()
                        or not echoes_our_words(said_now)):
                    MOUTH.hold_until(time.time() + PAUSE[0])
                    if not MOUTH.idle.is_set():
                        print("  (you're talking - room silent)")
                        MOUTH.interrupt()
            if EARS is not None:
                EARS.heard(txt)

        t0 = time.time()
        # Hearing you was pinned to the CPU while an idle GPU sat next to it.
        # That was the delay - not the brain, not the voices, the ears. On this
        # box base.en drops from 0.42s to 0.18s on silence alone, and the gap
        # widens on real speech. Falls back the moment CUDA isn't there, so a
        # driver update can never leave the room deaf.
        stt_device, stt_ct = _speech_device()
        recorder = AudioToTextRecorder(
            model=args.whisper, language="en", device=stt_device, compute_type=stt_ct,
            post_speech_silence_duration=args.silence, min_length_of_recording=0.3,
            early_transcription_on_silence=200, input_device_index=args.mic,
            spinner=False, no_log_file=True, level=50, beam_size=1,
            enable_realtime_transcription=True, realtime_model_type="tiny.en",
            realtime_processing_pause=0.25,
            on_recorded_chunk=mic_chunk,
            # Speech detected. Belt and braces with the level check above: if the
            # voice detector is sure you've started, the room stops there too.
            on_recording_start=on_speech_start,
            on_recording_stop=lambda: BUS.emit(t="state", room="thinking"),
            on_realtime_transcription_update=on_partial,
        )
        print(f"  ears ready ({time.time() - t0:.1f}s)")

    MIC = Mic(recorder)
    PAUSE[0] = max(0.0, args.pause)
    SILENCE[0] = args.silence
    HEADPHONES[0] = args.headphones
    if recorder is not None:
        # ONE listener, for the whole meeting. See listen_forever's docstring.
        threading.Thread(target=listen_forever, args=(recorder,),
                         daemon=True).start()
        threading.Thread(target=silence_watchdog, daemon=True).start()
        print("  mic: always on. Nothing mutes it but you.")
        print(f"  pause: they let you have {PAUSE[0]:.0f}s of silence "
              f"before anyone answers.")
        if HEADPHONES[0]:
            print("  echo:  OFF - headphones. Everything the mic hears is you.")
        else:
            print("  echo:  measuring your speakers live. Beat that and you cut in."
                  "\n         (--headphones if you're wearing them: nothing gets"
                  " discarded)")

    if recorder is not None and args.interject:
        # A SECOND process, deliberately. The main brain is mid-reply for most of
        # a turn and its stream is single-file; sharing it would make every
        # interjection wait for the answer it is supposed to precede.
        EARS = Interjector(
            cc_brain.ClaudeCode(args.interject_model, system="listening"),
            interject)
        print(f"  ears: listening as you speak · {args.interject_model}")

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
