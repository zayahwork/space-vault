"""contact_find.py - for the routes that 404'd or 403'd, find the real door.

Tries a short list of likely contact paths per domain, records the HTTP status,
and pulls any mailto:/plain email addresses off the pages that load.
Prints one line per hit; writes nothing unless --out is given.
"""
import argparse
import re
import ssl
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1",
}
PATHS = ["/contact", "/contact/", "/contact-us", "/contact-us/", "/contacts",
         "/get-in-touch", "/company/contact", "/about/contact", "/"]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
JUNK = ("sentry.io", "example.com", "wixpress", "sentry-next", ".png", ".jpg")


def get(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.geturl(), r.read(400000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:
        return None, url, type(e).__name__


def emails(html, domain):
    found = set()
    for m in EMAIL_RE.findall(html):
        m = m.strip(".")
        low = m.lower()
        if any(j in low for j in JUNK):
            continue
        # keep addresses on the company's own domain, or obvious role addresses
        if low.endswith(domain) or low.split("@")[0] in (
                "info", "contact", "hello", "sales", "press", "media"):
            found.add(low)
    return sorted(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("domains", nargs="+")
    args = ap.parse_args()
    for dom in args.domains:
        dom = dom.replace("https://", "").replace("http://", "").strip("/")
        print("\n== %s" % dom)
        seen_emails = set()
        for p in PATHS:
            url = "https://" + dom + p
            code, final, body = get(url)
            if code != 200:
                print("   %-22s %s" % (p, code))
                continue
            found = emails(body, dom.replace("www.", ""))
            new = [e for e in found if e not in seen_emails]
            seen_emails.update(found)
            has_form = "<form" in body.lower()
            print("   %-22s 200 %s form=%s %s" % (
                p, "" if final.rstrip("/") == url.rstrip("/") else "-> " + final,
                has_form, ",".join(new[:6])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
