---
description: Break a PRD into small, independently-grabbable issues (the Kanban) for the ralph loop
argument-hint: [PRD file in issues/]
---

Break the PRD into independently grabbable issues using vertical slices (tracer bullets). PRD: $ARGUMENTS (if empty, use the newest `issues/PRD - *.md`).

Write each issue as `issues/NNN - <short-name>.md` (three-digit numbers continuing from the highest existing) with this frontmatter and body:

```markdown
---
status: open            # open | done
type: AFK               # AFK = an agent can do it alone | HITL = needs Zayah present
blocked-by: []          # list of issue numbers that must be done first
---
# <title>

**Goal:** one sentence — what exists when this is done.
**Done when:** a concrete, checkable outcome (a passing test, a chart that renders, a number in a log). Never "code is written".
**Notes:** pointers into the code, decisions from the PRD that apply here.
```

Rules for the split:
- **Vertical slices**: every issue must end in something visible or checkable end-to-end — a runnable script producing a number, a passing test, a chart. Reject your own slice if it's "all the schema first, all the logic later" — that's horizontal, and it means zero feedback until the end.
- Each issue must fit comfortably in one fresh context window (smart zone). Split anything big.
- Mark blocking honestly but minimize it — unblocked issues can be worked in parallel by different windows.
- Tag HITL for anything needing judgment, taste, or external humans (sending emails, research conclusions, founder decisions). Tag AFK only when the "done when" is mechanically checkable.
- Quiz me before writing the files if any split decision is genuinely ambiguous.

Show me the proposed board (title, type, blocked-by) for approval BEFORE writing files. After approval, write them and tell me how many are immediately grabbable.
