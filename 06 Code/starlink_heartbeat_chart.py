"""
starlink_heartbeat_chart.py - one clean before/after picture for the pitch.

Pulls ~120 days of public orbit history for a single well-known Starlink from
Space-Track (free, public), and draws its altitude over time: the long flat stretch
where the operator actively holds the satellite at a set altitude (its normal
"heartbeat"), and the clear break where it maneuvers away from that altitude - here,
the start of STARLINK-3200's deliberate descent to burn up (a controlled deorbit).

Pure standard library - emits an SVG, no matplotlib needed. Runs on any python 3.
"""
import json, os, urllib.request, urllib.parse, http.cookiejar, math
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)
EARTH = 6371.0

NORAD = 49753          # STARLINK-3200
WIN = 8                # records each side when hunting the sustained level change

def login():
    c = json.load(open("spacetrack_auth.json"))
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.open("https://www.space-track.org/ajaxauth/login",
            data=urllib.parse.urlencode(c).encode(), timeout=30).read()
    return op

def history(op, norad):
    url = ("https://www.space-track.org/basicspacedata/query/class/gp_history/"
           f"NORAD_CAT_ID/{norad}/EPOCH/%3Enow-120/orderby/EPOCH%20asc/format/json")
    return json.loads(op.open(url, timeout=120).read().decode())

def altitude(row):
    sma = row.get("SEMIMAJOR_AXIS")
    if sma:
        return float(sma) - EARTH
    n = float(row["MEAN_MOTION"]) * 2 * math.pi / 86400.0
    return (398600.4418 / n**2) ** (1/3) - EARTH

def main():
    op = login()
    rows = history(op, NORAD)
    name = rows[0].get("OBJECT_NAME", f"NORAD {NORAD}")
    seen, pts = set(), []
    for r in rows:
        ep = r["EPOCH"]
        if ep in seen:
            continue
        seen.add(ep)
        pts.append((datetime.fromisoformat(ep), altitude(r)))
    pts.sort()
    ts = [p[0] for p in pts]
    al = [p[1] for p in pts]

    # find the maneuver: the point where the altitude makes its biggest SUSTAINED
    # change - compare the average of the WIN records before against the WIN after.
    ji, jmag = WIN, 0.0
    for i in range(WIN, len(al) - WIN):
        before = sum(al[i-WIN:i]) / WIN
        after = sum(al[i:i+WIN]) / WIN
        if abs(after - before) > abs(jmag):
            jmag, ji = after - before, i
    man_t, man_a = ts[ji], al[ji]
    held = sum(al[:ji]) / ji            # the altitude it was holding beforehand
    end_a = al[-1]
    print(f"{name}: {len(pts)} records, {ts[0]:%Y-%m-%d}..{ts[-1]:%Y-%m-%d}")
    print(f"held {held:.1f} km, then broke on {man_t:%Y-%m-%d}; now {end_a:.1f} km "
          f"({end_a-held:+.1f} km)")

    # ---- draw SVG ----
    W, H = 1000, 560
    L, R, T, B = 90, 40, 70, 70
    pw, ph = W - L - R, H - T - B
    t0, t1 = ts[0].timestamp(), ts[-1].timestamp()
    amin, amax = min(al), max(al)
    pad = (amax - amin) * 0.12 or 1
    amin, amax = amin - pad, amax + pad
    def X(t): return L + (t.timestamp() - t0) / (t1 - t0) * pw
    def Y(a): return T + (amax - a) / (amax - amin) * ph

    poly = " ".join(f"{X(t):.1f},{Y(a):.1f}" for t, a in zip(ts, al))

    # y gridlines
    ylines = ""
    step = 5
    lo = math.ceil(amin / step) * step
    v = lo
    while v <= amax:
        y = Y(v)
        ylines += (f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" '
                   f'stroke="#e6e6e6"/><text x="{L-10}" y="{y+4:.1f}" '
                   f'text-anchor="end" font-size="13" fill="#666">{v:.0f}</text>')
        v += step
    # x month labels
    xlab = ""
    seen_m = set()
    for t in ts:
        key = (t.year, t.month)
        if key in seen_m:
            continue
        seen_m.add(key)
        x = X(t)
        xlab += (f'<text x="{x:.1f}" y="{H-B+24}" text-anchor="middle" '
                 f'font-size="13" fill="#666">{t:%b}</text>')

    mx, my = X(man_t), Y(man_a)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, Arial, sans-serif">
<rect width="{W}" height="{H}" fill="white"/>
<text x="{L}" y="34" font-size="20" font-weight="bold" fill="#1a1a1a">{name}: held steady for months, then we caught it starting to deorbit</text>
<text x="{L}" y="56" font-size="14" fill="#666">Altitude above Earth over 4 months, from free public tracking data</text>
{ylines}{xlab}
<polyline points="{poly}" fill="none" stroke="#2f81f7" stroke-width="2"/>
<line x1="{mx:.1f}" y1="{T}" x2="{mx:.1f}" y2="{H-B}" stroke="#e5534b" stroke-width="1.5" stroke-dasharray="5,4"/>
<circle cx="{mx:.1f}" cy="{my:.1f}" r="6" fill="none" stroke="#e5534b" stroke-width="2.5"/>
<text x="{mx-12:.1f}" y="{my-26:.1f}" text-anchor="end" font-size="14" font-weight="bold" fill="#e5534b">maneuver detected</text>
<text x="{mx-12:.1f}" y="{my-8:.1f}" text-anchor="end" font-size="12" fill="#e5534b">{man_t:%b %d} &#183; leaves its held orbit</text>
<text x="{mx+150:.1f}" y="{(T+H-B)/2 - 40:.1f}" text-anchor="middle" font-size="13" fill="#2f81f7" font-weight="bold">flat = actively held</text>
<text x="{mx+150:.1f}" y="{(T+H-B)/2 - 22:.1f}" text-anchor="middle" font-size="12" fill="#888">(the "heartbeat")</text>
<text x="{L}" y="{H-18}" font-size="12" fill="#999">Blue line = altitude (km). Held flat at {held:.0f} km for months (station-keeping), then breaks into a steady, deliberate fall. Data: Space-Track GP history, NORAD {NORAD}.</text>
</svg>'''
    path = os.path.join(OUT, "starlink3200_deorbit.svg")
    open(path, "w", encoding="utf-8").write(svg)
    print("saved:", path)

if __name__ == "__main__":
    main()
