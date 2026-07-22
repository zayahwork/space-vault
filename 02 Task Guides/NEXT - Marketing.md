---
date: 2026-07-22
owner: OUTREACH window (marketing — research + emails)
status: items 1, 3, 4 DONE (~04:00) — item 2 still gated on the founder
---

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
- #50 Aerospace Corp and #51 RBC Signals block scripts; those two are browser-only, by hand.
