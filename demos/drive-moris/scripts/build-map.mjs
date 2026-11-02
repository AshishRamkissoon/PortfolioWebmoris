// Builds Drive Moris's map of Mauritius and the coast route from OpenStreetMap data
// (© OpenStreetMap contributors, ODbL). Same projection as the Island Explorer map.
//
//   npm run build:map            uses .cache/osm-mauritius.json, downloading it once if missing
//   npm run build:map -- --fetch  downloads fresh data first
//
// Writes:
//   src/static/img/map/mauritius.svg   the styled base map (coastline, reefs, lakes, parks, airport, roads)
//   src/_data/mapFrame.json            the projection, so markers land on exactly the same spot
//   src/_data/route.json               the coast route (SVG path), its length and where each stop falls on it
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";

// Shares the download with Island Explorer when it is there.
const CACHE = existsSync("../island-explorer/.cache/osm-mauritius.json")
  ? "../island-explorer/.cache/osm-mauritius.json"
  : ".cache/osm-mauritius.json";
const SVG_OUT = "src/static/img/map/mauritius.svg";
const FRAME_OUT = "src/_data/mapFrame.json";
const ROUTE_OUT = "src/_data/route.json";
// Route stops, in driving order from the airport: south, west, north, then down the east coast.
const STOPS = [
  { name: "Airport", lat: -20.4302, lng: 57.6836 },
  { name: "Souillac", lat: -20.5187, lng: 57.5225 },
  { name: "Le Morne", lat: -20.456, lng: 57.315 },
  { name: "Flic en Flac", lat: -20.2741, lng: 57.3711 },
  { name: "Port Louis", lat: -20.1625, lng: 57.5028 },
  { name: "Grand Baie", lat: -20.013, lng: 57.5846 },
  { name: "Belle Mare", lat: -20.19, lng: 57.775 },
  { name: "Mahébourg", lat: -20.4081, lng: 57.7 },
];

// Map frame: the whole main island plus the northern islets.
const WEST = 57.28;
const EAST = 57.83;
const NORTH = -19.92;
const SOUTH = -20.54;
const HEIGHT = 1000;

const BBOX = "(-20.56,57.27,-19.90,57.84)";
const QUERY = `[out:json][timeout:120];
(
  way["natural"="coastline"]${BBOX};
  way["natural"="reef"]${BBOX};
  relation["natural"="reef"]${BBOX};
  way["natural"="water"]${BBOX};
  relation["natural"="water"]${BBOX};
  relation["boundary"="national_park"]${BBOX};
  way["boundary"="national_park"]${BBOX};
  way["aeroway"="aerodrome"]${BBOX};
  way["highway"~"^(trunk|primary)$"]${BBOX};
);
out geom;`;

// Equirectangular projection scaled for the island's latitude: accurate to a few metres at this size.
const ky = HEIGHT / (NORTH - SOUTH);
const kx = ky * Math.cos((((NORTH + SOUTH) / 2) * Math.PI) / 180);
const WIDTH = Math.round((EAST - WEST) * kx);
const project = ({ lat, lon }) => [(lon - WEST) * kx, (NORTH - lat) * ky];

async function loadOsm() {
  if (!process.argv.includes("--fetch") && existsSync(CACHE)) {
    return JSON.parse(await readFile(CACHE, "utf8"));
  }
  console.log("Downloading OpenStreetMap data from Overpass…");
  const response = await fetch("https://overpass-api.de/api/interpreter", {
    method: "POST",
    headers: { "User-Agent": "webmoris-demo-map/1.0", "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ data: QUERY }),
  });
  if (!response.ok) throw new Error(`Overpass returned ${response.status}`);
  const data = await response.json();
  await mkdir(".cache", { recursive: true });
  await writeFile(CACHE, JSON.stringify(data));
  return data;
}

// Douglas–Peucker line simplification, in map units.
function simplify(points, tolerance) {
  if (points.length < 3) return points;
  const [ax, ay] = points[0];
  const [bx, by] = points[points.length - 1];
  const length = Math.hypot(bx - ax, by - ay) || 1;
  let worst = 0;
  let index = 0;
  for (let i = 1; i < points.length - 1; i++) {
    const [px, py] = points[i];
    const distance = Math.abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / length;
    if (distance > worst) [worst, index] = [distance, i];
  }
  if (worst <= tolerance) return [points[0], points[points.length - 1]];
  return [...simplify(points.slice(0, index + 1), tolerance).slice(0, -1), ...simplify(points.slice(index), tolerance)];
}

// Closed rings start and end on the same point, so simplify them as two halves.
function simplifyRing(points, tolerance) {
  const middle = Math.floor(points.length / 2);
  return [...simplify(points.slice(0, middle + 1), tolerance).slice(0, -1), ...simplify(points.slice(middle), tolerance)];
}

function area(points) {
  let sum = 0;
  for (let i = 0; i < points.length; i++) {
    const [x1, y1] = points[i];
    const [x2, y2] = points[(i + 1) % points.length];
    sum += x1 * y2 - x2 * y1;
  }
  return Math.abs(sum / 2);
}

const fmt = (n) => Math.round(n * 10) / 10;
const toPath = (points, closed) =>
  points.map(([x, y], i) => `${i ? "L" : "M"}${fmt(x)} ${fmt(y)}`).join("") + (closed ? "Z" : "");

// Joins way segments that share end nodes into closed rings (used for the coastline and multipolygons).
function stitch(segments) {
  const rings = [];
  const pool = segments.map((s) => [...s]);
  while (pool.length) {
    let ring = pool.shift();
    let grown = true;
    while (grown && !samePoint(ring[0], ring[ring.length - 1])) {
      grown = false;
      for (let i = 0; i < pool.length; i++) {
        const seg = pool[i];
        const end = ring[ring.length - 1];
        if (samePoint(seg[0], end)) ring = ring.concat(seg.slice(1));
        else if (samePoint(seg[seg.length - 1], end)) ring = ring.concat([...seg].reverse().slice(1));
        else continue;
        pool.splice(i, 1);
        grown = true;
        break;
      }
    }
    if (samePoint(ring[0], ring[ring.length - 1])) rings.push(ring);
  }
  return rings;
}
const samePoint = (a, b) => a.lat === b.lat && a.lon === b.lon;

function polygons(elements, tolerance, minArea) {
  const rings = [];
  const loose = [];
  for (const element of elements) {
    if (element.type === "way") {
      const g = element.geometry;
      samePoint(g[0], g[g.length - 1]) ? rings.push(g) : loose.push(g);
    } else {
      const outers = element.members.filter((m) => m.type === "way" && m.role !== "inner" && m.geometry);
      rings.push(...stitch(outers.map((m) => m.geometry)));
    }
  }
  rings.push(...stitch(loose));
  return rings
    .map((ring) => simplifyRing(ring.map(project), tolerance))
    .filter((points) => points.length > 3 && area(points) >= minArea)
    .map((points) => toPath(points.slice(0, -1), true))
    .join("");
}

function lines(elements, tolerance) {
  return elements
    .map((element) => simplify(element.geometry.map(project), tolerance))
    .filter((points) => points.length > 1)
    .map((points) => toPath(points, false))
    .join("");
}

const { elements } = await loadOsm();
const tagged = (test) => elements.filter((e) => e.tags && test(e.tags));

const coastline = stitch(tagged((t) => t.natural === "coastline").map((e) => e.geometry))
  .map((ring) => simplifyRing(ring.map(project), 0.5))
  .filter((points) => points.length > 3 && area(points) >= 2)
  .map((points) => toPath(points.slice(0, -1), true))
  .join("");
const reefs = polygons(tagged((t) => t.natural === "reef"), 0.6, 4);
const lakes = polygons(tagged((t) => t.natural === "water" && t.water !== "river" && t.water !== "pond"), 0.6, 8);
const parks = polygons(tagged((t) => t.boundary === "national_park"), 0.8, 20);
const airport = polygons(tagged((t) => t.aeroway === "aerodrome"), 0.6, 20);
const trunk = lines(tagged((t) => t.highway === "trunk"), 0.9);
const primary = lines(tagged((t) => t.highway === "primary"), 0.9);

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${WIDTH} ${HEIGHT}" width="${WIDTH}" height="${HEIGHT}">
<!-- Map data © OpenStreetMap contributors, ODbL. Generated by scripts/build-map.mjs -->
<defs>
<radialGradient id="sea" cx="48%" cy="52%" r="70%"><stop offset="0" stop-color="#e4f3f6"/><stop offset="1" stop-color="#c9e4eb"/></radialGradient>
<filter id="lift" x="-5%" y="-5%" width="110%" height="112%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#0a2a3d" flood-opacity=".14"/></filter>
</defs>
<rect width="${WIDTH}" height="${HEIGHT}" fill="url(#sea)"/>
<path d="${coastline}" fill="none" stroke="#e9f7f4" stroke-width="22" stroke-linejoin="round"/>
<path d="${reefs}" fill="#d3eee8" stroke="#fff" stroke-width="1.2" stroke-opacity=".9"/>
<path d="${coastline}" fill="#fbf8f1" filter="url(#lift)"/>
<path d="${parks}" fill="#dcecd2" stroke="#c4dcb3" stroke-width="1"/>
<path d="${airport}" fill="#ece7dc" stroke="#ddd5c5" stroke-width="1"/>
<path d="${lakes}" fill="#bfe0ea"/>
<g fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="${primary}" stroke="#dccdb2" stroke-width="3.4"/>
<path d="${primary}" stroke="#fff" stroke-width="2"/>
<path d="${trunk}" stroke="#e7b98a" stroke-width="4.6"/>
<path d="${trunk}" stroke="#f8d3a6" stroke-width="3"/>
</g>
<path d="${coastline}" fill="none" stroke="#dccfb6" stroke-width="1.2"/>
</svg>
`;

// --- Coast route: the main island's coastline, smoothed and pulled slightly inland, like the coast road. ---
const KM_PER_UNIT = 111.32 / ky;
const rings = stitch(tagged((t) => t.natural === "coastline").map((e) => e.geometry)).map((r) => r.map(project));
const island = rings.sort((a, b) => area(b) - area(a))[0];
let ring = simplifyRing(island, 11).slice(0, -1);
for (let pass = 0; pass < 3; pass++) {
  // Chaikin smoothing rounds the corners the way a road does.
  ring = ring.flatMap((p, i) => {
    const q = ring[(i + 1) % ring.length];
    return [
      [0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]],
      [0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]],
    ];
  });
}
const cx = ring.reduce((sum, p) => sum + p[0], 0) / ring.length;
const cy = ring.reduce((sum, p) => sum + p[1], 0) / ring.length;
ring = ring.map(([x, y]) => {
  const d = Math.hypot(x - cx, y - cy) || 1;
  return [x - ((x - cx) / d) * 14, y - ((y - cy) / d) * 14];
});
const distance = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const nearestIndex = (points, target) =>
  points.reduce((best, p, i) => (distance(p, target) < distance(points[best], target) ? i : best), 0);
const stops = STOPS.map((stop) => ({ ...stop, point: project({ lat: stop.lat, lon: stop.lng }) }));
// Start at the airport and set off towards Souillac.
const start = nearestIndex(ring, stops[0].point);
let ordered = [...ring.slice(start), ...ring.slice(0, start)];
if ((nearestIndex(ring, stops[1].point) - start + ring.length) % ring.length > ring.length / 2) {
  ordered = [ordered[0], ...ordered.slice(1).reverse()];
}
ordered.push(ordered[0]);
const cumulative = [0];
for (let i = 1; i < ordered.length; i++) cumulative.push(cumulative[i - 1] + distance(ordered[i], ordered[i - 1]));
const total = cumulative[cumulative.length - 1];
const loop = ordered.slice(0, -1);
const routeStops = stops.map((stop, index) => {
  const i = index === 0 ? 0 : nearestIndex(loop, stop.point);
  return {
    name: stop.name,
    at: +(cumulative[i] / total).toFixed(4),
    km: Math.round(cumulative[i] * KM_PER_UNIT),
    x: fmt(ordered[i][0]),
    y: fmt(ordered[i][1]),
  };
});
const route = {
  d: toPath(ordered, false),
  length: Math.round(total),
  km: Math.round(total * KM_PER_UNIT),
  width: WIDTH,
  height: HEIGHT,
  stops: routeStops,
};

await mkdir("src/static/img/map", { recursive: true });
await writeFile(SVG_OUT, svg);
await writeFile(FRAME_OUT, JSON.stringify({ west: WEST, north: NORTH, kx, ky, width: WIDTH, height: HEIGHT }, null, 2) + "\n");
await writeFile(ROUTE_OUT, JSON.stringify(route, null, 2) + "\n");
console.log(`Route: ${route.km} km · ${route.stops.map((stop) => `${stop.name} ${stop.km}`).join(" · ")}`);
console.log(`Wrote ${SVG_OUT} (${(svg.length / 1024).toFixed(0)} KB, ${WIDTH}×${HEIGHT}) and ${FRAME_OUT}`);
