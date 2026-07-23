---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# The neural brain, v0 — train against the SPLID labeled dataset

**Goal:** the company's first learned model, started the credible way: not replacing the physics pipeline, but trained and scored on the one labeled maneuver dataset that exists (MIT ARCLab SPLID challenge — devkit already cloned in `06 Code/splid-devkit/`). The physics detector generates candidates; the ML layer's job is to learn what the physics can't articulate.

**Done when:** (1) dataset status verified — if the full SPLID dataset isn't on disk, document exactly what to download and from where (the earlier scripted download failed; note if it needs the founder's browser) and stop there as BLOCKED-founder; (2) with data present: the devkit's own baseline reproduced end-to-end (their heuristic + their ML baseline, their metric), our scores vs the published leaderboard numbers in a RESULTS note; (3) one honest experiment: our detector's features (age-aware gap, persistence count, regime, inclination step) fed to a simple model vs the devkit baseline — does our feature engineering beat their baseline at all? Win or lose reported with the same discipline as everything else.

**Notes:** sequencing — this must NOT displace Jul 29 prep (quiet exam, holdout, broker packet). It's the background build: pull it when priority cards are blocked. The long game: SPLID labels + Randy's documented-maneuver set + the Intelsat [PM] feed become our training corpus; that combination is proprietary-grade and nobody else is assembling it from free data.
