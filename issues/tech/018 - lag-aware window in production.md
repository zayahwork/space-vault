---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Make the lag-aware verify window the production default

> [!warning] Duplicate card number — two 018s exist
> `018 - lag-aware GEO verify window.md` covers the same follow-up, filed independently in
> the same window. Zayah to pick one and renumber or close the other; I have corrected the
> spec in both rather than silently deleting either.

**Goal:** the referee's winning configuration (altitude observable + lag-aware **asymmetric −3/+14 day** window, 13/14 documented maneuvers, 5/6 double-sourced) becomes what the live pipeline actually runs — not a harness-only result.

**Corrected from the first draft of this card:** the window is one-sided (3 days before, 14 after), not a symmetric ±10 or ±14. Catalog lateness runs one way; a symmetric window credits two of the documented dockings with inclination steps landing 12.3 days *before* the event. And ±10 is one day short of Intelsat 33e's +10.98-day step.

**Done when:** `verify.py` (and `verify_geo.py` where it stays in use) take the window from measured per-fleet catalog lag instead of a hardcoded ±3 days, with the lag measurement and chosen window printed in the output and stamped in provenance; the full verify pass is re-run on all four fleets with the new window; `RESULTS - Checked Against History.md` and `RESULTS - Beyond Starlink.md` get the re-measured numbers (if the headline ~68–72% vs ~10% moves, say so in bold — do not quietly keep the old figure); and a regression test covers the window derivation.

**Notes:** referee evidence in `06 Code/output/referee_015.json` and the 015 card. Watch the false-positive side: a wider window catches more real maneuvers but also more coincidences — report the control group's rate under the new window right next to the suspects', same discipline as always. The GEO 1.0 km floor stays flagged as unvalidated.
