"""
cc_brain.py - the room's brain, running on Claude Code instead of an API key.

THE PROBLEM THIS SOLVES
There were only two brains before, and neither was what the founder asked for:

  ollama (llama3:8b)   free, and it invents details. Its own banner says so.
  Claude via API key   sharp, and every turn is a line item on a credit card.

The ask was "insanely smart while keeping everything 100% free". Those are only
in conflict if you assume the model has to be reached through the API. It does
not. `claude -p` is Claude Code running headless, authenticated by the same
subscription already signed in on this machine - no ANTHROPIC_API_KEY, no
separate bill. It is the same class of model that writes this codebase.

HONEST ABOUT "FREE"
Free means no API invoice. It is NOT free of your Claude Code plan usage - a
turn here is a turn there, and heavy days will move you toward your plan limit.
The `total_cost_usd` the CLI reports is what the same call WOULD have cost on
the API. It is shown on the board as exactly that: a shadow price, not a charge.

WHY A LONG-LIVED PROCESS AND NOT ONE CALL PER TURN
A cold `claude -p` costs ~1.4s of startup and re-sends its whole preamble every
time - measured at 17,778 fresh cache tokens for a one-line reply. Streaming
mode keeps ONE process alive for the whole meeting: the conversation stays
warm on the far side, startup is paid once, and each turn is just a line of
JSON down a pipe. Same trick as keeping ollama loaded with keep_alive.

    room -> {"type":"user",...}\\n -> [ claude -p, still running ] -> deltas back

INTERFACE
Identical to room.Ollama and room.Claude: `.stream(system, history)` yields text.
The system prompt is fixed when the process starts, so `system` is honoured on
the first call and refreshed by `restart()` when the task list moves under us.
"""

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parent

# The room TALKS here; it does not touch files. Work that needs tools goes
# through worker.py as a ticket, deliberately, so nothing edits the vault
# because a sentence drifted that way mid-conversation.
NO_TOOLS = ["Bash", "Edit", "Write", "Read", "Glob", "Grep", "NotebookEdit",
            "WebSearch", "WebFetch", "TodoWrite", "Task"]


def _blind_cwd():
    """An empty directory for the brain to live in, so it has nothing to read."""
    d = HERE / ".brain_cwd"
    d.mkdir(exist_ok=True)
    (d / "README.txt").write_text(
        "Deliberately empty. The room's brain runs here so it cannot wander the\n"
        "vault mid-conversation and narrate the search out loud. Work with files\n"
        "goes through worker.py as a claimed job instead.\n", encoding="utf-8")
    return d


class ClaudeCode:
    """Claude Code, held open, speaking as the whole room."""

    name = "claude-code"

    def __init__(self, model="claude-sonnet-4-6", system="", cwd=None):
        if not _cli_ok():
            raise SystemExit(
                "the `claude` CLI isn't on PATH, so the free brain can't start.\n"
                "  install:  https://claude.com/claude-code\n"
                "  or run the local one:  jarvis --brain ollama")
        self.model = model
        # The brain runs in an EMPTY folder, not the vault.
        #
        # Both --disallowed-tools and --allowed-tools "" were measured as NOT
        # actually stopping it: asked to count the files in Office with tools
        # "disallowed", it went and counted them anyway, in five turns. So the
        # room narrated its own file-hunting out loud - "let me check", "that's
        # not right", "PowerShell's being stubborn" - as if that were dialogue.
        #
        # Giving it nowhere to look is the fix those flags wouldn't do. The
        # brain talks; worker.py has the vault and the tools. If the room needs
        # a fact off disk, it has to claim a job - which is the entire point.
        self.cwd = str(cwd or _blind_cwd())
        self._system = system
        self._lock = threading.Lock()
        self.last_cost = 0.0        # shadow price of the last turn, USD
        self.total_cost = 0.0
        self.proc = None
        self._spawn()

    # ------------------------------------------------------------- process

    def _spawn(self):
        cmd = [
            "claude", "-p",
            "--input-format", "stream-json",
            "--output-format", "stream-json",
            "--verbose",                      # required alongside stream-json
            "--include-partial-messages",     # deltas, so voices start early
            "--model", self.model,
            "--system-prompt", self._system or "You are a helpful meeting room.",
            "--disallowed-tools", *NO_TOOLS,
        ]
        env = dict(os.environ)
        # An API key on this machine would silently move the billing back onto
        # a card. The whole point of this brain is that it does not.
        env.pop("ANTHROPIC_API_KEY", None)
        # Extended thinking was costing the room EIGHT AND A HALF SECONDS before
        # anyone opened their mouth - measured, 9.71s to first token with it on
        # and 1.22s with it off. Nobody in a live conversation reasons silently
        # for nine seconds first. Tickets still think; worker.py sets its own
        # budget, because doing the work is where reasoning actually earns its
        # latency. This is the talking.
        env["MAX_THINKING_TOKENS"] = "0"
        self.proc = subprocess.Popen(
            cmd, cwd=self.cwd, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self):
        # An unread stderr pipe eventually fills and deadlocks the child.
        try:
            for line in self.proc.stderr:
                if line.strip():
                    print(f"    [claude] {line.strip()[:160]}")
        except Exception:
            pass

    def restart(self, system=None):
        """Fresh session - used when the system prompt has genuinely changed."""
        if system is not None:
            self._system = system
        self.close()
        self._spawn()

    def close(self):
        if not self.proc:
            return
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=3)
        except Exception:
            self.proc.kill()
        self.proc = None

    # ---------------------------------------------------------------- turn

    def stream(self, system, history):
        """Yield the reply piece by piece. Only the newest user line is sent -
        the running process is already holding everything said before it."""
        if system and system != self._system:
            self.restart(system)

        text = ""
        for msg in reversed(history):
            if msg.get("role") == "user":
                text = msg.get("content", "")
                break
        if not text:
            return

        with self._lock:
            if self.proc is None or self.proc.poll() is not None:
                self._spawn()                 # it died; the meeting continues
            payload = {"type": "user", "message": {
                "role": "user", "content": [{"type": "text", "text": text}]}}
            try:
                self.proc.stdin.write(json.dumps(payload) + "\n")
                self.proc.stdin.flush()
            except (BrokenPipeError, OSError) as exc:
                raise RuntimeError(f"the brain stopped listening ({exc})")

            for line in self.proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if ev.get("type") == "stream_event":
                    inner = ev.get("event", {})
                    if inner.get("type") == "content_block_delta":
                        d = inner.get("delta", {})
                        # thinking_delta is the model reasoning to itself. It is
                        # not dialogue and must never reach a voice.
                        if d.get("type") == "text_delta" and d.get("text"):
                            yield d["text"]

                elif ev.get("type") == "result":
                    self.last_cost = float(ev.get("total_cost_usd") or 0.0)
                    self.total_cost += self.last_cost
                    return


def _cli_ok():
    from shutil import which
    return which("claude") is not None


# ------------------------------------------------------------------ check

def _selftest():
    """Prove the free brain answers, and say how fast and at what shadow price."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    system = ("You are two people in a meeting: Rook (engineer, Australian, dry) "
              "and Nova (explainer, warm). Output ONLY lines shaped `Name: words`. "
              "One sentence each. No markdown.")
    print("\n  starting the free brain (claude -p, no API key)...")
    t0 = time.time()
    b = ClaudeCode(system=system)
    print(f"  up in {time.time() - t0:.1f}s")

    for q in ("are we live?", "and what did I just ask you?"):
        t0, first, buf = time.time(), None, ""
        for piece in b.stream(system, [{"role": "user", "content": q}]):
            if first is None:
                first = time.time() - t0
            buf += piece
        print(f"\n  you > {q}")
        for ln in buf.splitlines():
            if ln.strip():
                print(f"    {ln.strip()}")
        print(f"    [first word {first or 0:.2f}s · turn {time.time()-t0:.1f}s · "
              f"shadow ${b.last_cost:.4f}]")
    print("\n  the second answer proves the session stayed warm between turns.\n")
    b.close()


if __name__ == "__main__":
    _selftest()
