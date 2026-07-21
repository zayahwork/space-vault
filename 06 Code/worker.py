"""
worker.py - the queue that hands work from the room to Claude Code.

THE SHAPE OF THE ROOM
The founder talks. The team argues it out and ONE of them commits to a job. That
job becomes a ticket. Tickets run STRICTLY ONE AT A TIME through `claude -p`,
which is Claude Code running headless in the vault - it reads files, writes code,
runs things, and comes back with a result. The person who raised the ticket
reports what came back, and banks what they learned.

Serial is the whole point. Six agents firing work in parallel is not a team, it's
a race condition with personalities. One ticket, finished and reported, then the
next.

APPROVAL
By default a ticket waits for you to press Do it, because this runs a tool that
can edit files in C:\\Space. `--auto` removes that gate. Nothing here is
recoverable-by-magic: the vault is a git-less folder, so `--auto` is a real
decision, not a convenience toggle.

COST
`claude -p` reports what each call actually cost. That number is real money, and
it goes on the board next to the notional salary ledger from payroll.py - so you
can always see the pretend budget and the actual spend side by side.
"""

import json
import subprocess
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parent                      # C:\Space
LEDGER = HERE / "work_ledger.jsonl"

# What a ticket is allowed to touch. Read/search freely; write and run only
# because that is the job. Nothing here reaches outside the vault's tree.
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep,Bash,TodoWrite"

WORKER_BRIEF = """You are the working half of a small satellite-analytics startup's
war room. A teammate in the room committed to this job out loud and handed it to you.

Do the job. Then reply with AT MOST 4 short lines, written to be read aloud in a
meeting by the person who asked for it:
- what you actually did (files touched, commands run)
- the number or result that matters, if there is one
- anything that turned out to be wrong or blocked
Never claim something ran if it did not. If you could not do it, say why in one line.
No markdown, no headings, no bullet characters."""


@dataclass
class Ticket:
    id: int
    who: str
    task: str
    status: str = "waiting"          # waiting | running | done | failed | skipped
    created: float = field(default_factory=time.time)
    started: float = 0.0
    finished: float = 0.0
    result: str = ""
    cost_usd: float = 0.0
    duration_s: float = 0.0

    def public(self):
        d = asdict(self)
        d["t"] = "ticket"
        return d


class WorkQueue:
    """One ticket at a time. Nothing overlaps, ever."""

    def __init__(self, emit, auto=False, model=None):
        self.emit = emit
        self.auto = auto
        self.model = model
        self.tickets = []
        self.lock = threading.Lock()
        self.pending = threading.Event()
        self.running = None
        threading.Thread(target=self._pump, daemon=True).start()

    # ---------------------------------------------------------------- api

    def add(self, who, task):
        with self.lock:
            t = Ticket(id=len(self.tickets) + 1, who=who, task=task.strip())
            if self.auto:
                t.status = "queued"
            self.tickets.append(t)
        self.emit(**t.public())
        if self.auto:
            self.pending.set()
        return t

    def approve(self, tid):
        with self.lock:
            t = self._find(tid)
            if not t or t.status != "waiting":
                return
            t.status = "queued"
        self.emit(**t.public())
        self.pending.set()

    def skip(self, tid):
        with self.lock:
            t = self._find(tid)
            if not t or t.status not in ("waiting", "queued"):
                return
            t.status = "skipped"
        self.emit(**t.public())

    def _find(self, tid):
        return next((x for x in self.tickets if x.id == int(tid)), None)

    def summary(self):
        done = [t for t in self.tickets if t.status == "done"]
        return {
            "open": sum(1 for t in self.tickets if t.status in ("waiting", "queued")),
            "done": len(done),
            "failed": sum(1 for t in self.tickets if t.status == "failed"),
            "spent_usd": round(sum(t.cost_usd for t in self.tickets), 4),
            "running": self.running.id if self.running else None,
        }

    # ---------------------------------------------------------------- loop

    def _pump(self):
        while True:
            self.pending.wait(timeout=2)
            self.pending.clear()
            while True:
                with self.lock:
                    nxt = next((t for t in self.tickets if t.status == "queued"), None)
                    if not nxt:
                        break
                    nxt.status = "running"
                    nxt.started = time.time()
                    self.running = nxt
                self.emit(**nxt.public())
                self._run(nxt)
                with self.lock:
                    self.running = None
                self.emit(**nxt.public())
                self.emit(t="work_summary", **self.summary())

    def _run(self, t):
        prompt = (f"{WORKER_BRIEF}\n\n"
                  f"The job, from {t.who}:\n{t.task}\n\n"
                  f"You are working in {VAULT}. The code lives in '06 Code'.")
        cmd = ["claude", "-p", prompt,
               "--output-format", "json",
               "--allowed-tools", ALLOWED_TOOLS,
               "--permission-mode", "acceptEdits"]
        if self.model:
            cmd += ["--model", self.model]
        try:
            proc = subprocess.run(cmd, cwd=str(VAULT), capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=900)
            if proc.returncode != 0:
                raise RuntimeError((proc.stderr or proc.stdout or "")[:300])
            data = json.loads(proc.stdout)
            t.result = (data.get("result") or "").strip()
            t.cost_usd = float(data.get("total_cost_usd") or 0.0)
            t.status = "failed" if data.get("is_error") else "done"
        except subprocess.TimeoutExpired:
            t.status, t.result = "failed", "took longer than 15 minutes and was stopped"
        except Exception as exc:
            t.status, t.result = "failed", str(exc)[:300]
        finally:
            t.finished = time.time()
            t.duration_s = round(t.finished - t.started, 1)
            self._log(t)

    def _log(self, t):
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(t)) + "\n")
