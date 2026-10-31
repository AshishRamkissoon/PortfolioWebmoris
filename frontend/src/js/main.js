import Alpine from "alpinejs";
import htmx from "htmx.org";

import { initHeader } from "./modules/header.js";
import { registerMediaComponents } from "./modules/media.js";
import {
  initCountUps,
  initHorizontalScroll,
  initReveals,
  initSmoothScroll,
  initSplitHeadings,
} from "./modules/motion.js";

window.htmx = htmx;
window.Alpine = Alpine;
registerMediaComponents(Alpine);
Alpine.start();

initSmoothScroll();
initReveals();
initSplitHeadings();
initCountUps();
initHorizontalScroll();
initHeader();

// Animate content that HTMX swaps in (filters, "load more", forms). Already-revealed
// elements are skipped, so rescanning the document is cheap and survives outerHTML swaps.
document.body.addEventListener("htmx:afterSettle", () => {
  initReveals();
  initSplitHeadings();
});
