---
status: open
type: AFK
owner: Tim (tech)
blocked-by: []
---
# Make the lag-aware verify window the production default

**Goal:** the referee's winning configuration (altitude observable + lag-aware ±10-day window, 12/14 documented maneuvers) becomes what the live pipeline actually runs — not a harness-only result.

**Done when:** `verify.py` (and `verify_geo.py` where it stays in use) take the window from measured per-fleet catalog lag instead of a hardcoded ±3 days, with the lag measurement and chosen window printed in the output and stamped in provenance; the full verify pass is re-run on all four fleets with the new window; `RESULTS - Checked Against History.md` and `RESULTS - Beyond Starlink.md` get the re-measured numbers (if the headline ~68–72% vs ~10% moves, say so in bold — do not quietly keep the old figure); and a regression test covers the window derivation.

**Notes:** consider the asymmetric window (−3/+14 days) from the deleted duplicate card — catalog lag is one-sided, so the window should be too. Referee evidence in `06 Code/output/referee_015.json` and the 015 card. Watch the false-positive side: a wider window catches more real maneuvers but also more coincidences — report the control group's rate under the new window right next to the suspects', same discipline as always. The GEO 1.0 km floor stays flagged as unvalidated.
