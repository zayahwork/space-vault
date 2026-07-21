"""Proves the live-meeting loop end to end without a human at the mic.

Fakes the founder's voice with edge-tts, feeds that audio to the local whisper
exactly as the mic would, runs one real brain turn, and renders the reply to
speech. Prints the latency of each stage, because latency is the whole question.
"""
import asyncio
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edge_tts  # noqa: E402
import numpy as np  # noqa: E402

import meeting  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="selftest_"))
SPOKEN = "Morning everyone. Where are we on the maneuver detector, and what is actually blocking it?"

# 1. fake the founder talking -------------------------------------------------
t0 = time.time()
asyncio.run(edge_tts.Communicate(SPOKEN, "en-US-BrianNeural").save(str(tmp / "you.mp3")))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "you.mp3"),
                "-ar", "16000", "-ac", "1", "-f", "s16le", str(tmp / "you.raw")], check=True)
audio = np.fromfile(tmp / "you.raw", dtype=np.int16).astype(np.float32) / 32768.0
print(f"[tts  ] founder audio rendered            {time.time()-t0:5.2f}s  "
      f"({len(audio)/16000:.1f}s of speech)")

# 2. ears ---------------------------------------------------------------------
t0 = time.time()
ears = meeting.Ears.__new__(meeting.Ears)          # skip the mic stream setup
ears.np = np
from faster_whisper import WhisperModel  # noqa: E402
ears.model = WhisperModel("base.en", device="cpu", compute_type="int8", cpu_threads=8)
print(f"[stt  ] whisper loaded                    {time.time()-t0:5.2f}s")

t0 = time.time()
heard = ears.transcribe(audio)
stt = time.time() - t0
print(f"[stt  ] heard: {heard!r}")
print(f"[stt  ] transcription                     {stt:5.2f}s"
      f"   ({len(audio)/16000/max(stt,1e-6):.1f}x realtime)")

# 3. brain --------------------------------------------------------------------
brain = meeting.Ollama("llama3:latest")
system = meeting.system_prompt(meeting.CONTEXT_FILE.read_text(encoding="utf-8"))
t0, first = time.time(), None
buf = ""
for piece in brain.stream(system, [{"role": "user", "content": heard}]):
    if first is None:
        first = time.time() - t0
    buf += piece
print(f"[brain] first token                       {first:5.2f}s")
print(f"[brain] full reply                        {time.time()-t0:5.2f}s")
print("-" * 62)
print(buf.strip())
print("-" * 62)

# 4. mouth --------------------------------------------------------------------
line = next((l for l in buf.splitlines() if meeting.LINE.match(l.strip())), None)
if line:
    m = meeting.LINE.match(line.strip())
    persona = m.group(1) if m.group(1) in meeting.TEAM else "Nova"
    part = meeting.TEAM[persona]
    t0 = time.time()
    asyncio.run(edge_tts.Communicate(m.group(2), part["voice"], rate=part["rate"],
                                     pitch=part["pitch"]).save(str(tmp / "reply.mp3")))
    print(f"[tts  ] {persona}'s voice rendered            {time.time()-t0:5.2f}s"
          f"   -> {tmp/'reply.mp3'}")
else:
    print("[tts  ] SKIPPED - model returned no 'Name: line' formatted lines")
    sys.exit(1)
print("\nOK - every stage of the loop works.")
