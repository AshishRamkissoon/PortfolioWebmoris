import { gsap } from "gsap";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(Flip);

const finePointer = () => window.matchMedia("(hover: hover) and (pointer: fine)").matches;
const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Header: transparent over the hero, solid once you scroll. */
export function initHeader() {
  const header = document.querySelector("[data-header]");
  if (!header) return;
  const update = () => header.classList.toggle("is-solid", window.scrollY > 60);
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
      gsap.from(menu.querySelectorAll("[data-menu-link]"), { y: 30, autoAlpha: 0, stagger: 0.05, duration: 0.6, ease: "expo.out" });
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

/** Menu page: section filter. Works as anchor links without JS; with JS it filters in place with Flip. */
export function initMenuFilter() {
  const nav = document.querySelector("[data-menu-filters]");
  const list = document.querySelector("[data-menu-list]");
  if (!nav || !list) return;
  const sections = [...list.querySelectorAll("[data-menu-section]")];
  const buttons = [...nav.querySelectorAll("[data-filter]")];
  const apply = (filter, animate) => {
    const state = Flip.getState(sections);
    sections.forEach((section) => {
      section.hidden = filter !== "all" && section.dataset.menuSection !== filter;
    });
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filter === filter)));
    if (!animate || reducedMotion()) return;
    Flip.from(state, {
      duration: 0.7,
      ease: "power3.inOut",
      absolute: true,
      onEnter: (els) => gsap.fromTo(els, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.7, ease: "expo.out" }),
      onLeave: (els) => gsap.to(els, { autoAlpha: 0, duration: 0.3 }),
    });
  };
  buttons.forEach((button) =>
    button.addEventListener("click", (event) => {
      event.preventDefault();
      apply(button.dataset.filter, true);
      history.replaceState(null, "", button.dataset.filter === "all" ? "/menu/" : `/menu/#${button.dataset.filter}`);
    }),
  );
  const initial = location.hash.slice(1);
  if (initial && buttons.some((b) => b.dataset.filter === initial)) apply(initial, false);
}

/** Dish names reveal a floating photo that follows the pointer and leans with its speed (desktop). */
export function initMenuPreview() {
  const rows = document.querySelectorAll("[data-preview]");
  if (!rows.length || !finePointer()) return;
  const box = document.createElement("div");
  box.className = "menu-preview";
  box.setAttribute("aria-hidden", "true");
  const img = document.createElement("img");
  img.alt = "";
  box.append(img);
  document.body.append(box);

  const moveX = gsap.quickTo(box, "x", { duration: 0.6, ease: "power3.out" });
  const moveY = gsap.quickTo(box, "y", { duration: 0.6, ease: "power3.out" });
  const tilt = gsap.quickTo(box, "rotation", { duration: 0.8, ease: "power3.out" });
  let lastX = 0;
  const follow = (event) => {
    moveX(event.clientX + 32);
    moveY(event.clientY - 150);
    tilt(gsap.utils.clamp(-14, 14, (event.clientX - lastX) * 0.6));
    lastX = event.clientX;
  };
  rows.forEach((row) => {
    // Warm the image cache so the photo is ready on hover.
    row.addEventListener("pointerenter", (event) => {
      img.src = row.dataset.preview;
      lastX = event.clientX;
      gsap.set(box, { x: event.clientX + 32, y: event.clientY - 150 });
      gsap.to(box, { autoAlpha: 1, scale: 1, duration: 0.45, ease: "expo.out", overwrite: "auto" });
    });
    row.addEventListener("pointermove", follow);
    row.addEventListener("pointerleave", () => gsap.to(box, { autoAlpha: 0, scale: 0.85, duration: 0.35, overwrite: "auto" }));
  });
  gsap.set(box, { scale: 0.85 });
}

/** Map: the link opens Google Maps in a new tab without JS; with JS it swaps in the live map on click. */
export function initMapEmbed() {
  document.querySelectorAll("[data-map-embed]").forEach((button) => {
    const map = button.closest("figure");
    const label = button.querySelector("[data-map-label]");
    const overview = label.textContent;
    let frame = null;
    button.setAttribute("role", "button");
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", (event) => {
      event.preventDefault();
      if (!frame) {
        frame = document.createElement("iframe");
        frame.src = button.dataset.mapEmbed;
        frame.title = button.dataset.mapTitle;
        frame.loading = "lazy";
        frame.allowFullscreen = true;
        frame.className = "absolute inset-0 z-[25] size-full border-0 bg-night-900";
        map.append(frame);
      } else {
        frame.hidden = !frame.hidden;
      }
      const live = !frame.hidden;
      label.textContent = live ? "Back to overview" : overview;
      button.setAttribute("aria-pressed", String(live));
    });
  });
}
