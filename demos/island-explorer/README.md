# Island Explorer — Webmoris demo website

A **fictional** Mauritius tour operator, built as the live demo for the "Island Explorer" ready-made website on webmoris.mu.

It is a static site: Eleventy and Tailwind generate plain HTML, so it is fast, cheap to host and has nothing to hack.

## Develop
```bash
npm install
npm run build          # first build encodes all photos (slow once, then cached)
npm run serve          # http://localhost:5002 (Eleventy dev server)
```
- **Tours:** `src/_data/tours.json`. Add a tour there, and its page, card and map pin are generated automatically. Each tour has real coordinates (`lat`/`lng`), an optional `meet` point (`name`, `time`, `lat`, `lng`) and a `pickup` time (or `null`). Town labels on the map live in `src/_data/mapPlaces.json`.
- **Photos:** `src/images/photos/`, with credits in `src/_data/photos.json`. The build turns them into responsive AVIF, WebP and JPEG files.
- **Site text:** `src/_data/site.json` holds the brand, FAQs, promises and booking steps.

## What makes it feel premium
- **Hero:** the photo comes alive. The lagoon gently moves and ripples follow the mouse (plain WebGL, desktop only, about 3 KB), over a slow Ken Burns zoom. It's skipped on software (no-GPU) renderers and switches itself off if the first second drops below ~30 fps.
- **Page transitions:** a tour card's photo morphs into the tour page header, using cross-document view transitions (Chrome and Edge; other browsers get a normal page load).
- **Scrolling:**
  - smooth scrolling with Lenis
  - headlines rise word by word, and photos wipe in
  - layered parallax
  - the featured tours slide sideways while the section is pinned
  - itinerary and booking-step lines draw themselves
- **Small touches:** a scrolling destinations ticker, drifting waves, magnetic buttons, a filter that rearranges with animation (GSAP Flip), a pulsing map pin and a gallery lightbox.
- **Accessibility:** all motion is off for visitors who prefer reduced motion. The hero headline uses CSS animation only, so it never waits for JavaScript.

## Demo safety
`demo-kit.js` (from `../../demo_kit/`) is on every page:
- it shows the "Demo website by Webmoris" bar
- **it blocks every form**
- it adds `noindex`

`robots.txt` disallows everything. Follow the checklist in `demo_kit/README.md` before publishing.

## Deploy (subdomain, e.g. `tours.demo.webmoris.mu`)
1. Run `npm run build` and upload `_site/` to `/srv/webmoris/demos/island-explorer/`.
2. Add `deploy/nginx.conf.example` as a server block, then run `certbot --nginx -d tours.demo.<domain>`.
3. In Webmoris admin, open the "Island Explorer" template and paste the URL into **Live demo URL**. This turns on the "Live demo" badge and button.
