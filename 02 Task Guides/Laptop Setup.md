# Putting the crew on the laptop

The vault lives in a **private** GitHub repo: `zayahwork/space-vault`. Clone it, run the
installer, done. (The `space-vault.bundle` file is the offline fallback if GitHub is down.)

## On the laptop, in order

1. **Install prerequisites** (skip any you have):
   - Git — https://git-scm.com/download/win
   - GitHub CLI — https://cli.github.com — then `gh auth login` (sign in as zayahwork)
   - Claude Code — https://claude.com/claude-code — then run `claude` once and sign in
   - (Only if running the detector there) Python 3 + `pip install sgp4 skyfield requests matplotlib numpy`
2. **Clone the vault:**
   ```
   gh repo clone zayahwork/space-vault C:\Space
   ```
   (Any folder works — nothing is hardcoded to C:\Space anymore.)
3. **Run the installer:**
   ```
   powershell -ExecutionPolicy Bypass -File "C:\Space\06 Code\install.ps1"
   ```
4. **Open a NEW terminal, type `t`.** The five crew windows come up; worktrees, personas,
   colors, and sessions all build themselves on first launch.

## Picking up where you left off — the `sync` habit

Type **`sync`** in a terminal (either machine): it pulls the latest and pushes every
branch — vault notes AND all crew branches. The rhythm:
- **Stand up from a machine** → `sync` (send your work up)
- **Sit down at a machine** → `sync` (get everything)
That's the whole system. If you forget to sync before switching, nothing is lost — it's
just waiting on the other machine.

## Gotchas

- `spacetrack_auth.json` / `gmail_auth.json` are NEVER in git — copy them from the PC by
  hand into `06 Code\` only if the laptop needs to run the data scripts.
- The SupGP archive lives on the PC only. Don't archive from two machines - one archive,
  one machine.
- Sessions don't transfer: laptop crew members start with fresh memories. The vault (notes,
  issues, code) IS the shared memory - work committed on one machine reaches the other by
  re-running the bundle transfer (or set up a private remote later).
- The bundle is a snapshot. To sync later changes: on the PC run
  `git bundle create space-vault.bundle --all` again and repeat the clone... or ask Claude
  to set up a private GitHub remote, which makes sync one command forever.
