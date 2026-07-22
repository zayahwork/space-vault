---
date: 2026-07-22
type: publication-draft
status: READY BUT GATED — do not post until the Kelso email has gone out
gate: "[[Guide - Kelso Goldmine]] reply sent, telling him we intend to publish + crediting CelesTrak"
chart: "06 Code/output/launch_delay.png"
reproduce: "python launch_id_delay.py · python launch_delay_chart.py"
---

# 📰 Publish — the launch-delay finding (prepped, waiting on the gate)

> [!warning] The gate, one more time
> Every number here comes from **Kelso's** published CelesTrak table, and he is a live
> contact who replied to us personally. Sequence: **(1)** send the Kelso reply, **(2)** in it,
> say we intend to publish this and will credit CelesTrak prominently, **(3)** then post.
> He asked us to spread awareness — publishing pays that debt *only if he hears it from us
> first*. The chart credits CelesTrak on the image itself so the credit travels with reposts.

## The finding (verified fresh, 2026-07-22)

- Median time from launch to first public orbit data: **0.65 days (2019) → 2.71 days (2026)** — **4.2×**, risen every year since 2021. 2,698 launches in the table.
- The tail is worse than the median: **Transporter-17's primary object took 12.62 days** and is *still* catalogued as "OBJECT A," source "TBD" — 13 objects launched in 2026 remain unidentified or unattributed.
- Bonus hook found in the same pull: the catalog has outgrown itself — **6-digit NORAD IDs have arrived** (100057, 100080), which breaks legacy TLE-format software.

## X thread — ready to paste (7 posts)

**1/** In 2019, a newly launched satellite showed up in the public tracking catalog in about 16 hours. In 2026 it takes almost 3 days — and it's gotten worse every year since 2021. Chart from 2,698 launches of free public data. 🧵

*(attach `launch_delay.png`)*

**2/** Why it matters: until an object has public orbit data, nobody else can screen it for collisions. Every satellite in that gap is invisible to everyone except its operator. The gap has quadrupled while launch cadence tripled.

**3/** The median hides the ugly part. Transporter-17 launched July 7 with dozens of rideshare payloads. Its primary object took 12.6 days to get orbit data — and two weeks later it's still in the catalog as "OBJECT A," owner "TBD."

**4/** That's not an outlier, it's a pattern: rideshares deploy dozens of near-identical cubesats in one shot, and matching each radar track to each satellite takes days to weeks. 13 objects launched this year are still unidentified or unattributed.

**5/** Found a second thing in the same data: the catalog just rolled past 100,000 tracked objects. NORAD IDs now have 6 digits — which the legacy TLE format literally cannot represent. Decades-old tracking software is quietly breaking right now.

**6/** All of this is measurable by anyone, for free: the data is @TSKelso's CelesTrak "Launch Until First GP Data" table, which he maintains as a public service. My analysis script is ~100 lines of Python. Data transparency is what makes accountability possible.

**7/** I work on exactly this seam — telling real satellite behaviour apart from catalog artifacts using only free public data. If you operate satellites and this gap costs you something, I'd genuinely like to hear how it shows up for you. DMs open.

## Notes on the thread

- **Post 6 is the debt payment** — CelesTrak credited by name and handle, framed as public service. Do not trim it.
- **Post 7 is the only ask**, and it's the same ask as the outreach emails: tell me how the pain shows up. No product claim anywhere — the detector is not mentioned because it isn't ready to survive scrutiny ([[Launch Playbook (external)]], "launch the finding, not the product").
- Numbers must match `python launch_id_delay.py` output on posting day — rerun it that morning; the table updates continuously. If 2026's median has moved, update posts 1 and 3 and regenerate the chart (`python launch_delay_chart.py`).
- Best posting window per the playbook: Tue–Thu morning US time.

## Long-form version (if the thread lands)

Same skeleton, ~600 words, for a blog post or newsletter pitch: lead with the 16-hours-to-3-days number, the invisible-gap safety argument, Transporter-17 as the worked example, the 6-digit catalog rollover as the closing "the system is creaking" note, CelesTrak credited in the first paragraph. Write it only if the thread earns >10 replies from space people — otherwise the thread was the publication.
