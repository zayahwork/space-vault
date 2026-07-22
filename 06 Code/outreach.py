"""
outreach.py - the daily outreach batch, drafted and tracked.

Fifteen emails a day only works if writing them isn't the bottleneck. This pulls
the next N untouched targets, fills the right template for their segment, and
keeps the sent/replied ledger in one CSV so nobody gets emailed twice.

It can also send, through Gmail, without a human pasting each one. That path is
off by default and stays off unless you type --live. Everything it would send
prints first. A bad send can't be unsent, so the safeties are not optional:
no email address means no send, an unfilled template placeholder means no send,
and it will never do more than MAX_PER_RUN in one go.

Bounces are handled in both directions. A 5xx refusal at send time means the
address is dead, so the row is marked bounced and never retried; a 4xx means
try later and the row is left alone. Bounces that arrive later, as mail, are
picked up by --check-bounces over IMAP.

Sending needs 06 Code/gmail_auth.json (gitignored):
  {"address": "you@gmail.com", "app_password": "abcd efgh ijkl mnop"}
That is a Google App Password (myaccount.google.com/apppasswords), not the
account password - normal passwords are refused by SMTP.

Usage:
  python outreach.py                      # today's 15 drafts
  python outreach.py -n 5 --segment insurer
  python outreach.py --send               # dry run: exactly what would go out
  python outreach.py --send --live        # actually send, log, mark sent
  python outreach.py --send --ids 61 59   # hand-send named rows, in that order
  python outreach.py --send --live --ids 61 59
  python outreach.py --check-bounces      # read bounce mail, mark dead addresses
  python outreach.py --sent 3 7 11        # log what went out by hand
  python outreach.py --replied 7 --note "wants a call"
  python outreach.py --status             # the ledger
"""

import argparse
import csv
import datetime
import email
import imaplib
import json
import mimetypes
import re
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
DRAFTS_DIR = HERE / "drafts"
CSV_PATH = HERE / "outreach_targets.csv"
AUTH_PATH = HERE / "gmail_auth.json"
LOG_PATH = HERE / "outreach_log.jsonl"
VALIDATION_PATH = HERE / "outreach_validation.jsonl"
FIELDS = ["id", "segment", "company", "why_them", "contact_route", "email",
          "status", "sent_on", "notes"]

FROM_NAME = "Zayah Nelson"
MAX_PER_RUN = 5           # hard ceiling per run. A loop bug costs 5 emails, not 500.
DAILY_CAP = 25            # across every run today, counted from the audit log.
#
# Why 25 and not more: Gmail's own SMTP limit for a free account is 500
# recipients a day, so volume is not what gets an account restricted. What gets
# it restricted is the PATTERN - cold mail to addresses that never reply, spam
# complaints, and bounces. 25/day from a personal address is invisible to the
# rate limiter and slow enough that a bad batch is caught before it repeats.
# MAX_PER_RUN is deliberately far below DAILY_CAP so the drip has to run many
# times to reach the cap; that is what spreads the send out across the day.
GAP_SECONDS = 20          # Gmail dislikes bursts, and so does a human reader.

# A Message-ID inside a bounce report is the one thing that survives intact -
# subjects get rewritten, addresses get rewritten, the ID we logged does not.
# Anchored to the header so From:/To: addresses in <brackets> aren't mistaken
# for it.
MSGID_RE = re.compile(r"(?im)^\s*Message-ID:\s*(<[^<>]+>)")

# If a drafted body still contains one of these, it is a template, not an email.
PLACEHOLDERS = ("[ONE specific", "(find a contact:", "replace this line")

SIGN = """Zayah Nelson
425-409-8684"""

# One template per segment. All of them ask a question and sell nothing - the
# scoreboard is people describing their pain unprompted, not pitches delivered.
#
# Each paragraph is ONE unbroken line on purpose. Hard-wrapping at 75 columns
# looks tidy in a terminal and broken in a mail client: the reader's window wraps
# it a second time, so every paragraph comes out as a ragged staircase, worst on
# a phone. Let the client do the wrapping - it knows the screen width and we do not.
TEMPLATES = {
    "operator": (
        "how do you handle a neighbour that changes its behaviour?",
        """Hi,

I'm working on detecting when a satellite breaks its own routine - a maneuver, a drift, anything off its normal pattern - using only public tracking data.

I'm trying to understand the operator side before I build any further. When something near one of your satellites starts behaving differently, how do you find out today, and how much of that is someone watching screens versus a tool telling you?

Genuinely just trying to learn how this works in practice - not selling anything. Fifteen minutes would help me a lot.

Thanks,"""),
    "insurer": (
        "question about how orbital behavior figures into space underwriting",
        """Hi,

I'm an ML engineer working on detecting satellite behavior - when objects maneuver or act outside their normal pattern - from public tracking data.

I'm trying to understand the insurance side: when a LEO mission gets priced, how much does the actual behavior of the objects around it factor in, and where does that information come from today?

Would someone on your space team have 15 minutes for a couple of questions? Not selling anything - genuinely trying to learn how underwriters see this.

Thanks,"""),
    "partner": (
        "public-data maneuver detection - comparing notes",
        """Hi,

I'm building maneuver detection and pattern-of-life from free public orbit data (GP history / OMM), and I'd rather learn from people already doing this than guess.

Two things I keep hitting: public GP data is smoothed around maneuvers by design, and the labelled datasets available are partly simulated. How do you handle either of those - or do you consider them solved?

Happy to share what I've measured, including where my own approach falls over.

Thanks,"""),
    "academic": (
        "question from someone working on maneuver detection from public data",
        """Hi,

I'm working on maneuver detection and pattern-of-life using only free public orbit data, and I've run into a question your work speaks to directly.

[ONE specific question about their paper or dataset - replace this line. A generic email to a researcher is a wasted email.]

I'd rather ask than assume. Thanks for any steer.

Thanks,"""),
    "gov": (
        "question about public orbit data availability",
        """Hi,

I'm building maneuver detection from free public orbit data and I'm trying to understand where that data is heading - what's expected to stay public, and what changes are planned.

Is there someone who handles questions like this? Happy to be pointed at a document rather than take anyone's time.

Thanks,"""),
}


def load():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(rows):
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def draft(row):
    subject, body = compose(row)
    hand = read_draft(row)
    to = row["email"] or f"(find a contact: {row['contact_route']})"
    attached = ", ".join(p.name for p in attachments_for(row))
    return (
        f"{'─' * 74}\n"
        f"#{row['id']}  {row['company']}   [{row['segment']}]"
        + ("  (hand-written)" if hand else "") + "\n"
        f"why them : {row['why_them']}\n"
        f"to       : {to}\n"
        f"subject  : {subject}\n"
        + (f"attached : {attached}\n" if attached else "")
        + f"\n{body}"
        + (f"\n⚠ {row['notes']}\n" if row["notes"] else "")
    )


def read_draft(row):
    """A hand-written email for this one row, or None to use the segment template.

    The segment templates are deliberately generic - they are a starting point for
    fifteen cold rows a day. But the targets worth the most are the ones where a
    real reason to write exists: an author of a paper we lean on, the person whose
    dataset we used as an answer key. Those emails get written by hand, and until
    now they lived only in the vault markdown, which meant the sender could not
    actually send them - it would silently fall back to the generic text.

    drafts/<id>.txt, headers then a blank line then the body:

        Subject: your low-latency maneuver paper - something I stumbled into
        Attach: output/starlink_deorbit_detected.png

        Patrick,
        ...

    Attach is optional and repeatable; paths are relative to 06 Code. The
    signature is appended by compose(), same as the templates, so drafts must
    not repeat it.
    """
    path = DRAFTS_DIR / f"{str(row['id']).strip()}.txt"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    head, _, body = text.partition("\n\n")
    subject, attachments = None, []
    for line in head.splitlines():
        key, sep, val = line.partition(":")
        if not sep:
            continue
        key, val = key.strip().lower(), val.strip()
        if key == "subject":
            subject = val
        elif key == "attach" and val:
            attachments.append(val)
    if not subject:
        raise SystemExit(f"\n  {path.name} has no 'Subject:' header line.\n")
    return subject, body.strip("\n"), attachments


def compose(row):
    """The actual email, as it would land: (subject, body)."""
    hand = read_draft(row)
    if hand is not None:
        subject, body, _ = hand
        return subject, f"{body}\n\n{SIGN}\n"
    subject, body = TEMPLATES.get(row["segment"], TEMPLATES["operator"])
    return subject, f"{body}\n{SIGN}\n"


def attachments_for(row):
    """Resolved attachment paths for this row. Missing file = hard stop.

    A silently dropped attachment is worse than no email: the body says "here is
    the picture" and the picture is not there, to the one contact who mattered.
    """
    hand = read_draft(row)
    if hand is None:
        return []
    out = []
    for rel in hand[2]:
        p = (HERE / rel).resolve()
        if not p.is_file():
            raise SystemExit(f"\n  drafts/{row['id']}.txt attaches {rel!r}, "
                             f"which does not exist.\n")
        out.append(p)
    return out


def validation():
    """id -> newest contact_check record. Empty dict if nobody has run the check.

    Written by contact_check.py. Half of batch two's contact URLs were 404s and
    a dead domain has no MX, so an unchecked route is not a route yet.
    """
    latest = {}
    if not VALIDATION_PATH.exists():
        return latest
    with VALIDATION_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            rid = str(rec.get("id", "")).strip()
            if rid:
                latest[rid] = rec  # append-only file, so last line wins
    return latest


def unreachable(row, checks):
    """Why validation says don't bother. None = go ahead."""
    rec = checks.get(str(row["id"]).strip())
    if rec is None:
        return None  # never checked - not the same as failed
    if rec.get("reachable"):
        return None
    return "route unreachable: %s (%s)" % (rec.get("detail", "?")[:60],
                                           rec.get("checked_at", "?"))


def sent_addresses(log=None):
    """Every address the audit log says we already mailed, lowercased.

    The CSV dedupes by row. Two rows can carry the same address - a parent
    company and its subsidiary, the same info@ found twice - and the second
    one would look untouched. The log knows better.
    """
    return {e["to"].strip().lower()
            for e in (read_log() if log is None else log)
            if e.get("ok") and e.get("to")}


def blockers(row, checks=None, mailed=None, ignore_status=False):
    """Every reason this row must not be auto-sent. Empty list = clear to send.

    ignore_status is for --ids only: a human naming a row by number has already
    made the decision that `status` exists to make on their behalf. Every other
    guard - dead route, duplicate address, missing address, unfilled template -
    still applies, because those catch mistakes rather than enforce a policy.
    """
    bad = []
    dead = unreachable(row, checks or {})
    if dead:
        bad.append(dead)
    if mailed and row["email"].strip().lower() in mailed:
        bad.append(f"already mailed {row['email'].strip()} on another row")
    if not row["email"].strip():
        bad.append(f"no email address (route: {row['contact_route'] or '?'})")
    elif "@" not in row["email"] or " " in row["email"].strip():
        bad.append(f"email doesn't look like an address: {row['email']!r}")
    if not ignore_status and row["status"] not in ("todo", "drafted"):
        bad.append(f"status is {row['status']}, not todo/drafted")
    # draft() quietly falls back to the operator template for unknown segments.
    # Fine when a human is reading it first; not fine when nobody is. A
    # hand-written draft is the row's own text, so no segment is needed.
    if row["segment"] not in TEMPLATES and read_draft(row) is None:
        bad.append(f"no template for segment {row['segment']!r}")
    _, body = compose(row)
    for p in PLACEHOLDERS:
        if p in body:
            bad.append("template placeholder never filled in")
            break
    return bad


def load_auth():
    if not AUTH_PATH.exists():
        raise SystemExit(
            f"\n  no {AUTH_PATH.name}. Sending needs a Google App Password:\n"
            f'    {{"address": "you@gmail.com", "app_password": "abcd efgh ijkl mnop"}}\n'
            f"  Make one at myaccount.google.com/apppasswords (2FA required).\n"
            f"  Write it to {AUTH_PATH} - it is already gitignored.\n")
    auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    for k in ("address", "app_password"):
        if not auth.get(k):
            raise SystemExit(f"\n  {AUTH_PATH.name} is missing '{k}'.\n")
    return auth


def build_message(row, from_addr):
    subject, body = compose(row)
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{from_addr}>"
    msg["To"] = row["email"].strip()
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@")[-1])
    msg.set_content(body)
    for path in attachments_for(row):
        ctype, _ = mimetypes.guess_type(path.name)
        maintype, _, subtype = (ctype or "application/octet-stream").partition("/")
        msg.add_attachment(path.read_bytes(), maintype=maintype,
                           subtype=subtype, filename=path.name)
    return msg


def log_send(record):
    """Append-only audit line. Every attempt lands here, sent or not."""
    record = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
              "day": datetime.date.today().isoformat(), **record}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def read_log():
    if not LOG_PATH.exists():
        return []
    out = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass        # a half-written line must not stop the send
    return out


# Which segment matters most when the day's quota has to be split. Operators are
# our declared validation customers and the fastest yes; academics are last here
# only because their template is deliberately unsendable until a human writes the
# question, so they never actually compete for a slot.
SEGMENT_PRIORITY = ["operator", "partner", "insurer", "gov", "contract", "academic"]


def interleave(pool):
    """Round-robin the pool across segments instead of walking the CSV in order.

    The CSV is grouped by segment because that is how it was written, so a
    straight walk sends nine insurers in a row, then nine operators. That is
    both worse marketing - a bad segment wastes a whole day before we notice -
    and a worse experiment, because a day's results can't be compared.
    """
    buckets = {}
    for r in pool:
        buckets.setdefault(r["segment"], []).append(r)
    order = ([s for s in SEGMENT_PRIORITY if s in buckets]
             + sorted(s for s in buckets if s not in SEGMENT_PRIORITY))
    out = []
    while any(buckets[s] for s in order):
        for s in order:
            if buckets[s]:
                out.append(buckets[s].pop(0))
    return out


def sent_today(log=None):
    """How many actually went out today, per the log - not per the CSV.

    The CSV can be edited by hand; the log is the thing that counts, so two
    runs in one afternoon can't quietly put out thirty emails.
    """
    today = datetime.date.today().isoformat()
    return sum(1 for e in (read_log() if log is None else log)
               if e.get("ok") and e.get("day") == today)


def smtp_permanent(exc):
    """5xx means the address is dead. 4xx means try again later.

    Retrying a 5xx forever is how you get an account flagged, so a permanent
    refusal parks the row instead of leaving it in the pool.
    """
    codes = []
    if isinstance(exc, smtplib.SMTPRecipientsRefused):
        codes = [c for c, _ in exc.recipients.values()]
    elif isinstance(exc, smtplib.SMTPResponseException):
        codes = [exc.smtp_code]
    return bool(codes) and all(500 <= c < 600 for c in codes)


def bounce_report_ids(raw):
    """Message-IDs of the dead originals named inside one bounce notice.

    Its own Message-ID is dropped - that's the bounce, not the email we sent.
    """
    msg = (email.message_from_bytes(raw) if isinstance(raw, bytes)
           else email.message_from_string(raw))
    own = (msg.get("Message-ID") or "").strip()

    # The dead original is attached as a part, and Gmail sometimes ships that
    # part base64'd, so decode each one rather than regexing the raw envelope.
    chunks = []
    for part in msg.walk():
        try:
            body = part.get_payload(decode=True)
        except Exception:
            body = None
        if body:
            chunks.append(body.decode("utf-8", "replace"))
        elif isinstance(part.get_payload(), str):
            chunks.append(part.get_payload())
    text = "\n".join([str(msg), *chunks])
    return [m for m in dict.fromkeys(MSGID_RE.findall(text)) if m != own]


def mark_bounced(row, reason):
    row["status"] = "bounced"
    row["notes"] = (row["notes"] + " | " if row["notes"] else "") + reason


def apply_bounces(rows, sends, msgids):
    """Match reported Message-IDs to our log and retire those rows.

    Split out from the IMAP plumbing so it can be tested without a mailbox.
    Returns the rows it changed.
    """
    by_id = {r["id"]: r for r in rows}
    hit = []
    for mid in msgids:
        rec = sends.get(mid)
        if not rec:
            continue                    # someone else's bounce, not ours
        row = by_id.get(str(rec["id"]))
        if row is None or row["status"] == "bounced":
            continue
        mark_bounced(row, f"bounced {rec.get('to')}")
        log_send({"kind": "bounce", "id": rec["id"],
                  "company": rec.get("company"), "to": rec.get("to"),
                  "message_id": mid, "ok": False,
                  "error": "delivery failure reported by mail"})
        hit.append(row)
    return hit


def check_bounces(rows, args):
    """Read the inbox for delivery failures and retire the dead addresses."""
    auth = load_auth()
    sends = {e["message_id"]: e for e in read_log()
             if e.get("ok") and e.get("message_id")}
    if not sends:
        print("\n  nothing sent yet, so nothing can have bounced.\n")
        return 0

    since = (datetime.date.today()
             - datetime.timedelta(days=args.since_days)).strftime("%d-%b-%Y")
    box = imaplib.IMAP4_SSL(args.imap_host, 993,
                            ssl_context=ssl.create_default_context())
    hits = 0
    try:
        box.login(auth["address"], auth["app_password"])
        box.select("INBOX", readonly=True)
        ok, data = box.search(None, f'(SINCE {since})', '(OR OR FROM '
                              '"mailer-daemon" FROM "postmaster" '
                              'SUBJECT "Undeliverable")')
        if ok != "OK":
            print(f"\n  IMAP search failed: {ok}\n")
            return 1
        nums = data[0].split()
        print(f"\n  {len(nums)} bounce-shaped messages since {since}.")
        for num in nums:
            ok, payload = box.fetch(num, "(RFC822)")
            if ok != "OK" or not payload or not isinstance(payload[0], tuple):
                continue
            for row in apply_bounces(rows, sends,
                                     bounce_report_ids(payload[0][1])):
                hits += 1
                print(f"  bounced #{row['id']:<3} {row['company']:<28} "
                      f"{row['email']}")
    finally:
        try:
            box.logout()
        except Exception:
            pass

    if hits:
        save(rows)
    print(f"\n  {hits} address{'' if hits == 1 else 'es'} marked bounced.\n")
    return 0


def send_batch(rows, args):
    """Dry run unless --live. Returns exit code."""
    # --ids is the hand-send path: a named list, in the order given, regardless
    # of status. It exists because the best emails we write are the ones parked
    # on `hold` precisely so the drip can never touch them - and "the machine
    # must not send this" should not mean "the human has to retype it into
    # Gmail and lose the audit log, the bounce handling and the Sent copy".
    by_id = {r["id"]: r for r in rows}
    if args.ids:
        missing = [i for i in args.ids if i not in by_id]
        if missing:
            raise SystemExit(f"\n  no such row(s): {', '.join(missing)}\n")
        pool = [by_id[i] for i in args.ids]
    else:
        pool = [r for r in rows
                if r["status"] in ("todo", "drafted")
                and (not args.segment or r["segment"] == args.segment)]
    # A named list means "these, in this order" - but MAX_PER_RUN still binds,
    # so naming nine rows sends five and says so rather than quietly dropping four.
    n = min(len(pool) if args.ids else args.n, MAX_PER_RUN)

    checks = {} if args.skip_validation else validation()
    log = read_log()
    mailed = sent_addresses(log)
    ready, held = [], []
    for r in pool:
        (held if blockers(r, checks, mailed, ignore_status=bool(args.ids))
         else ready).append(r)
    if args.mix and not args.ids:
        ready = interleave(ready)      # --ids means "this order", so never reshuffle it

    already = sent_today(log)
    left = max(0, DAILY_CAP - already)
    batch = ready[:min(n, left)]

    print(f"\n  {len(pool)} unsent targets. {len(ready)} sendable, "
          f"{len(held)} held back. This run: {len(batch)}.")
    print(f"  {already} already sent today; {left} left under the {DAILY_CAP}/day cap.")
    if ready and not left:
        print("\n  daily cap reached. Tomorrow.\n")
        return 0
    if held:
        print("\n  held back:")
        for r in held[:20]:
            print(f"    #{r['id']:<3} {r['company']:<30} "
                  f"{'; '.join(blockers(r, checks, mailed, ignore_status=bool(args.ids)))}")
        if len(held) > 20:
            print(f"    ... and {len(held) - 20} more")
    if not batch:
        print("\n  nothing sendable. Find real addresses first.\n")
        return 0

    from_addr = "DRY-RUN@localhost"
    auth = None
    if args.live and args.smtp_plain:
        # No login on the plain path, so no password needed. The only server
        # that accepts this is the local sink; Gmail refuses unauthenticated.
        from_addr = "harness@localhost"
    elif args.live:
        auth = load_auth()
        from_addr = auth["address"]

    print("\n  " + ("SENDING FOR REAL" if args.live else "DRY RUN - nothing leaves this machine"))
    for r in batch:
        msg = build_message(r, from_addr)
        print(f"{'-' * 74}\n  #{r['id']}  {r['company']}  ->  {msg['To']}")
        print(f"  subject: {msg['Subject']}")
    print("-" * 74)

    if not args.live:
        print(f"\n  add --live to send these {len(batch)}.\n")
        return 0

    today = datetime.date.today().isoformat()
    sent = failed = bounced = 0
    server = None
    try:
        if args.smtp_plain:
            server = smtplib.SMTP(args.smtp_host, args.smtp_port, timeout=30)
        else:
            server = smtplib.SMTP_SSL(args.smtp_host, args.smtp_port,
                                      context=ssl.create_default_context(),
                                      timeout=30)
            server.login(auth["address"], auth["app_password"])
        for i, r in enumerate(batch):
            if r["email"].strip().lower() in mailed:
                # Two rows in the same batch sharing an address: the pre-loop
                # set can't catch the second one, so re-check here.
                print(f"  skipped #{r['id']} {r['company']}: duplicate address")
                continue
            msg = build_message(r, from_addr)
            try:
                server.send_message(msg)
            except Exception as e:
                failed += 1
                perm = smtp_permanent(e)
                if perm:
                    bounced += 1
                    mark_bounced(r, f"bounced at send: {e}")
                    save(rows)
                print(f"  {'BOUNCED' if perm else 'FAILED '} #{r['id']} "
                      f"{r['company']}: {e}")
                log_send({"kind": "send", "id": r["id"], "company": r["company"],
                          "to": msg["To"], "ok": False, "error": str(e),
                          "bounced": perm})
                if isinstance(e, (smtplib.SMTPServerDisconnected,
                                  smtplib.SMTPSenderRefused)):
                    # The connection or the account is the problem, not the
                    # address. Grinding through the rest just logs 14 copies.
                    print("  connection/sender refused - stopping the batch.")
                    break
                continue
            sent += 1
            mailed.add(r["email"].strip().lower())
            r["status"] = "sent"
            r["sent_on"] = today
            log_send({"kind": "send", "id": r["id"], "company": r["company"],
                      "to": msg["To"], "subject": msg["Subject"],
                      "message_id": msg["Message-ID"], "ok": True})
            save(rows)          # after each one: a crash can't lose the record
            print(f"  sent #{r['id']} {r['company']} -> {msg['To']}")
            if i < len(batch) - 1 and args.gap:
                time.sleep(args.gap)
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass

    print(f"\n  {sent} sent, {failed} failed ({bounced} dead addresses parked). "
          f"Logged to {LOG_PATH.name}."
          + ("" if args.smtp_plain else " Copies are in Gmail's Sent folder.")
          + "\n")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=15, help="how many drafts today")
    ap.add_argument("--segment", default=None)
    ap.add_argument("--sent", nargs="+", default=None, metavar="ID")
    ap.add_argument("--replied", nargs="+", default=None, metavar="ID")
    ap.add_argument("--dead", nargs="+", default=None, metavar="ID")
    ap.add_argument("--note", default=None)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--send", action="store_true",
                    help="dry run of the send batch; add --live to actually send")
    ap.add_argument("--ids", nargs="+", default=None, metavar="ID",
                    help="hand-send exactly these rows, in this order, whatever "
                         "their status. Every other safety still applies.")
    ap.add_argument("--mix", action="store_true",
                    help="round-robin across segments instead of CSV order")
    ap.add_argument("--count-today", action="store_true",
                    help="print how many went out today, per the audit log, and exit")
    ap.add_argument("--live", action="store_true",
                    help="really send. Requires --send and gmail_auth.json.")
    ap.add_argument("--smtp-host", default="smtp.gmail.com")
    ap.add_argument("--smtp-port", type=int, default=465)
    ap.add_argument("--smtp-plain", action="store_true",
                    help="unencrypted SMTP - local test harness only, never Gmail")
    ap.add_argument("--gap", type=int, default=GAP_SECONDS,
                    help="seconds between sends (0 only for the test harness)")
    ap.add_argument("--check-bounces", action="store_true",
                    help="read bounce mail over IMAP and park dead addresses")
    ap.add_argument("--imap-host", default="imap.gmail.com")
    ap.add_argument("--since-days", type=int, default=14)
    ap.add_argument("--csv", default=None,
                    help="use a different target list (test harness)")
    ap.add_argument("--log", default=None,
                    help="use a different audit log (test harness)")
    ap.add_argument("--skip-validation", action="store_true",
                    help="ignore outreach_validation.jsonl (draft a dead route anyway)")
    ap.add_argument("--validation", default=None,
                    help="use a different contact_check log (test harness)")
    args = ap.parse_args()

    if args.csv:
        globals()["CSV_PATH"] = Path(args.csv).resolve()
    if args.log:
        globals()["LOG_PATH"] = Path(args.log).resolve()
    if args.validation:
        globals()["VALIDATION_PATH"] = Path(args.validation).resolve()
    rows = load()
    today = datetime.date.today().isoformat()

    if args.live and not args.send:
        print("\n  --live does nothing without --send. Refusing.\n")
        return 2
    if args.ids and not args.send:
        print("\n  --ids only means something with --send. Refusing.\n")
        return 2
    if args.count_today:
        print(sent_today())          # bare integer: the drip reads this to pace itself
        return 0
    if args.check_bounces:
        return check_bounces(rows, args)
    if args.send:
        return send_batch(rows, args)

    for flag, state in (("sent", "sent"), ("replied", "replied"), ("dead", "dead")):
        ids = getattr(args, flag)
        if not ids:
            continue
        for r in rows:
            if r["id"] in ids:
                r["status"] = state
                if state == "sent":
                    r["sent_on"] = today
                if args.note:
                    r["notes"] = (r["notes"] + " | " if r["notes"] else "") + args.note
                print(f"  #{r['id']:<3} {r['company']:<28} -> {state}")
        save(rows)
        return 0

    if args.status:
        counts = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print("\n  " + "  ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
        for r in rows:
            if r["status"] != "todo":
                print(f"  #{r['id']:<3} {r['status']:<8} {r['sent_on'] or '':<11} "
                      f"{r['company']:<28} {r['notes'][:40]}")
        print()
        return 0

    checks = {} if args.skip_validation else validation()
    candidates = [r for r in rows
                  if r["status"] == "todo"
                  and (not args.segment or r["segment"] == args.segment)]
    dropped = [(r, unreachable(r, checks)) for r in candidates]
    batch = [r for r, dead in dropped if not dead][:args.n]
    dead_rows = [(r, why) for r, why in dropped if why]
    if not batch:
        print("\n  nothing reachable left in the list. add rows to "
              "outreach_targets.csv, or re-run contact_check.py.\n")
        return 0

    if dead_rows:
        print(f"\n  {len(dead_rows)} target(s) skipped - contact_check says dead:")
        for r, why in dead_rows[:20]:
            print(f"    #{r['id']:<3} {r['company']:<28} {why}")

    print(f"\n  {len(batch)} drafts for {today}. Nothing is sent automatically.")
    print("  Find a real human at each contact route first - 'info@' converts at ~zero.")
    print("  Then: python outreach.py --sent " + " ".join(r["id"] for r in batch) + "\n")
    for r in batch:
        print(draft(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
