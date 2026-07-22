"""contact_check.py - is each outreach route actually reachable?

For every row in outreach_targets.csv (or just the batch-2 slice with --batch2):
  - email routes  -> does the domain have MX records? (can it receive mail at all)
  - form routes   -> does the URL return a live page? (HTTP status, follows redirects)

No sending, no scraping of personal data. Just: can we reach this door.
Writes contact_check.csv next to the targets file, and appends one JSON line
per route to outreach_validation.jsonl - that file is what outreach.py reads
before it will draft or send to anybody, so this is the gate, not a report.

Usage:
  python contact_check.py --batch2              # ids 41-52
  python contact_check.py --batch2 --reachable  # print only the live ones
"""
import argparse
import csv
import datetime
import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = os.path.join(HERE, "outreach_targets.csv")
OUT = os.path.join(HERE, "contact_check.csv")
VALIDATION = os.path.join(HERE, "outreach_validation.jsonl")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def has_mx(domain, timeout=6):
    """True/False/None(unknown) - does this domain publish MX records?

    No dnspython here, so shell out to nslookup, which Windows always has.
    """
    import subprocess
    try:
        p = subprocess.run(["nslookup", "-type=MX", domain],
                           capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return None, str(e)
    txt = (p.stdout or "") + (p.stderr or "")
    hits = [ln.strip() for ln in txt.splitlines() if "mail exchanger" in ln.lower()]
    if hits:
        return True, hits[0]
    if "can't find" in txt.lower() or "non-existent" in txt.lower():
        return False, "no MX / NXDOMAIN"
    return None, "inconclusive"


def check_url(url, timeout=15):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(200000).decode("utf-8", "ignore").lower()
            form = ("<form" in body) or ("mailto:" in body) or ("hubspot" in body)
            return r.status, r.geturl(), form, ""
    except urllib.error.HTTPError as e:
        return e.code, url, False, "http error"
    except Exception as e:
        return None, url, False, type(e).__name__ + ": " + str(e)[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-id", type=int, default=1)
    ap.add_argument("--batch2", action="store_true", help="ids 41-52 only")
    ap.add_argument("--reachable", action="store_true",
                    help="print only the routes that came back reachable")
    args = ap.parse_args()
    checked_at = datetime.datetime.now().isoformat(timespec="seconds")
    lo = 41 if args.batch2 else args.from_id

    rows = list(csv.DictReader(open(TARGETS, encoding="utf-8")))
    out = []
    for row in rows:
        try:
            rid = int(row["id"])
        except (TypeError, ValueError):
            continue
        if rid < lo:
            continue
        route = (row.get("email") or row.get("contact_route") or "").strip()
        route = route.split(" ")[0]  # strip "(unverified)" tails
        rec = {"id": rid, "company": row["company"], "route": route,
               "kind": "", "ok": "", "detail": ""}
        if "@" in route:
            rec["kind"] = "email"
            dom = route.split("@")[-1]
            ok, detail = has_mx(dom)
            rec["ok"] = {True: "YES", False: "NO", None: "?"}[ok]
            rec["detail"] = detail
        elif route.startswith("http"):
            rec["kind"] = "form"
            code, final, form, err = check_url(route)
            # A 403/429 is the server answering - it's refusing a bot, not gone.
            # Aerospace Corp returned 200 then 403 three minutes apart. Marking
            # that "dead" would bin a live target forever. Only 404/410/DNS is dead.
            if code == 200:
                rec["ok"] = "YES" if form else "PAGE"
            elif code in (401, 403, 405, 406, 429):
                rec["ok"] = "BLOCK"
            else:
                rec["ok"] = "NO"
            rec["detail"] = "%s %s%s" % (code, final if final != route else "",
                                         (" | " + err) if err else "")
        else:
            rec["kind"] = "none"
            rec["ok"] = "NO"
            rec["detail"] = "no route on file"
        out.append(rec)
        if not args.reachable or rec["ok"] in ("YES", "PAGE", "BLOCK"):
            print("%-3s %-24s %-5s %-5s %s" % (rec["id"], rec["company"][:24],
                                               rec["kind"], rec["ok"],
                                               rec["detail"][:70]), flush=True)

    # The gate outreach.py reads. Append-only: an old check stays on the record,
    # the newest line for an id wins.
    with open(VALIDATION, "a", encoding="utf-8") as f:
        for rec in out:
            # Reachable = the door opened: MX exists, or the page returned 200.
            # PAGE = 200, no <form> spotted. BLOCK = 403/429, a human browser gets in.
            f.write(json.dumps({**rec, "reachable": rec["ok"] in ("YES", "PAGE", "BLOCK"),
                                "checked_at": checked_at}) + "\n")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "company", "route", "kind",
                                          "ok", "detail"])
        w.writeheader()
        w.writerows(out)
    live = [r for r in out if r["ok"] in ("YES", "PAGE", "BLOCK")]
    dead = [r for r in out if r["ok"] not in ("YES", "PAGE", "BLOCK")]
    print("\n%d/%d routes reachable (%d confirmed, %d live page, %d bot-blocked "
          "- open those in a browser) -> %s"
          % (len(live), len(out), sum(1 for r in live if r["ok"] == "YES"),
             sum(1 for r in live if r["ok"] == "PAGE"),
             sum(1 for r in live if r["ok"] == "BLOCK"), OUT))
    print("logged %d checks -> %s" % (len(out), os.path.basename(VALIDATION)))
    print("reachable ids: " + (", ".join(str(r["id"]) for r in live) or "none"))
    print("dead        : " + (", ".join("%s %s" % (r["id"], r["company"])
                                        for r in dead) or "none"))


if __name__ == "__main__":
    main()
