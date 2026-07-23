---
status: done
type: AFK
owner: Tim (tech)
blocked-by: []
closed: 2026-07-23
closed-by: tim
---
# Prove the headline number on truly unseen data

**Goal:** the 96%-vs-11% (or whatever the settled figure is after CTO ruling) survives the question "did you tune on what you tested?" — the first question any technical diligence asks.

**Done when:** a holdout protocol exists and ran: bars/thresholds learned ONLY on data through a cutoff timestamp, then scored on snapshots strictly after it (zero overlap, stated in writing); the ground-truth events split the same way (events used to tune the window never reused for scoring); results reported as tuned-set vs holdout-set side by side in `RESULTS - Checked Against History.md`. If holdout is materially lower than the quoted number, the quoted number changes — in bold — before anyone external hears it.

**Notes:** the archive grows every 6h, so genuinely-unseen data accumulates daily; document the cutoff so the protocol is reusable weekly. This protects the company's single most valuable asset: the credibility of its numbers.

---

## ✅ Closed 2026-07-23 — protocol shipped and ran; unseen day reproduces the tuned floor at matched reach; settled figure pending by physics, not by omission

`06 Code/holdout.py` + `_test_holdout.py` (26 cases, all fakes). **Cutoff 2026-07-23
00:00Z**, basis documented in the file: every constant, the window table (018), the
observability correction (003) and the stored bars (learned 07-22 19:16Z from snapshots
≤ 07-22/1400Z) froze at or before it. Enforced, not asserted: the script **refuses** if
the bars' provenance contains a post-cutoff snapshot, refuses if no strictly-after
snapshot exists, and prints the zero-overlap statement in writing every run.

**First run, first unseen snapshot (2026-07-23/0200Z), top-75, production selection:**
at matched forward reach (0.00 d), **unseen 76% vs 11%** (31/41 suspects vs 8/75
controls) beside tuned 76%/93% — the tuned sets' own zero-reach floor, reproduced on a
day no tuning ever saw. The settled number needs the +3 d window to fill with published
orbit determinations; the run measures reach **from the fetched data, not the wall
clock** (GP_HISTORY materializes ~6–12 h late — a fetch 5.8 h after the snapshot held
0.00 d of forward reach), labels itself PROVISIONAL, and says when to re-run. Each
scored snapshot gets its own `holdout_cache/<snapshot>/` because the shared
`verify_cache` is keyed by object only — a file cached yesterday silently ends
yesterday, which for a fresh snapshot is zero forward reach wearing a full window's
label.

**Ground-truth split:** the 16 GEO rows that existed at issue 015 chose the −3/+14 d
window — frozen key list, tuning-side forever (their 13/14 is tuning-set performance,
not validation). The 3 rows issue 026 added later — Astra 3B, Intelsat 1002 (2025-02-28),
AMC 11 (2025-06-10) — are the event-holdout: **3/3 caught** by a window frozen before
they entered the file. First non-circular window evidence; single-sourced tier, said so.
Future rows land holdout-side automatically.

**What the unseen day also showed:** 34 of its top-75 are one fresh launch batch
(analyst-range NORADs 100012–100056, 2–3 history records each) — excluded from the
denominator by the standing thin-history rule, reported, not hidden.

RESULTS table + reuse instructions in `RESULTS - Checked Against History.md`. Run saved
to `output/holdout_033.json`. Whole tech suite green (the two failing files in the shared
folder import `outreach.py` — outreach lane's, absent from this sparse view, failing
before this card was touched).
