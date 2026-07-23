---
date: 2026-07-22
owner: OUTREACH window (marketing — research + emails)
status: items 1, 3, 4 DONE (~04:00) — item 2 still gated on the founder
---

> [!success] 📨 Marketing → CTO, 2026-07-22 night — VOLUME MODE IS LIVE. Mail is going out.
> Founder said send; sending is on. **5 emails out tonight, 0 failed, all 3 accounts used**,
> 1 dead address auto-caught:
> - #1 Planet (zayahwork), #31 ExoAnalytic (zayahnelson97) — **#31 bounced, retired to `bounced`**
> - #4 Capella (zayahwork), #76 Aerospace/Skinner (zayahnelson97), #67 ESA/Merz (zayahwork1)
>
> **The drip is now autonomous:** the "Outreach Drip" task is repointed from the old
> `C--Space-outreach` tree to **`C:\Space\06 Code`** (our 3-account setup + tonight's queue),
> fires **every 30 min, 08:00–19:00**, jittered so sends scatter through the hour, chasing
> **DailyTarget 45** — the 25/account/day cap is still the hard ceiling. It self-skips weekends
> and off-hours. Randomized-through-the-hour + continuous = exactly the "send, don't stop" order.
>
> **Bug found and fixed in the act:** `--check-bounces` still assumed one account and crashed the
> drip's post-send step; now it checks every inbox (a bounce lands in the sending account's inbox).
>
> ⚠️ **Two things for you:** (1) the drip mutates `outreach_targets.csv` + `outreach_log.jsonl`
> on `C:\Space` every run — those accumulate as uncommitted working-tree changes between sessions;
> that's expected, the files on disk are the source of truth. (2) **Watch all 3 inboxes** (or
> forward the two new ones into the primary) — replies land where the mail left from.

> [!info] 📨 Earlier tonight — VOLUME MODE ARMED (superseded by the LIVE note above)
> Everything below is done. The queue is loaded, the guards are green, three accounts are live.
> **54 rows are machine-sendable right now** and none of them trip the placeholder guard —
> every one renders a real, hand-written email.
>
> **Sending accounts (3, all warmed, passwords stored in [[Credentials - Email Accounts]]):**
> `zayahwork@gmail.com` · `zayahnelson97@gmail.com` · `zayahwork1@gmail.com`. The sender
> **alternates** between them, 25/day each → **75/day ceiling**. Replies land in whichever
> account sent, so those two new inboxes need watching or forwarding into the primary.
>
> **What changed tonight, all merged to master:**
> - Multi-account sending built and tested (`_test_multi_account.py`, all green).
> - 12 contract rows released hold→todo (59–66, 77–79, 83) — the ML-contract + subcontract batch.
> - 13 new hand-written drafts (77–94, 82) so the researchers and companies are sendable
>   without gutting the guard. Full preflight: **0 rows still on a placeholder.**
> - Credentials stored in the vault, gitignored so they never reach GitHub.
>
> **The one thing I did NOT do: press live-send.** Two reasons, both in your interest:
> 1. My standing order is drafts-only; you send. That's the boundary that's kept us safe.
> 2. **Firing all 54 today would hurt reach, not help it.** Freshly-warmed accounts doing a
>    same-day cold blast — several to the same institutions (multiple ESA, GMV-adjacent) — is
>    exactly the *pattern* Gmail flags. The 25/account/day cap and the drip's jitter exist for
>    this. Blasting burns the accounts and the address pool in one night; the drip grows reach
>    without either. **Recommend: enable the drip at a high daily target and let it push near
>    75/day continuously, plus one supervised burst now if you want to see mail move tonight.**
>
> Commands are at the very bottom of this note under **▶ Send controls**.

> [!todo] ⚡ FOUNDER ORDER 2026-07-22 evening — VOLUME MODE, manual, founder at the keyboard
> Sending is authorized NOW, founder supervising live. In this order:
> 1. **Fire today's full sendable queue** via `outreach.py --live`: every addressable open
>    row, target ~25 today, in 2–3 humanized bursts (keep the dice timing) — Gmail-safe,
>    reputation-safe. Named-human rows go first, role inboxes after.
> 2. **The 6 paper-author emails (rows 54–58, 68)**: hand the founder the ready-to-send
>    packet — those go out founder-voiced today.
> 3. **Then straight into card 019** — 20 new named addresses. Volume mode dies without
>    supply; this is the real bottleneck, treat it as today's main work.
> 4. Standing: reply-watch stays hot; nudges fire on their dated windows (day-1 = Jul 23).
> RULES UNCHANGED: no LinkedIn, no invented addresses, honest caveat in every mail, retired
> numbers never. The autonomous loops still NEVER send — live sends happen only in this
> supervised mode or the scheduled drip.

> [!warning] 🚪 Workspace rule (standing)
> Work ONLY in this folder, on your own branch. Never run git commands against other
> branches, never merge or pull master unless the CTO note tells you to, and never open
> files outside your lane. Facts you need from elsewhere arrive in THIS note — if something
> is missing, say BLOCKED and stop; the CTO will supply it.


> [!todo] ⚡ CTO orders — 2026-07-22 (day plan, grilled with the founder — these supersede everything below)
> The pipe is live and has sent real mail (five sends logged 02:35, message-IDs in
> `outreach_log.jsonl`). Today, in this order:
>
> 1. **The Heldreth email goes out TODAY.** Melissa Heldreth, Gallagher US space practice
>    director, Seattle. Founder-approved this morning. Spec: **5–7 sentences, no
>    attachment**, from Zayah's address via the live pipe. Lead with the verified number
>    (below). One sentence that a "went-quiet" health signal for insured GEO fleets comes
>    online next week. Coffee ask, Seattle-local framing, and **steer the dates**: offer
>    Jul 30 / Jul 31 / Aug 1 explicitly ("slammed until the 30th") so an early acceptance
>    can't land before the capability unlocks. Log it, add the CSV row. The
>    [[Insurer Target List]] one-pager becomes the **meeting leave-behind** — keep building
>    it in parallel, it does NOT ride along as an attachment.
> 2. **Book the Moriba Jah call this week.** Email his EA Deidra (`team.moriba@outlook.com`)
>    today with 2–3 concrete slots. Prep doc already exists
>    ([[Idea - Moriba Call Question Prep]]).
> 3. **Kelso reply stays armed.** Fires the moment the founder says "go" (he's reading
>    [[Kelso Reading - Digest]] today). Update the draft's numbers per the language rule
>    below before it fires.
> 4. **Drip continues** on the rewritten drafts. Reply-watch stays hot — a reply gets
>    answered in minutes.
>
> **Language rule, effective now: the 11.3× multiple is RETIRED** (it swung to 23.8×
> between snapshots). The number we quote is **"~68–72% of our top suspects show a real,
> independently-checked burn signature, against ~10% of matched controls."** Sweep every
> unsent draft and the Kelso reply for 11.3× / 72%-vs-11% phrasing and replace it. The
> honest caveat (two of our own methods agreeing, not operator ground truth) stays,
> verbatim. Randy is building operator ground truth this week (issue 004) — soon we get to
> upgrade the caveat itself.

> [!done] Progress — 2026-07-22 ~04:00
> 1. ✅ **All 16 unsent drafts rewritten around the number** — every one leads with "built
>    and checked" and carries 11.3× / 72%-vs-11% plus the honest caveat, verbatim. That's the
>    12 drip targets (`drafts/1…31.txt`) and the 4 form-blocked batch-2 ones (44, 49, 50, 51).
>    The **drip stays DISABLED** until the founder clears the new text
>    (`Enable-ScheduledTask "Outreach Drip"` turns it back on).
>    Already gone with the old "I'm building" pitch and unrecallable: Miga + the 7 sent 02:30.
> 2. ⏳ Kelso reply — still gated on the founder reading [[Kelso Reading - Digest]].
> 3. ✅ Insurer names researched → [[Insurer Target List]]. Headline: **Melissa Heldreth**,
>    Gallagher's new US space practice director, is **in Seattle**. Also Kunstadter (AXA XL,
>    already bought SSA data once via SpaceAble) and Wade (Atrium/ASIC). **No one emailed.**
> 4. ✅ Launch-delay publication prepped → [[Publish - Launch Delay Finding]]: 7-post thread
>    drafted, chart generated (`06 Code/output/launch_delay.png`, CelesTrak credited on the
>    image), numbers re-verified fresh (0.65 → 2.71 d, 4.2×). Still gated on #2, by design.

> [!todo] ⚡ CTO update ~04:30 — good work on 1/3/4. New orders while the drip is held
> **The hold stays** — and there's a second reason beyond the founder clearing the new text:
> the 10 **day-1** emails were sent by hand and never logged, so your dedupe guard can't see
> them. **That reconciliation is YOUR job now** (lanes clarified: only you touch emails).
> Dig through [[Outreach Emails]], [[Guide - Last Two Emails]], and the 99 Archive day files;
> match the 10 day-1 recipients to their `outreach_targets.csv` ids; produce the list plus one
> ready-to-run `python outreach.py --sent <ids> --note "day-1 manual send"` command. **Don't
> run it** — the founder confirms against his Gmail Sent folder first. Then the drip can come
> back on. **Send nothing until both gates clear.**
>
> Meanwhile, in order (reconciliation first, then):
> 1. **Reply watch.** 8 emails went out tonight. Prep [[Guide - Handling Replies]]-style
>    response drafts for the likeliest repliers (Miga first — warm referral), so a reply gets
>    answered in minutes, not hours.
> 2. **Deepen the insurer file.** Melissa Heldreth being in Seattle is the single most
>    actionable fact in [[Insurer Target List]] — the founder can meet her in person. Build a
>    one-pager: her background, what Gallagher's space practice covers, what she's said
>    publicly, and the natural warm path to her. **Still no emailing insurers.**
> 3. **Nudge queue.** Anyone from day-1 silent 3+ business days gets a Friday-style nudge
>    drafted (not sent) — but only after the day-1 reconciliation lands, so we know who
>    actually got mail.

> [!info] 📨 Marketing → CTO report, ~05:00 (on master as 0bbd44a so you can see it)
> **Delivered since your 04:30 orders, founder-directed:** name hunt across all 12 queued
> targets. **5 now address a real person** — Planet: James Mason (Chief Space Officer,
> co-author of their own differential-drag papers; the greeting cites them); Capella:
> Christopher Gehant (VP Constellation Ops); Sidus: John Curry (CMOO, ex-NASA flight
> director); D-Orbit: Andrea Testore (Head of Service Ops); ExoAnalytic: Bill Therien (CTO,
> found via their AMOS 2022 paper — pulled the PDF, no author emails published). The other 7
> are documented dead ends (nothing published anywhere; Loft's flight-dynamics lead left).
> Names, not addresses — no pattern-guessing after the Williams bounce — so all five route
> through the role inboxes with a named routing line. Everything recorded in the CSV notes.
>
> **Your order #0, day-1 reconciliation — DONE, awaiting founder confirmation:**
>
> | day-1 email | CSV row | state |
> |---|---|---|
> | 3 — Moriba Jah | **#36** | blocked `hand-contacted` (live thread — he replied) |
> | 7 — TraCSS | **#40** | blocked `hand-contacted` |
> | 9 — T.S. Kelso | **#38** | blocked `hand-contacted` (live thread — he replied) |
> | 6 — B. Williams, Slingshot | — | bounced day-1; fallback #41 Miga already sent 02:15 |
> | 1 UW Morgansen · 2 Starfish · 4 Kayhan · 5 Xplore · 8 WA Space Grant · 10 AMOS | none | **no CSV rows exist → zero machine re-email risk** |
>
> The three CSV-resident rows are already status-blocked, so the machine physically cannot
> template them even before logging. Ready to run **only after the founder confirms against
> his Gmail Sent folder**:
> `python outreach.py --sent 36 38 40 --note "day-1 manual send, reconciled 2026-07-22"`
> The six no-row recipients need no CSV action; their record lives in [[Outreach Emails]].
>
> **Not started yet, in your priority order:** (1) reply-watch drafts, Miga first;
> (2) the Heldreth one-pager; (3) nudge queue — which correctly waits on this reconciliation.
> Gates respected: drip disabled, nothing sent since the 8 at 02:30, bounce checks clean.

> [!info] 📨 Marketing → CTO report, 2026-07-22 evening (branch `mark`, 3 new commits)
> **1. Card 017 is done and machine-checked.** `06 Code/reply_watch/` holds **16 reply drafts,
> 16 nudge drafts and a STATUS.md** covering every in-flight contact; `python
> check_reply_watch.py` passes clean. Replies cover both live threads (Jah, Kelso), all eight
> batch-2 sends, the five routed-but-unsent named contacts (Mason, Gehant, Curry, Testore,
> Therien) and Heldreth — each with a posture note (do **not** sell to Vyoma or Neuraspace;
> don't pose as a buyer to LeoLabs or Digantara; a student replying for Linares *is* the
> reply). Nudges are dated to when the window actually opens: **2026-07-23** for day-1,
> **2026-07-28** for batch 2. Slingshot is not a nudge — that address bounced, nothing was
> ever delivered, so the file documents the re-route and says do not resend. **Zero sends.**
>
> **2. The retired number was still live in the send queue.** All 16 queued outreach drafts
> still carried the 11.3× / 72%-vs-11% phrasing. Re-enabling the drip would have mailed
> retired numbers to real people. Swept: one sentence replaced per file, sixteen files,
> nothing else touched, subjects and paragraph structure verified intact afterwards.
>
> **3. Six paper-author emails written, after actually reading the six papers.** Rows 54–58
> and 68 were deliberately unsendable (the academic placeholder guard). I pulled all six PDFs
> from the ESA proceedings and wrote each email around a specific claim in the recipient's own
> paper — Lim/Colombo's "you can't get the epoch from TLEs" conclusion is our staleness finding
> from the other side; Raviola's no-labels showstopper is our no-labels problem; Siminski
> reports a measured false-positive rate, so he gets asked whether our ~10% control base rate
> can stand in for a calibrated statistic; GMV's own future-work list asks for real low-thrust
> data, which we have and offered free; Indra gets asked whether "no external catalogue" is
> accuracy or sovereignty. **Correction:** row 68's paper title was wrong in the CSV — SDC6
> paper 171 is tracklet association from the ZimSMART survey, not conjunction-analysis
> manoeuvre detection. Row fixed, email written to the real paper.
>
> **Two things for you.** (a) `outreach.py` drafts now understand a `Cc:` header — Prof.
> Colombo sees the email to her doctoral researcher — and an unknown draft header is now a
> hard stop rather than a silent drop. (b) `reply_watch/` was **outside this lane's
> sparse-checkout**, sitting untracked and one `sparse-checkout reapply` from deletion; I added
> the two paths to the lane. Nothing sent, no branch touched but `mark`.

# 📣 NEXT — marketing

> [!warning] Everything you've drafted is now out of date — in a good way
> As of tonight the detector has a **verified number**: **~68–72% of our top suspects show a
> real burn signature against ~10% of matched controls** (replicated on two snapshots; the
> old 11.3× multiple is retired — see the CTO orders above).
> Checked with a completely separate method on 30 days of altitude history.
> → [[RESULTS - Checked Against History]]
>
> Every draft currently says some version of *"I'm building."* We can now say *"I built it,
> I checked it, here's the number."* That is a different email.

## 1. Rewrite the pitch around the number (do this before sending anything else)

11 batch-2 drafts are queued and one has already gone out (Miga, 02:15). **Hold the remaining
11** until they carry the number.

The old pitch was a claim. The new one is evidence:

> *"Most of what looks like a maneuver is just old data — we can tell the difference from free
> public data. Checked against 30 days of altitude history: ~68–72% of our top candidates show
> a real burn signature, against ~10% of matched controls."*

Keep it short and keep the caveat honest — this is two of our own methods agreeing, not
operator ground truth. Saying that out loud has earned us credibility twice already.

## 2. The Kelso reply — add the number

The draft in [[Guide - Kelso Goldmine]] is ready and gated on the founder reading
[[Kelso Reading - Digest]]. When it goes, it should mention the verified rate (~68–72% vs
~10%) and specifically **the control group** — Kelso is exactly the person who will notice
that we bothered to run one,
and exactly the person who'd have asked "compared to what?"

Also worth telling him: we caught ourselves publishing a wrong reason for the >500 km gate and
corrected it. He values that more than a clean result.

## 3. Research job — name the insurers

[[Pricing - What to Charge and Who]] says the insurer market is "a handful of Lloyd's
syndicates and specialists." That's not actionable. Find the actual names: who underwrites
satellites, who the brokers are (Marsh, Gallagher, and whoever else), and which have publicly
said anything about on-orbit risk or in-orbit data.

Small market, so **do not email any of them yet** — [[Guide - Insurer Probe]] is a later move
and every conversation counts. This is a target list, not a send list.

## 4. Publishable now — the launch-delay finding

[[Launch Playbook (external)]]: the median launch→first-GP delay quadrupling since 2019 needs
no working product and is publishable today. Still gated on the Kelso email going out first,
telling him we intend to publish, and crediting CelesTrak. Prep it so it's ready the moment
that gate clears.

## Standing rules

- Real mail now leaves this machine. Anything going to a new batch gets seen before it fires.
- No LinkedIn — email, X, contact forms, and paper-author addresses only.
- #51 RBC Signals blocks scripts; browser-only, by hand. (#50 Aerospace is now covered by #76
  Skinner — real address — so it's marked duplicate.)

---

## ▶ Send controls (run these in `C:\Space\06 Code`)

**See exactly what would go out — sends nothing:**
```
python outreach.py --send -n 6 --mix
```

**Supervised live burst now (recommended: 6, watch it, then repeat):**
```
python outreach.py --send --live -n 6 --mix
```
`--mix` rotates segments so it's never six ESA authors in a row. Named-human rows go first by
design. The 25/account/day cap and the alternation across the 3 accounts are automatic — you
cannot exceed 75/day even by re-running.

**Continuous volume — the drip (this is how you "send like crazy" safely):**
```
Get-ScheduledTask "Outreach Drip"                              # is it on / pointed at C:\Space?
Enable-ScheduledTask "Outreach Drip"                           # turn autonomous sending on
# raise the daily target from 8 toward the cap now that there are 3 accounts + real supply:
#   the task's argument is -DailyTarget N  (edit the scheduled task, or run drip.ps1 -DailyTarget 40)
powershell -File drip.ps1 -DailyTarget 40 -NoJitter -DryRun    # preview one catch-up run
```

**Ramp recommendation, so reach grows instead of the accounts dying:**
- Tonight: one or two supervised bursts of 6 (≈12), just to confirm deliverability on all 3 accounts.
- Then enable the drip at `-DailyTarget 40` and let it climb. If bounces stay near zero and
  nothing lands in spam over 2–3 days, raise toward 70.
- Watch all three inboxes (or forward the two new ones into the primary) — replies are the scoreboard.

---

## -> CTO report — night shift 4, 2026-07-23 (card 032)

**(a) Completed:** Card 032 — traffic channel strategy, everything drafted, nothing posted. `Channel Plan - Traffic Beyond Cold Email.md` (vault root), machine-checked by the new `check_channel_plan.py` (test-first, red → green; all five existing loops re-run green). **Kept 4:** (1) X/Twitter technical presence — 2–3 posts/week to start, small checkable findings only, first post is the STARLINK-3200 deorbit picture (chart already exists); (2) published findings as citable posts — first post drafted: the matched-control verification method write-up, the canonical URL everything else links; (3) vlog cross-promotion — standing end-card + description link block drafted, ~10 min/episode; (4) one timed HN Show-HN — title + first comment pre-drafted, fires earliest week 2 with the founder at the keyboard, only after citable post #1 is live. **Killed Reddit/forums with reasons** (enthusiast-scale or wrong-culture audiences, mod hostility to builder posts, the CelesTrak community overlaps a live email relationship we won't risk, and three-forum sustained presence is a solo-founder overcommitment). All drafts carry the approved dated ~68–72% sentence + verbatim caveat where a rate is quoted; the linter mechanically bans the retired multiple, the unruled re-measured figure, named people in post blocks, and enforces both gates as required phrases — **nothing posts without founder approval, and the launch-delay thread stays gated on the Kelso reply.** Zero sends, zero posts.

**(b) Recommended next move — the queue is now effectively empty for my lane, and that's the finding:**
1. **YC deadline is now inside 4 days (July 27, 8pm PT)** — unchanged from last night's report but one day closer. Still the only expiring item on the board; needs the founder's yes/no before Monday.
2. **Only 028 and 029 remain open, and both are stuck on the same two CTO actions:** 028 needs your re-scope ruling (the NEXT note says the 3-account engine + drip already shipped from `C:\Space` — the card as written looks overtaken by events; last two reports flagged this, no ruling yet), and 029 is blocked by 028 **and** by the pending 96-vs-11 language ruling. One CTO pass — re-scope/close 028, rule on the number — unblocks the entire remaining lane in one stroke, and 029 matters: the drip is live and will eventually reach the 33 template-only rows still carrying the pre-verification pitch. If you want my vote: close 028 as shipped (fold any residue — warm-ramp caps, `founder_approved` batch flags — into a new small card), rule the number, and let me take 029 next shift.
3. After that, the natural sequence stays: fold 031's findings + `CHECK`-row verification into the investor pack, then the channel plan's week-1 items go to the founder for approval (they're drafted and waiting).

**(c) Blocked on:** nothing for this card. For the lane: everything open is behind the two CTO rulings above — without them my next shift has NO qualifying card. Housekeeping: sparse-checkout gained `/Channel Plan*` and the new linter path (via `--stdin`, per the banked Git-Bash lesson).

---

## -> CTO report — night shift 3, 2026-07-23 (card 030)

**(a) Completed:** Card 030 (priority 1, per your order) — investor warm outreach prep, everything drafted, nothing sent. Two artifacts, both machine-checked by the new `check_investor_prep.py` (test-first, red → green): **(1) `Investor Target List.md`** at vault root — 25 named rows (10 space-specialist funds, 12 deep-tech funds with space deals on record, 3 Seattle-local), each with fund / person / stage / why-them / warm path / cold path / confidence flag; documented dead ends included (Countdown Capital wound down 2024; competitor-strategic VCs parked with reasoning). Warm paths mapped to threads we actually have: D-Orbit→Seraphim, Capella→DCVC, Stoke→NFX, the Seattle cluster, and the two field legends — whom I explicitly recommend NOT spending on a fundraise ask yet. **(2) `06 Code/drafts/INVESTOR_DRAFTS.md`** — the 2-sentence one-liner, the warm intro-request email with a forwardable blurb, and the cold intro email, all in the founder's voice, all on the approved dated ~68–72% language with the verbatim caveat (the linter bans the unruled re-measured figure from these files entirely). Card 031's findings drop into marked `[031-SLOT]`s — the drafts read complete without them, so 031 upgrades rather than gates. All existing loops still green. Zero sends.

**(b) Recommended next move — one thing has a hard clock:**
1. **YC Fall 2026 applications close July 27, 8:00pm PT — that is FOUR DAYS from now.** Verified live tonight from ycombinator.com/apply (urllib; `06 Code/_fetch_yc_deadline.py` shows the method): decisions by Aug 28, they fund on acceptance, $500k standard deal, and applying costs ~30 founder-minutes plus an optional 1-minute video. The one-liner in INVESTOR_DRAFTS drops straight into the application. Whatever else is queued, **the founder needs to make the yes/no on YC before Monday** — it's the only item on the entire investor map that expires this week, and a filed application loses nothing even if the round strategy changes. Recommend you put this at the top of the next founder sync.
2. Second: today (Jul 23) is the day-1 nudge window from reply_watch — those 7 dated nudge drafts are ready and founder-sendable. Third: the `CHECK`-confidence rows in the target list need a verification pass (people move funds) before any investor mail; that plus folding in 031's findings is the natural next investor card.

**(c) Blocked on:** nothing for this card. Notes: card 031 hasn't landed (slots are marked and waiting); the CTO number ruling (96-vs-11) is still pending and investor drafts deliberately stay on the approved sentence until it lands — investor diligence makes stale-vs-ruled language matter even more here than in outreach. Housekeeping: this lane's sparse-checkout gained the three new paths (target list, linter, fetch script) — heads-up that Git-Bash mangles leading-slash `sparse-checkout add` args on Windows (MSYS path conversion writes `C:/Program Files/Git/...` garbage patterns); the reliable form is `git sparse-checkout set --stdin < patterns.txt`. The mangled entries were cleaned out; `sparse-checkout list` verifies clean.

---

## -> CTO report — night shift 2, 2026-07-22 (card 023)

**(a) Completed:** Card 023 — `06 Code/drafts/SEGMENT_NOTES.md`: per-segment value language for all 7 segments actually in rotation (the card named "launch-adjacent"; no such rows exist — `contract` and `competitor` do, so those got notes). Each segment: pain in their words, dated verified number, caveat at their sophistication, one ask. Test-first via a new linter `check_segment_notes.py` (red → green) that enforces the language rules mechanically: no retired multiple, GEO only via the external-safe sentence, no named people, dated number + caveat + single ask per section. All existing loops still green (`check_reply_watch`, competitor-template test, multi-account test). Audited all 78 queued rows against the notes; mismatches **listed, not rewritten**, in the notes' audit section. Zero sends.

**(b) Recommended next move — two things, the first is urgent:**
1. **You need to rule on the number, tonight if possible.** `RESULTS - Checked Against History` re-measured the headline late today (issue 003): 68–72% was scored before the forward window existed and is struck as an underestimate — the settled value is **96% vs 11%**. Meanwhile the drip is LIVE and every queued draft plus my new segment notes quote the approved 68–72% sentence. We are currently mailing real people a number our own results page has struck. Underselling, not overselling — but it's stale language going out at volume, and the fix is one language rule from you plus a one-sentence sweep (same shape as the 11.3× retirement, ~30 min of work once ruled). I did NOT switch anything to 96% unilaterally.
2. **The audit's headline finding: 33 of 78 queued rows are template-only, and the `outreach.py` segment templates still carry the pre-verification "I'm trying to learn" pitch with no number at all** (operator 15, insurer 7, partner 8, gov 5 — ids in the notes). Every hand draft was swept onto the new number; the templates never were. Once the drip exhausts the hand-drafted tier it starts sending the old pitch. Recommend a card: rewrite the 6 segment templates around the (post-ruling) number using SEGMENT_NOTES.md as the spec — cheap, high-leverage, and it should land before the drip reaches the template tier. Smaller items also listed in the audit: #23 lacks the verified rate its founder-approved spec requires; contract #59–66 are undated/weak-caveat (one sentence each).

**(c) Blocked on:** nothing for this card. Card 028 (three-account engine) I deliberately did not take: its done-when starts with founder-supplied app passwords in `gmail_auth.json`, and the NEXT note above says the 3-account engine + drip already shipped on master from `C:\Space` — 028 looks partially overtaken by events; needs a CTO pass to re-scope or close before anyone burns a night on it.

---

## -> CTO report — night shift, 2026-07-22 (card 026)

**(a) Completed:** Card 026 — the `competitor` segment is now sendable. Added an honest `competitor` template to `outreach.py` (posture straight from `reply_watch/replies/43-digantara.md`: one engineer on free data, "I'm not a customer, and I'm not going to pretend to be one", asking where the method breaks). Chose template over retiring the segment: re-tagging to `partner` would have mailed competitors a "comparing notes" email that hides who we are. Test-first via new `_test_competitor_template.py` (was red, now green); `_test_multi_account.py` and `check_reply_watch.py` still green; `--send --ids 82` renders in a dry run. Zero sends.

**(b) Recommended next move:** **Card 023 (per-segment value notes) before any more supply work.** The queue has 54 machine-sendable rows and a 75/day ceiling, so supply is no longer the bottleneck — conversion is. Once the founder flips the drip on, every generic-template send is a spent contact; the segment value-prop pass is the last cheap chance to raise reply rate across the whole queue before it burns. It also audits queued drafts for segment mismatches — exactly what we want caught before volume mode, not after. After 023, the next supply batch can draw from the 134 benched addresses documented on card 019.

**(c) Blocked on:** nothing for my lane. Two founder-side items worth flagging: live-send remains founder-only (correct), and the two new inboxes still need forwarding/watching or replies to zayahnelson97/zayahwork1 will sit unseen.
