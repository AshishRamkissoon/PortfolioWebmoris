# Street Food Co. — food truck / takeaway demo

A demo of the Webmoris "Street Food Co." ready-made website. Street Food Co. is a **fictional** Mauritian food truck; menu and prices are examples. The demo kit (`../../demo_kit/demo-kit.js`) adds the "Demo by Webmoris" bar, blocks the order form and keeps the site out of search engines.

## Run it

```
npm install
npm run build     # builds the site into _site/
npm run serve     # http://127.0.0.1:5007 (rebuilds pages on save; run `npm run build` after CSS/JS changes)
```

`_site/` is the whole website as static files; deploy it as-is (see `deploy/nginx.conf.example`).

## Content

- **Business, weekly schedule (day, place, hours, coordinates), steps, FAQ:** `src/_data/site.json`
- **Menu:** `src/_data/menu.json` (categories, dishes, prices, veg/spicy tags; `best: true` shows on the home page).
- **Photos and credits:** `src/images/photos/` and `src/_data/photos.json` (all from Wikimedia Commons, listed on `/credits/`).

## Ordering

`src/assets/js/ui.js`: "Add" buttons put dishes in a basket kept in `localStorage`, with the count on the Order button and a little fly-to-bag animation. The order page prefills from the basket, adds −/+ steppers and a live total. Without JavaScript, "Add" links to the dish on the order page, which is a plain form with quantity boxes. On a client's live site the order would go to WhatsApp, email or a POS.

"Find the truck" highlights today's stop on the list and the map, and the hero shows where the truck is today.

## Motion

GSAP + ScrollTrigger + SplitText: word-by-word headings, reveals, counters, scroll zoom, magnetic buttons, plus CSS stickers that wiggle, float and spin. Everything respects `prefers-reduced-motion`.
