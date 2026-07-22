---
date: 2026-07-22
type: research
status: pass complete — 7 rows added, and a structural finding that matters more
parent: "[[Guide - Daily Outreach]]"
---

# 📉 Volume pass — the drip's addressable universe is small, and we've nearly used it

Ran `contact_find.py` over **33 candidate companies** not already in the CSV: satellite
operators, IoT constellations, servicing/debris firms, propulsion. It tries nine likely contact
paths per domain and pulls any published address off whatever loads.

## What came back

**Seven usable inboxes out of thirty-three.** Rows 69–75, all MX-verified:

| # | Company | Address | Why them |
|---|---|---|---|
| 69 | **Astroscale** | `info@astroscale.com` | They rendezvous with objects whose behaviour they must predict. A neighbour that went quiet is their operating problem, not a hypothetical |
| 70 | **Orbit Fab** | `bd@orbitfab.com` | *"This satellite stopped manoeuvring because it ran out of propellant"* is literally their market thesis. Best-fit target in this batch, and `bd@` is a real door rather than a press inbox |
| 71 | **AST SpaceMobile** | `info@ast-science.com` | Unusually large LEO satellites — conjunction-relevant, and a fleet everyone watches |
| 72 | **Sateliot** | `info@sateliot.com` | LEO IoT, Spain, small enough that one email reaches someone technical |
| 73 | **FOSSA Systems** | `contact@fossa.systems` | Spanish smallsat IoT, small team |
| 74 | **Alén Space** | `info@alen.space` | Smallsat builder/operator, Vigo |
| 75 | **Hiber** | `info@hiber.global` | LEO IoT, Netherlands |

Queue went from **12 sendable → 19**.

## The finding that matters more than the seven rows

**Twenty-six of thirty-three companies publish no address at all.** Not a hidden one — none.
Eutelsat, SES, Telesat, Hispasat, Omnispace, Swarm, Kinéis, Astrocast, Lynk, Slingshot,
ClearSpace, Exotrail, Katalyst: contact form only.

That is not an obstacle to route around, it's the shape of the market. **The drip's ceiling is
the number of space companies that publish an inbox, and it is roughly a hundred, not a
thousand.** We have now worked through most of the reachable ones.

So a 12/day target is not sustainable by finding more addresses. Nineteen sendable rows is
**a day and a half of drip**, and the next pass will yield less than this one did — the easy
domains are gone.

## What to do about it — three honest options

1. **Lower the target to what inventory supports** (~6–8/day) and spend the difference on
   hand-written emails. Slower on paper, almost certainly better: our two actual replies so far
   came from Moriba Jah and T.S. Kelso, both individually written to people whose work we'd read.
2. **Work the forms by hand.** 26 companies × one form each is maybe three hours of founder
   time, and forms convert *better* than `info@` because someone is assigned to read them. The
   machine cannot do this and should not pretend to.
3. **Change what the drip sends.** The ~130 harvested paper-author addresses are real, verified
   and reachable — they're just wrong for a template. A short, genuinely per-person email is the
   only thing that should go to them, which is founder work, not drip work.

**My recommendation:** option 1 plus option 2. Set `-DailyTarget 8`, work the form list in
batches, and treat the paper authors as the quality channel they are. The number that matters
was never emails sent — it's people describing their pain unprompted, and we have two.

## Method note

`contact_find.py` is slow (nine paths × network timeouts). Thirty-three domains took several
minutes and one batch had to be split. Keep future runs to ~10 domains per invocation.
