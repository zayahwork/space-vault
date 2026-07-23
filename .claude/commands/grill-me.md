---
description: Interview me relentlessly until we reach a shared understanding (run before any plan). Also triggers on "grill me".
argument-hint: <the idea, brief, pasted message, or attached file to grill>
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. The subject:

$ARGUMENTS

Rules:
- **If a file is attached or dropped in with this command** (image, PDF, markdown, code, screenshot) and no other subject is given in the text, **that file IS the subject** — read it in full before asking anything. If both a file and text are given, the text frames the question and the file is supporting evidence to read first.
- First, if this is a fresh session, explore the relevant parts of the repo (use a subagent so exploration doesn't fill this context).
- Walk down each branch of the decision tree, resolving dependencies one by one.
- Ask questions ONE AT A TIME. For each question, provide your recommended answer so I can just say "yes" or push back.
- Do not produce a plan, a document, or any code. The goal is alignment — a shared design concept — not an artifact. Keep grilling until the important ambiguities are resolved or I say stop.
- Surface the nasty questions I haven't considered (edge cases, retroactivity, who pays, what's out of scope, what could invalidate this) — those are the whole point.
- This works on anything: a feature, an email strategy, a research direction, a founder decision. Match your questions to the domain.

When we're done (I say "done" or you genuinely have nothing left to ask), give a 5-line recap of what we agreed, then suggest `/prd` if this should become buildable work.
