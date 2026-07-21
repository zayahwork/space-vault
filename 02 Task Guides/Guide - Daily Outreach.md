# 📬 Guide — Daily Outreach (10–15 a day, without turning into a spammer)

**The machine:** `06 Code/outreach.py` + `06 Code/outreach_targets.csv`.
Forty targets are seeded across five segments. The script drafts the batch and keeps the
ledger; **it does not send.** No mail account is connected here, and a bad send can't be unsent.

```
python outreach.py                      # today's 15 drafts
python outreach.py -n 5 --segment insurer
python outreach.py --sent 3 7 11        # log what actually went out
python outreach.py --replied 7 --note "wants a call"
python outreach.py --status             # the ledger
```

## The 20 minutes this actually takes

1. Run it. You get 15 drafts, each with a **contact route** — a company page, not an address.
2. For each: **find one human.** Ops lead, mission ops, flight dynamics, head of space practice.
   Company team pages, conference speaker lists, paper author lines, X. **Not LinkedIn** — that
   account is banned and using it risks nothing good.
3. Paste, adjust one line so it's obviously not a mailmerge, send.
4. `--sent` the ids. Tomorrow's batch is automatically the next untouched fifteen.

## The rules that keep this from being spam

- **One question, zero pitch.** Every template asks how they do something today. Nobody
  replies to a pitch from a stranger; a fair number reply to being asked about their job.
- **No `info@`.** It converts at roughly zero. If you cannot find a human in two minutes,
  use the contact form and address it to a role ("for whoever runs flight dynamics").
- **Never claim a number we haven't measured.** SupGP-vs-GP is ours and it's real — median
  3.72 km, 90th percentile 16.6 km, 6.0% of Starlink over 25 km. SPLID is partly simulated,
  so it never gets cited as proof of anything.
- **Segments matter.** `partner` and `academic` rows are *peers* — you are learning from them,
  not selling. Sending a sales email to Neuraspace or Vyoma buys a bad reputation in a field
  with about two hundred people in it.
- The `academic` template has a **bracketed line you must replace** with a specific question
  about their actual paper. A generic email to a researcher is a wasted email.

## What counts as progress

Not sends. The scoreboard in [[01 TASKS]] is still: **5 people describing this pain
unprompted, 1 asking "can I try it?"** Fifteen a day is how you get enough at-bats for that
to happen — it is not itself the achievement. If 60 emails produce zero pain descriptions,
the message is wrong and no amount of volume fixes it. Re-read the replies before scaling
further.

## Adding targets

Append rows to `outreach_targets.csv` — `id,segment,company,why_them,contact_route,email,
status,sent_on,notes`. `why_them` is for you: if you can't write a real reason, they're not
a target. Good sources of new names: smallsat conference exhibitor lists, SmallSat Symposium
and AMOS attendee lists, recent launch manifests (who just put birds up = who just acquired
this problem).
