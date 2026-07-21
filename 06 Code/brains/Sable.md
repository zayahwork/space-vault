# 🧠 Sable — ML Engineer

What Sable has learned on this project. Written by `brain.py`; read back
before Sable speaks. `proven` means something demonstrated it. `hypothesis`
means we think so and haven't shown it yet — say so out loud.

- [proven] 2026-07-21 — A gap between SupGP and the public catalog is only evidence of a maneuver if you condition on how OLD the catalog entry was. Rank on raw gap and you are mostly ranking staleness.  **How we know:** detect.py on 10,780 Starlink objects: raw-gap ranking surfaces 3,555; age-binned ranking surfaces 541. 85% of the naive list was old data.
- [proven] 2026-07-21 — Build the baseline out of the population you are testing, not out of a physics model. Per-age-bin percentiles need no drag assumptions and no tuning.  **How we know:** AGE_BINS percentile method in detect.py works with zero fitted parameters.
