---
updated: 2026-07-21
code: "06 Code/roomserver.py · room_ui/ · jarvis.cmd"
---

# 🖥️ The Room

The war room: you talk, they answer out loud in their own voices, and you see them at the
table. Runs entirely on this machine.

```
mic → RealtimeSTT (local) → brain (+ each person's memory) → Kokoro (local) → speakers
                                  ↓
                          events → the browser
```

## Running it

```
cd "C:\Space\06 Code"
jarvis                     free + local (llama3)
jarvis --brain claude      sharper, needs ANTHROPIC_API_KEY
jarvis --no-mic            type only
jarvis --calibrate         measure your speakers vs your mic
jarvis --list-mics
```

Startup is ~8 seconds — 6 voices warming plus the speech model — then it's live.

## What you see

- **The table**, seen from your chair at the head of it. Six seated, in perspective.
- **The screen at the far end** — budget used, archive row count, lessons banked, the
  scoreboard. Real numbers, read off `budget.json`, `health.jsonl`, `brains/` and
  [[01 TASKS]] at the moment you ask.
- **Your words appear under the table as you speak**, from the live partial transcript.
- **A ring round whoever's talking** — that's RMS of the audio actually leaving your
  speakers. **A still ring means silence, not idle.** There is no ambient animation anywhere.
- **The near edge of the table** brightens with your own mic level. You're the camera, so
  there's no figure of you.

## Controls

| | |
|---|---|
| **Talk** | Just talk. It waits 0.35s of quiet, then they answer. |
| **Interrupt** | Talk over them. They stop mid-word. You're the boss. |
| `Esc` | Cuts them off without ending anything |
| **Type** | The box at the bottom, if you'd rather not talk |
| **End call** | Stops the voices, releases the mic, saves the transcript, exits |

Transcripts land in `06 Code/meetings/`.

## 🔊 The echo problem, and how it's handled

A soundbar plus an open mic is a feedback loop: they speak → the mic hears it → the room
treats its own voice as you → it answers itself → **it never stops.** This happened, and it's
why the meeting once ran forever.

It's defended twice:

1. **Text.** Anything recognised that closely overlaps something we just said is discarded.
   This is the defence that actually breaks the loop, because it doesn't care how loud the
   room is.
2. **Level.** While they're speaking, the mic must clear a loudness gate before it counts as
   you. You're a foot away; the soundbar is across the room.

**Calibrate it once:**

```
jarvis --calibrate
```

It measures the room quiet, then the bleed from your speakers, then your voice, and prints
the exact `--gate` to use. If your voice isn't clearly louder than the bar it says so plainly
rather than pretending — at that point it's turn the bar down, move the mic closer, or wear
headphones. **No software can separate two signals at the same level.**

```
jarvis --gate 0.38          they ignore you → lower it
jarvis --gate 0.55          the speakers cut themselves off → raise it
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `.ps1 cannot be loaded` | PowerShell execution policy | Use `jarvis`, not `jarvis.ps1` |
| Still running after closing the tab | Closing a browser tab doesn't stop a server | **End call**. If it's already orphaned: `Get-CimInstance Win32_Process -Filter "Name='python.exe'"` and stop the roomserver one |
| Talks to itself forever | Echo loop | `jarvis --calibrate`, then use the gate it prints |
| Ignores you when you interrupt | Gate too high | Lower `--gate` |
| Cuts itself off constantly | Gate too low, or the bar is very loud | Raise `--gate`, turn the bar down |
| Answers before you've finished | Silence window too short | `--silence 0.5` |
| They sound dumb | The free local model | `--brain claude` — see [[The Team]] |

## What's real, measured on this machine

| stage | time |
|---|---|
| speech → text | transcribes **while** you talk |
| silence before they answer | 0.35s |
| brain first token (local) | 0.18s |
| voice starts | 0.34–0.45s |
| **you stop → first word back** | **~0.9s** |

> [!warning] `localhost` costs two seconds
> Windows resolves it to `::1` first, Ollama binds `127.0.0.1` only, and every request ate
> the IPv6 timeout. Measured: `localhost` 2.18s vs `127.0.0.1` 0.14s. **Never point anything
> on this machine at `localhost`** — including the Obsidian AI plugins.
