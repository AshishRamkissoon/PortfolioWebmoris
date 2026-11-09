# Webmoris demo kit

Use this on **every public demo** of a ready-made website (for example `bistro.demo.webmoris.mu`).

## 1. Include the script
Copy `demo-kit.js` into the demo's static files and add it to every page as the **first element inside `<body>`**, without `defer`. That way the bar is in place before the first paint and nothing jumps (no layout shift):

```html
<body>
<script src="/static/demo-kit.js"
        data-template="lagon-bistro"
        data-agency="https://webmoris.mu"
        data-lang="en"></script>
```

- **`data-template`**: the template's slug on webmoris.mu. The bar's button opens that template's enquiry form.
- **`data-lang`**: `en` or `fr`.

If the demo has a fixed header, position it below the bar with `top: var(--demo-bar-h, 0px)`. The kit sets that variable to the bar's height.

The script does three things:
- shows a "Demo website by Webmoris" bar with a "Get this website" button
- blocks every form submission and shows a short explanation instead
  (one exception: a same-site `method="get"` form marked `data-demo-navigation`, such as a search bar that only opens another demo page)
- adds a `noindex` meta tag

## Optional: badge, "See why it converts" tour, mobile bar, nudge
Serve a `demo-tour.json` next to `demo-kit.js`, and copy `demo-kit.css` there too. Without the JSON file, the kit only shows the bar (as before). So that the badge appears as soon as the page loads, link both files in the demo's `<head>`:

```html
<link rel="stylesheet" href="/demo-kit.css">
<link rel="preload" href="/demo-tour.json" as="fetch" crossorigin="anonymous">
``` Lagon Bistro is the reference: `demos/lagon-bistro/src/static/demo-tour.json`.

- **`badge`:** `price` (text, or `null` for "Price on request") and `pitch` (EN/FR).
- **`stops`:** the tour, in page order. Each stop has a CSS `target` (prefer `data-tour="…"` attributes in the demo's templates) and EN/FR `title`, `text` and `why`. Stops whose element is missing or hidden (for example on phones) are skipped.
- **`blueprint`:** the page sections as a journey (Attention → Interest → Desire → Trust → Action), each with a `target` section.
- **`mobileBar`:** phones only. Call and WhatsApp show a "this is a demo" notice, so no real number is ever dialled; `action` links to a page of the demo.
- **`nudge`:** shown once after the visitor scrolls past the `after` section.
- **`theme`:** the demo's own colours for the mobile bar and the nudge.

No cookies, no tracking, no requests outside the demo. Everything works with the keyboard (Esc closes, arrow keys move through the tour) and stays still for visitors who turn animations off. The kit speaks French to browsers set to French.

## 2. Keep demos out of Google (server side)
The meta tag is only a backup. Set the header on the whole demo subdomain:

```nginx
# inside the demo's server { } block
add_header X-Robots-Tag "noindex, nofollow" always;
location = /robots.txt { return 200 "User-agent: *\nDisallow: /\n"; }
```

## 3. Checklist before publishing a demo
- [ ] **Fictional names only:** business names, people and addresses are invented. Never use a real company.
- [ ] **No fake social proof:** no invented testimonials, reviews, star ratings or "X happy customers" counters.
- [ ] **Licensed images:** your own photos, or properly licensed stock. Keep a note of the source.
- [ ] **Safe forms:** every form is blocked by the kit. Test it by submitting each form once.
- [ ] **Content stays fictional:** no real phone numbers or emails. Use `+230 5000 0000` / `hello@example.com`.
- [ ] **Search engines blocked:** `X-Robots-Tag` header set and `robots.txt` disallows everything.
- [ ] **Linked from the main site:** paste the demo URL into the template's "Live demo URL" field in Webmoris admin.
- [ ] **Health check:** Lighthouse, mobile check, and no console errors.
