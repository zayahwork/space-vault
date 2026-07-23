---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Prove the headline number on truly unseen data

**Goal:** the 96%-vs-11% (or whatever the settled figure is after CTO ruling) survives the question "did you tune on what you tested?" — the first question any technical diligence asks.

**Done when:** a holdout protocol exists and ran: bars/thresholds learned ONLY on data through a cutoff timestamp, then scored on snapshots strictly after it (zero overlap, stated in writing); the ground-truth events split the same way (events used to tune the window never reused for scoring); results reported as tuned-set vs holdout-set side by side in `RESULTS - Checked Against History.md`. If holdout is materially lower than the quoted number, the quoted number changes — in bold — before anyone external hears it.

**Notes:** the archive grows every 6h, so genuinely-unseen data accumulates daily; document the cutoff so the protocol is reusable weekly. This protects the company's single most valuable asset: the credibility of its numbers.
