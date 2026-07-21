---
title: Glossary — space words, in plain English
type: reference
created: 2026-07-20
tags: [glossary, learning]
---

# Glossary — plain English

> Every weird acronym from this project, explained like you're new (because we are).
> Add to this whenever a new one shows up in the [[Daily Updates]] notes.

## Orbits (where stuff is)

- **LEO — Low Earth Orbit.** The "close to Earth" zone, roughly 160–2,000 km up. Where Starlink,
  the ISS, and most satellites live. It's crowded — that's why collisions are the big worry here.
- **GEO — Geosynchronous (or Geostationary) Orbit.** Way out at ~36,000 km. Satellites there
  orbit at the same speed Earth spins, so they hover over one spot. TV and military comm sats
  live here. Fewer objects, but each one is expensive and important.
- **Cislunar / XGEO.** The space *beyond* GEO, out toward the Moon. Almost nobody tracks stuff
  out there yet — the military is starting to care a lot.

## The field we're entering

- **SSA — Space Situational Awareness.** Knowing what's up there and where it's going.
  Basically: air traffic control, but for space.
- **SDA — Space Domain Awareness.** The military's newer name for SSA. Same idea, but with an
  extra question attached: *"is that satellite doing something suspicious?"*
- **Conjunction.** A close approach between two objects in orbit — a possible crash.
  A "conjunction warning" = "heads up, these two might hit each other."
- **CDM — Conjunction Data Message.** The standard file/alert that says "object A and object B
  will pass close to each other at this time, with this probability." The free warnings
  operators get are CDMs.
- **Maneuver.** A satellite firing its thrusters to change its orbit. Detecting maneuvers
  matters because: (1) a maneuver you didn't know about ruins collision predictions, and
  (2) militarily, "that satellite just moved unexpectedly" is the whole ballgame.
- **Pattern of Life (PoL).** A satellite's normal routine — like knowing your neighbor leaves
  at 8am daily. Once you know the routine, the *break* in the routine is the interesting part.
  **Our product idea is basically: learn every object's routine, flag the weird.**

- **Debris.** Dead stuff in orbit — broken satellites, spent rocket stages, fragments from old
  collisions. Over half the catalog. It can't steer, can't follow rules, and doesn't answer the
  radio. The main thing everyone's trying not to hit.
- **STM — Space Traffic Management.** The dream of real traffic rules for orbit — lanes, rights
  of way, coordination. Mostly still an idea (see [[Space Highway - the far-future vision]]).
- **Outer Space Treaty (1967).** The base law of space: no country owns space or any part of
  it. Great for peace, terrible for building a highway — nobody has authority to enforce lanes.
- **ITU — International Telecommunication Union.** The UN body that assigns satellite radio
  frequencies and GEO parking slots. Proof that international "space rules" CAN work — it just
  took ~50 years.

## The data (what we build on)

- **TLE — Two-Line Element (set).** The old-school format for describing a satellite's orbit in
  two lines of text. Invented decades ago. Free and public. Problem: it literally can't count
  past 99,999 objects — and we just passed 100,000 in July 2026.
- **OMM — Orbit Mean-elements Message.** The modern replacement for TLE (comes in JSON, etc.).
  New objects above #100,000 are ONLY published this way. **We build on OMM, not TLE.**
- **Space-Track.org.** The free official US Space Force website that publishes the catalog of
  tracked objects. You registered there today. Our raw material.
- **CelesTrak.** A friendlier free site that repackages the same kind of data. Good for quick
  grabs, no login.
- **SATCAT — Satellite Catalog.** The big list of every tracked object in orbit (~50,000+ and
  counting). Each object gets a number (the ISS is #25544).
- **Epoch.** Just a fancy word for "the timestamp this data snapshot was taken."
- **SGP4.** The standard math (and the Python library named after it) that turns a TLE/OMM into
  "here's where the satellite is at time X."
- **TraCSS.** The US government's new free traffic-warning system for satellite operators
  (run by the Office of Space Commerce). Important to us because it makes basic collision
  warnings free — so we must sell something *smarter* than basic warnings.
- **SPLID.** A free MIT dataset of satellite behavior with the maneuvers already labeled by
  experts. Like a practice exam with the answer key — perfect for training/testing our ML
  without doing months of manual labeling.

## The money (how we get paid)

- **SBIR — Small Business Innovation Research.** A US government program that PAYS small
  companies to build new tech. Not a loan, not investment — they pay you, you keep the company.
- **STTR.** SBIR's sibling program where you partner with a university.
- **SpaceWERX / AFWERX.** The Space Force's / Air Force's "innovation front doors" that run
  their SBIR programs. SpaceWERX = our door.
- **Phase I / II / III.** SBIR steps: Phase I ≈ $150K to prove the idea → Phase II ≈ $1–2M to
  build it → Phase III = the government actually buys it.
- **Open Topic.** An SBIR flavor where YOU pitch your own idea (instead of answering their
  specific request). Friendliest to newcomers. Our target.
- **Specific Topic.** The opposite — the government describes exactly what it wants and you
  answer. One of these windows opens Jul 22.
- **D2P2 — Direct to Phase II.** Skipping Phase I. Needs a government customer already signed
  on. Not us yet.
- **DSIP.** The government website where SBIR proposals actually get submitted. Clunky but
  mandatory.
- **SAM.gov / UEI.** The government's business registry. You must register (free) and get a UEI
  number before you can be paid a government dollar. Slow — we start it Day 3.
- **Valley of Death.** SBIR slang: winning Phase I and II money but never landing real
  customers, then dying. The trap we're consciously avoiding by doing outreach NOW.

## Companies to know (the neighbors)

- **Slingshot Aerospace** — big funded US player; their "Agatha" AI product does what we want
  to do, but sold expensively to governments/enterprises. Our wedge: same idea, way cheaper,
  for everyone they ignore.
- **LeoLabs** — owns radars, tracks LEO, sells data. Sensor company.
- **Kayhan Space** — sells collision-avoidance tools to operators, ~$2K/month. Proof people pay.
- **Starfish Space** — Kent, WA neighbor; builds satellites that grab/service other satellites.
- **ExoAnalytic → Anduril** — huge telescope network, just bought by defense-tech giant Anduril.
- **Privateer** — Moriba Jah's data company (he's the guy we emailed).
