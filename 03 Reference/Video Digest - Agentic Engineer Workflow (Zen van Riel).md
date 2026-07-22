# Video Digest: The Agentic Engineer Workflow You Need In 2026

**Source:** [YouTube — Zen van Riel](https://www.youtube.com/watch?v=ElYxdpYi4U0) · ~17 min · watched/digested 2026-07-22

One-line takeaway: **run a few parallel Claude Code windows at different effort levels, keep contexts short, use git worktrees for parallel streams, and expect 30–60% gains — not 5x.**

## The workflow

- **4 parallel Claude Code terminals**, not 50 agents. Two at high effort (big planning/feature work), one medium, one low (quick questions like "what languages does this repo use"). Four is his ceiling for human mental capacity.
- **Context window management:** watch the context meter; long contexts = slower + drift. Use `/compact` or `/clear` when it fills up. No magic rule — build a feel for it per project.
- **Git worktrees** (jargon: a worktree is a temporary extra copy of your repo so two agents can edit the same files without stepping on each other). Needed because parallel windows otherwise share one git checkout — one window switching branches switches them all. Delete worktrees when done; note you may need to reinstall dependencies in each one (automate that with a skill/command if it's frequent).
- **Custom "smell" command:** a review prompt built from Clean Code / design-patterns books that nudges the model toward those standards before opening a PR. He deliberately does NOT share his review commands — the right one depends on language, team, and code style.
- **AI code review in PRs** (Claude Code review, or a headless-agent pipeline) but always combined with human review.

## MCP vs Bash vs skills (his heuristic)

- **Bash/CLI** for common platforms (GitHub CLI, curl, small Python scripts) — the model already knows them and auth is inherited from your shell.
- **MCP servers** for unknown/internal services the model can't know (internal diagnostics), or specialized backends like Context7 (docs retrieval) and Serena (language server search).
- Single simple operation → bash. Rich unfamiliar service → MCP.

## The opinions worth remembering

- **Skeptical of methodology hype** (spec-driven development, BMAD, prompt-vs-context-engineer labels): anything that works gets absorbed into the tools themselves (e.g. Claude Code's built-in todo tracking). His filter: if a pattern survives 3–4 months of hype, it's probably real.
- **Scale changes everything:** freelance/MVP work feels god-mode; on real teams, 10k lines/day of AI code gets bounced in review or breeds long-term bugs. His own 2-day AI-built feature got (rightly) pushed back for lacking architectural thinking — he'd only skimmed the code.
- **Realistic gains: 30–60%**, with occasional big wins on one-off scripts. Coding is becoming a smaller share of the engineering job; the job shifts, it doesn't vanish.
- Mindset framing: "vibe coder" vs "AI-native engineer" (one who takes the gains but can still fix the system when it breaks).

> [!done] Implemented 2026-07-22 — see [[02 Task Guides/Parallel Claude Windows (t)|Parallel Claude Windows (t)]] for how to use it.

## Relevance to us

- We already run the multi-agent [[Office/Calling the Crew|room/crew]] setup — his "4 streams max, mixed effort levels" point supports keeping the crew small rather than scaling agent count.
- Worktree-per-agent is worth adopting if crew agents ever edit the same files in parallel.
- His MCP-vs-bash heuristic matches how our scripts already lean on plain Python/CLI calls.
