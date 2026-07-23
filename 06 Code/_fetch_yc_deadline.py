"""One-shot research fetch (card 030): find YC's next batch + application deadline.

Read-only web GET. No email, no sends, nothing posted.
"""
import re
import urllib.request

URLS = [
    "https://www.ycombinator.com/apply",
    "https://www.ycombinator.com/deadline",
]

for url in URLS:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"{url} -> FETCH FAILED: {e}")
        continue
    print(f"=== {url} ({len(html)} bytes) ===")
    hits = re.findall(
        r"[^<>]{0,140}(?:deadline|Deadline|apply by|Apply by|[Bb]atch)[^<>]{0,140}", html
    )
    seen = set()
    for h in hits:
        h = " ".join(h.split())[:220]
        if h and h not in seen:
            seen.add(h)
            print("  ", h)
        if len(seen) >= 30:
            break
