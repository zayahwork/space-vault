---
date: 2026-07-22
type: send-plan
status: READY — 8 curated emails written, addresses verified, nothing sent
parent: "[[Contract Work - Space ML Subcontract]]"
---

# 📤 Send Plan — the contract batch (8 emails)

All eight are written, personalised to the recipient's own paper, and sitting on `hold` so the
drip cannot touch them. This page is how they leave.

## Timing: seven of the eight are European

It is **12:30 Pacific**, which is **21:30 in Madrid, Munich and Tallinn**. An email landing at
half nine at night gets opened tomorrow, at the bottom of a full inbox.

| Send | When | Who |
|---|---|---|
| **Today** | now | **#62 Applied Defense Solutions** (Maryland) — the only US target; lands mid-afternoon their time |
| **Tomorrow 06:00–08:00 Pacific** | Thu 23 Jul | the seven Europeans — lands 15:00–17:00 CET, mid-afternoon, still a working day |

That one night of patience is worth more than any wording change on this page.

## Order, and why

1. **#61 GMV NSL — Keiran McNally.** Best odds: their own paper carried outside contributors,
   so that team already works this way.
2. **#59 OKAPI:Orbits — Jonas Radtke.** Our staleness finding lands directly on their product.
3. **#60 Deimos — Emma Kerr.** She wrote the future-needs paper; the question flatters and is real.
4. **#62 Applied Defense — Islam Hussein.** Closest US company to the method.
5. **#63 Sybilla — Agnieszka Sybilska.** Small shop, concrete overlap.
6. **#65 Guardtime — Kaarel Hanson.** Coordination monitoring needs independent verification.
7. **#66 CGI — Daniel Novak.** Consultancies carry work past their headcount.
8. **#64 Beechleaf — Duncan Smith.** **Not a pitch** — asks an independent how he built his
   practice. Send it last, and send it even if the others land: it costs nothing and the answer
   is useful whatever happens.

## The commands

`--ids` was added to `outreach.py` today for exactly this: it sends **named rows, in the order
given, regardless of status**, while keeping the audit log, the duplicate-address check, the
bounce handling and the Gmail Sent copy. Every other safety still applies. `MAX_PER_RUN` is 5,
so eight emails is two runs.

Run from wherever the merged tree lives (`C:\Space\06 Code` after the merge), and **dry-run
first** — it prints exactly what would go:

```
python outreach.py --send --ids 61 59 60 62 63          # dry run, reads the 5
python outreach.py --send --live --ids 61 59 60 62 63   # sends them
python outreach.py --send --ids 65 66 64                # dry run, the last 3
python outreach.py --send --live --ids 65 66 64         # sends them
```

**Pre-flight, once:** `06 Code/gmail_auth.json` must exist in the tree you run from (it is
gitignored, so it does not travel with the merge).

## After they go

- The ledger marks them `sent` automatically and logs the Message-ID, so bounces get caught.
- **Replies go to [[Reply Watch - Batch 2]] rules**: answer within the hour, aim at 15 minutes,
  offer 2–3 concrete times.
- A reply to a *contract* email is different from a product reply — the goal is a **scoped paid
  week**, not a call about the wedge. Don't let the two blur; if they ask about the detector,
  answer generously and then come back to the week.
- Nudge clock: 3 business days → **Tue 28 Jul** for tomorrow's seven. One line, once.

## What is deliberately NOT in this batch

- **Advanced Space** (Popplewell, Kwon) — live product thread with Miga. One ask per company.
- **Aerospace Corporation** — six new addresses, but that's product outreach, not contract.
- **ESA (Merz, Flohrer, Siminski)** — one shot each, institutional, hand-written, later.
- **Privateer** — Moriba Jah's company, live thread.
