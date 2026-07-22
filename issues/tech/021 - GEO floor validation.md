---
status: open
type: AFK
owner: Tim (tech)
blocked-by: [016]
---
# Validate the GEO 1.0 km floor against typed ground truth

**Goal:** the "least defensible constant in detect.py" (the GEO min-km floor) gets judged by documented maneuvers instead of judgement.

**Done when:** using the type-tagged ground truth from research card 016, the floor analysis answers: what floor value catches the documented GEO events while excluding the measured sub-km noise? Report the distribution of documented-event step sizes vs the noise floor per regime, recommend keep/change with numbers, and update the danger callout in `RESULTS - Beyond Starlink.md` either way. Never tune to make output look better — tune to the documented events.

**Notes:** blocked until 016's maneuver_type column lands in `ground_truth.csv`.
