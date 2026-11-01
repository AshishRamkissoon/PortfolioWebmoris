// CSP-safe Alpine build: evaluates x-* expressions without eval()/new Function().
import Alpine from "@alpinejs/csp";
import htmx from "htmx.org";

import { initHeader } from "./modules/header.js";
import { registerAnalytics } from "./modules/analytics.js";
import { registerMediaComponents } from "./modules/media.js";
import { registerUiComponents } from "./modules/ui.js";
import {
  canRenderHero,
  initCountUps,
  initHorizontalScroll,
  initMagnetic,
  initReveals,
  initSmoothScroll,
  initSplitHeadings,
  initTilt,
} from "./modules/motion.js";

// Hardening: no eval-based htmx features, and no injected <style> (we style indicators in CSS).
htmx.config.allowEval = false;
htmx.config.includeIndicatorStyles = false;
window.htmx = htmx;
window.Alpine = Alpine;
registerUiComponents(Alpine);
registerMediaComponents(Alpine);
registerAnalytics(Alpine);
Alpine.start();

initSmoothScroll();
initReveals();
initSplitHeadings();
initCountUps();
initHorizontalScroll();
initMagnetic();
initTilt();
initHeader();

// Home hero 3D visual: separate chunk, only on capable devices.
const hero3d = document.querySelector("[data-hero-3d]");
if (hero3d && canRenderHero()) {
  import("./modules/hero3d.js").then(({ initHero3D }) => initHero3D(hero3d));
}

// Only order pages have [data-paypal]; the PayPal module is a separate, lazily loaded chunk.
if (document.querySelector("[data-paypal]")) {
  import("./modules/paypal.js").then(({ initPayPal }) => initPayPal());
}

// Animate content that HTMX swaps in (filters, "load more", forms). Already-revealed
// elements are skipped, so rescanning the document is cheap and survives outerHTML swaps.
document.body.addEventListener("htmx:afterSettle", () => {
  initReveals();
  initSplitHeadings();
  initTilt();
});
