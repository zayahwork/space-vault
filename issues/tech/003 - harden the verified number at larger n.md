---
status: done
type: AFK
blocked-by: []
closed: 2026-07-22
closed-by: tim
---
# Push the verified number to larger n

**Goal:** the number we quote everywhere — **~68–72% of top suspects clear a bar only ~10% of matched controls clear** — holds (or honestly sags) as n grows. It's currently strongest at top-75; the full 489-object list verifies at ~4× control rate, which is a different (weaker) claim.

**Done when:**
- The control-matched comparison is re-run at n = 150 and n = 300 on both banked snapshots (0200Z and 0800Z), same matching rules as `RESULTS - Checked Against History.md`.
- A short table lands in that RESULTS file: n vs suspect-rate vs control-rate per snapshot.
- If the separation sags at higher n, that goes in the file in bold before anyone outside reads it. We find out before Kelso does, not after.

**Notes:** do NOT resurrect the 11.3× multiple — it swung to 23.8× between snapshots and is retired; rates, not multiples. This is lower priority than 002 (GEO) — grab it when 002 is blocked or done.

---

## ✅ Closed 2026-07-22 — folded into the post-018 re-run, and it surfaced a bigger correction

`06 Code/hardening.py` scores n = 25/75/150/300 on both published snapshots (0200Z, 0800Z)
under the **production** window (`verify.window_for_regime`, LEO -3/+3d) and picks its two
groups with the **same** `verify.select_groups` the live path calls - factored out of
`run_top` so the hardened rate is the production measurement at a bigger n, not a copy of it.

**Does it sag? Yes, exactly as a ranked list must.** Top-75 96%, n=150 79-86%, n=300 52-63%,
against a control rate pinned at 10% throughout. Even the n=300 tail clears the bar 5-6x as
often as controls. Full table (both snapshots, rates side by side) in
`RESULTS - Checked Against History.md`.

**The thing this re-run caught that the card did not ask for:** the published 68-72% was
measured minutes after its snapshot, when the forward half of the window held no data yet.
Re-scored aged, the SAME top-75 give **96% vs 11%** - controls unmoved, so it is a real
correction, not inflation. It plateaus by ~0.5d forward reach. The old number is struck (not
deleted) in the RESULTS file with the observability sweep that explains it. Practical rule
now recorded: a same-day LEO verify under-reports; re-run ~12h later before quoting.

Regression: `select_groups` pinned by 5 new cases in `_test_verify_window.py` (36 total).
Multiples stay retired - rates only, as the card required.
