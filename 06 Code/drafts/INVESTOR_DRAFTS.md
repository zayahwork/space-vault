# Investor draft artifacts (card 030) — founder's voice, ZERO sends

Written 2026-07-23 (night shift). Three artifacts, per the card: the
two-sentence company one-liner, the intro-request email for warm paths, and
the cold intro email. Checked by `python check_investor_prep.py`.

**Status: ready for founder review, not for sending.** Card 031 (materials
research) is still open — every place its findings belong is marked
`[031-SLOT: …]`. The emails read complete without those slots filled; 031
findings upgrade them, they don't gate them.

**Language:** the approved dated number only (~68–72% vs ~10%, July 22). The
stronger re-measured figure in `RESULTS - Checked Against History` is NOT used
anywhere here — it stays internal until the CTO language ruling lands. Investors in this space do diligence:
every claim below is one the founder can defend document-by-document.
No named third parties — the two field legends and the insurer stay unnamed
until the founder chooses to name them live.

---

## The one-liner (2 sentences)

> I built a system that tells real satellite maneuvers apart from stale
> catalog data using only free public data — checked against 30 days of
> independent orbit history, as of July 22 ~68–72% of its top suspects show a
> real burn signature versus ~10% of matched controls. Operators, insurers,
> and defense all pay for exactly this signal today, and I shipped and
> verified it alone in under two weeks, in public.

*Variant for space-specialist funds (assumes catalog literacy):* "About five
in six apparent maneuvers in the public catalog are just old data. I built the
filter that tells the difference — verified against independent altitude
history (~68–72% of top suspects vs ~10% of matched controls, July 22) — and
I'm turning it into the behavior layer for space traffic."

`[031-SLOT: if 031's materials research lands a sharper market line (TAM
figure, named budget line, comparable exit), it replaces the second sentence
of the main one-liner.]`

---

## Warm intro-request email (founder → the person doing the introducing)

**Use:** field-legend threads, portfolio-company contacts (D-Orbit→Seraphim,
Capella→DCVC, Stoke→NFX), local Seattle network. Short on purpose — the
introducer forwards it; the forwardable blurb is the bottom half.

**Subject:** intro to [FUND]?

Hi [FIRST NAME],

Thank you again for the conversation about the maneuver-detection work — it
genuinely sharpened it. I'm starting to raise a small pre-seed round, and
[FUND] keeps coming up as the right kind of early believer for this. Would you
be comfortable introducing me to [PERSON]? If it's any easier, here's a blurb
you could forward as-is — and if you'd rather not, say so plainly and nothing
changes between us.

Forwardable blurb:

> Zayah is a solo technical founder near Seattle building maneuver detection
> from free public orbit data. Built and verified in under two weeks, in
> public: checked against 30 days of independent altitude history, as of
> July 22 about 68–72% of the system's top suspects show a real,
> independently-checked burn signature versus ~10% of matched controls —
> that's two of his own methods agreeing, not operator ground truth, and he'll
> tell you that himself unprompted. Two of the best-known people in the space
> domain have engaged with the work, and he has an in-person meeting in motion
> on the insurance side. Worth 20 minutes.

`[031-SLOT: one sentence of 031's market sizing goes at the end of the blurb
if it lands a defensible number.]`

Thanks either way,
Zayah

---

## Cold intro email (founder → investor, no intro available)

**Use:** the strong-cold-path rows (Space.VC, Ubiquity, Root, SpaceFund,
E2MC, Boost). Rule from the outreach lane applies here too: reference
something THEY actually said or funded — the placeholder below is a hard stop,
not decoration.

**Subject:** solo founder, verified maneuver detection from public data

Hi [FIRST NAME],

[ONE SENTENCE ON WHY THEM — their portfolio company, essay, or public
statement that makes this their kind of deal. Blank = do not send.]

I'm a solo technical founder near Seattle. Most of what looks like a satellite
maneuver in the public catalog is just stale data — about five in six. I built
the system that tells the difference, using only free public data, and then
checked it against 30 days of independent altitude history: as of July 22,
~68–72% of my top suspects show a real, independently-checked burn signature,
versus ~10% of matched controls. That's two of my own methods agreeing, not
operator ground truth — I'd rather tell you that up front than have it found
in diligence.

Why now: I shipped and verified this in under two weeks, alone, documented in
public. Two of the field's best-known experts have replied and engaged with
the results, and I have an in-person meeting in motion on the insurance side —
underwriters currently price on-orbit risk with launch-era information, and a
behavior feed for the neighborhood around an insured asset doesn't exist yet.
`[031-SLOT: 031's market/materials findings — one sentence, dated — go here.]`

I'm raising a small pre-seed to turn a working detector into that feed. 20
minutes for the worked example — including where it breaks?

Zayah Nelson
[vlog + GitHub links]

---

## Review notes for the founder

- Every number above is the approved July 22 sentence; if the CTO rules the
  new figure in, all three artifacts get the same one-sentence sweep as the
  drafts did.
- The blurb and cold email deliberately under-claim (engaged experts, meeting
  "in motion", no revenue claims). Investors here call references — the story
  has to match what the references say.
- YC is not an email: it's a form, deadline **July 27, 8pm PT** (verified).
  The one-liner above drops into the application's "describe your company"
  box as-is.
