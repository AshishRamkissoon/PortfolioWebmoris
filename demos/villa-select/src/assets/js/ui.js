import { gsap } from "gsap";
import { Flip } from "gsap/Flip";

import { setOdometer } from "./odometer.js";

gsap.registerPlugin(Flip);

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const usd = (n) => `$${Math.round(n).toLocaleString("en-US")}`;

/** Header: transparent with white text over the home hero, solid once you scroll. */
export function initHeader() {
  const header = document.querySelector("[data-hero-header]");
  if (!header) return;
  const update = () => {
    const solid = window.scrollY > 40;
    header.classList.toggle("is-solid", solid);
    header.classList.toggle("text-white", !solid);
  };
  update();
  window.addEventListener("scroll", update, { passive: true });
}

export function initMobileMenu() {
  const button = document.querySelector("[data-menu-button]");
  const menu = document.getElementById("mobile-menu");
  if (!button || !menu) return;
  const header = button.closest("[data-header]");
  const setOpen = (open) => {
    menu.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    if (header?.hasAttribute("data-hero-header")) {
      header.classList.toggle("is-solid", open || window.scrollY > 40);
      header.classList.toggle("text-white", !open && window.scrollY <= 40);
    }
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

/**
 * Properties page: type chips, area, budget and bedrooms filter the cards in place (with Flip).
 * Reads the same query string the home search sends (?area=…&type=…&budget=…), and keeps the URL in sync.
 * Without JS every listing is shown.
 */
export function initPropertyFilter() {
  const form = document.querySelector("[data-property-filter]");
  const grid = document.querySelector("[data-property-grid]");
  if (!form || !grid) return;
  const cards = [...grid.querySelectorAll("[data-property]")];
  const chips = [...form.querySelectorAll("[data-type-chip]")];
  const count = document.querySelector("[data-property-count]");
  const empty = document.querySelector("[data-property-empty]");

  const query = new URLSearchParams(location.search);
  for (const name of ["area", "budget", "beds"]) if (query.get(name) && form[name]) form[name].value = query.get(name);
  let type = query.get("type") || "";

  const apply = (animate) => {
    const area = form.area.value;
    const budget = Number(form.budget.value) || 0;
    const beds = Number(form.beds.value) || 0;
    const state = Flip.getState(cards);
    let shown = 0;
    cards.forEach((card) => {
      const match =
        (!type || card.dataset.type === type) &&
        (!area || card.dataset.area === area) &&
        (!budget || Number(card.dataset.price) <= budget) &&
        (!beds || Number(card.dataset.beds) >= beds);
      card.hidden = !match;
      shown += match ? 1 : 0;
    });
    chips.forEach((chip) => chip.setAttribute("aria-pressed", String(chip.dataset.typeChip === type)));
    if (count) count.textContent = String(shown);
    if (empty) empty.hidden = shown > 0;
    const params = new URLSearchParams();
    if (type) params.set("type", type);
    if (area) params.set("area", area);
    if (budget) params.set("budget", String(budget));
    if (beds) params.set("beds", String(beds));
    history.replaceState(null, "", params.size ? `?${params}` : location.pathname);
    if (!animate || reducedMotion()) return;
    Flip.from(state, {
      duration: 0.6,
      ease: "power3.inOut",
      absolute: true,
      onEnter: (els) => gsap.fromTo(els, { autoAlpha: 0, scale: 0.94 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: "power3.out" }),
      onLeave: (els) => gsap.to(els, { autoAlpha: 0, scale: 0.94, duration: 0.3 }),
    });
  };
  chips.forEach((chip) =>
    chip.addEventListener("click", (event) => {
      event.preventDefault();
      type = chip.dataset.typeChip;
      apply(true);
    }),
  );
  form.addEventListener("change", () => apply(true));
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    apply(true);
  });
  form.querySelector("[data-filter-submit]")?.setAttribute("hidden", "");
  apply(false);
}

/** Map: hovering or focusing a pin shows its price card; the list beside it highlights the same home. */
export function initMap() {
  const map = document.querySelector("[data-map]");
  if (!map) return;
  const pins = [...map.querySelectorAll("[data-pin]")];
  const items = [...document.querySelectorAll("[data-map-item]")];
  const activate = (slug) => {
    pins.forEach((pin) => pin.classList.toggle("is-active", pin.dataset.pin === slug));
    items.forEach((item) => item.classList.toggle("is-active", item.dataset.mapItem === slug));
  };
  [...pins, ...items].forEach((el) => {
    const slug = el.dataset.pin || el.dataset.mapItem;
    el.addEventListener("pointerenter", () => activate(slug));
    el.addEventListener("focusin", () => activate(slug));
  });
  if (pins[0]) activate(pins[0].dataset.pin);
}

/** Property page gallery: thumbnails swap the main photo; the main photo opens a full-screen viewer. */
export function initGallery() {
  const gallery = document.querySelector("[data-gallery]");
  if (!gallery) return;
  const links = [...gallery.querySelectorAll("[data-gallery-item]")];
  let index = 0;
  let trigger = null;
  const box = document.createElement("div");
  box.className = "fixed inset-0 z-[60] hidden flex-col items-center justify-center gap-4 bg-emerald-950/95 p-4 backdrop-blur";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", "Photo viewer");
  box.innerHTML = `
    <img class="max-h-[80vh] max-w-full rounded-2xl object-contain shadow-2xl" alt="">
    <div class="flex items-center gap-3">
      <button type="button" class="btn btn-white" data-prev>← Prev</button>
      <span class="min-w-14 text-center text-sm text-white/80" data-count></span>
      <button type="button" class="btn btn-white" data-next>Next →</button>
      <button type="button" class="btn btn-primary" data-close>Close</button>
    </div>`;
  document.body.append(box);
  const img = box.querySelector("img");
  const show = (i) => {
    index = (i + links.length) % links.length;
    img.src = links[index].href;
    img.alt = links[index].dataset.caption || "";
    box.querySelector("[data-count]").textContent = `${index + 1} / ${links.length}`;
    if (!reducedMotion()) gsap.fromTo(img, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.4, ease: "power3.out" });
  };
  const open = (i) => {
    trigger = document.activeElement;
    box.classList.replace("hidden", "flex");
    document.documentElement.style.overflow = "hidden";
    show(i);
    box.querySelector("[data-close]").focus();
  };
  const close = () => {
    box.classList.replace("flex", "hidden");
    document.documentElement.style.overflow = "";
    trigger?.focus();
  };
  links.forEach((link, i) =>
    link.addEventListener("click", (event) => {
      event.preventDefault();
      open(i);
    }),
  );
  box.querySelector("[data-prev]").addEventListener("click", () => show(index - 1));
  box.querySelector("[data-next]").addEventListener("click", () => show(index + 1));
  box.querySelector("[data-close]").addEventListener("click", close);
  box.addEventListener("click", (event) => event.target === box && close());
  document.addEventListener("keydown", (event) => {
    if (box.classList.contains("hidden")) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowRight") show(index + 1);
    if (event.key === "ArrowLeft") show(index - 1);
  });
}

/** Monthly payment estimate: price, deposit, rate and term → monthly repayment, rolling like a counter. */
export function initMortgage() {
  const form = document.querySelector("[data-mortgage]");
  if (!form) return;
  const out = form.querySelector("[data-mortgage-out]");
  const loanOut = form.querySelector("[data-loan-out]");
  const labels = form.querySelectorAll("[data-value-for]");
  form.querySelector("[data-mortgage-result]").hidden = false;
  let first = true;
  const update = () => {
    const price = Number(form.dataset.price);
    const deposit = Number(form.deposit.value) / 100;
    const rate = Number(form.rate.value) / 100 / 12;
    const months = Number(form.years.value) * 12;
    const loan = price * (1 - deposit);
    const monthly = rate ? (loan * rate) / (1 - (1 + rate) ** -months) : loan / months;
    labels.forEach((label) => {
      const input = form[label.dataset.valueFor];
      label.textContent = `${input.value}${label.dataset.unit}`;
    });
    loanOut.textContent = usd(loan);
    setOdometer(out, usd(monthly), { animate: !first && !reducedMotion(), duration: 0.6 });
    first = false;
  };
  form.addEventListener("input", update);
  update();
}
