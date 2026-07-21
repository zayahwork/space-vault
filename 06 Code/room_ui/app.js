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

// Identity, not decoration: one muted hue each, so the eye learns the seat.
// Brightness carries state; hue only carries who.
const HUE = {
  Sable: "#79e8ae", Rook: "#6fa8dc", Fitz: "#e4a33c",
  Tim: "#a98fe0", Nova: "#e8dcc0", Vega: "#e88a76", CTO: "#d6e3dd",
};

const el = (id) => document.getElementById(id);
const chairsG = el("chairs"), peopleG = el("people"), platesG = el("plates");
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

function buildRoom(people) {
  [chairsG, peopleG, platesG].forEach((g) => { g.textContent = ""; });
  seats.clear();

  people.forEach((p, i) => {
    const side = i % 2 === 0 ? LEFT : RIGHT;
    const pos = seatAt(side, ALONG[Math.floor(i / 2)]);
    const s = pos.scale;
    const hue = HUE[p.name] || "#d6e3dd";

    const chair = NS("path");
    chair.setAttribute("class", "chair");
    chair.setAttribute("d", "M-21,20 q0,-36 21,-36 q21,0 21,36 z");
    chair.setAttribute("transform",
      "translate(" + pos.x + " " + (pos.y + 22 * s) + ") scale(" + s.toFixed(3) + ")");
    chairsG.appendChild(chair);

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

    seats.set(p.name, { g, level, plate });
  });
}

/* -------------------------------------------------------------- the screen */

function paintBoard(board) {
  const body = el("tv-body");
  body.textContent = "";
  el("tv-eyebrow").textContent = board.title || "ON THE BOARD";
  (board.rows || []).forEach((row, i) => {
    const y = 106 + i * 26;

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
      turn(ev.who, ev.role, ev.text);
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

el("end").addEventListener("click", () => {
  if (!confirm("End the call? This shuts the meeting down completely.")) return;
  fetch("/end", { method: "POST" });
  setState("closed");
});

// Escape still cuts them off mid-sentence. Ending the call is deliberate.
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") fetch("/cut", { method: "POST" });
});

setInterval(() => {
  el("clock").textContent = new Date().toISOString().slice(11, 19);
}, 1000);

connect();
