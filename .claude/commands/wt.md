---
description: Create a git worktree for an independent parallel work stream
argument-hint: <branch-name>
---

Create a git worktree so this work stream can't collide with the other Claude windows.

Branch/worktree name: $ARGUMENTS (if empty, propose a short kebab-case name from what we're working on and use it).

Steps:
1. Ensure `C:\Users\Administrator\.claude\worktrees` exists.
2. From the current repo, run: `git worktree add "C:\Users\Administrator\.claude\worktrees\<repo-name>-<branch-name>" -b <branch-name>` (drop `-b` if the branch already exists, and just check it out).
3. If the repo has installable dependencies (requirements.txt, package.json, etc.), install them inside the new worktree so it actually runs.
4. Tell me the full worktree path and remind me to either `cd` there in this window or open a new Claude window in that folder — the status line will show `[worktree]` when I'm inside one.

When done with the stream, I'll run /wt-done <branch-name>.
