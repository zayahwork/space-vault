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

# --- per-account cap + warm ramp (card 028) ------------------------------
warm = {"address": "new@gmail.com", "app_password": "p", "warm_start": "2026-07-23"}
old = {"address": "old@gmail.com", "app_password": "p"}
d_early = datetime.date(2026, 7, 25)   # 2 days into the warm-up
d_late = datetime.date(2026, 8, 5)     # well past the first week
check("a new account is capped low in week one", o.account_cap(warm, d_early), o.WARM_CAP)
check("a warmed account reaches the full per-account cap", o.account_cap(warm, d_late),
      o.PER_ACCOUNT_CAP)
check("an account with no warm_start is treated as already warm",
      o.account_cap(old, d_early), o.PER_ACCOUNT_CAP)
check("an account can carry its own explicit cap",
      o.account_cap({"address": "x@x", "daily_cap": 12}, d_late), 12)

# --- segment-per-account home + thread stickiness ------------------------
homes_accts = [{"address": "a@gmail.com", "segments": ["operator", "insurer"]},
               {"address": "b@gmail.com", "segments": ["partner"]},
               {"address": "c@gmail.com"}]
hm = o.segment_homes(homes_accts)
check("an explicitly-assigned segment routes to its account", hm["operator"], "a@gmail.com")
check("a second explicit segment routes to its account", hm["partner"], "b@gmail.com")
check("every template segment gets a home", all(s in hm for s in o.TEMPLATES), True)
check("homes only point at real accounts", set(hm.values()) <= {"a@gmail.com", "b@gmail.com", "c@gmail.com"}, True)

thread_log = [{"ok": True, "id": "7", "account": "c@gmail.com"}]
check("a live thread keeps its original sender, not its segment home",
      o.home_address({"id": "7", "segment": "operator"}, homes_accts, hm, thread_log),
      "c@gmail.com")
check("a fresh row uses its segment home",
      o.home_address({"id": "8", "segment": "operator"}, homes_accts, hm, thread_log),
      "a@gmail.com")

# --- home-aware assignment defers rather than switching a thread's sender -
ha = [{"address": "a@gmail.com"}, {"address": "b@gmail.com"}]
hm2 = {"operator": "a@gmail.com", "insurer": "b@gmail.com"}
hrows = [{"id": "1", "segment": "operator"}, {"id": "2", "segment": "operator"},
         {"id": "3", "segment": "insurer"}]
paired, deferred = o.assign_home(ha, hrows, {"a@gmail.com": 1, "b@gmail.com": 5}, hm2, [])
check("home routing places each row on its home while room lasts",
      [(r["id"], acct["address"]) for r, acct in paired], [("1", "a@gmail.com"), ("3", "b@gmail.com")])
check("a row whose home is full is deferred, never rerouted",
      [r["id"] for r, _ in deferred], ["2"])

# --- founder-approval gate + warm/named hard block -----------------------
o.APPROVALS_PATH = tmp / "approvals.json"
o.APPROVALS_PATH.write_text(json.dumps({"operator": True}), encoding="utf-8")
check("an approved segment reads true", o.template_approved("operator"), True)
check("an unlisted segment defaults to not-approved", o.template_approved("insurer"), False)

o.DRAFTS_DIR = tmp / "nodrafts"
o.DRAFTS_DIR.mkdir(exist_ok=True)
base = {"company": "X", "notes": "", "email": "a@b.co", "sent_on": ""}
check("an approved-template todo row clears the automation gate",
      o.automated_holds({**base, "id": "1", "segment": "operator", "status": "todo"}), [])
check("an unapproved-template todo row is held from automation",
      bool(o.automated_holds({**base, "id": "2", "segment": "insurer", "status": "todo"})), True)
check("a hold/warm row is hard-blocked from automation",
      bool(o.automated_holds({**base, "id": "23", "segment": "insurer", "status": "hold"})), True)
check("an active-thread note is protected even at status todo",
      bool(o.automated_holds({**base, "id": "9", "segment": "operator", "status": "todo",
                              "notes": "ACTIVE THREAD - handle by hand"})), True)

print()
if fails:
    print(f"{len(fails)} FAILING: {fails}")
    sys.exit(1)
print("all green")
