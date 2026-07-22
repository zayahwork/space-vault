---
date: 2026-07-22
owner: DETECTOR window
status: approved, ready to build
follows: "06 Code/detect.py @ 77b8b93"
---

# 🔬 Plan — stop ranking, start checking

> [!success] Your persistence work is merged
> `77b8b93` is on master as of `20ee731`. Age-binning + persistence + the `load_gp`
> time-travel fix are all in. `_test_detect.py` passes. **This note is what comes next.**

## Why this is the next chunk

Two ways to fool ourselves are now closed:

| how we'd fool ourselves | fix | status |
|---|---|---|
| "old data looks like movement" | age-binned baselines | ✅ Jul 21 |
| "one measurement looks like evidence" | independent looks / persistence | ✅ `77b8b93` |
| **"nothing was ever checked against reality"** | **this note** | ⬅️ **now** |

Both shipped fixes make the list **shorter and better reasoned**. Neither makes one entry
**true**. [[01 TASKS]] says it plainly: *"541 candidates and no way to check them is not a
detector, it's a ranked guess."*

Everything we have is self-graded. This chunk produces the first number that isn't.

## Step 1 — Confirm persistence unblocks itself (a check, NOT a build)

Only `supgp_archive/2026-07-22/0200Z` had a catalog beside it, so persistence had nothing to
be persistent across and said so. **That message is correct — do not "fix" it.**

The `SupGP Archive` scheduled task is healthy (last result `0`) and captures the catalog
alongside SupGP on every run, ~4/day. So it unblocks on its own.

```bash
cd "C:\Space\06 Code"
ls supgp_archive/*/*/gp_active.csv.gz     # 2+ means you can run
python detect.py --group starlink
```

Expect the refusal to be replaced by `PERSISTENT SUSPECT / unconfirmed / cleared`.
If it still refuses, **read why before touching code** — it is probably right.

📌 The number worth writing down: how far **524** falls once a candidate must survive two
independent looks. That drop is the honest sequel to "85% was just old data."

## Step 2 — Build `06 Code/verify.py`

Check suspects with a **different method on differently-shaped data**, then see if the two
agree. We already own both halves; this is mostly wiring.

The independent path is the v0.1/v0.2 chart detector that went **3/3 on ISS reboosts**
([[RESULTS - First Charts]]): Space-Track `GP_HISTORY`, months of altitude, look for jumps
and sustained descent. Nothing like `detect.py`'s instantaneous SupGP-vs-GP RMS.

### 2a. FIRST: the 17 data-quality flags

[[RESULTS - Maneuver vs Stale]] already asserts in writing that the >500 km gaps are
*"likely decay or bad TLE, not a maneuver."* **That is a guess we published.** It is also a
specific, falsifiable prediction on a bounded set.

Pull `GP_HISTORY` for those 17 NORADs, run the existing descent logic:
- **decaying** → the 500 km gate is confirmed and that sentence becomes a finding
- **not decaying** → we published something wrong and need to know today

17 objects. Fast. Can only end in a real answer. That's why it goes first.

### 2b. THEN: the top persistent suspects

Same machinery on the top ~25 **by persistence, not by raw gap** — raw gap puts the least
trustworthy objects on top. Three buckets:

- **corroborated** — altitude history shows a burn near the flagged window
- **contradicted** — history is flat and clean; the RMS gap came from somewhere else
- **invisible** — electric/gradual, under what altitude-jump detection can see

> [!warning] "Invisible" is not a miss
> It's blind spot #1 (known since STARLINK-2083) and it's a limit of the **verifier**, not of
> `detect.py`. Scoring it as a failure would repeat exactly the mistake this chunk exists to
> stop. The three-way split matters more than any single score.

### Reuse, don't rewrite

| file | take |
|---|---|
| `06 Code/maneuver_chart.py` | `altitude_km(row)` — handles the `SEMIMAJOR_AXIS` → `MEAN_MOTION` fallback |
| `06 Code/maneuver_chart.py` | `get_history()` — **`QUERY_URL` line 24 hardcodes NORAD 25544.** Parameterize into `get_history(norad, days)`; don't copy-paste it |
| `06 Code/deorbit_check.py` | `descent_rate_km_per_day(points, i, window_days=7)` — the logic that caught STARLINK-2083 |
| `06 Code/spacetrack_auth.json` | credentials, already in place |

### Two constraints

1. **Space-Track rate limits** (~30 req/min, 300/hr). Do **not** issue one request per object.
   `GP_HISTORY` takes a comma-separated `NORAD_CAT_ID` list — batch it, and cache to disk so
   re-runs are free.
2. **State the limitation in the output.** `GP_HISTORY` is the *public catalog's* history, so
   it shares the GP side with `detect.py`. It's independent of the SupGP side, of the
   age-binning, and of the persistence logic — but it is **not operator ground truth**. Real
   ground truth needs operator maneuver logs, which aren't public for Starlink. Write that
   caveat in, the same way the "public GP is smoothed around maneuvers by design" one was.

## ⛔ Not in this chunk: the 4 GB SPLID download

[[Kelso Reading - Digest]] §5A settled it, and reading the devkit confirms it: SPLID is
**simulated GEO**, dense 2-hourly osculating elements, EW/NS station-keeping labels. Our
entire input signal is *operator-vs-public-catalog disagreement*, which **does not exist in a
simulated single-trajectory dataset**. `detect.py` cannot ingest SPLID at all.

`06 Code/splid-devkit` (4.2 MB, baselines + `evaluation.py`) is already cloned and is enough
to learn the problem shape. **Leave the 4 GB alone.**

## Done when

The 17 flags have a verdict backed by altitude history, and the top persistent suspects are
split corroborated / contradicted / invisible with counts. Write it up as
`RESULTS - Checked Against History.md`, caveat included.

Then the detector has a number that isn't self-graded — and that's the number that goes in
front of Kelso and Moriba.

```bash
python verify.py --flags      # 2a
python verify.py --top 25     # 2b
```
