# Villa Select — real estate demo

A demo of the Webmoris "Villa Select" ready-made website. Villa Select is a **fictional** estate agency in Mauritius; all listings and prices are examples. The demo kit (`../../demo_kit/demo-kit.js`) adds the "Demo by Webmoris" bar, blocks the viewing and contact forms and keeps the site out of search engines.

## Run it

```
npm install
npm run build     # builds the site into _site/
npm run serve     # http://127.0.0.1:5005 (rebuilds pages on save; run `npm run build` after CSS/JS changes)
```

`_site/` is the whole website as static files; deploy it as-is (see `deploy/nginx.conf.example`).

## Content

- **Agency, benefits, buying steps, FAQ, property types, budgets:** `src/_data/site.json`
- **Listings:** `src/_data/properties.json`. Each has real coordinates (`lat`/`lng`) for the map, price in USD, specs, features and photos. `"featured": true` shows it on the home page.
- **Areas:** `src/_data/areas.json`
- **Photos and credits:** `src/images/photos/` and `src/_data/photos.json` (all from Wikimedia Commons, listed on `/credits/`).
- **Map:** the OpenStreetMap base map shared with Drive Moris (`src/static/img/map/mauritius.svg` and `src/_data/mapFrame.json`).

## Pages

Home (hero search by area, type and budget; featured homes; every listing on the map; dolly reveal; areas; 4-step buying guide; FAQ), Properties (type chips, area, budget and bedroom filters, synced to the URL), one page per property (gallery with viewer, key facts, features, location, monthly payment estimate, sticky viewing request), Contact (shortlist request), Credits, 404.

## Motion

GSAP + ScrollTrigger + SplitText (`src/assets/js/motion.js`): hero camera dolly in on load and out on scroll, a pinned dolly reveal, word-by-word headings, map pins that drop in, counting stats, a places marquee, scroll zoom on area photos, a drawn line between the buying steps and magnetic buttons. Everything respects `prefers-reduced-motion`, and every page works without JavaScript (all listings shown, forms still submit to the demo kit).
