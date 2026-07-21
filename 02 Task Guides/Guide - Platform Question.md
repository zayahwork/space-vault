# ☁️ Guide — The Platform Question (parked ON PURPOSE)

**The question:** where should the product run (cloud provider, compute, costs)?

**The rule we set:** infrastructure decisions come **after** the prototype exists — because the
prototype tells us the real requirements (data volume, compute per satellite, refresh rate).
Researching platforms before having those numbers = comparing prices for an imaginary workload.

**When to unpark:** the [[Guide - SPLID Detector|SPLID detector]] has run end-to-end and the
live-data pipeline works. Then this becomes a real (and short) research task:
- How much data does watching the full catalog daily actually mean? (We'll have the number.)
- Does detection need a GPU or is CPU fine? (We'll know.)
- Free tiers first: our scale at the start is tiny. A $0–20/mo box likely carries us for months.

Until then: **the laptop is the platform.** It's free and it's enough.
