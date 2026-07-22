# The Kanban (Pocock-style)

This folder is the backlog the agents work from. Flow: `/grill` an idea → `/prd` writes the
destination here → `/issues` splits it into numbered issue files → `/ralph` (in a window) or
`ralph.ps1` (headless loop, the night shift) implements the `type: AFK` ones.

- `status: open|done` · `type: AFK|HITL` · `blocked-by: [numbers]`
- HITL issues are Zayah's — agents never pick them up.
- Delete PRDs and done issues once merged: stale docs mislead future agents (doc rot).

Full write-up: [[Video Digest - Matt Pocock AI Coding Workflow]].
