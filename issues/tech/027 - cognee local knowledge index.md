---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Cognee — local knowledge index over the vault (read-only, disposable)

**Goal:** "didn't we decide this already?" gets answered in seconds from a knowledge graph built over the vault — without the vault ever having a competitor for truth.

**Done when:** Cognee runs fully local (local embeddings/LLM config — zero API credits); `06 Code/cognee_ingest.py` rebuilds the index from the vault's markdown (RESULTS, day files, Decision Log, NEXT files, issues) idempotently; a query CLI (`python cognee_ask.py "why was 11.3x retired?"`) answers 5 real test questions correctly (11.3× retirement, referee verdict, drip gates, roster, budget rule); full delete + re-ingest reproduces the answers (proves disposability); and a one-line schtask registration command for the nightly rebuild is written in the RESULTS/setup note for the founder to run.

**Notes:** vault always wins — if graph and vault disagree, the fix is re-ingest, never editing the graph. CTO-side tool first; workers don't query it yet. If Cognee's local-model path fights you for more than a session, say so in your → CTO report with the specific blocker rather than burning days — there's a fallback (plain local embedding index) the CTO will decide on.
