---
description: Review uncommitted changes for code smells (Clean Code + design patterns) before a PR
---

Review the current uncommitted changes for code smells. Run `git status` and `git diff` (plus `git diff --cached`) to see what changed, and read the surrounding files for context — a diff alone hides architectural problems.

Judge the changes against these principles:

**Clean Code (Robert Martin):**
- Functions do one thing, at one level of abstraction; short over long.
- Names reveal intent — no abbreviations that need decoding, no misleading names.
- No duplicated logic (DRY) — flag copy-paste between the diff and existing code too.
- Comments only where the code can't speak for itself; delete commented-out code.
- Error handling is explicit — no swallowed exceptions, no bare excepts.
- Boundaries: side effects (I/O, network, globals) separated from pure logic.

**Design / architecture:**
- Single Responsibility: does each changed class/module still have one reason to change?
- Does the change fight the existing architecture or follow it? Flag "functional but structurally wrong" — code that works today but ignores the bigger picture of how this codebase is organized.
- Leaky abstractions, God objects, feature envy (a function that mostly manipulates another module's data).
- Magic numbers/strings that should be named constants or config.
- New dependencies or coupling that a future change will regret.

**AI-code-specific smells:**
- Over-engineering: speculative options, wrappers, or config nobody asked for.
- Redundant re-implementation of something that already exists in this repo or its libraries.
- Inconsistency with this repo's existing naming, idiom, and comment density.

Report findings ranked by severity (will-cause-bugs first, style last). For each: file:line, what's wrong, which principle it violates, and a one-line suggested fix. If the diff is clean, say so plainly — do not invent findings. Do NOT change any code unless I ask.
