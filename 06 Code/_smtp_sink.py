"""End-to-end feedback loop for the three-account send engine (card 028).

This is the one test that actually opens sockets - but only to a throwaway SMTP
sink on 127.0.0.1 that speaks just enough of the protocol to swallow a message
and remember which account sent it. Nothing leaves the machine, no Gmail login
happens (the plain path skips it), and the whole thing runs against temp files.

What it proves the machinery does, live, across three mailboxes:
  - each mailbox honours its OWN daily cap, and a run that wants to send more
    than the caps allow sends exactly the caps and no more;
  - a brand-new account is held to the warm-up ceiling, not its full cap;
  - every row goes out from its segment's home account;
  - a thread NEVER changes sender - a row with an earlier send from account C
    goes back out from C even though its segment's home is a different account.

Run:  python _smtp_sink.py
"""
import datetime
import importlib.util
import json
import re
import socket
import sys
import tempfile
import threading
import types
from collections import Counter
from pathlib import Path

CODE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("outreach", CODE / "outreach.py")
o = importlib.util.module_from_spec(spec)
sys.modules["outreach"] = o
spec.loader.exec_module(o)

FIELDS = o.FIELDS
TODAY = datetime.date.today().isoformat()
fails = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}: got {got!r}, want {want!r}")
        fails.append(name)


# --- the sink -------------------------------------------------------------
class Sink:
    """A minimal SMTP server that accepts everything and records MAIL FROM.

    It has to survive several messages down one connection, because the engine
    opens exactly one connection per account and reuses it for that account's
    whole batch.
    """

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(8)
        self.sock.settimeout(0.3)
        self.port = self.sock.getsockname()[1]
        self.senders = []            # one MAIL FROM per message accepted
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=2)
        self.sock.close()

    def reset(self):
        self.senders = []

    def _serve(self):
        while not self._stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn):
        f = conn.makefile("rwb", buffering=0)

        def reply(line):
            f.write((line + "\r\n").encode())

        reply("220 sink ready")
        mail_from = None
        try:
            while True:
                raw = f.readline()
                if not raw:
                    break
                cmd = raw.decode("utf-8", "replace").strip()
                up = cmd.upper()
                if up.startswith(("EHLO", "HELO")):
                    reply("250 sink")
                elif up.startswith("MAIL FROM"):
                    m = re.search(r"<([^>]*)>", cmd)
                    mail_from = m.group(1) if m else ""
                    reply("250 ok")
                elif up.startswith("RCPT"):
                    reply("250 ok")
                elif up == "DATA":
                    reply("354 end with .")
                    while True:
                        d = f.readline()
                        if not d or d in (b".\r\n", b".\n"):
                            break
                    self.senders.append(mail_from)
                    mail_from = None
                    reply("250 queued")
                elif up == "RSET":
                    mail_from = None
                    reply("250 ok")
                elif up == "QUIT":
                    reply("221 bye")
                    break
                elif up.startswith("NOOP"):
                    reply("250 ok")
                else:
                    reply("250 ok")
        except OSError:
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass


def send_args(port, segment=None):
    return types.SimpleNamespace(
        n=o.MAX_PER_RUN, segment=segment, ids=None, mix=True, live=True,
        smtp_host="127.0.0.1", smtp_port=port, smtp_plain=True, gap=0,
        skip_validation=True)


def write_workspace(rows, accounts, approvals):
    ws = Path(tempfile.mkdtemp())
    o.CSV_PATH = ws / "targets.csv"
    o.LOG_PATH = ws / "log.jsonl"
    o.AUTH_PATH = ws / "auth.json"
    o.APPROVALS_PATH = ws / "approvals.json"
    o.DRAFTS_DIR = ws / "drafts"          # empty: templates only, no hand drafts
    o.VALIDATION_PATH = ws / "validation.jsonl"
    o.DRAFTS_DIR.mkdir()
    o.save(rows)
    o.AUTH_PATH.write_text(json.dumps({"accounts": accounts}), encoding="utf-8")
    o.APPROVALS_PATH.write_text(json.dumps(approvals), encoding="utf-8")
    return ws


def row(rid, segment, email, status="todo", notes=""):
    return {"id": str(rid), "segment": segment, "company": f"{segment}-{rid}",
            "why_them": "sink test", "contact_route": "test", "email": email,
            "status": status, "sent_on": "", "notes": notes}


def run_until_dry(port, segment=None, cap_iters=25):
    """Fire the drip over and over until a run sends nothing, like the real
    scheduled task would across a day. Returns the workspace's final rows."""
    for _ in range(cap_iters):
        before = None
        rows = o.load()
        # count sends in the log before this run
        before = sum(1 for e in o.read_log() if e.get("ok"))
        o.send_batch(rows, send_args(port, segment))
        after = sum(1 for e in o.read_log() if e.get("ok"))
        if after == before:
            break
    return o.load()


# =========================================================================
sink = Sink()
sink.start()
try:
    # --- scenario 1: three accounts, real caps, home routing, warm ramp ---
    accounts = [
        {"address": "a@sink", "app_password": "a a a a", "segments": ["operator"],
         "daily_cap": 3},
        {"address": "b@sink", "app_password": "b b b b", "segments": ["insurer"],
         "warm_start": TODAY},                       # warm: capped at WARM_CAP
        {"address": "c@sink", "app_password": "c c c c", "segments": ["partner"],
         "daily_cap": 3},
    ]
    rows = ([row(i, "operator", f"op{i}@t.co") for i in range(1, 7)]     # 6, cap 3
            + [row(i, "insurer", f"in{i}@t.co") for i in range(11, 21)]  # 10, warm cap 8
            + [row(i, "partner", f"pa{i}@t.co") for i in range(31, 35)]) # 4, cap 3
    write_workspace(rows, accounts, {"operator": True, "insurer": True, "partner": True})

    run_until_dry(sink.port)
    counts = Counter(sink.senders)

    check("account a stops at its daily cap", counts["a@sink"], 3)
    check("a warm account stops at the warm-up ceiling, not its full cap",
          counts["b@sink"], o.WARM_CAP)
    check("account c stops at its daily cap", counts["c@sink"], 3)
    check("no mailbox ever exceeds its own cap",
          all([counts["a@sink"] <= 3, counts["b@sink"] <= o.WARM_CAP,
               counts["c@sink"] <= 3]), True)
    check("total sent equals the sum of the caps, no more",
          sum(counts.values()), 3 + o.WARM_CAP + 3)

    # every send went out from its segment's home account
    id_seg = {r["id"]: r["segment"] for r in rows}
    seg_home = {"operator": "a@sink", "insurer": "b@sink", "partner": "c@sink"}
    log = o.read_log()
    routed_right = all(e.get("account") == seg_home[id_seg[str(e["id"])]]
                       for e in log if e.get("ok"))
    check("every email left from its segment's home account", routed_right, True)
    check("the log records the sending account on every row",
          all(e.get("account") for e in log if e.get("ok")), True)

    # --- scenario 2: a thread never changes sender -----------------------
    sink.reset()
    # One insurer row whose segment home is b@sink, but whose thread already
    # went out from c@sink. Stickiness must win: it goes back out from c@sink.
    accounts2 = [
        {"address": "a@sink", "app_password": "a a a a", "segments": ["operator"]},
        {"address": "b@sink", "app_password": "b b b b", "segments": ["insurer"]},
        {"address": "c@sink", "app_password": "c c c c", "segments": ["partner"]},
    ]
    ws = write_workspace([row(11, "insurer", "in11@t.co")], accounts2,
                         {"insurer": True})
    # seed the audit log with the thread's original send from c@sink
    o.log_send({"kind": "send", "id": "11", "company": "insurer-11",
                "to": "old@t.co", "account": "c@sink", "ok": True})
    o.send_batch(o.load(), send_args(sink.port))
    check("a thread goes back out from its original sender, not its segment home",
          sink.senders, ["c@sink"])

finally:
    sink.stop()

print()
if fails:
    print(f"{len(fails)} FAILING: {fails}")
    sys.exit(1)
print("all green")
