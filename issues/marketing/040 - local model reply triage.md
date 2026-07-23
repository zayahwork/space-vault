---
status: open
type: AFK
owner: Mark (marketing)
blocked-by: []
---
# Local-model reply triage (suggestion only, never a gate)

**Goal:** use `06 Code/local_brain.py` (free, local Ollama, proven live at ~3s/call) to pre-sort incoming replies for reply-watch, so a human scans a labeled list instead of reading every raw email cold — without ever letting the local model suppress or auto-send anything.

**Done when:** a script classifies new replies into INTERESTED / AUTO_REPLY / NOT_INTERESTED / NEEDS_HUMAN_JUDGMENT and writes the label next to each entry in `reply_watch/STATUS.md` as a suggestion, clearly marked "local-model guess, unverified." Every reply still gets a human-reviewed draft exactly as today — this only reorders what a human looks at first, it changes nothing about what gets sent.

**Known failure mode (measured, not theoretical) — CTO tested this live:** the 3B model classified a real out-of-office auto-reply as NOT_INTERESTED instead of AUTO_REPLY on the first try. Design around this: prompt it only for the clearest, cheapest signal to sort by (has an unsubscribe/OOO pattern = likely auto-reply is fine for regex, not even AI needed) rather than nuanced intent; anything it's unsure about should default to NEEDS_HUMAN_JUDGMENT rather than guessing confidently wrong. If the model's real-world accuracy on a 20-reply spot-check is below ~90%, don't ship it as anything more than a lowest-priority hint — say so plainly rather than quietly ship a wrong sort order.

**Notes:** this is the credit-saving pattern going forward — the founder wants routine, low-stakes text tasks pinged to the free local model instead of spending Claude usage. `local_brain.ask(prompt, system=...)` is the call; see its docstring for the guardrail rule (never load-bearing, never a fact source).
