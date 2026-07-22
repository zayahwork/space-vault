---
description: Clean up a git worktree when its work stream is finished
argument-hint: <branch-name>
---

Clean up the worktree for: $ARGUMENTS (if empty, run `git worktree list` and ask me which one).

Steps:
1. Check for uncommitted changes inside that worktree (`git -C <path> status`). If there are any, STOP and show them to me — do not remove a dirty worktree without my explicit OK.
2. Check whether the branch's commits are merged or pushed. If the branch has unmerged, unpushed commits, warn me before proceeding.
3. Remove it: `git worktree remove <path>` (only use `--force` if I explicitly confirm discarding changes).
4. Ask me whether to also delete the branch; if yes and it's merged, `git branch -d <branch-name>`.
5. Confirm with `git worktree list` that it's gone.
