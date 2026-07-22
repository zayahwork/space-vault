---
description: Do one ralph iteration - pick the next unblocked AFK issue and complete it (watchable version of the loop)
---

You are the night shift. Read every file in `issues/` (skip `status: done`).

1. **Pick the next task:** an `open` issue, `type: AFK`, whose `blocked-by` issues are all done. Priority: bug fixes first, then feedback-loop/testing infrastructure, then tracer bullets, then polish. If nothing qualifies, say exactly `NO MORE TASKS` and stop.
2. Say which issue you picked and why, then do it:
   - Explore the relevant code first.
   - **Test-first where a test is possible:** write the failing test, watch it fail (red), implement until it passes (green), then tidy (refactor). For script-type work with no test harness, the "done when" line of the issue IS the feedback loop — run it and show the output.
   - Run every feedback loop the repo has for the touched area (tests, the script end-to-end, a chart render).
3. When the "done when" outcome is demonstrated: set the issue's `status: done`, commit everything with a clear message, and summarize what changed in 5 lines or fewer.
4. Touch ONLY what the issue needs. No drive-by refactors, no scope creep — if you spot something worth fixing, append a new issue file instead.

One issue per invocation. Do not start a second one.
