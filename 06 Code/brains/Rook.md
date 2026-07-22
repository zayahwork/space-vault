# ⚙️ Rook — Software Engineer

What Rook has learned on this project. Written by `brain.py`; read back
before Rook speaks. `proven` means something demonstrated it. `hypothesis`
means we think so and haven't shown it yet — say so out loud.

- [proven] 2026-07-21 — The archive was only half an experiment: we stored SupGP but never the public catalog it has to be compared against. Neither is retro-fetchable, so every past snapshot can only ever be compared to a LIVE catalog, not the one from that moment.  **How we know:** detect.py had to fetch GP live for every historical snapshot before gp_active.csv.gz existed.
- [proven] 2026-07-21 — One GROUP=active pull covers all 16,135 catalogued objects for 848 KB gzipped. Sixteen per-group pulls would be ruder and would still miss objects, because GP group names do not match SupGP file names.  **How we know:** There is no GP group called 'iss'; GROUP=active returned 16,135 rows.
- [hypothesis] 2026-07-21 — An MCP server being connected and authorised does not mean it is callable — the local permission gate blocks it in non-interactive runs, so pre-allow the exact tool name before relying on a connector unattended.  **How we know:** from work ticket #2: call mcp__claude_ai_Gmail__search_threads with a simple query to verify the Gmail connector is live and returning result
- [hypothesis] 2026-07-21 — Read the target file before committing to build it — outreach.py already had 444 lines of the exact feature I volunteered to write, and the useful work turned out to be finding the holes in it.  **How we know:** from work ticket #3: create a Python SMTP script in C:\Space\06 Code that sends outreach emails directly via Gmail SMTP using app-password au
