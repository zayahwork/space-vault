# 📬 Guide — Daily Outreach (10–15 a day, without turning into a spammer)

**The machine:** `06 Code/outreach.py` + `06 Code/outreach_targets.csv` + `06 Code/drafts/`.
Fifty-two targets across six segments. The script drafts the batch, keeps the ledger, and
**can now send** — but only with `--live`, and only once `gmail_auth.json` exists.

```
python outreach.py                      # today's 15 drafts
python outreach.py -n 5 --segment insurer
python outreach.py --send               # dry run: exactly what would go out
python outreach.py --send --live        # actually send, log, mark sent
python outreach.py --sent 3 7 11        # log what went out by hand
python outreach.py --replied 7 --note "wants a call"
python outreach.py --status             # the ledger
```

## Two kinds of email: template vs hand-written

The five segment templates are the *cold* path — fine for fifteen unknown rows a day.
But the targets worth the most are the ones where a real reason to write exists: the author
of a paper we lean on, the person whose dataset we used as an answer key. Those get written
by hand as `06 Code/drafts/<id>.txt`:

```
Subject: your low-latency maneuver paper — something I stumbled into
Attach: output/starlink_deorbit_detected.png

Patrick,
...
```

`Attach:` is optional and repeatable; paths are relative to `06 Code`. **Don't repeat the
signature** — the script appends it. If a draft file exists for a row, it wins over the
segment template everywhere: preview, dry run, and send. All twelve batch-2 emails now live
here, so they send as written instead of silently reverting to generic text.

## The drip (automatic, since 2026-07-22)

Scheduled task **"Outreach Drip"** runs `06 Code/drip.ps1` every hour from 8am to 7pm.
Each run sends **at most 2**, then checks for bounces. Nothing runs overnight on purpose:
mail that arrives at 3am is buried under the 9am pile, and nobody is awake to notice a misfire.

**It doesn't actually send on the hour** (since 2026-07-22). The scheduler can only fire on an
exact interval, and mail leaving at 08:00:04, 09:00:04, 10:00:04 — two at a time, twenty seconds
apart, every day — reads as a machine to anyone who looks at the headers, and Gmail looks. So
each run rolls dice before it does anything:

| dice | effect |
|---|---|
| wait `0–25 min` | the send lands somewhere inside the hour, not at the top of it |
| `20%` skip | one run in five sends nothing, so there are natural quiet gaps |
| `1 or 2` emails | not always the same number |
| `35–95s` between sends | not a metronome |

Weekends are skipped (`-Weekends` overrides), and a jitter roll that would land after 7pm is
dropped rather than sent late. `-NoJitter` fires immediately, for when you're running it by hand.

### It chases a daily number, not a per-run number (since 2026-07-22)

`-DailyTarget` is **12**. Each run asks *"given the time of day, how far behind are we?"* and
sends that much, up to 3 in one burst:

- **behind pace** → catch up
- **on pace** → usually nothing, sometimes one, so the rhythm stays uneven
- the **25/day cap is still the law** and still counted from the audit log

A fixed 1–2 per run either misses the target or overshoots, because runs get skipped and the
sendable pool moves under us. Chasing the number means the day lands near 12 while still
looking nothing like a scheduler — bursty early, quiet mid-afternoon, a straggler at five.

### What runs without anyone touching it

| Every run | What it does |
|---|---|
| **Preflight** | Refuses to run at all if `gmail_auth.json` is missing from the tree it's in, and says so in the log — silent credential failure used to look identical to a quiet day |
| **Low-queue alarm** | Logs `LOW QUEUE` when fewer than 5 rows are sendable. An empty queue is the failure nobody notices: the drip keeps running and mails nobody |
| **Pacing** | Reads the audit log (`--count-today`), compares to where it should be for the hour, sends the difference |
| **Jitter / skip / weekend / after-hours** | As above |
| **Segment rotation** | `--mix` |
| **Bounce sweep** | `--check-bounces` after every run; dead addresses are parked, never retried |
| **Ledger** | Status, date and Message-ID written per send, after each one, so a crash can't lose the record |

**Target is 8/day**, not 12 — that's what the queue can feed
([[Volume Pass - What the Drip Can Actually Reach]]). Raise `-DailyTarget` when inventory does.

> [!warning] The one thing that is NOT automatic
> The **"Outreach Drip" scheduled task still points at a different worktree**, so none of the
> above is live until it points at the merged tree. After merging to `C:\Space`:
>
> ```
> $t = Get-ScheduledTask "Outreach Drip"
> $t.Actions[0].Arguments = '-NonInteractive -ExecutionPolicy Bypass -File "C:\Space\06 Code\drip.ps1"'
> $t.Actions[0].WorkingDirectory = "C:\Space\06 Code"
> Set-ScheduledTask $t
> ```
>
> And `gmail_auth.json` must exist in `C:\Space\06 Code` — it's gitignored, so it does not
> travel with the merge. The preflight check will tell you loudly if it's missing.

### It rotates segments (`--mix`)

The CSV is grouped by segment because that's how it was written, so a plain walk sends nine
insurers in a row, then nine operators. `--mix` round-robins across segments by priority
(operator → partner → insurer → gov → contract → academic). A bad segment now shows up the
same day instead of burning the whole queue first, and a day's results can actually be compared.

**The schedule is a suggestion; the cap is the law.** `outreach.py` counts today's sends from
its own audit log and refuses to exceed `DAILY_CAP` (25), so a scheduler misfire cannot become
a blast. `MAX_PER_RUN` is 5, well under the cap, which is what forces the send to spread out.

Why 25 and not 200: Gmail's actual SMTP limit for a free account is **500 recipients a day**,
so volume is not what gets an account restricted — the *pattern* is. Cold mail that nobody
replies to, spam complaints, and bounces are what trip it. 25/day is invisible to the rate
limiter and slow enough that a bad batch gets caught before it repeats.

```
powershell -File drip.ps1 -DryRun      # what would go out, sends nothing
powershell -File drip.ps1 -NoJitter    # send now, skip the dice (manual run)
powershell -File drip.ps1 -N 1         # one at a time
Get-ScheduledTask "Outreach Drip"      # is it on?
Disable-ScheduledTask "Outreach Drip"  # stop everything, now
```

Log: `06 Code/drip.log`. Ledger: `python outreach.py --status`.

## Turning on sending

One-time: make a Google App Password at `myaccount.google.com/apppasswords` (needs 2FA),
then write `06 Code/gmail_auth.json` — already gitignored, never commit it:

```json
{"address": "zayahwork@gmail.com", "app_password": "abcd efgh ijkl mnop"}
```

To rehearse the whole path without mailing a human, use the local sink and throwaway copies —
this is how the batch-2 send was verified:

```
python _smtp_sink.py --port 8026 --expect 8          # in one window
python outreach.py --send --live --smtp-plain \
  --smtp-host 127.0.0.1 --smtp-port 8026 \
  --csv /tmp/t.csv --log /tmp/t.jsonl                # in another
```

The safeties are not optional and have already earned their keep: no address = no send,
an unfilled `[placeholder]` = no send, a missing attachment = hard stop, 15/day hard cap,
a 5xx at send time parks the address as dead, and the audit log dedupes by address so a
crash mid-batch can't double-mail anyone.

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
