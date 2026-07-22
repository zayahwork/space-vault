"""
supgp_archive.py - save CelesTrak's SupGP data before it disappears.

WHY THIS EXISTS
CelesTrak publishes Supplemental GP data: high-accuracy orbits built from operator
ephemerides, covering ~76% of active satellites, refreshed every ~30 minutes. It is
the closest thing to free ground truth in this field - where SupGP and the public
catalog disagree, something happened that the catalog missed (often a maneuver).

As far as we can tell, only the CURRENT element set is served. There is no public
archive. So every snapshot we do not take is training data that is gone forever.
This script takes the snapshot.

BEING A GOOD CITIZEN
CelesTrak is a free service run by a very small team, and its founder is a contact
of ours. We identify ourselves honestly in the User-Agent, fetch on a slow cadence,
and pause between requests. Do not crank the schedule up without a real reason.

Usage:
  python supgp_archive.py                 # snapshot every group
  python supgp_archive.py --groups iss gps ses
  python supgp_archive.py --dry-run
"""

import argparse
import csv
import gzip
import io
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# The scheduled task's console is cp1252 and will crash on a warning glyph, which
# would turn a cosmetic character into a failed archive run.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = "https://celestrak.org/NORAD/elements/supplemental/sup-gp.php"
ARCHIVE = Path(__file__).parent / "supgp_archive"

# Identify ourselves honestly - CelesTrak's operator should be able to tell who we
# are and why we are here from the logs alone.
HEADERS = {
    "User-Agent": (
        "SpaceProject-SupGP-Archiver/1.0 "
        "(research: maneuver detection from public data; contact zayahwork@gmail.com)"
    )
}

# The real constellation groups. The starlink-g17-39* files are per-launch subsets
# of `starlink`, so archiving them too would just duplicate rows.
GROUPS = [
    "ast", "cpf", "css", "eumetsat", "glonass", "gps", "intelsat", "iridium",
    "iss", "kuiper", "oneweb", "orbcomm", "planet", "ses", "starlink", "telesat",
]

POLITE_DELAY_SEC = 2.0
RETRIES = 3
RETRY_BACKOFF_SEC = 8.0     # first backoff; doubles each attempt (8, 16, 32...)
RETRY_BACKOFF_CAP_SEC = 120.0

# The public 18 SDS catalog for the same objects. We archive it beside SupGP because
# the maneuver-vs-stale question needs BOTH element sets captured at the same instant,
# and neither is retro-fetchable. Archiving SupGP alone was archiving half the
# experiment: you can compare them live, but never for a moment that has passed.
GP_BASE = "https://celestrak.org/NORAD/elements/gp.php"
HEALTH_LOG = ARCHIVE / "health.jsonl"


UNCHANGED = "<unchanged>"   # sentinel: CelesTrak says we already have this data


class Refused(Exception):
    """CelesTrak answered and told us no. Not retryable inside this run.

    A 403 here is a decision by the server, not a glitch: we are blocked, or asking
    for something we may not have. Retrying it is both useless and rude - the only
    correct move is to record it and let the next scheduled cycle try again.
    """

    def __init__(self, status, detail):
        super().__init__(f"HTTP {status}: {detail}")
        self.status = status
        self.detail = detail


def _retry_after_sec(resp):
    """CelesTrak's own rate-limit signal, if it sent one. Header wins over guesswork."""
    raw = resp.headers.get("Retry-After", "").strip()
    if not raw:
        return None
    try:
        wait = float(raw)                       # the delta-seconds form
    except ValueError:
        return None                             # HTTP-date form - fall back to backoff
    return max(0.0, min(wait, RETRY_BACKOFF_CAP_SEC))


def fetch(group, session, timeout=120, base=BASE, param="FILE"):
    """Return CSV text for one constellation group, or None if it has no data.

    CelesTrak's GP endpoint answers a redundant download with 403 and a plain-text
    body saying the data hasn't updated since your last successful fetch (GP moves
    once every 2 hours). That is politeness enforcement, not an error - treat it as
    UNCHANGED, or we'd retry three times against a server deliberately saying stop.
    The SupGP endpoint does not do this; back-to-back fetches both return 200.

    Any OTHER 403 is a refusal (Refused) and is never retried. A 429 or 5xx is the
    server asking for time, so it raises normally and the caller backs off.
    """
    resp = session.get(
        base, params={param: group, "FORMAT": "csv"}, headers=HEADERS, timeout=timeout
    )
    if resp.status_code == 403:
        if "has not updated" in resp.text.lower():
            return UNCHANGED
        raise Refused(403, " ".join(resp.text.split())[:200] or "no body")
    if resp.status_code == 429:
        # Explicit rate limit. Attach the server's own wait so we honour it exactly
        # instead of doubling blindly past it.
        exc = requests.HTTPError(f"429 rate limited for {group}", response=resp)
        exc.retry_after = _retry_after_sec(resp)
        raise exc
    resp.raise_for_status()
    text = resp.text
    if not text.strip() or text.lower().startswith(("no supgp data", "no gp data")):
        return None
    return text


def fetch_with_retry(group, session, base=BASE, param="FILE"):
    """fetch(), but a transient failure costs a snapshot we can never retake.

    Telesat vanished from the 14:00Z snapshot on 2026-07-21: one failed request, no
    retry, and the manifest simply had no telesat key at all. The run did exit
    non-zero - nobody was watching. So: retry, then record the hole explicitly.

    Backoff doubles (8s, 16s, 32s...) rather than sitting flat, and a Retry-After
    header overrides it. A Refused (403) breaks out immediately - retrying a server
    that has said no is how a polite client becomes a banned one.
    """
    last = None
    wait = RETRY_BACKOFF_SEC
    for attempt in range(1, RETRIES + 1):
        try:
            return fetch(group, session, base=base, param=param), None
        except Refused as exc:
            print(f"  {group:<12} REFUSED ({exc}) - not retrying, next cycle will")
            return None, exc
        except requests.RequestException as exc:
            last = exc
            if attempt < RETRIES:
                pause = getattr(exc, "retry_after", None)
                pause = wait if pause is None else pause
                print(f"  {group:<12} attempt {attempt} failed "
                      f"({exc.__class__.__name__}) - retrying in {pause:.0f}s")
                time.sleep(pause)
                wait = min(wait * 2, RETRY_BACKOFF_CAP_SEC)
    return None, last


def row_count(csv_text):
    return max(0, sum(1 for _ in csv.reader(io.StringIO(csv_text))) - 1)


def previous_manifest():
    """The most recent manifest, for spotting a group that shrank suspiciously."""
    hits = sorted(ARCHIVE.glob("*/*/manifest.json"))
    if not hits:
        return {}
    try:
        return json.loads(hits[-1].read_text(encoding="utf-8")).get("groups", {})
    except (json.JSONDecodeError, OSError):
        return {}


def snapshot(groups, dry_run=False, with_gp=True):
    stamp = datetime.now(timezone.utc)
    out_dir = ARCHIVE / stamp.strftime("%Y-%m-%d") / stamp.strftime("%H%MZ")
    before = previous_manifest()

    manifest = {
        "captured_utc": stamp.isoformat(),
        "source": BASE,
        "expected_groups": list(groups),   # so a hole is visible, not just absent
        "groups": {},
        "gp_active": None,
        "missing": [],
        "refused": [],     # server said no on purpose - distinct from a broken request
        "suspect": [],
        "total_rows": 0,
    }

    session = requests.Session()
    failures = []

    for i, group in enumerate(groups):
        text, err = fetch_with_retry(group, session)
        if err is not None:
            if isinstance(err, Refused):
                manifest["refused"].append({"group": group, "detail": str(err)})
            else:
                print(f"  {group:<12} FAILED after {RETRIES} attempts: {err}")
            manifest["groups"][group] = None      # an explicit hole, not a silence
            manifest["missing"].append(group)
            failures.append(group)
            continue

        if text is UNCHANGED:
            # SupGP has not historically done this, but if it starts, the last
            # snapshot's copy is still the current data - not a hole.
            print(f"  {group:<12} unchanged since last pull")
            manifest["groups"][group] = "unchanged"
            continue

        if text is None:
            print(f"  {group:<12} (no data)")
            manifest["groups"][group] = 0
            continue

        rows = row_count(text)
        manifest["groups"][group] = rows
        manifest["total_rows"] += rows

        # A group that halved since last snapshot is a partial response, not news.
        was = before.get(group)
        if isinstance(was, int) and was > 20 and rows < was * 0.5:
            manifest["suspect"].append({"group": group, "was": was, "now": rows})
            print(f"  {group:<12} {rows:>6} objects  ⚠ was {was} last snapshot")

        if not dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            # gzip: this is highly repetitive text, compresses ~8x, and we intend
            # to keep every snapshot forever.
            target = out_dir / f"{group}.csv.gz"
            with gzip.open(target, "wt", encoding="utf-8", newline="") as fh:
                fh.write(text)

        if not any(s["group"] == group for s in manifest["suspect"]):
            print(f"  {group:<12} {rows:>6} objects")

        if i < len(groups) - 1:
            time.sleep(POLITE_DELAY_SEC)

    # The matching public-catalog element sets, captured at the same instant. One
    # request for GROUP=active covers every object we archive and then some - far
    # politer than 16 per-group calls, and the GP group names don't line up with
    # SupGP file names anyway (there is no GP group called "iss").
    if with_gp:
        time.sleep(POLITE_DELAY_SEC)
        gp_text, gp_err = fetch_with_retry("active", session, base=GP_BASE, param="GROUP")
        if gp_text is UNCHANGED:
            # Not a hole. The catalog genuinely hasn't moved since our last pull, so
            # the previous snapshot's copy IS this snapshot's copy.
            manifest["gp_active"] = "unchanged"
            print(f"  {'gp active':<12} unchanged since last pull (GP moves every 2h)")
        elif gp_err is not None or gp_text is None:
            manifest["gp_active"] = None
            manifest["missing"].append("gp_active")
            failures.append("gp_active")
            if isinstance(gp_err, Refused):
                manifest["refused"].append({"group": "gp_active", "detail": str(gp_err)})
            print(f"  {'gp active':<12} FAILED - no public catalog for this snapshot")
        else:
            gp_rows = row_count(gp_text)
            manifest["gp_active"] = gp_rows
            if not dry_run:
                out_dir.mkdir(parents=True, exist_ok=True)
                with gzip.open(out_dir / "gp_active.csv.gz", "wt",
                               encoding="utf-8", newline="") as fh:
                    fh.write(gp_text)
            print(f"  {'gp active':<12} {gp_rows:>6} objects  (public catalog)")

    if not dry_run:
        if manifest["total_rows"]:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        # Log even a zero-row run. A cycle where CelesTrak refused everything is the
        # single most important line in this file, and the old guard threw it away.
        _log_health(manifest, out_dir)

    return manifest, failures, out_dir


def _log_health(manifest, out_dir):
    """One line per run, so 'has the archive been healthy?' is a file, not a hunt."""
    entry = {
        "captured_utc": manifest["captured_utc"],
        "snapshot": out_dir.name,
        "total_rows": manifest["total_rows"],
        "missing": manifest["missing"],
        "refused": [r["group"] for r in manifest.get("refused", [])],
        "suspect": [s["group"] for s in manifest["suspect"]],
        "ok": not manifest["missing"] and not manifest["suspect"],
    }
    HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with HEALTH_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--groups", nargs="+", default=GROUPS, help="subset to fetch")
    ap.add_argument("--dry-run", action="store_true", help="fetch but write nothing")
    ap.add_argument("--no-gp", action="store_true",
                    help="skip the matching public-catalog capture (halves requests)")
    ap.add_argument("--health", action="store_true", help="show the run log and exit")
    args = ap.parse_args()

    if args.health:
        if not HEALTH_LOG.exists():
            print("  no runs logged yet")
            return 0
        for line in HEALTH_LOG.read_text(encoding="utf-8").splitlines()[-30:]:
            e = json.loads(line)
            flag = "ok " if e["ok"] else "BAD"
            note = ""
            if e["missing"]:
                note += f"  missing={','.join(e['missing'])}"
            if e.get("refused"):
                note += f"  refused={','.join(e['refused'])}"
            if e["suspect"]:
                note += f"  suspect={','.join(e['suspect'])}"
            print(f"  {flag} {e['captured_utc'][:16]}  {e['total_rows']:>6} rows{note}")
        return 0

    print(f"SupGP snapshot - {len(args.groups)} groups")
    manifest, failures, out_dir = snapshot(args.groups, args.dry_run,
                                           with_gp=not args.no_gp)

    print(f"\n  total: {manifest['total_rows']} objects")
    if manifest["missing"]:
        print(f"  ⚠ MISSING (recorded as holes): {', '.join(manifest['missing'])}")
    for r in manifest["refused"]:
        print(f"  ⚠ REFUSED {r['group']}: {r['detail']} - retry is next cycle, not now")
    for s in manifest["suspect"]:
        print(f"  ⚠ SUSPECT {s['group']}: {s['was']} -> {s['now']} objects")
    if args.dry_run:
        print("  dry run - nothing written")
    else:
        size = sum(f.stat().st_size for f in out_dir.glob("*.gz")) if out_dir.exists() else 0
        print(f"  saved to {out_dir}  ({size/1024:.0f} KB compressed)")

    if failures:
        # Exit non-zero so a scheduled run shows up as failed rather than silently
        # archiving a partial snapshot we would later mistake for complete.
        print(f"\n  FAILED groups: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
