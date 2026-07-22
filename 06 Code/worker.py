"""
worker.py - the queue that hands work from the room to Claude Code.

THE SHAPE OF THE ROOM
The founder talks. The team argues it out and ONE of them commits to a job. That
job becomes a ticket. Tickets run STRICTLY ONE AT A TIME through `claude -p`,
which is Claude Code running headless in the vault - it reads files, writes code,
runs things, and comes back with a result. The person who raised the ticket
reports what came back, out loud, in their own voice.

Serial is the whole point. Six agents firing work in parallel is not a team, it's
a race condition with personalities. One ticket, finished and reported, then the
next.

THE TICKET RUNS AS THE PERSON WHO CLAIMED IT
This is what makes them more than narrators. When Fitz takes a job, the headless
session is briefed as Fitz - their role, their temperament, and every lesson
already banked in `brains/Fitz.md`. So the debugger goes looking for the boring
failure nobody checked, because that is who is holding the keyboard. The work and
the personality are the same thing, not a costume worn over a generic agent.

AND THEY LEARN FROM IT
A ticket may end its reply with one `[LEARNED] ...` line. Only then is anything
written to that person's brain, and it is banked as a hypothesis unless the work
demonstrably proved it. Auto-banking every ticket would fill six files with noise
and launder guesses into facts - the one thing brain.py exists to prevent.

APPROVAL
By default a ticket waits for you to press Do it, because this runs a tool that
can edit files in C:\\Space. `--auto` removes that gate. Nothing here is
recoverable-by-magic: the vault is a git-less folder, so `--auto` is a real
decision, not a convenience toggle.

COST
No ANTHROPIC_API_KEY is used or wanted - this rides the Claude Code subscription
already signed in on this machine. The `total_cost_usd` the CLI reports is what
the same call WOULD have cost on the API, so it goes on the board as a shadow
price next to the notional salary ledger from payroll.py. Neither is a charge.
"""

import json
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parent                      # C:\Space
LEDGER = HERE / "work_ledger.jsonl"
BRAINS = HERE / "brains"

# What a ticket is allowed to touch. Read/search freely; write and run only
# because that is the job. Nothing here reaches outside the vault's tree.
ALLOWED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "TodoWrite"]

WORKER_BRIEF = """You are {who}, the {role} of a small satellite-analytics startup.
This is not a role you are playing - it is your job, and you are the one doing it.

{persona}

{memory}
You committed to this job out loud in the war room a moment ago, in front of the
founder. Now do it for real: read the files, make the change, run the thing, check
the number.

Then reply with AT MOST 4 short lines, written the way YOU talk, to be read aloud
in the meeting by you:
- what you actually did (files touched, commands run)
- the number or result that matters, if there is one
- anything that turned out to be wrong or blocked

Never claim something ran if it did not. If you could not do it, say why in one
line - the room would rather hear that than a tidy sentence covering a failure.
No markdown, no headings, no bullet characters, no stage directions.

If - and only if - this job taught you something worth carrying into future work,
add one final line starting with [LEARNED] followed by the lesson in one sentence.
Most jobs teach nothing reusable. Leave it off when that is the case."""


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
    learned: str = ""
    cost_usd: float = 0.0
    duration_s: float = 0.0

    def public(self):
        d = asdict(self)
        d["t"] = "ticket"
        return d


def _memory_of(who):
    """That person's banked lessons, so they start the job knowing what they know."""
    f = BRAINS / f"{who}.md"
    if not f.exists():
        return ""
    lessons = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines()
               if ln.strip().startswith("- [") and "[retired]" not in ln]
    if not lessons:
        return ""
    return ("What you have already learned on this project - use it, and keep the\n"
            "proven/hypothesis distinction if you refer to any of it:\n"
            + "\n".join(lessons) + "\n")


class WorkQueue:
    """One ticket at a time. Nothing overlaps, ever."""

    def __init__(self, emit, team, auto=False, model=None, on_done=None):
        self.emit = emit
        self.team = team                 # name -> {role, persona, ...}
        self.auto = auto
        self.model = model
        self.on_done = on_done           # called with the finished Ticket
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
        self.emit(t="work_summary", **self.summary())
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
        self.emit(t="work_summary", **self.summary())

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
                self.emit(t="work_summary", **self.summary())
                self._run(nxt)
                with self.lock:
                    self.running = None
                self.emit(**nxt.public())
                self.emit(t="work_summary", **self.summary())
                if self.on_done:
                    try:
                        self.on_done(nxt)
                    except Exception as exc:
                        print(f"    [report-back failed: {exc}]")

    def _run(self, t):
        person = self.team.get(t.who, {})
        brief = WORKER_BRIEF.format(
            who=t.who,
            role=person.get("role", "engineer"),
            persona=person.get("persona", ""),
            memory=_memory_of(t.who),
        )
        prompt = (f"The job you committed to:\n{t.task}\n\n"
                  f"You are working in {VAULT}. The code lives in '06 Code'.")
        cmd = ["claude", "-p", prompt,
               "--output-format", "json",
               "--append-system-prompt", brief,
               "--allowed-tools", *ALLOWED_TOOLS,
               "--permission-mode", "acceptEdits"]
        if self.model:
            cmd += ["--model", self.model]
        env = dict(os.environ)
        env.pop("ANTHROPIC_API_KEY", None)     # subscription, never a card
        try:
            proc = subprocess.run(cmd, cwd=str(VAULT), capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=900, env=env)
            if proc.returncode != 0:
                raise RuntimeError((proc.stderr or proc.stdout or "")[:300])
            data = json.loads(proc.stdout)
            t.result = (data.get("result") or "").strip()
            t.cost_usd = float(data.get("total_cost_usd") or 0.0)
            t.status = "failed" if data.get("is_error") else "done"
            self._split_lesson(t)
        except subprocess.TimeoutExpired:
            t.status, t.result = "failed", "took longer than 15 minutes and was stopped"
        except Exception as exc:
            t.status, t.result = "failed", str(exc)[:300]
        finally:
            t.finished = time.time()
            t.duration_s = round(t.finished - t.started, 1)
            self._log(t)

    def _split_lesson(self, t):
        """Pull the optional [LEARNED] line out of the reply and bank it."""
        keep = []
        for line in t.result.splitlines():
            if line.strip().upper().startswith("[LEARNED]"):
                t.learned = line.strip()[9:].strip(" :-")
            else:
                keep.append(line)
        t.result = "\n".join(keep).strip()
        if not t.learned or t.status != "done":
            return
        try:
            import brain
            brain.learn(t.who, t.learned,
                        evidence=f"from work ticket #{t.id}: {t.task[:120]}",
                        proven=False)
        except Exception as exc:
            print(f"    [couldn't bank {t.who}'s lesson: {exc}]")

    def _log(self, t):
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(t)) + "\n")
