import { gsap } from "gsap";
import { Flip } from "gsap/Flip";

import { setOdometer } from "./odometer.js";

gsap.registerPlugin(Flip);

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Header: transparent over the hero, solid once you scroll. */
export function initHeader() {
  const header = document.querySelector("[data-header]");
  if (!header) return;
  const update = () => header.classList.toggle("is-solid", window.scrollY > 10);
  update();
  window.addEventListener("scroll", update, { passive: true });
}

export function initMobileMenu() {
  const button = document.querySelector("[data-menu-button]");
  const menu = document.getElementById("mobile-menu");
  if (!button || !menu) return;
  const setOpen = (open) => {
    menu.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    if (open && !reducedMotion()) {
      gsap.from(menu.querySelectorAll("[data-menu-link]"), { y: 12, autoAlpha: 0, stagger: 0.04, duration: 0.4, ease: "power2.out" });
    }
  };
  button.addEventListener("click", () => setOpen(menu.hidden));
  menu.querySelectorAll("[data-menu-link]").forEach((link) => link.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !menu.hidden) {
      setOpen(false);
      button.focus();
    }
  });
}

/** Fleet filter: plain links without JS; with JS it filters the cards in place with a smooth Flip animation. */
export function initFleetFilter() {
  const nav = document.querySelector("[data-filters]");
  const list = document.querySelector("[data-fleet]");
  if (!nav || !list) return;
  const rows = [...list.querySelectorAll("[data-class]")];
  const buttons = [...nav.querySelectorAll("[data-filter]")];
  const count = document.querySelector("[data-fleet-count]");
  const apply = (filter, animate) => {
    const state = Flip.getState(rows);
    let shown = 0;
    rows.forEach((row) => {
      const match = filter === "all" || row.dataset.class === filter;
      row.hidden = !match;
      shown += match ? 1 : 0;
    });
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filter === filter)));
    if (count) count.textContent = String(shown);
    if (!animate || reducedMotion()) return;
    Flip.from(state, {
      duration: 0.7,
      ease: "power3.inOut",
      absolute: true,
      onEnter: (els) => gsap.fromTo(els, { autoAlpha: 0, scale: 0.94 }, { autoAlpha: 1, scale: 1, duration: 0.6, ease: "power3.out" }),
      onLeave: (els) => gsap.to(els, { autoAlpha: 0, scale: 0.94, duration: 0.3 }),
    });
  };
  buttons.forEach((button) =>
    button.addEventListener("click", (event) => {
      event.preventDefault();
      apply(button.dataset.filter, true);
      history.replaceState(null, "", button.dataset.filter === "all" ? "/fleet/" : `/fleet/?class=${button.dataset.filter}`);
    }),
  );
  const initial = new URLSearchParams(location.search).get("class");
  if (initial && buttons.some((b) => b.dataset.filter === initial)) apply(initial, false);
}

/**
 * Book page: the booking summary. Days × daily rate, extras, delivery fees and the total update live,
 * each figure rolling like an odometer. Without JS the form still submits (the demo kit stops it)
 * and the price table below shows the rates.
 */
export function initTripTicket() {
  const form = document.querySelector("[data-trip]");
  const ticket = document.querySelector("[data-ticket]");
  if (!form || !ticket) return;
  const config = JSON.parse(document.getElementById("trip-data").textContent);
  ticket.hidden = false;
  document.querySelector("[data-ticket-fallback]")?.setAttribute("hidden", "");

  // Values from the home page's quote bar (?pickup_date=…&return_date=…&car=…).
  const query = new URLSearchParams(location.search);
  for (const name of ["pickup_date", "return_date"]) if (query.get(name)) form[name].value = query.get(name);
  const preselect = query.get("car");
  if (preselect) {
    const radio = form.querySelector(`input[name="car"][value="${CSS.escape(preselect)}"]`);
    if (radio) radio.checked = true;
  }
  // Sensible default dates: tomorrow for a week.
  const day = (offset) => new Date(Date.now() + offset * 86400000).toISOString().slice(0, 10);
  if (!form.pickup_date.value) form.pickup_date.value = day(1);
  if (!form.return_date.value) form.return_date.value = day(8);

  const out = (name) => ticket.querySelector(`[data-out="${name}"]`);
  const money = (amount) => `Rs ${Math.round(amount).toLocaleString("en-US")}`;
  let first = true;
  const update = () => {
    const pickup = new Date(`${form.pickup_date.value}T${form.pickup_time.value || "10:00"}`);
    const back = new Date(`${form.return_date.value}T${form.return_time.value || "10:00"}`);
    const days = Math.max(1, Math.ceil((back - pickup) / 86400000) || 1);
    const car = config.cars.find((c) => c.slug === form.car.value) || config.cars[0];
    const extras = config.extras.filter((extra) => form.querySelector(`input[name="extras"][value="${extra.value}"]`)?.checked);
    const extrasTotal = extras.reduce((sum, extra) => sum + extra.price * (extra.per === "day" ? days : 1), 0);
    const fee = (name) => config.places.find((p) => p.value === form[name].value)?.fee || 0;
    const delivery = fee("pickup_place") + fee("return_place");
    const rental = car.price * days;
    const total = rental + extrasTotal + delivery;

    out("car").textContent = car.name;
    out("dates").textContent = `${form.pickup_date.value || "—"} → ${form.return_date.value || "—"}`;
    const roll = (name, text) => setOdometer(out(name), text, { animate: !first && !reducedMotion(), duration: 0.7 });
    roll("days", String(days));
    roll("rate", money(car.price));
    roll("rental", money(rental));
    roll("extras", money(extrasTotal));
    roll("delivery", money(delivery));
    roll("total", money(total));
    out("warning").hidden = back > pickup;
    first = false;
  };
  form.addEventListener("input", update);
  form.addEventListener("change", update);
  update();
}
