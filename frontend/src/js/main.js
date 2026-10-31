import Alpine from "alpinejs";
import htmx from "htmx.org";

import { initHeader } from "./modules/header.js";
import { initReveals, initSmoothScroll } from "./modules/motion.js";

window.htmx = htmx;
window.Alpine = Alpine;
Alpine.start();

initSmoothScroll();
initReveals();
initHeader();

// Animate content that HTMX swaps in (filters, "load more", forms).
document.body.addEventListener("htmx:afterSwap", (event) => initReveals(event.target));
