/* The room.
   One rule in here: nothing animates unless a measured number arrived to move it.
   Every ring radius below is RMS from real audio - the mic, or the voice being
   played. When it goes quiet, the ring goes still, because it is silent. */

const SVG = "http://www.w3.org/2000/svg";
const NS = (n) => document.createElementNS(SVG, n);

// The ellipse IS the table. The founder sits at its focus, not its centre -
// where the primary body sits in a real orbit. c = sqrt(rx^2 - ry^2).
const CX = 430, CY = 270, RX = 320, RY = 212;
const FOCUS_X = CX - Math.sqrt(RX * RX - RY * RY);

// Identity, not decoration: one muted hue each, so the eye learns the seat.
// Brightness carries state; hue only carries who.
const HUE = {
  Sable: "#79e8ae", Rook: "#6fa8dc", Fitz: "#e4a33c",
  Tim: "#a98fe0", Nova: "#e8dcc0", Vega: "#e88a76", CTO: "#d6e3dd",
};

const el = (id) => document.getElementById(id);
const seatsG = el("seats"), linksG = el("links"), logEl = el("log");
const seats = new Map();
let lineCount = 0;

/* ------------------------------------------------------------- the table */

function buildSeats(people) {
  seatsG.textContent = "";
  seats.clear();
  const n = people.length;
  people.forEach((p, i) => {
    // Start at the top and go clockwise, leaving the founder's side open.
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    const x = CX + RX * Math.cos(a);
    const y = CY + RY * Math.sin(a);

    // Labels sit radially OUTSIDE the track, or they collide with it - the seats
    // at the sides are the ones that break a naive above/below rule.
    const ox = Math.cos(a), oy = Math.sin(a);
    const lx = Math.round(ox * 42);
    const ly = Math.round(oy * 34) + (oy < -0.35 ? -30 : 22);
    const anchor = ox > 0.35 ? "start" : ox < -0.35 ? "end" : "middle";

    const g = NS("g");
    g.setAttribute("class", "seat");
    g.setAttribute("transform", `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
    g.style.color = HUE[p.name] || "#d6e3dd";

    const level = NS("circle");            // the measured ring
    level.setAttribute("class", "seat-level");
    level.setAttribute("r", 30);

    const ring = NS("circle");
    ring.setAttribute("class", "seat-ring");
    ring.setAttribute("r", 26);

    const mono = NS("text");
    mono.setAttribute("class", "seat-mono");
    mono.setAttribute("text-anchor", "middle");
    mono.setAttribute("dy", "6");
    mono.textContent = p.name[0];

    const label = (cls, dy, txt) => {
      const t = NS("text");
      t.setAttribute("class", cls);
      t.setAttribute("text-anchor", anchor);
      t.setAttribute("x", lx);
      t.setAttribute("y", ly + dy);
      t.textContent = txt;
      return t;
    };
    const name = label("seat-name", 0, p.name);
    const role = label("seat-role", 13, p.role);
    const mem = label("seat-lessons", 25,
                      p.lessons === 1 ? "1 lesson" : `${p.lessons} lessons`);

    g.append(level, ring, mono, name, role, mem);
    seatsG.appendChild(g);
    seats.set(p.name, { g, level, x, y });
  });
}

function placeYou() {
  const g = el("you");
  g.setAttribute("transform", `translate(${FOCUS_X.toFixed(1)} ${CY})`);
  // A diamond, not another circle - you are not one of the six.
  el("you-mark").setAttribute("d", "M0,-19 L19,0 L0,19 L-19,0 Z");
  el("you-label").setAttribute("y", 46);
  el("you-focus").setAttribute("y", 60);
}

/* --------------------------------------------------------------- levels */

function setLevel(node, rms) {
  if (!node) return;
  // 26 is the seat radius; the ring grows outward from the rim only.
  node.setAttribute("r", (26 + rms * 22).toFixed(1));
  node.style.opacity = rms < 0.02 ? 0 : Math.min(0.9, 0.25 + rms * 0.8);
}

function link(name) {
  linksG.textContent = "";
  const s = seats.get(name);
  if (!s) return;
  const l = NS("line");
  l.setAttribute("class", "link");
  l.setAttribute("x1", s.x); l.setAttribute("y1", s.y);
  l.setAttribute("x2", FOCUS_X); l.setAttribute("y2", CY);
  l.style.color = HUE[name] || "#d6e3dd";
  linksG.appendChild(l);
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
  head.innerHTML = `<b>${who}</b>${role ? " · " + role : ""}`;

  const body = document.createElement("div");
  body.className = "turn-text";
  body.textContent = text;

  p.append(head, body);
  logEl.appendChild(p);
  logEl.scrollTop = logEl.scrollHeight;
  lineCount += 1;
  el("count").textContent = lineCount === 1 ? "1 line" : `${lineCount} lines`;
}

const STATE_TEXT = {
  listening: "listening",
  hearing: "hearing you",
  thinking: "thinking",
  speaking: "speaking",
  closed: "meeting closed",
  idle: "idle",
};

function setState(s) {
  el("lamp").dataset.state = s;
  el("state").textContent = STATE_TEXT[s] || s;
}

/* ------------------------------------------------------------- the wire */

/* ?snapshot=1 renders the room from a single /history fetch and never opens a
   stream. A live SSE connection means a headless browser never finishes loading,
   so this is the only way to screenshot-check the design. Live use never uses it. */
function snapshot() {
  fetch("/history").then((r) => r.json()).then((d) => {
    handle(d.roster);
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
        buildSeats(ev.people);
        placeYou();
        el("brain").textContent = ev.brain || "";
        break;

      case "state":
        setState(ev.room);
        if (ev.room !== "speaking") linksG.textContent = "";
        break;

      case "mic":
        setLevel(el("you-ring"), ev.rms);
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
        if (s) s.g.classList.add("live");
        link(ev.who);
        break;
      }

      case "speak_end": {
        const s = seats.get(ev.who);
        if (s) { s.g.classList.remove("live"); setLevel(s.level, 0); }
        break;
      }

      case "level":
        setLevel((seats.get(ev.who) || {}).level, ev.rms);
        break;

      case "cut":
        linksG.textContent = "";
        seats.forEach((s) => { s.g.classList.remove("live"); setLevel(s.level, 0); });
        turn("Room", "", "You cut in.", "sys");
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

el("cut").addEventListener("click", () => fetch("/cut", { method: "POST" }));

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") fetch("/cut", { method: "POST" });
});

setInterval(() => {
  el("clock").textContent = new Date().toISOString().slice(11, 19);
}, 1000);

placeYou();
connect();
