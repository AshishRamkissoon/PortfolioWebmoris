import { initFilters, initHeader, initLightbox, initMenu } from "./ui.js";
import { canRipple, initMotion, motionAllowed } from "./motion.js";

window.__motionReady = true;

initHeader();
initMenu();
initLightbox();
initFilters();
initMotion();

// Hero water ripple: separate chunk, desktop-class devices only.
const ripple = document.querySelector("[data-ripple]");
if (ripple && motionAllowed() && canRipple()) {
  import("./ripple.js").then(({ initRipple }) => initRipple(ripple));
}
