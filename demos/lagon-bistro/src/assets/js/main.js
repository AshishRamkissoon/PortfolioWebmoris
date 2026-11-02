import { initHeader, initMapEmbed, initMenuFilter, initMenuPreview, initMobileMenu } from "./ui.js";
import { canWebGL, initMotion, motionAllowed } from "./motion.js";

window.__motionReady = true;

initHeader();
initMobileMenu();
initMenuFilter();
initMapEmbed();
initMotion();
if (motionAllowed()) initMenuPreview();

// Hero sunset shader: separate chunk, desktop-class devices only.
const sunset = document.querySelector("[data-sunset]");
if (sunset && motionAllowed() && canWebGL()) {
  import("./sunset.js").then(({ initSunset }) => initSunset(sunset));
}
