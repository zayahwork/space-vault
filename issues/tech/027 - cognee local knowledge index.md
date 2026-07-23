---
status: blocked
type: AFK
owner: Tim (tech)
blocked-by: [env-python314-litellm-needs-rust]
---
# Cognee — local knowledge index over the vault (read-only, disposable)

**Goal:** "didn't we decide this already?" gets answered in seconds from a knowledge graph built over the vault — without the vault ever having a competitor for truth.

**Done when:** Cognee runs fully local (local embeddings/LLM config — zero API credits); `06 Code/cognee_ingest.py` rebuilds the index from the vault's markdown (RESULTS, day files, Decision Log, NEXT files, issues) idempotently; a query CLI (`python cognee_ask.py "why was 11.3x retired?"`) answers 5 real test questions correctly (11.3× retirement, referee verdict, drip gates, roster, budget rule); full delete + re-ingest reproduces the answers (proves disposability); and a one-line schtask registration command for the nightly rebuild is written in the RESULTS/setup note for the founder to run.

> [!warning] Blocked 2026-07-23 (tim, night) — install is impossible on this machine as configured; measured, not guessed
> `pip install cognee` (1.4.0, latest) fails during dependency resolution: its hard dependency
> **`litellm` publishes no wheel for Python 3.14** (system python is 3.14.6), so pip falls back
> to the 1.93.0 sdist, whose build requires **Rust/Cargo — not installed** ("Cargo, the Rust
> package manager, is not installed or is not on PATH"). Reproduced with `litellm` alone, so no
> cognee version pin escapes it. Two founder-machine fixes, either unblocks: (1) install the
> Rust toolchain (rustup.rs), or (2) a Python 3.12 venv for cognee, where litellm wheels exist.
> Both are machine config — founder's call, per the same rule as the schtask. Secondary note
> for whoever builds this: ollama is installed (`%LOCALAPPDATA%\Programs\Ollama`) but the
> server is not left running — the local-LLM config and the nightly rebuild both need
> `ollama serve` up, so the setup note must cover starting it, and AFK sessions can't.
> The card's own fallback (plain local embedding index, CTO decides) is still on the table.

**Notes:** vault always wins — if graph and vault disagree, the fix is re-ingest, never editing the graph. CTO-side tool first; workers don't query it yet. If Cognee's local-model path fights you for more than a session, say so in your → CTO report with the specific blocker rather than burning days — there's a fallback (plain local embedding index) the CTO will decide on.
