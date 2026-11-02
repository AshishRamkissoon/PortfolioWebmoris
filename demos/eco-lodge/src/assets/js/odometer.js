import { gsap } from "gsap";

/**
 * Odometer: numbers roll digit by digit, like an analogue dashboard.
 * Works on any element with text such as "Rs 12,400" or "194": digits get their own reel,
 * everything else stays as it is. Screen readers get the plain value (aria-label).
 */
const REEL = "0123456789".split("");

function build(el, text) {
  el.classList.add("odo");
  el.setAttribute("aria-label", text);
  el.textContent = "";
  for (const char of text) {
    if (/\d/.test(char)) {
      const windowEl = document.createElement("span");
      windowEl.className = "odo-digit";
      windowEl.setAttribute("aria-hidden", "true");
      const reel = document.createElement("span");
      reel.className = "odo-reel";
      reel.innerHTML = REEL.map((d) => `<span class="block">${d}</span>`).join("");
      windowEl.append(reel);
      el.append(windowEl);
    } else {
      const span = document.createElement("span");
      span.setAttribute("aria-hidden", "true");
      span.textContent = char === " " ? " " : char; // a plain space would collapse in the flex row
      el.append(span);
    }
  }
  el.dataset.odoText = text;
}

/** Shows `text` on the odometer, rolling each digit to its new position. */
export function setOdometer(el, text, { animate = true, duration = 1 } = {}) {
  text = String(text);
  if (el.dataset.odoText === undefined || el.dataset.odoText.length !== text.length || el.dataset.odoText.replace(/\d/g, "0") !== text.replace(/\d/g, "0")) {
    build(el, text);
  }
  el.dataset.odoText = text;
  el.setAttribute("aria-label", text);
  const reels = el.querySelectorAll(".odo-reel");
  const digits = text.replace(/\D/g, "").split("");
  reels.forEach((reel, i) => {
    const target = -Number(digits[i]) * 10;
    if (animate) gsap.to(reel, { yPercent: target, duration: duration + i * 0.08, ease: "power3.inOut", overwrite: true });
    else gsap.set(reel, { yPercent: target });
  });
}

/** Turns [data-odo] numbers into odometers that roll up from zero when they scroll into view. */
export function initOdometers(ScrollTrigger) {
  document.querySelectorAll("[data-odo]").forEach((el) => {
    const text = el.textContent.trim();
    setOdometer(el, text.replace(/\d/g, "0"), { animate: false });
    ScrollTrigger.create({ trigger: el, start: "top 90%", once: true, onEnter: () => setOdometer(el, text, { duration: 1.4 }) });
  });
}
