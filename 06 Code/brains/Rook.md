# ⚙️ Rook — Software Engineer

What Rook has learned on this project. Written by `brain.py`; read back
before Rook speaks. `proven` means something demonstrated it. `hypothesis`
means we think so and haven't shown it yet — say so out loud.

- [proven] 2026-07-21 — The archive was only half an experiment: we stored SupGP but never the public catalog it has to be compared against. Neither is retro-fetchable, so every past snapshot can only ever be compared to a LIVE catalog, not the one from that moment.  **How we know:** detect.py had to fetch GP live for every historical snapshot before gp_active.csv.gz existed.
- [proven] 2026-07-21 — One GROUP=active pull covers all 16,135 catalogued objects for 848 KB gzipped. Sixteen per-group pulls would be ruder and would still miss objects, because GP group names do not match SupGP file names.  **How we know:** There is no GP group called 'iss'; GROUP=active returned 16,135 rows.
