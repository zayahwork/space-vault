"""local_brain.py - free, local inference for the mechanical stuff that doesn't need
Claude. Any script (PowerShell or Python) can call this instead of spending plan/API
credits on a task that's really just classification or reformatting over facts someone
else already assembled.

Reuses the exact fix room.py found: 127.0.0.1, never localhost (Windows resolves
localhost to ::1 first; Ollama only binds 127.0.0.1; that round trip costs ~2s per call
which multiplies fast in a loop).

DO NOT use this for anything load-bearing: published numbers, code, email text a human
receives, or company judgment calls. It reliably invents details under pressure - that's
fine for "is this reply interested or an auto-responder", not fine for "what's our
verified rate." See Decision Log 2026-07-22: "local 8B only for low-stakes classification."

Usage as a library:
    from local_brain import ask
    ask("Classify this email as interested/not-interested/auto-reply: ...")

Usage from the command line (so PowerShell scripts can call it with zero Python glue):
    python local_brain.py "your prompt here"
    python local_brain.py "your prompt" --model qwen2.5-coder:1.5b
"""
import argparse
import json
import sys
import time
import urllib.request
import urllib.error

OLLAMA = "http://127.0.0.1:11434"          # NOT localhost. See the docstring.
DEFAULT_MODEL = "qwen2.5:3b"               # already pulled on this machine; general text.


def _server_up(timeout=2):
    try:
        urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=timeout).read()
        return True
    except Exception:
        return False


def _nudge_server_awake():
    """Ollama's own CLI lazily launches the background server if it's not running -
    same side effect that happened when this was diagnosed. Harmless if already up."""
    import subprocess
    try:
        subprocess.run(["ollama", "list"], capture_output=True, timeout=10)
    except Exception:
        pass


def ask(prompt, system=None, model=DEFAULT_MODEL, timeout=60, retries=1):
    """One-shot, non-streaming call. Returns the model's full text response, or raises
    RuntimeError with a clear reason (never silently returns empty on failure)."""
    if not _server_up():
        _nudge_server_awake()
        for _ in range(10):
            if _server_up():
                break
            time.sleep(1)
        else:
            raise RuntimeError(
                f"ollama isn't answering on {OLLAMA} after nudging it awake. "
                "Is Ollama installed and on PATH?"
            )

    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    body = json.dumps({
        "model": model, "stream": False, "keep_alive": "10m",
        "messages": messages,
        "options": {"temperature": 0.2, "num_predict": 400},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/chat", data=body,
        headers={"Content-Type": "application/json"},
    )
    last_exc = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                return data.get("message", {}).get("content", "").strip()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            time.sleep(1)
    raise RuntimeError(f"local_brain.ask() failed after {retries + 1} attempt(s): {last_exc}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("prompt")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--system", default=None)
    args = p.parse_args()
    try:
        print(ask(args.prompt, system=args.system, model=args.model))
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
