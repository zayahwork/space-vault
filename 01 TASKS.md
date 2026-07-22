# ✅ THE LIST

> [!tip] How to use this
> Work top to bottom. Each task links to a guide with **everything** — addresses, drafts, steps,
> and why it matters. Tick the box, tell Claude when a chunk is done, keep moving.
> (Daily anchors stay the same: 🏋️ lift at 10:00, meals, bed by 22:00.)

---

> [!todo] 🌅 TUESDAY MORNING — in this order, nothing else
> ☕ 7:15 breakfast + Moriba's TED talk (~10 min)
> 💻 7:45 Kelso block — **reading is DONE** ([[Kelso Reading - Digest]]): read the digest (15 min, so you can defend it) → **send the reply** ([[Guide - Kelso Goldmine]]) → inbox sweep (Deidra?)
> 🏋️ 10:00 lift → shower → lunch
> 🔧 12:15 tell Claude: **"let's build the SPLID detector"** — but read finding **A** in the digest first; SupGP may beat SPLID as our validation set

## 🔥 Now (tonight / next work session)

- [x] Send the TraCSS email → [[Guide - Last Two Emails]]
- [x] Send the AMOS message (their contact form) → [[Guide - Last Two Emails]]
- [x] Put your Space-Track login into the auth file (2 min, no one sees it but the script) → [[Guide - First Maneuver Chart]]
- [x] Run the ISS maneuver chart — **✅ FIRST LIGHT: 3/3 maneuvers detected, $0 data** 🛰️ → [[RESULTS - First Charts]]
- [x] Chart 2–3 more satellites — **✅ caught a Starlink mid-deorbit + found v0.1's two blind spots** → [[RESULTS - First Charts]]

- [x] ✅ **CHECKED AGAINST REALITY (2026-07-22).** Top suspects move **11.3x** more than
      satellites we called ordinary; **72%** clear a bar only **11%** of controls clear.
      First number the detector didn't grade itself — **this is the number for Kelso and
      Moriba.** Also caught us publishing a wrong reason for the >500 km gate.
      → [[RESULTS - Checked Against History]]
- [ ] 🕒 **Re-run the detector once a second catalog snapshot is banked** (`python detect.py`
      in `06 Code`). Temporal persistence is built and tested, but it needs **two** snapshots
      with a public catalog saved beside them and we only have one (`2026-07-22/0200Z`). The
      scheduled archiver fetches one every run, so this unblocks itself — just re-run and the
      524 candidates split into *persisted* vs *one-off*. → [[RESULTS - Maneuver vs Stale]]

## 📬 Ongoing (every day, ~15 min, until further notice)

- [ ] **📤 Daily outreach batch — 15 emails** → `python outreach.py` in `06 Code` drafts them and
      keeps the ledger (40 targets seeded: operators, insurers, peers, academics).
      It does NOT send — you find one human per contact route and send it yourself.
      → [[Guide - Daily Outreach]]
- [ ] **📤 Batch 2 — 12 new targets drafted, not sent yet.** Fallback contact (Miga), MIT ARCLab
      (SPLID author), 2 more AMOS competitor-paper authors (Digantara, Kratos), and 6 peer/bench
      companies (LeoLabs, COMSPOC, Vyoma, Neuraspace, Scout, Aerospace Corp, RBC Signals, Stoke
      Space). Find a human per contact form, send, then log with `--sent` → [[Outreach Emails - Batch 2]]
      **Validated 2026-07-21: all 12 routes are live — none are dead.** 10 confirmed by MX
      record or live contact form. 2 (Aerospace Corp #50, RBC Signals #51) return 403 to a
      script but open fine in a browser — do those two by hand. Re-check any time with
      `python contact_check.py --batch2` in `06 Code`; it writes `outreach_validation.jsonl`,
      and `outreach.py` now refuses to draft or send anything that file marks unreachable.
- [ ] Check inbox → reply fast → log it → [[Guide - Handling Replies]]
- [ ] Send the short reply to Moriba + the booking email to his EA Deidra (`team.moriba@outlook.com`) — drafts in [[Guide - Moriba Jah Call]] / chat
- [ ] **Moriba homework (PROMISED — do before the call):** TED talk, ASTRIAGraph, Wayfinder, his articles → checklist in [[Guide - Moriba Jah Call]]

## ⏰ Has a real deadline

- [x] ~~Read the SBIR topic list~~ — **scanned live Jul 21: all 72 open/pre-release topics, ZERO
      from USSF, zero on SDA/maneuver/tracking. Nothing to apply for. Do not sprint for Aug 18.**
      → [[SBIR Scan - 2026-07-21]] / [[Guide - SBIR Steps]]
- [x] ✅ **Un-park trigger is ARMED (2026-07-21).** Windows task **`SBIR Watch`** runs
      `sbir_scan.py --watch` every Monday 8am. Silent when nothing matches; when a USSF topic or an
      SDA/maneuver/tracking topic appears it writes **`🚨 SBIR ALERT - un-park SAM.gov.md`** into
      02 Task Guides. Log: `06 Code/sbir_watch.jsonl`. Nobody has to remember to check.
- [ ] 🪫 **SAM.gov — PARKED 2026-07-21 (founder's call, and it's the right one).** *"If we don't have
      a customer and we don't have any topic to chase, why do it."* Registering means choosing a
      business name, forming an entity, getting an EIN, then 4–6 weeks of validation — all to be
      payable by a program that currently has **zero** topics we could apply to. Nothing downstream
      is blocked. **Un-park the moment either of these is true:** a USSF row shows up in
      `python sbir_scan.py`, or someone asks "can I try it?" → [[Guide - SBIR Steps]]
- [x] ~~Find when the next Open Topic window opens~~ — **not announced anywhere public as of Jul 21.**
      Re-run `python sbir_scan.py` weekly; a USSF row appearing is the signal → [[Guide - SBIR Steps]]
- [ ] *(Only if silent by Jul 30)* one nudge to Moriba → [[Guide - Moriba Jah Call]]

## 🧠 Learn (feeds everything else)

- [x] **💎 Kelso's reading list — DONE.** Both IAC papers + SMOPS keynote read, and we independently analyzed his launch table: **median launch→first-GP delay has more than quadrupled since 2019 (0.65 d → 2.71 d)** → [[Kelso Reading - Digest]]
- [ ] **Read the digest, then send the reply** (it cites our own numbers — own them) → [[Guide - Kelso Goldmine]]
- [ ] **Re-evaluate the launch-ID wedge — it's NARROWER than we thought.** Kelso solved the *cooperative* case in 2017 (RMS-over-orbits assignment, ~1 min for 104 objects). Open case = attribution with **no operator data at all** (Transporter-16 & -17 still "OBJECT A/TBD" today) → [[Kelso Reading - Digest]] §5B
- [ ] **Reality check on our own detector:** public GP data is smoothed *around maneuvers by design* (short fit spans chosen to avoid propagating through them; SP inherits it via eGP). Explains GOES-18 going noise-drunk. Saying this out loud is a credibility asset → [[Kelso Reading - Digest]] §2
- [ ] The 4 orbit concepts you actually need → [[Guide - Orbit Physics Crash Course]]
- [ ] Skim the 4 fresh competitor papers (abstracts are free) → [[Guide - Competitor Papers]]
- [ ] Read what a Phase I proposal contains (so it stops being scary) → [[Guide - SBIR Steps]]

## 🔧 Build (the real prototype)

- [x] **⭐ SupGP archive is LIVE and VALIDATED (Jul 21, 4am).** Scheduled task snapshots **12,645 satellites every 6 hours**, forever (`supgp_archive.py`). Then we tested the premise with `supgp_vs_gp.py`: propagated both orbit sets with SGP4 over 6h and measured the gap. **Median 3.72 km, 90th percentile 16.6 km, max 9,827 km — 6.0% of Starlink over 25 km.** Kelso's published figure is 12.3% on a different day, so our pipeline is correct. **The gap is real and it's huge.**
- [x] **⭐ Separate "maneuvered" from "just stale" — DONE 2026-07-21 (`06 Code/detect.py`).** Age-binned
      baselines: an object is flagged only if its gap is extreme *for its own catalog-age bin*. On
      10,780 Starlink objects, naive gap-ranking surfaces 3,555; age-aware surfaces **541**. **85% of
      the naive list was just old data.** No physics model, nothing tuned → [[RESULTS - Maneuver vs Stale]]
- [x] **Archive hardened + doubled (`supgp_archive.py`).** Retries transient failures (the telesat hole),
      records misses as explicit `null` holes instead of silence, flags a group that halved, writes
      `health.jsonl`, and now captures the **public catalog at the same instant** (`gp_active.csv.gz`) —
      without which no past snapshot can ever be re-analysed properly. Check it: `python supgp_archive.py --health`
- [ ] 🔬 **Verify the suspects against real maneuver records — Tim owns this. THE bottleneck now.**
      541 candidates and no way to check them is not a detector, it's a ranked guess. Start with the
      top ones: 5,337 km and 8,412 km RMS are physically implausible for a burn and are probably
      decaying objects or bad elements → [[RESULTS - Maneuver vs Stale]]
- [ ] 📐 **Sable: the structure question.** Before more detector work — what shape does the data have to
      be in for a claim to be possible at all? Age bins are non-monotonic at 24–48h vs 48–96h (618 vs 45
      objects). Do we need per-constellation baselines, per-altitude, or longer history first?
- [ ] Download SPLID (MIT's answer-key dataset) + run their baseline detector → [[Guide - SPLID Detector]]
- [ ] Study the 2024 winner's solution → [[Guide - SPLID Detector]]
- [ ] Build our own detector, try to beat the baseline → [[Guide - SPLID Detector]]
- [ ] Screenshot every win (these become the pitch) → [[Guide - SPLID Detector]]

## 📣 More outreach (after the above is moving)

- [ ] **💡 "Launch the finding, not the product"** — the launch-delay stat is publishable *now* and needs no working product. **Gated on the Kelso email going out first + telling him we intend to publish + crediting CelesTrak** → [[Launch Playbook (external)]]

- [ ] Friday-style nudges to anyone silent 3+ business days → [[Guide - Handling Replies]]
- [ ] If Brian's email bounced: fallback contact (Patrick Miga) → [[Guide - Handling Replies]]
- [ ] The insurance-industry probe email (the sleeper wedge) → [[Guide - Insurer Probe]]

## 🪫 Parked (not worth fighting right now)

- [ ] Phone ↔ PC Remote Control — feature is in research preview and errored repeatedly ("failed to disconnect: session_url"). Device links fine ("PC" + "pc-snug-hippo" visible on phone), but this session won't attach. Retry after a Claude app update; fallback: start a fresh session on the PC from the phone (vault + memory carry all context anyway).

## 🧭 Strategy (once conversations + prototype exist)

- [ ] Write the 1-page Wedge Memo → [[Guide - Wedge Memo]]
- [ ] Week synthesis: what did we LEARN (not do) → [[Guide - Week Synthesis]]
- [ ] Decide week 2's direction → [[Guide - Week Synthesis]]
- [ ] Platform/infrastructure research — **only after** the prototype gives us real numbers → [[Guide - Platform Question]]

---

> [!note] Scoreboard (the only one that matters)
> 🗣️ People describing their pain unprompted: **1 / 5** (Kelso — USSF tracking weaknesses, unsolved launch-ID, in writing, unprompted) · 💰 "Can I try it?" asks: **0 / 1**
> Emails out: **10 / 10** ✅ · Replies: **2 — Moriba (call door open) + Kelso (full roadmap, same night)**
