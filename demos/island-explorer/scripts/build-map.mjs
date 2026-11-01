// Builds the tour-page map of Mauritius from OpenStreetMap data (© OpenStreetMap contributors, ODbL).
//
//   npm run build:map            uses .cache/osm-mauritius.json, downloading it once if missing
//   npm run build:map -- --fetch  downloads fresh data first
//
// Writes:
//   src/static/img/map/mauritius.svg   the styled base map (coastline, reefs, lakes, parks, airport, roads)
//   src/_data/mapFrame.json            the projection, so markers land on exactly the same spot
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";

const CACHE = ".cache/osm-mauritius.json";
const SVG_OUT = "src/static/img/map/mauritius.svg";
const FRAME_OUT = "src/_data/mapFrame.json";

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
    headers: { "User-Agent": "island-explorer-demo-map/1.0", "Content-Type": "application/x-www-form-urlencoded" },
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

await mkdir("src/static/img/map", { recursive: true });
await writeFile(SVG_OUT, svg);
await writeFile(FRAME_OUT, JSON.stringify({ west: WEST, north: NORTH, kx, ky, width: WIDTH, height: HEIGHT }, null, 2) + "\n");
console.log(`Wrote ${SVG_OUT} (${(svg.length / 1024).toFixed(0)} KB, ${WIDTH}×${HEIGHT}) and ${FRAME_OUT}`);
