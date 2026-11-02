import { initGallery, initHeader, initMap, initMobileMenu, initMortgage, initPropertyFilter } from "./ui.js";
import { initMotion } from "./motion.js";

window.__motionReady = true;

initHeader();
initMobileMenu();
initPropertyFilter();
initMap();
initGallery();
initMortgage();
initMotion();
