import { initFleetFilter, initGarage, initHeader, initMobileMenu, initTripTicket, initTurntable } from "./ui.js";
import { canWebGL, initMotion, motionAllowed } from "./motion.js";

window.__motionReady = true;

initHeader();
initMobileMenu();
initGarage();
initFleetFilter();
initTurntable();
initTripTicket();
initMotion();

// Night-drive hero: separate chunk, desktop-class devices only.
const road = document.querySelector("[data-nightdrive]");
if (road && motionAllowed() && canWebGL()) {
  import("./nightdrive.js").then(({ initNightDrive }) => initNightDrive(road));
}
