# Video Digest: Full Walkthrough — Workflow for AI Coding (Matt Pocock)

**Source:** [YouTube — AI Engineer conference](https://www.youtube.com/watch?v=-QFHIoCo-Ko) · ~96 min workshop · digested 2026-07-22

One-line takeaway: **plan WITH the AI until you share one mental model (the "grilling"), turn that into small parallelizable issues, then let agents implement AFK in a loop — and let your tests, not your hope, be the quality ceiling.**

## The two constraints everything is built on

1. **Smart zone / dumb zone.** An LLM does its best work in roughly the first ~100k tokens of context (regardless of the advertised window — 200k or 1M). Past that it gets measurably dumber. So: size every task to fit inside the smart zone, and watch your token count constantly (this is why the status line matters).
2. **The Memento model.** The AI forgets everything on `/clear` — and Pocock says that's a *feature*. He prefers `/clear` over `/compact` because a cleared session always restarts from the exact same known state. Design your workflow so any session can be killed and restarted cold.

## The pipeline (idea → shipped)

**Idea → GRILL → PRD → Issues (Kanban) → AFK implementation loop → QA → repeat**

- **Grill me** (the core move): a tiny skill — "interview me relentlessly about every aspect of this plan until we reach a shared understanding; one question at a time; give your recommended answer each time." Sessions run 20–100 questions. The point is NOT the document — it's getting you and the AI onto the same *design concept* (Fred Brooks). He starts virtually every piece of work this way. Works on meeting transcripts too: feed one in and grill the assumptions.
- **PRD = destination document.** Problem, solution, user stories, implementation + testing decisions, **out-of-scope list** (that's where rejected ideas live), and — crucially — **the module map**: which modules get created/modified. He does NOT re-read/polish the PRD: if the grilling worked, the PRD is just summarization, which LLMs are good at.
- **Issues = the journey, as a Kanban.** Break the PRD into *independently grabbable* issues with explicit blocked-by relationships (a DAG, so agents can parallelize), each tagged **HITL** (human must be there) or **AFK** (agent can do it alone). Planning is HITL; implementation is AFK — "day shift queues work, night shift does it."
- **Vertical slices, not horizontal layers.** AI loves coding layer-by-layer (all schema → all API → all UI), which means zero feedback until the end. Force *tracer bullets*: each issue crosses all layers and produces something visible/testable. He rejects slices that are "too horizontal" during review.
- **The Ralph loop** (AFK implementation): a dumb bash loop — cat ALL the issues + last 5 commits + a fixed prompt into `claude -p` with accept-edits; the prompt says "pick the next unblocked AFK task by priority, do it with TDD, run the feedback loops, commit; if no tasks remain output NO MORE TASKS." Run once while watching to tune the prompt, then loop it. His parallel version (Sandcastle): planner picks non-blocking issues → each implemented in its own **worktree** sandbox → a merger agent merges branches and fixes conflicts. Sonnet implements, the smarter model reviews.

## The quality rules

- **Feedback loops are the ceiling.** "The quality of your feedback loops is the ceiling on how well AI can code in your repo." No tests = AI codes blind. If output is bad, improve the loops before blaming the model.
- **TDD (red-green-refactor) stops test-cheating.** Written after the implementation, tests get written to pass. Written first, they instrument the code before it exists.
- **Review in a FRESH context.** After implementing, the session is deep in the dumb zone — a reviewer there is dumber than the implementer was. `/clear`, then review. **Pull vs push:** implementer *pulls* coding standards when it needs them (skills); reviewer gets them *pushed* into its prompt.
- **Deep modules (Ousterhout).** Few big modules with small interfaces beat many shallow files — easier for AI to navigate, and you can draw one big test boundary around real functionality. His "if you take one thing away" tip: run an *improve-codebase-architecture* scan on your repo.
- **Design the interface, delegate the implementation.** Keep the module map in your head; treat module internals as gray boxes. That's how you move fast without losing your codebase.
- **QA is where taste lives.** He automates a lot but never QA — human QA is how you impose taste, and each QA pass feeds new issues back into the Kanban. Automate everything and "you end up with slop."
- **Kill doc rot.** Delete/close PRDs and issues once implemented — a stale PRD found by a future agent actively misleads it.
- **Own your planning stack** (vs Spec Kit / Taskmaster / BMAD): when it breaks you can fix it. And: the old books (Pragmatic Programmer, Philosophy of Software Design, Design of Design, Refactoring) are prompt gold — pre-AI engineering wisdom verbalized in English.
- He explicitly rejects **specs-to-code** ("edit the spec, ignore the code") — "the code is your battleground."

> [!done] Implemented 2026-07-22 — `/grill`, `/prd`, `/issues`, `/ralph` + the loop script. See [[02 Task Guides/Parallel Claude Windows (t)|the t guide]].

## Honest fit for us

- **Grill-me is the biggest win** — and not just for code. Founder decisions (which wedge, what to say to Kelso, SBIR) are exactly "misalignment risk" territory.
- **Feedback-loops-as-ceiling names our real gap:** detect.py has zero automated tests. His claim predicts AI works worse in our repo because of it.
- **We already have** his infrastructure: worktrees per stream, status line with context, fresh-context review (/smell), effort-tiered windows.
- **Vertical slices matter less** for research scripts, but "every issue produces something visible/checkable" still applies (a chart, a number, a validated table).
- **Ralph AFK fits best** for well-specified chores: tests for detect.py math, contact_check hardening, room refactors — not for research judgment calls.
