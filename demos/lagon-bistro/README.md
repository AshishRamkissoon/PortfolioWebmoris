# Lagon Bistro — restaurant / beach bar demo

A demo of the Webmoris "Lagon Bistro" ready-made website. Lagon Bistro is a **fictional** beach restaurant at Flic en Flac, Mauritius. The demo kit (`../../demo_kit/demo-kit.js`) adds the "Demo by Webmoris" bar, blocks every form and keeps the site out of search engines.

## Run it

```
npm install
npm run build     # builds the site into _site/
npm run serve     # http://127.0.0.1:5003 (rebuilds pages on save; run `npm run build` after CSS/JS changes)
```

`_site/` is the whole website as static files; deploy it as-is (see `deploy/nginx.conf.example`).

## Content

- **Site details, hours, the day timeline and events:** `src/_data/site.json`
- **Menu** (sections, dishes, prices, dietary tags, cocktail colours): `src/_data/menu.json`. Dishes with `"signature": true` appear on the home page; drinks with a `photo` and `color` appear in the cocktail reel.
- **Photos and credits:** `src/_data/photos.json`, files in `src/images/photos/` (all from Wikimedia Commons, credited on `/credits/`).
- **Map:** the OpenStreetMap base map is shared with Island Explorer (`npm run build:map` there regenerates it).

## Visual effects

- **Hero:** the sunset photo is re-drawn with WebGL (`src/assets/js/sunset.js`): the sea shimmers and glitters, the palms sway, and ripples and a warm glow follow the mouse. Desktop with a real GPU only; it switches itself off below ~30 fps.
- **Our day:** a pinned scene where the sky turns from noon to sunset to night as you scroll, with a running clock, stars, moon and festoon lights.
- **Cocktails:** a pinned horizontal reel whose background takes each drink's colour.
- **Also:** split-text headlines, a scroll-velocity marquee, floating photo previews on dish names, 3D tilt cards, magnetic buttons, a custom cursor and film grain.

Everything respects `prefers-reduced-motion` and the content works without JavaScript.
