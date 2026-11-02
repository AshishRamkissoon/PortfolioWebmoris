# Drive Moris — car rental demo

A demo of the Webmoris "Drive Moris" ready-made website. Drive Moris is a **fictional** car rental company at Mauritius airport. The design direction is "Bright island" (see [docs/drive-moris-creative-direction.md](../../docs/drive-moris-creative-direction.md)). The demo kit (`../../demo_kit/demo-kit.js`) adds the "Demo by Webmoris" bar, blocks the booking form and keeps the site out of search engines.

## Run it

```
npm install
npm run build     # builds the site into _site/
npm run serve     # http://127.0.0.1:5004 (rebuilds pages on save; run `npm run build` after CSS/JS changes)
```

`_site/` is the whole website as static files; deploy it as-is (see `deploy/nginx.conf.example`).

## Content

- **Company, benefits, steps, pick-up places, extras, FAQ:** `src/_data/site.json`
- **Fleet** (classes, cars, specs, example prices, photos): `src/_data/fleet.json`. Cars with `"featured": true` appear on the home page; a second photo appears on the car page.
- **Day trips:** `src/_data/drives.json`
- **Photos and credits:** `src/images/photos/` and `src/_data/photos.json` (all from Wikimedia Commons, listed on `/credits/`).

## Pages

Home (search, benefits, popular cars, how it works, coast route, day trips, FAQ), Our cars (filter), one page per car, Book a car (4 steps with a live price summary), Credits, 404.

## Map

`npm run build:map` draws the map and the coast route from OpenStreetMap data (`scripts/build-map.mjs`). It writes `src/static/img/map/mauritius.svg`, `src/_data/mapFrame.json` and `src/_data/route.json` (the route path, its length and where each stop falls). It reuses Island Explorer's downloaded data when present. On desktop the map is pinned while the route draws itself around the island.

Motion (GSAP + ScrollTrigger + SplitText, in `src/assets/js/motion.js`): hero camera dolly in on load and out on scroll, a pinned dolly reveal of the lagoon photo, word-by-word headings, counting stats, a destinations marquee, scroll zoom on photos, drawn lines, magnetic buttons and the coast route. All of it respects `prefers-reduced-motion`. Every page works without JavaScript (the booking page shows a rate table instead of the live summary).
