import { initAddButtons, initMenuTabs, initMobileMenu, initOrder, initToday } from "./ui.js";
import { initMotion } from "./motion.js";

window.__motionReady = true;

initMobileMenu();
initAddButtons();
initMenuTabs();
initToday();
initOrder();
initMotion();
