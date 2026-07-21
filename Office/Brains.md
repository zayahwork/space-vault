---
updated: 2026-07-21
code: "06 Code/brain.py · 06 Code/brains/"
---

# 🧠 Brains

Each person has a memory file in `06 Code/brains/`. It's read back into the room before they
speak, so what they learned in July still applies in September. **This is the same design as
Remend's playbook**: proven outcomes get distilled into reusable lessons and retrieved next
time they're relevant.

It works. In a live test Sable quoted the measured 3.72 km median unprompted, and Fitz brought
up the age-binning method — both straight out of their own files.

## The rule that keeps it honest

A lesson is `proven` only when something demonstrated it. Everything else is `hypothesis` and
says so out loud. **A brain full of confident guesses is worse than no brain**, because it
launders yesterday's guess into today's fact. Retiring a lesson is normal — being wrong in
writing is the point.

## Using it

```
python brain.py                                  who knows what
python brain.py Sable                            read one brain
python brain.py --learn Tim "..." --evidence "..." --proven
python brain.py --demote Fitz 2                  that one didn't hold up
python brain.py --context Sable Rook             brains as prompt text
```

## Why not fine-tune a model per person?

You'd need thousands of examples each, a training run every time anyone learned anything, and
you'd end up with a model that *sounds* like them rather than one that *knows more than
yesterday*. **Memory beats weights here.** Wrong tool, and far more work for a worse result.

---

## What's banked — 14 lessons, 8 proven

### 🧠 Sable — ML Engineer
- ✓ A gap between SupGP and the public catalog is only evidence of a maneuver **if you
  condition on how old the catalog entry was**. Rank on raw gap and you're mostly ranking
  staleness. *(10,780 Starlink objects: raw ranking 3,555, age-binned 541 — 85% was old data)*
- ✓ Build the baseline out of the population you're testing, not a physics model. Per-age-bin
  percentiles need no drag assumptions and no tuning. *(zero fitted parameters in `detect.py`)*

### ⚙️ Rook — Software Engineer
- ✓ The archive was **half an experiment** — we stored SupGP but never the public catalog it
  has to be compared against, and neither is retro-fetchable. Fixed.
- ✓ One `GROUP=active` pull covers all 16,135 catalogued objects for 848 KB gzipped. Sixteen
  per-group pulls would be ruder *and* miss objects — there is no GP group called `iss`.

### 🔍 Fitz — Debugger
- ✓ CelesTrak answers a redundant GP download with **403 and "has not updated since your last
  successful download"**. That's politeness enforcement, not an error; retrying it three times
  is arguing with a server telling you to stop. *(SupGP doesn't do this — verified)*
- ✓ **A run that exits non-zero is not a warning if nobody reads exit codes.** Telesat vanished
  from the 14:00Z snapshot, the script correctly returned 1, and it went unnoticed for seven
  hours.

### 📚 Tim — Researcher
- ? The suspects with 1,000+ km disagreements need checking against **actual maneuver records**
  before anyone calls them detections. 5,337 km and 8,412 km RMS are implausible for a
  station-keeping burn — decaying objects or bad elements are likelier.
- ✓ Kimi-K2-class models are ~1T parameters and cannot run on an 8 GB 3070 Ti. Local speed was
  never the bottleneck anyway.

### 📣 Vega — Marketing
- ? The line that lands isn't *"we detect maneuvers"*. It's *"most of what looks like a
  maneuver is just old data, and we can tell the difference."* **Untested on a real audience.**
- ✓ Zayah stacks several requests into one message and notices when one gets dropped. Answer
  all of them.

### 💡 Nova — Explainer
- ? Explain the detector as *"is the map wrong because the car moved, or because the map is
  old"* before using the words maneuver or stale. **Not yet tried on anyone outside the team.**
- ✓ `C:\Space` is under git as of `2a581d1`. Credentials and the archive are deliberately
  untracked.

### 🎯 CTO
- ✓ The room talks on a free local model and does its work through Claude Code on this machine.
  Talking is free; building runs on the existing Claude plan, not a new API key.
- ? Zayah reverses decisions fast, and that's usually him being right rather than indecisive.
  **Build things so they can be switched off rather than arguing.**

---

> [!note] The three hypotheses worth proving
> Vega's pitch line and Nova's explanation both need **one real person outside the team** to
> hear them. Tim's is the company's actual bottleneck. Those three are the next lessons that
> should flip to `proven` — or get retired.
