"""Feedback loop for card 026: a competitor row must be sendable without a
hand-written draft. Nothing here opens a socket or touches the real CSV."""
import importlib.util
import sys
import tempfile
from pathlib import Path

CODE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("outreach", CODE / "outreach.py")
o = importlib.util.module_from_spec(spec)
sys.modules["outreach"] = o
spec.loader.exec_module(o)

# Point drafts at an empty dir so no hand-written draft can rescue the row -
# the whole bug was that only a hand draft made competitor rows sendable.
o.DRAFTS_DIR = Path(tempfile.mkdtemp())

fails = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}: got {got!r}, want {want!r}")
        fails.append(name)


row = {"id": "999", "segment": "competitor", "company": "Testco SSA",
       "why_them": "published on pattern-of-life", "contact_route": "paper",
       "email": "person@testco.example", "status": "todo",
       "sent_on": "", "notes": ""}

check("competitor segment has a template", "competitor" in o.TEMPLATES, True)
check("a template-less competitor row has no blockers",
      o.blockers(row, checks={}, mailed=set()), [])

subject, body = o.compose(row)
check("composed body carries no unfilled placeholder",
      [p for p in o.PLACEHOLDERS if p in body], [])
check("the email says straight who we are (not a customer)",
      "not a customer" in body.lower(), True)
raw = o.TEMPLATES["competitor"][1]   # the signature compose() appends is 2 lines by design
check("hard-wrap rule: each template paragraph is one unbroken line",
      all(len(par.splitlines()) == 1 for par in raw.split("\n\n") if par.strip()),
      True)

print()
if fails:
    print(f"{len(fails)} FAILING: {fails}")
    sys.exit(1)
print("all green")
