# Eco Lodge — nature lodge / guesthouse demo

A demo of the Webmoris "Eco Lodge" ready-made website. Eco Lodge is a **fictional** nature lodge in the Chamarel hills, Mauritius; rooms and prices are examples. The demo kit (`../../demo_kit/demo-kit.js`) adds the "Demo by Webmoris" bar, blocks the booking form and keeps the site out of search engines.

## Run it

```
npm install
npm run build     # builds the site into _site/
npm run serve     # http://127.0.0.1:5006 (rebuilds pages on save; run `npm run build` after CSS/JS changes)
```

`_site/` is the whole website as static files; deploy it as-is (see `deploy/nginx.conf.example`).

## Content

- **Lodge, "book direct" perks, commitments, experiences, FAQ:** `src/_data/site.json`. `directDiscount` (10) sets the saving shown against booking sites.
- **Rooms:** `src/_data/rooms.json` (guests, beds, size, direct price per night, amenities, photos). `seed` gives each room its own demo availability pattern.
- **Photos and credits:** `src/images/photos/` and `src/_data/photos.json` (all from Wikimedia Commons, listed on `/credits/`).
- **Map:** the OpenStreetMap base map shared with the other demos.

## Pages

Home (hero availability search, book-direct perks, rooms, dolly reveal, experiences, commitments, breakfast, location, FAQ), Rooms, one page per room (gallery, amenities, availability calendar, sticky "book direct" card), Book (room, dates with calendar, details, live summary with the saving and the free transfer from 3 nights), Credits, 404.

## Availability calendar

`src/assets/js/ui.js`: two months of free and booked nights (demo availability, deterministic per room), check-in/check-out by clicking, stays can't cross a booked night, synced with the date inputs. On a client's live site it would read real availability from their booking system or channel manager.

## Motion

GSAP + ScrollTrigger + SplitText: hero camera dolly, a pinned dolly reveal, word-by-word headings, counting figures, scroll zoom on photos, magnetic buttons. Everything respects `prefers-reduced-motion`, and every page works without JavaScript (the booking page shows a rate table and plain date inputs).
