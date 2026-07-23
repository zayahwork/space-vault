# 📚 Tim — Researcher

What Tim has learned on this project. Written by `brain.py`; read back
before Tim speaks. `proven` means something demonstrated it. `hypothesis`
means we think so and haven't shown it yet — say so out loud.

- [hypothesis] 2026-07-21 — The suspects with 1,000+ km disagreements need checking against actual maneuver records before anyone calls them detections. A gap that large is as likely to be a decaying object or a bad element set as a burn.  **How we know:** Top Starlink suspects show 5,337 km and 8,412 km RMS - physically implausible for a station-keeping burn.
- [proven] 2026-07-21 — Kimi K2 class models are around a trillion parameters and cannot run on this machine's 8GB 3070 Ti. Local speed was never the bottleneck anyway - the brain answers in 180ms.  **How we know:** Measured TTFT 0.18s on llama3 via 127.0.0.1; VRAM is 8GB.
- [hypothesis] 2026-07-21 — Check web-tool access with one cheap call before promising a research deliverable, so a blocked session gets flagged in seconds, not after a full write-up.  **How we know:** from work ticket #1: research successful space detection startups and their first-week strategy
- [proven] 2026-07-23 — A learned/config file can change SHAPE, not just value, when the data changes regime — and every consumer written against the old shape dies silently. Whatever writes a learned file, test its readers against every shape the writer can produce, and always run new orchestration once on REAL data before closing the card: the fakes pass, the real run is what finds this class of bug.  **How we know:** SES re-learned as mixed GEO+MEO and `learn_baselines` began stamping `min_km` as a list ([1.0, 2.0]); `daily_alert.py` forwarded it as a scalar and the scheduled ledger crashed on every snapshot after 2026-07-22/1400Z, unnoticed until issue 020's `detect.py --all` first real run isolated the failure to one fleet line instead of dying.
