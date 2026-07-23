---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Pre-commit hooks — bad work physically can't land

**Goal:** every lane's existing checks run automatically before any commit; a worker (or human) cannot commit broken work even by accident. Zero tokens, milliseconds per commit.

**Done when:** a shared hook script (`06 Code/hooks/pre-commit.ps1` + installer `install_hooks.ps1` that sets core.hooksPath per worktree) runs, based on which files are staged: tech changes → `python -m pytest`-equivalent of our `_test_*.py` suite (fast subset, full suite stays in ralph's loop); marketing changes → `check_reply_watch.py`, `check_segment_notes.py`, `check_channel_plan.py`; any `.md` card change → frontmatter validation (status/type/blocked-by parse). A failing check blocks the commit with the failing output shown. Installer run documented in each lane's NEXT file; hooks proven by one deliberately-broken commit being rejected per lane.

**Notes:** keep the staged-file detection dumb and fast (path prefixes, not git diff parsing heroics). Bypass (`--no-verify`) stays available for emergencies but every bypass gets called out at the next standup — culture, not cage.
