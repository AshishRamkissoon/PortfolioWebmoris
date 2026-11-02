import { initBooking, initGallery, initHeader, initMobileMenu, initRoomCalendar } from "./ui.js";
import { initMotion } from "./motion.js";

window.__motionReady = true;

initHeader();
initMobileMenu();
initGallery();
initRoomCalendar();
initBooking();
initMotion();
