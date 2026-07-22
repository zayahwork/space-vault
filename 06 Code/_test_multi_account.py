"""Feedback loop for multi-account sending. Nothing here opens a socket."""
import datetime
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

CODE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("outreach", CODE / "outreach.py")
o = importlib.util.module_from_spec(spec)
sys.modules["outreach"] = o
spec.loader.exec_module(o)

tmp = Path(tempfile.mkdtemp())
fails = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}: got {got!r}, want {want!r}")
        fails.append(name)


# --- load_auth ------------------------------------------------------------
o.AUTH_PATH = tmp / "auth.json"

o.AUTH_PATH.write_text(json.dumps({"address": "one@gmail.com",
                                   "app_password": "aaaa bbbb cccc dddd"}), encoding="utf-8")
check("legacy single account still loads", [a["address"] for a in o.load_auth()], ["one@gmail.com"])

o.AUTH_PATH.write_text(json.dumps({"accounts": [
    {"address": "one@gmail.com", "app_password": "aaaa bbbb cccc dddd"},
    {"address": "two@gmail.com", "app_password": "eeee ffff gggg hhhh"}]}), encoding="utf-8")
check("two accounts load in order", [a["address"] for a in o.load_auth()],
      ["one@gmail.com", "two@gmail.com"])

o.AUTH_PATH.write_text(json.dumps({"accounts": [
    {"address": "one@gmail.com", "app_password": "aaaa bbbb cccc dddd"},
    {"address": "two@gmail.com", "app_password": "PASTE THE APP PASSWORD HERE"}]}), encoding="utf-8")
check("an unconfigured account is skipped, not fatal",
      [a["address"] for a in o.load_auth()], ["one@gmail.com"])

# --- per-account daily counting ------------------------------------------
today = datetime.date.today().isoformat()
accounts = [{"address": "one@gmail.com", "app_password": "x"},
            {"address": "two@gmail.com", "app_password": "y"}]
log = [
    {"ok": True, "day": today},                              # pre-multi-account
    {"ok": True, "day": today, "from": "two@gmail.com"},
    {"ok": True, "day": today, "from": "TWO@gmail.com"},     # case shouldn't matter
    {"ok": False, "day": today, "from": "one@gmail.com"},    # failures don't count
    {"ok": True, "day": "2020-01-01", "from": "one@gmail.com"},
]
check("legacy rows count against the first account",
      o.sent_today_by_account(accounts, log),
      {"one@gmail.com": 1, "two@gmail.com": 2})

# --- rotation -------------------------------------------------------------
room = {"one@gmail.com": 25, "two@gmail.com": 25}
check("alternates between accounts",
      [a["address"] for a in o.assign_senders(accounts, room, 4)],
      ["one@gmail.com", "two@gmail.com", "one@gmail.com", "two@gmail.com"])

room = {"one@gmail.com": 1, "two@gmail.com": 25}
check("skips an account that has used its allowance",
      [a["address"] for a in o.assign_senders(accounts, room, 4)],
      ["one@gmail.com", "two@gmail.com", "two@gmail.com", "two@gmail.com"])

room = {"one@gmail.com": 0, "two@gmail.com": 0}
check("no allowance means no senders, and no infinite loop",
      o.assign_senders(accounts, room, 4), [])

print()
if fails:
    print(f"{len(fails)} FAILING: {fails}")
    sys.exit(1)
print("all green")
