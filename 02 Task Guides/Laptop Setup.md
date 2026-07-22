# Putting the crew on the laptop

The whole setup travels inside the vault repo. One file (`space-vault.bundle`) carries the
entire vault + history; one script installs the machine bits.

## On the laptop, in order

1. **Install prerequisites** (skip any you have):
   - Git — https://git-scm.com/download/win
   - Claude Code — https://claude.com/claude-code — then run `claude` once and sign in
   - (Only if running the detector there) Python 3 + `pip install sgp4 skyfield requests matplotlib numpy`
2. **Copy `space-vault.bundle` over** (USB stick, drive, however) and clone it:
   ```
   git clone space-vault.bundle C:\Space
   cd C:\Space
   git checkout master
   ```
   (Any folder works — nothing is hardcoded to C:\Space anymore.)
3. **Run the installer:**
   ```
   powershell -ExecutionPolicy Bypass -File "06 Code\install.ps1"
   ```
4. **Open a NEW terminal, type `t`.** The five crew windows come up; worktrees, personas,
   colors, and sessions all build themselves on first launch.

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
