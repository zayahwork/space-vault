---
status: done
type: AFK
owner: Tim (tech)
blocked-by: []
closed: 2026-07-22
closed-by: tim
---
# Make the lag-aware verify window the production default

**Goal:** the referee's winning configuration (altitude observable + lag-aware **asymmetric −3/+14 day** window, 13/14 documented maneuvers, 5/6 double-sourced) becomes what the live pipeline actually runs — not a harness-only result.

**Corrected from the first draft of this card:** the window is one-sided (3 days before, 14 after), not a symmetric ±10 or ±14. Catalog lateness runs one way; a symmetric window credits two of the documented dockings with inclination steps landing 12.3 days *before* the event. And ±10 is one day short of Intelsat 33e's +10.98-day step.

**Done when:** `verify.py` (and `verify_geo.py` where it stays in use) take the window from measured per-fleet catalog lag instead of a hardcoded ±3 days, with the lag measurement and chosen window printed in the output and stamped in provenance; the full verify pass is re-run on all four fleets with the new window; `RESULTS - Checked Against History.md` and `RESULTS - Beyond Starlink.md` get the re-measured numbers (if the headline ~68–72% vs ~10% moves, say so in bold — do not quietly keep the old figure); and a regression test covers the window derivation.

**Notes:** consider the asymmetric window (−3/+14 days) from the deleted duplicate card — catalog lag is one-sided, so the window should be too. Referee evidence in `06 Code/output/referee_015.json` and the 015 card. Watch the false-positive side: a wider window catches more real maneuvers but also more coincidences — report the control group's rate under the new window right next to the suspects', same discipline as always. The GEO 1.0 km floor stays flagged as unvalidated.

---

## ✅ Closed 2026-07-22 — shipped, and **currently inert by design**

`verify.py` owns one regime-keyed window table; `verify_geo.py` reads it rather than
keeping a private copy (that duplication is how the two verifiers silently disagreed
before). Both step-finders take `(before_days, after_days)`; a single positional argument
still means symmetric, so no existing caller changed meaning.

| regime | window | basis printed at runtime |
|---|---|---|
| LEO | −3 / +3 d | unchanged; measured Starlink update interval median **0.27 d** (n=2,701) |
| GEO | **−3 / +14 d** | documented lag up to **+10.98 d** (Intelsat 33e, issue 015) |
| MEO · mixed | −3 / +14 d | **UNVALIDATED** — no MEO ground truth, labelled as a judgement |

**The finding that mattered more than the constant.** A forward-looking window can only be
evaluated in retrospect. The newest snapshot is 2 hours old, so **0.08 d of the +14 d reach
has been published**. Recomputed across all 80 cached objects, the old ±3 d and the new
−3/+14 d give **identical steps on 80 of 80** — this change moves nothing today and cannot.
Every run now prints `** PROVISIONAL: only 0.08 d of the +14 d forward reach has been
published yet **` and how long until it settles, so the widened reach can never be quoted
as if it had already been observed.

**Four fleets re-run.** Starlink 375× / 100% vs 12%; OneWeb 60.3× / 100% vs 0%; Intelsat
1.1× / 50% vs 25% (n=2); SES 21.8× / 50% vs 13% (n=4). Control rates printed beside
suspects' throughout, as required.

**SES moved and I am not claiming it.** It read *NO SIGNAL* before and separates now — but
the two windows are provably identical on this data, so the cause is the archive and the
suspect list (4 vs 15 now, 3 vs 3 then), not this change. Recorded in
`RESULTS - Beyond Starlink.md` as a thing to chase, not a result.

**Headline check:** LEO numbers unchanged, by construction and verified 80/80.
`RESULTS - Checked Against History.md` says so explicitly rather than staying silent.

Regression: `_test_verify_window.py`, 31 cases. `_test_referee.py`'s "shipped window is
3.0" assertion was **updated deliberately, not deleted** — it now asserts the shipped GEO
window is the referee's winning −3/+14d and that both verifiers read the same table.

Spotted and filed rather than fixed here: issue **026** — ground truth grew to 17 scoreable
GEO rows, so 015's x/14 needs re-scoring.
