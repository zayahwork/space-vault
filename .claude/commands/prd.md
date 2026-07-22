---
description: Write a PRD (destination document) from the grilling session we just had
argument-hint: [feature name]
---

Write a PRD — the destination document — for: $ARGUMENTS (if empty, use what we just grilled about in this conversation).

If we have NOT just had a grilling session about this, stop and run the /grill flow first — a PRD without alignment is a guess.

Write it to `issues/PRD - <short-name>.md` with exactly these sections:
1. **Problem** — what hurts, for whom, in plain words.
2. **Solution** — one paragraph.
3. **User stories** — "As X, I can Y" list. For research/ops work, frame as outcomes: "When I run Z, I see Y."
4. **Module map** — which files/modules get created or modified, and which is the deep module we test around. Be specific; this is the part that keeps the codebase shape in our heads.
5. **Implementation decisions** — the choices we made while grilling.
6. **Testing decisions** — what feedback loop proves each piece works.
7. **Out of scope** — everything we decided NOT to do, with the one-line reason. This is where rejected ideas are recorded.

Keep it short — it's a summary of an alignment we already have, not a novel. When done, suggest `/issues` to break it into the Kanban.

Doc-rot rule: PRDs get deleted once implemented (the code becomes the truth). Never treat an old PRD in `issues/` as current documentation.
