# Drive Moris — Creative Direction

> **Revised 2026-11-01.** The owner reviewed the first build ("Coast Road", a dark, cinematic road-sign look, described from section 1 onwards) and asked for something more intuitive, professional and appealing. They chose the **"Bright island"** direction below, and the demo was rebuilt to it. The original concept is kept underneath for reference; where they differ, this section wins.
>
> **Bright island**
> - **Feel:** light, airy and trustworthy, like a leading travel brand. Built for a tourist who has just landed and wants a car without effort.
> - **Colour:** white and soft sand backgrounds, deep lagoon blue `#0e6e8c` for brand and links, coral `#ff6b4a` only for the main actions ("Book a car", "See prices"), dark ink `#0f2433` for text.
> - **Type:** Plus Jakarta Sans throughout, sentence case, bold friendly headings.
> - **Photos:** full colour, rounded corners, real Mauritius roads and coast.
> - **Structure:** search first (dates and car in the hero), then benefits, popular cars as clear cards (photo, seats, bags, gearbox, price, Book), how it works in 3 steps, the coast route on the map, day trips, FAQ and a call to action. Car pages have a sticky summary card; the booking page has 4 numbered steps and a live price summary.
> - **Colour (update):** deeper lagoon blues (`#08394d` to `#0e6e8c`) with turquoise `#2fd3cf` and a coral-to-sun gradient (`#ff6b4a` → `#ffb547`) on the main buttons and accent words.
> - **Motion (update, owner asked for more VFX):** a full-bleed hero photo with a camera dolly (pushes in on load, pulls further in and fades the text on scroll, slight mouse parallax); a pinned "dolly reveal" where a framed lagoon photo widens to fill the screen; word-by-word headings; counting stats; a destinations marquee; photos that zoom while they scroll; a line that draws between the booking steps; magnetic buttons; the coast route. Reduced motion turns all of it off.
> - **Conversion:** search card in the hero, prices visible everywhere, and a "Book now" bar always on screen on phones.

---

A demo website for a **fictional** car rental company at the airport in Mauritius. It's the third Webmoris live demo, after Island Explorer (tourism) and Lagon Bistro (restaurant). This brief sets the creative direction and also specifies how to build it, so it can be built as written.

---

## 1. The idea: "Coast Road"

Most car rental websites sell **cars**: a grid of hatchbacks on white backgrounds, a date picker, a price. Drive Moris sells **the road**.

Mauritius is small enough that one road runs around the whole coast. Every visitor lands at the airport in the south-east, and from there the island is theirs. The website plays out like the opening of a road movie: the night drive out of the airport, sugarcane on both sides, then the coast at dawn. The cars appear as the way to get there, not as stock.

**One sentence:** *the island is a road, and this is your key to it.*

**Headline:** "The whole island. One key."
**Supporting line:** "Pick up at the airport. Hand back wherever the road ends."

### Three emotions, in order
1. **Anticipation:** night, headlights, an empty road. The moment just after landing.
2. **Freedom:** the coast opening up, place names passing like road signs.
3. **Confidence:** clear prices, honest terms, a car ready at arrivals. The calm a traveller wants after a long flight.

The design moves through these three states from top to bottom of the home page.

---

## 2. What it must not look like

These are rules, not suggestions:

- **No** white-background car grids, gradient blobs, glassmorphism cards, bento grids or floating 3D phone mock-ups.
- **No** testimonial carousel, star ratings, "trusted by 10,000 drivers" or award badges. The business is fictional, so all social proof would be fake.
- **No** sports cars or luxury clichés. The fleet is what tourists really rent: small, honest cars. The premium feeling comes from the craft, not the price tag.
- **No** stock photos of smiling couples with keys.
- **No** bouncy, playful easing. Cars don't bounce.

---

## 3. Art direction: the language of the road

Everything visual comes from one source: **road infrastructure.** Signs, lane markings, tarmac, sodium streetlights, kilometre posts, dashboard instruments. It's a world everyone recognises, it's almost never used for websites, and it belongs to this business.

| Road element | Becomes on the website |
|---|---|
| Lane markings (dashed white line) | Section dividers, scroll progress, the hero animation |
| Road signs (white text on dark green or black panels) | Navigation, place names, section titles |
| Kilometre posts | Section numbers: "KM 00", "KM 12", "KM 47" |
| Dashboard instruments | Prices, the trip calculator, fuel and seat counts |
| Sodium streetlight amber | The single accent colour: calls to action and highlights |
| Tarmac | The page background, with real grain |
| Tail lights | One rare red, used only to mark something as selected |

### Composition
- **Letterboxed frames.** Large images use a cinema ratio (2.39:1) with thin black bars, like stills from a film. This one choice makes the site feel like a film rather than a template.
- **Strong horizontals.** Lines run edge to edge, like the horizon or the road. Very little is centred. Layouts are asymmetric, with the eye always pulled **left to right**, the direction of travel.
- **Big type, small type, nothing in between.** Huge condensed headlines set against small monospace data. That contrast is the signature of road signs and instrument panels.
- **Generous darkness.** At least half of every screen is empty tarmac, which leaves room to breathe and makes the amber stand out.

---

## 4. Typography

Three typefaces, each with one job. All are free, open-licence fonts, self-hosted like the other demos.

| Role | Typeface | Why |
|---|---|---|
| **Display:** headlines, place names, prices | **Big Shoulders Display** (Black, 900) | A tall, condensed civic signage face. It reads like a road sign from a distance and holds huge sizes without feeling loud. |
| **Text:** body copy, buttons, forms | **Barlow** (400 / 500 / 600) | Drawn from the lettering on California highway signs. A calm partner to the display face, from the same world. |
| **Data:** prices, times, specs, km markers | **IBM Plex Mono** (400 / 500) | Instrument-panel figures. Monospaced digits line up and can roll like an odometer. |

**Rules**
- Display face always in **uppercase**, tight tracking (−1%), line height 0.85. Sizes from 64 px on mobile up to about 220 px on desktop.
- Body text 17–19 px, line height 1.55, never wider than about 60 characters.
- Every number on the site (prices, kilometres, times, seats) uses the mono face with `tabular-nums`.
- Labels and eyebrows: mono, uppercase, 12 px, tracking 0.2em, preceded by a short dash like a lane marking: `— KM 12 · THE FLEET`.

Font availability on Fontsource is to be confirmed when the project is set up; if a face isn't available, swap for the nearest open-licence equivalent (for example Anton for display).

---

## 5. Colour

A palette taken from the road at night, with one light source.

| Name | Hex | Use |
|---|---|---|
| **Tarmac** | `#111213` | Page background |
| **Asphalt** | `#1b1d1f` | Raised surfaces: panels, forms |
| **Kerb** | `#2a2d30` | Lines, borders, quiet UI |
| **Road white** | `#efece4` | Main text, lane markings (warm, never pure white) |
| **Dust** | `#8c8a83` | Secondary text |
| **Sodium** | `#ffae1a` | The accent: calls to action, active states, highlights. Used sparingly. |
| **Sign green** | `#1f3d2e` | Road-sign panels in navigation and place names |
| **Cane** | `#9db06a` | Sugarcane in the hero and the map's inland fields |
| **Lagoon** | `#2e7d84` | The sea, on the map only |
| **Tail light** | `#e2412f` | Only for "selected" (the chosen car, the active filter) |

**Proportion:** about 80% tarmac and asphalt, 15% road white, 5% sodium. Sign green, cane, lagoon and tail-light red appear only where they mean something.

Contrast: road white on tarmac and tarmac on sodium both pass WCAG AA. Sodium text on tarmac is used only at large sizes.

---

## 6. Imagery, lighting and texture

### The problem, and the answer
Free licensed photos of cars and Mauritian roads all differ in colour, light and quality. Laid side by side, they'd look like a template.

**The answer is one consistent darkroom treatment.** Every photo goes through the same grade at build time:
- a **duotone** from tarmac (shadows) to road white (highlights)
- **sodium amber** added only to the brightest highlights, as if lit by streetlights
- the same grain, and a slight vignette

The photos then look like stills from one film, and the colour in each frame comes from the light, not the source. This is a design decision that also makes free photography cohesive.

### What we show
- **Roads of Mauritius**, not cars on white: coastal roads, sugarcane lanes, mountain switchbacks, villages at dusk. Sourced from Wikimedia Commons, each checked and credited as in the other demos.
- **Cars:** real, everyday models (compact, SUV, 7-seater, convertible), shown on location with the same grade. No brand logos in close-up.
- **No people's faces.** Hands on a steering wheel, a silhouette at a viewpoint, at most.

### Lighting
Night and the edges of the day only: **blue hour** and **golden hour**. Light sources are headlights, streetlights and the low sun. Never flat midday light.

### Textures and depth
- **Tarmac grain:** a fine noise texture across the whole page (CSS, like Lagon Bistro's film grain, but coarser and static).
- **Road paint:** lane markings are slightly rough-edged (SVG with a subtle displacement filter), not perfect vector lines.
- **Depth by light, not shadows:** elements sit forward when lit by a soft amber glow, not with drop shadows. No glass, no blur panels.

---

## 7. Motion language: "always forward"

Motion is how the site feels like driving. Three principles.

1. **Direction: left to right.** Things enter from the right and leave to the left, like scenery from a car window. Nothing drops from above or pops from the centre.
2. **Weight: clutch and brake.** Movement starts gently and stops firmly, with no overshoot and no bounce. Standard easing is `power3.inOut` for travel and `expo.out` for arrivals; durations are 0.6–1.2 s.
3. **Speed follows the scroll.** The faster you scroll, the faster the road moves. Stop scrolling and the scene coasts to a halt.

### Signature motions
| Name | What happens |
|---|---|
| **Night drive** (hero) | A WebGL road at night, drawn with code rather than a photo: lane dashes rush towards the viewer, cane fields pass in silhouette, headlight glow sweeps across. The mouse steers slightly left and right. Scrolling accelerates it. |
| **Odometer** | Prices and kilometres roll digit by digit like an analogue odometer, never just fading in. |
| **Sign pass** | Section titles arrive like road signs: a green or black panel slides in from the right, then the text appears. |
| **Lane line** | One continuous dashed line runs down the left edge of the page. It fills as you scroll and is the page's progress bar. |
| **Truck pass** (page transitions) | Moving between pages, a black panel sweeps across the screen left to right, like a lorry passing close. Uses cross-document view transitions, as in Island Explorer. |

### Respect and restraint
- With `prefers-reduced-motion`: no WebGL, no scroll-driven movement; content simply appears. The odometer shows final numbers.
- Without JavaScript: every page is complete and readable.
- WebGL only on capable desktops with a real GPU, with the same frame-rate safety switch as the other demos. Phones get a still, graded frame.

---

## 8. The pages

### Home: one drive, top to bottom
The home page is a single journey. Each section is a kilometre marker.

1. **KM 00 · Arrivals.** Full-screen night drive (WebGL). Headline "THE WHOLE ISLAND. ONE KEY." Below it, a quick quote bar styled like a dashboard: pick-up date, return date, car type, "See prices". It works without JavaScript as a plain form leading to the Book page.
2. **KM 04 · The promise.** Three plain statements set like road signs on green panels: *Car waiting at arrivals.* *Full insurance in the price.* *Hand it back anywhere on the island.* No icons.
3. **KM 12 · The coast.** The signature section. The real map of Mauritius (the OpenStreetMap base map already built for the other demos) is pinned while you scroll, and a route draws itself around the island along the real coast roads. Place names pass on sign panels as the line reaches them: Mahébourg, Blue Bay, Souillac, Le Morne, Flic en Flac, Port Louis, Grand Baie, Belle Mare. An odometer counts the kilometres. Each stop shows one graded, letterboxed photo.
4. **KM 47 · The fleet.** Not a grid. A single **garage stage**: one car at a time, large, on a dark floor under one light. Arrows (or swiping on phones) change the car; the spec panel is set like an instrument cluster (seats, bags, gearbox, air conditioning, price per day in odometer digits).
5. **KM 60 · Five drives.** A strip of five suggested day trips (south coast, Chamarel and the gorges, the north, the east lagoons, Port Louis and the west). Each is a letterboxed frame with distance and driving time. This content is what makes people want a car at all.
6. **KM 72 · Honest terms.** What's included, the deposit, fuel policy, driving on the left, plus a short FAQ, set like the small print on a rental agreement, but readable.
7. **KM 80 · Hand-back.** Closing call to action. Enormous display type: "THE ROAD'S READY." with the amber button, and the WhatsApp link that leads to the Webmoris enquiry form (as in the other demos).

### Fleet
All cars, filterable by size, seats and gearbox. Each car is a wide, letterboxed "specimen" row (not a card): photo on the left, instrument-style specs on the right, price per day. Filtering animates with GSAP Flip, moving left to right.

### Car page (one per car)
- A large, graded hero of the car on location.
- **Turntable:** where we have photos from several angles, a drag-to-rotate view. Otherwise a short sequence of letterboxed stills.
- The instrument-cluster spec panel.
- The trip calculator (below), with this car pre-selected.

### Book: the trip calculator
The working tool of the site, built like a dashboard rather than a form.
- Pick-up and return: date, time, place (airport, hotel, Port Louis office).
- Car, then extras: child seat, second driver, GPS, full-to-full or prepaid fuel.
- A live **trip ticket** on the right: number of days, daily rate, extras, delivery fee, total. Every figure rolls like an odometer when it changes.
- Name, email, flight number. The demo kit blocks submission, as in the other demos.
- Without JavaScript the form still submits to the demo kit, and prices are shown as a static table.

### Also
Credits (photo licences and OpenStreetMap), 404 ("You took a wrong turn", with a U-turn sign), and the demo bar on every page.

---

## 9. Content (fictional, honest)

- **Company:** Drive Moris, a small family rental company based near the airport at Plaine Magnien. Invented phone (`+230 5000 0000`) and email (`hello@example.com`).
- **Fleet:** about 8 cars across 4 classes (city, compact SUV, 7-seater, convertible), using real everyday models. Daily prices in MUR, clearly marked as example prices.
- **Data files**, like the other demos: `site.json` (company, promises, terms, FAQ), `fleet.json` (cars, specs, prices, photos), `drives.json` (the five day trips, with coordinates for the route), `photos.json` (credits).
- **Banned:** reviews, ratings, customer counts, "best" or "cheapest" claims, real company names.

---

## 10. How it gets built

Same foundation as Island Explorer and Lagon Bistro, so it's predictable to build and maintain:

- **Eleventy + Tailwind 4 + esbuild**, static output, deployed to a subdomain.
- **GSAP** (ScrollTrigger, SplitText, Flip) and **Lenis** for motion.
- **Plain WebGL** for the night-drive hero (a procedural shader: no photo, no Three.js), lazy-loaded on capable desktops only.
- **The OpenStreetMap map** already built in this repo, plus the road data from the same download to draw the real coast route.
- **The photo grade** (duotone, amber highlights, grain) applied at build time with Sharp, so every photo ships already graded and light.
- **Demo kit** first in `<body>`, `noindex`, blocked forms.

### Quality bar (same as the other demos)
- Mobile LCP ≤ 2.5 s, CLS ≤ 0.1, no console errors.
- Every page complete without JavaScript and with reduced motion.
- Contrast AA for all text.
- Every photo credited.

### Suggested order
1. Fonts, colours, grain, lane line, sign panels: the design system.
2. The night-drive hero and the dashboard quote bar.
3. The coast route on the map, with the odometer.
4. The garage stage, fleet page and car pages.
5. The trip calculator and Book page.
6. Photo sourcing and grading; credits.
7. QA, speed, screenshots for the Webmoris ready-made card.

---

## 11. Why this will be remembered

A visitor will forget the colours and the fonts. They'll remember three moments:

1. **The night drive** on arrival: the feeling of landing and driving off.
2. **The route drawing itself around the island**, with the odometer counting.
3. **The trip ticket** whose numbers roll as they choose their car.

Each one is tied to the business, so they don't just look good: they're the reasons to book.
