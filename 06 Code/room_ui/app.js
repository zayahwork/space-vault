/* The room.
   One rule in here: nothing animates unless a measured number arrived to move it.
   Every ring below is RMS from real audio - the mic, or the voice being played.
   When it goes quiet, the ring goes still, because it is silent. */

const SVG = "http://www.w3.org/2000/svg";
const NS = (n) => document.createElementNS(SVG, n);

// The room, seen from your chair at the head of the table. Three down each side.
// Perspective does the work: the far seats are smaller and sit closer together,
// which is what makes this read as a room rather than a diagram.
const LEFT = { far: [330, 302], near: [148, 508] };
const RIGHT = { far: [570, 302], near: [752, 508] };
const ALONG = [0.10, 0.46, 0.82];        // far end of the table first

// The head of the table, facing you down its length. Whoever chairs the meeting
// sits here - smaller than the far side seats because they are further away
// still, and behind the table's far edge rather than beside it.
const HEAD = { x: 450, y: 282, scale: 0.68 };

// Identity, not decoration: one muted hue each, so the eye learns the seat.
// Brightness carries state; hue only carries who.
const HUE = {
  Sable: "#79e8ae", Rook: "#6fa8dc", Fitz: "#e4a33c",
  Tim: "#a98fe0", Nova: "#e8dcc0", Vega: "#e88a76", CTO: "#d6e3dd",
};

const el = (id) => document.getElementById(id);
const chairsG = el("chairs"), peopleG = el("people"), platesG = el("plates");
const desksG = el("desks");
const logEl = el("log");
const seats = new Map();
let lineCount = 0;

/* ------------------------------------------------------------- the table */

function seatAt(side, t) {
  // Walk the table edge from the far corner toward you, then step outward and
  // up so the figure sits BESIDE the table and slightly behind its edge - which
  // is what a person at a table looks like from the far end of it.
  const x = side.far[0] + (side.near[0] - side.far[0]) * t;
  const y = side.far[1] + (side.near[1] - side.far[1]) * t;
  const out = side === LEFT ? -1 : 1;
  const scale = 0.74 + t * 0.3;
  return { x: x + out * 66 * scale, y: y - 34 * scale,
           ex: x, ey: y, scale, out };
}

/* An open laptop and, for some of them, a mug. Six identical place settings
   would read as a diagram; a table people actually work at is uneven. */
function deskFor(pos, i) {
  const s = pos.scale;
  const g = NS("g");
  const x = pos.ex - pos.out * 64 * s;
  g.setAttribute("transform",
    "translate(" + x + " " + (pos.ey + 10 * s) + ") scale(" + s.toFixed(3) + ")");

  const screen = NS("path");
  screen.setAttribute("class", "lid");
  screen.setAttribute("d", "M-9,-8 L9,-8 L11,0 L-11,0 z");

  const base = NS("path");
  base.setAttribute("class", "deck-base");
  base.setAttribute("d", "M-11,0 L11,0 L13,4 L-13,4 z");

  g.append(screen, base);

  if (i % 3 === 0) {
    const mug = NS("circle");
    mug.setAttribute("class", "mug");
    mug.setAttribute("cx", pos.out >= 0 ? 22 : -22);
    mug.setAttribute("cy", 2);
    mug.setAttribute("r", 3.4);
    g.appendChild(mug);
  }

  // What's actually open on the screen right now - a ticket's status word, lit
  // on the laptop lid itself. Empty text takes no space, so a desk with nothing
  // claimed looks exactly like it did before this existed.
  const status = NS("text");
  status.setAttribute("class", "desk-status");
  status.setAttribute("text-anchor", "middle");
  status.setAttribute("y", -11);
  g.appendChild(status);

  return { g, status };
}

function buildRoom(people) {
  [chairsG, peopleG, platesG, desksG].forEach((g) => { g.textContent = ""; });
  seats.clear();

  // The head seat is taken out of the side-by-side count, so six people still
  // sit three-and-three however many chair the meeting.
  let sideIndex = 0;

  people.forEach((p) => {
    let pos;
    if (p.head) {
      pos = { x: HEAD.x, y: HEAD.y, ex: HEAD.x, ey: 302, scale: HEAD.scale, out: 0 };
    } else {
      const side = sideIndex % 2 === 0 ? LEFT : RIGHT;
      pos = seatAt(side, ALONG[Math.floor(sideIndex / 2)]);
      sideIndex += 1;
    }
    const s = pos.scale;
    const hue = HUE[p.name] || "#d6e3dd";

    const chair = NS("path");
    chair.setAttribute("class", "chair");
    chair.setAttribute("d", "M-21,20 q0,-36 21,-36 q21,0 21,36 z");
    // Seen from across the table, the chair back rises BEHIND the person, so
    // the head seat's chair is flipped rather than drawn in front of them.
    chair.setAttribute("transform", p.head
      ? "translate(" + pos.x + " " + (pos.y - 10 * s) + ") scale(" +
        s.toFixed(3) + " " + (-s).toFixed(3) + ")"
      : "translate(" + pos.x + " " + (pos.y + 22 * s) + ") scale(" + s.toFixed(3) + ")");
    chairsG.appendChild(chair);
    const desk = deskFor(pos, sideIndex);
    desksG.appendChild(desk.g);

    // Head and shoulders, deliberately plain. A drawn face would be a cartoon,
    // and this is a console.
    const g = NS("g");
    g.setAttribute("class", "person");
    g.setAttribute("transform",
      "translate(" + pos.x + " " + pos.y + ") scale(" + s.toFixed(3) + ")");
    g.style.color = hue;

    const level = NS("circle");
    level.setAttribute("class", "level");
    level.setAttribute("cy", -16);
    level.setAttribute("r", 16);

    const body = NS("path");
    body.setAttribute("class", "body");
    body.setAttribute("d", "M-24,26 q0,-26 24,-26 q24,0 24,26 z");

    const head = NS("circle");
    head.setAttribute("class", "head");
    head.setAttribute("cy", -16);
    head.setAttribute("r", 13);

    const initial = NS("text");
    initial.setAttribute("class", "initial");
    initial.setAttribute("text-anchor", "middle");
    initial.setAttribute("y", -11);
    initial.textContent = p.name[0];

    g.append(level, body, head, initial);
    peopleG.appendChild(g);

    // Nameplate, lying on the table in front of them.
    const plate = NS("g");
    plate.setAttribute("class", "plate");
    plate.setAttribute("transform",
      "translate(" + (pos.ex - pos.out * 26 * s) + " " + (pos.ey + 18 * s) +
      ") scale(" + s.toFixed(3) + ")");
    plate.style.color = hue;

    const nm = NS("text");
    nm.setAttribute("class", "plate-name");
    nm.setAttribute("text-anchor", "middle");
    nm.textContent = p.name;

    const rl = NS("text");
    rl.setAttribute("class", "plate-role");
    rl.setAttribute("text-anchor", "middle");
    rl.setAttribute("y", 13);
    rl.textContent = p.role;

    plate.append(nm, rl);
    platesG.appendChild(plate);

    seats.set(p.name, { g, level, plate, desk: desk.status });
  });
}

/* -------------------------------------------------------------- the screen */

function paintBoard(board) {
  const body = el("tv-body");
  body.textContent = "";
  el("tv-eyebrow").textContent = board.title || "ON THE BOARD";
  // Six rows at 22px is what fits inside the glass (y 52-220). Any looser and
  // the sixth row prints below the screen it is supposed to be on.
  (board.rows || []).forEach((row, i) => {
    const y = 104 + i * 22;

    const k = NS("text");
    k.setAttribute("class", "tv-key");
    k.setAttribute("x", 316);
    k.setAttribute("y", y);
    k.textContent = row.k;

    const v = NS("text");
    v.setAttribute("class", "tv-val" + (row.hot ? " hot" : ""));
    v.setAttribute("x", 584);
    v.setAttribute("y", y);
    v.setAttribute("text-anchor", "end");
    v.textContent = row.v;

    body.append(k, v);
  });
}

/* ---------------------------------------------------------------- work */

/* A ticket is a teammate's promise made concrete: they said they'd do a thing,
   and this is that thing being handed to Claude Code with tools. Nothing runs
   until you press Do it, because the vault has no git history to undo a bad
   edit. There is no progress bar here on purpose - we do not know how far along
   a job is, and drawing a bar that pretends to would be inventing a number. */

const STATUS_WORD = {
  waiting: "needs you", queued: "queued", running: "working",
  done: "done", failed: "failed", skipped: "skipped",
};

/* The sidebar card is the record; this is the glance. A person's own desk shows
   only what THEY are doing right now, so it clears the moment the ticket lands -
   done or failed both belong to the card, not to a screen that's supposed to
   read as "in progress". */
function paintDeskStatus(t) {
  const seat = seats.get(t.who);
  if (!seat || !seat.desk) return;
  const active = t.status === "waiting" || t.status === "queued" || t.status === "running";
  seat.desk.dataset.status = t.status;
  seat.desk.textContent = active ? (STATUS_WORD[t.status] || t.status) : "";
}

function paintTicket(t) {
  const empty = el("work-empty");
  if (empty) empty.remove();
  let card = document.getElementById("tk" + t.id);
  if (!card) {
    card = document.createElement("div");
    card.id = "tk" + t.id;
    card.className = "tk";
    el("work-body").appendChild(card);
  }
  card.dataset.status = t.status;
  card.style.color = HUE[t.who] || "#d6e3dd";
  card.textContent = "";

  const head = document.createElement("div");
  head.className = "tk-head";
  head.innerHTML = "<span class='tk-id'>#" + t.id + "</span> <b>" + t.who + "</b>";

  const state = document.createElement("span");
  state.className = "tk-state";
  state.textContent = STATUS_WORD[t.status] || t.status;
  head.appendChild(state);

  const task = document.createElement("div");
  task.className = "tk-task";
  task.textContent = t.task;
  card.append(head, task);

  if (t.status === "waiting") {
    const row = document.createElement("div");
    row.className = "tk-row";
    row.append(tkButton("Do it", "/approve", t.id, "go"),
               tkButton("Skip", "/skip", t.id, ""));
    card.appendChild(row);
  }

  if (t.result) {
    const res = document.createElement("div");
    res.className = "tk-result";
    res.textContent = t.result;
    card.appendChild(res);
  }

  if (t.duration_s) {
    const foot = document.createElement("div");
    foot.className = "tk-foot";
    foot.textContent = t.duration_s + "s"
      + (t.cost_usd ? "  ·  $" + t.cost_usd.toFixed(3) + " if this were the API" : "");
    card.appendChild(foot);
  }
  el("work-body").scrollTop = el("work-body").scrollHeight;
}

function tkButton(label, url, id, cls) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "tk-btn " + cls;
  b.textContent = label;
  b.addEventListener("click", () => {
    b.parentElement.querySelectorAll("button").forEach((x) => { x.disabled = true; });
    fetch(url, { method: "POST", body: JSON.stringify({ id }) });
  });
  return b;
}

/* --------------------------------------------------------------- levels */

function setLevel(node, rms) {
  if (!node) return;
  // 16 is the head radius; the ring only ever grows outward from it.
  node.setAttribute("r", (16 + rms * 15).toFixed(1));
  node.style.opacity = rms < 0.02 ? 0 : Math.min(0.9, 0.25 + rms * 0.8);
}

/* ------------------------------------------------------------ transcript */

function turn(who, role, text, kind) {
  const empty = logEl.querySelector(".empty");
  if (empty) empty.remove();

  const p = document.createElement("div");
  p.className = "turn" + (kind ? " " + kind : "");
  if (HUE[who]) p.style.color = HUE[who];

  const head = document.createElement("div");
  head.className = "turn-who";
  head.innerHTML = "<b>" + who + "</b>" + (role ? " · " + role : "");

  const body = document.createElement("div");
  body.className = "turn-text";
  body.textContent = text;

  p.append(head, body);
  logEl.appendChild(p);
  logEl.scrollTop = logEl.scrollHeight;
  lineCount += 1;
  el("count").textContent = lineCount === 1 ? "1 line" : lineCount + " lines";
}

const STATE_TEXT = {
  listening: "listening",
  hearing: "hearing you",
  thinking: "thinking",
  speaking: "speaking",
  closed: "call ended",
  idle: "idle",
};

function setState(s) {
  el("lamp").dataset.state = s;
  el("state").textContent = STATE_TEXT[s] || s;
}

/* ------------------------------------------------------------- the wire */

/* ?snapshot=1 renders from a single /history fetch and never opens a stream. A
   live SSE connection means a headless browser never finishes loading, so this
   is the only way to screenshot-check the design. Live use never uses it. */
function snapshot() {
  fetch("/history").then((r) => r.json()).then((d) => {
    handle(d.roster);
    if (d.board) handle(d.board);
    (d.tickets || []).forEach(handle);
    if (d.work) handle(d.work);
    d.events.forEach(handle);
    setState("listening");
  });
}

function connect() {
  if (new URLSearchParams(location.search).has("snapshot")) return snapshot();
  const src = new EventSource("/events");
  src.onmessage = (e) => handle(JSON.parse(e.data));
  src.onerror = () => setState("idle");
}

function handle(ev) {
  switch (ev.t) {
    case "roster":
      buildRoom(ev.people);
      el("brain").textContent = ev.brain || "";
      break;

    case "board":
      paintBoard(ev);
      break;

    case "state":
      setState(ev.room);
      break;

    case "mic":
      // You are the camera, so there is no figure of you to light. Your own
      // level lights the near edge of the table instead.
      el("table-edge").style.opacity = (0.2 + ev.rms * 0.8).toFixed(2);
      break;

    case "partial":
      el("partial").textContent = ev.text || "";
      break;

    case "you":
      el("partial").textContent = "";
      turn("You", "founder", ev.text, "mine");
      break;

    case "said":
      turn(ev.who, ev.role, ev.text, ev.cut ? "cut" : "");
      break;

    case "speak_start": {
      setState("speaking");
      const s = seats.get(ev.who);
      if (s) { s.g.classList.add("live"); s.plate.classList.add("live"); }
      break;
    }

    case "speak_end": {
      const s = seats.get(ev.who);
      if (s) {
        s.g.classList.remove("live");
        s.plate.classList.remove("live");
        setLevel(s.level, 0);
      }
      break;
    }

    case "level":
      setLevel((seats.get(ev.who) || {}).level, ev.rms);
      break;

    case "cut":
      seats.forEach((s) => {
        s.g.classList.remove("live");
        s.plate.classList.remove("live");
        setLevel(s.level, 0);
      });
      break;

    case "ticket":
      paintTicket(ev);
      paintDeskStatus(ev);
      break;

    case "mic_state":
      paintMic(ev);
      break;

    case "work_summary": {
      // The header answers "is anyone doing anything right now" first, because
      // that is the question the panel exists to answer.
      const bits = [];
      bits.push(ev.running ? "running #" + ev.running : "nothing running");
      if (ev.open) bits.push(ev.open + " waiting");
      if (ev.done) bits.push(ev.done + " done");
      if (ev.failed) bits.push(ev.failed + " failed");
      el("work-count").textContent = bits.join(" · ");
      break;
    }

    case "error":
      turn("Room", "", ev.text, "sys");
      break;
  }
}

/* ------------------------------------------------------------- controls */

el("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const text = el("input").value.trim();
  if (!text) return;
  el("input").value = "";
  fetch("/say", { method: "POST", body: JSON.stringify({ text }) });
});

/* The mic has two independent reasons to be shut and the button must say which,
   because "why can't they hear me" has two different answers and only one of
   them is something you did. */
let micByUser = false;

function paintMic(ev) {
  micByUser = ev.by_user;
  const b = el("mic");
  b.dataset.state = ev.by_user ? "user" : ev.by_room ? "room" : "open";
  b.setAttribute("aria-pressed", String(ev.by_user));
  // Honest about the difference: yours is a real shut mic, theirs is the room
  // holding the floor while still listening for you to take it back.
  el("mic-label").textContent = ev.by_user ? "Unmute"
    : ev.by_room ? "Speak to cut in" : "Mute";
}

function toggleMic() {
  fetch("/mic", { method: "POST", body: JSON.stringify({ muted: !micByUser }) });
}

el("mic").addEventListener("click", toggleMic);

el("end").addEventListener("click", () => {
  if (!confirm("End the call? This shuts the meeting down completely.")) return;
  fetch("/end", { method: "POST" });
  setState("closed");
});

// Escape still cuts them off mid-sentence. Ending the call is deliberate.
// M toggles the mic, but not while you're typing an M into the composer.
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") fetch("/cut", { method: "POST" });
  if ((e.key === "m" || e.key === "M") && e.target !== el("input")) toggleMic();
  // N is the reset. Escape stops the sentence; N stops everyone, throws away
  // whatever was queued behind it, and hands the floor back clean.
  if ((e.key === "n" || e.key === "N") && e.target !== el("input")) {
    fetch("/hush", { method: "POST" });
    setState("listening");
  }
});

setInterval(() => {
  el("clock").textContent = new Date().toISOString().slice(11, 19);
}, 1000);

connect();
