# Drive Moris — car rental demo

A demo of the Webmoris "Drive Moris" ready-made website. Drive Moris is a **fictional** car rental company at Mauritius airport. The creative direction ("Coast Road") is in [docs/drive-moris-creative-direction.md](../../docs/drive-moris-creative-direction.md). The demo kit (`../../demo_kit/demo-kit.js`) adds the "Demo by Webmoris" bar, blocks the booking form and keeps the site out of search engines.

## Run it

```
npm install
npm run build     # grades the photos, then builds the site into _site/
npm run serve     # http://127.0.0.1:5004 (rebuilds pages on save; run `npm run build` after CSS/JS changes)
```

`_site/` is the whole website as static files; deploy it as-is (see `deploy/nginx.conf.example`).

## Content

- **Company, promises, pick-up places, extras, terms:** `src/_data/site.json`
- **Fleet** (classes, cars, specs, example prices, photos): `src/_data/fleet.json`. Cars with `"featured": true` appear on the home page's garage stage; cars with two photos (front and rear) get the drag-to-turn view.
- **Five drives:** `src/_data/drives.json`
- **Photos and credits:** originals in `src/images/photos/`, credits in `src/_data/photos.json` (all from Wikimedia Commons, listed on `/credits/`).

## Build steps

- **`npm run build:photos`** grades every photo with the same duotone (`scripts/grade-photos.mjs`) into `src/images/graded/` (generated, not committed). Pages only use graded photos.
- **`npm run build:map`** draws the night-styled map and the coast route from OpenStreetMap data (`scripts/build-map.mjs`). It writes `src/static/img/map/mauritius.svg`, `src/_data/mapFrame.json` and `src/_data/route.json` (the route path, its length and where each stop falls). It reuses Island Explorer's downloaded data when present.

## Visual effects

- **Night drive** (hero): a road at night drawn in a shader (`src/assets/js/nightdrive.js`), no photo. Mouse steers, scrolling speeds it up. Capable desktops only; elsewhere a matching static SVG road (`partials/road.njk`).
- **The coast:** the map is pinned while the route draws itself around the island, with an odometer and the stops' signs and photos.
- **Odometers** (`odometer.js`): prices, distances and the trip ticket roll digit by digit.
- **Also:** signs that slide in, letterboxed photos that open like a film, a lane-line progress bar, a page-change "truck pass", magnetic buttons and tarmac grain.

Everything respects `prefers-reduced-motion` and every page works without JavaScript (the booking form shows a rate table instead of the live ticket).
