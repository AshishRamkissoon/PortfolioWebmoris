import { gsap } from "gsap";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(Flip);

/** Header: transparent over the hero, solid once you scroll. */
export function initHeader() {
  const header = document.querySelector("[data-hero-header]");
  if (!header) return;
  const update = () => {
    const solid = window.scrollY > 80;
    header.classList.toggle("is-solid", solid);
    header.classList.toggle("text-white", !solid);
  };
  update();
  window.addEventListener("scroll", update, { passive: true });
}

export function initMenu() {
  const button = document.querySelector("[data-menu-button]");
  const menu = document.getElementById("mobile-menu");
  if (!button || !menu) return;
  const header = button.closest("[data-header]");
  const setOpen = (open) => {
    menu.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    header?.classList.toggle("is-solid", open || window.scrollY > 80);
    if (header?.hasAttribute("data-hero-header")) header.classList.toggle("text-white", !open && window.scrollY <= 80);
  };
  button.addEventListener("click", () => setOpen(menu.hidden));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !menu.hidden) {
      setOpen(false);
      button.focus();
    }
  });
}

/** Tour filter: works as plain links; with JS it filters in place and animates with Flip. */
export function initFilters() {
  const nav = document.querySelector("[data-filters]");
  const grid = document.querySelector("[data-tour-grid]");
  if (!nav || !grid) return;
  const cards = [...grid.querySelectorAll("[data-tour-card]")];
  const buttons = [...nav.querySelectorAll("[data-filter]")];
  const count = document.querySelector("[data-filter-count]");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const apply = (filter, animate) => {
    const state = Flip.getState(cards);
    let shown = 0;
    cards.forEach((card) => {
      const match = filter === "all" || card.dataset.category === filter;
      card.hidden = !match;
      shown += match ? 1 : 0;
    });
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filter === filter)));
    if (count) count.textContent = `${shown} tour${shown === 1 ? "" : "s"}`;
    if (!animate || reduced) return;
    Flip.from(state, {
      duration: 0.7,
      ease: "power3.inOut",
      absolute: true,
      onEnter: (els) => gsap.fromTo(els, { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: 0.6 }),
      onLeave: (els) => gsap.to(els, { opacity: 0, scale: 0.92, duration: 0.4 }),
    });
  };

  buttons.forEach((button) =>
    button.addEventListener("click", (event) => {
      event.preventDefault();
      const filter = button.dataset.filter;
      apply(filter, true);
      const url = filter === "all" ? "/tours/" : `/tours/?category=${filter}`;
      history.replaceState(null, "", url);
    }),
  );

  const initial = new URLSearchParams(location.search).get("category");
  if (initial && buttons.some((b) => b.dataset.filter === initial)) apply(initial, false);
}

/** Gallery lightbox with keyboard support; links still work without JS. */
export function initLightbox() {
  const gallery = document.querySelector("[data-gallery]");
  if (!gallery) return;
  const items = [...gallery.querySelectorAll("[data-lightbox-item]")];
  let index = 0;
  let trigger = null;

  const box = document.createElement("div");
  box.className = "fixed inset-0 z-[60] hidden flex-col items-center justify-center gap-4 bg-ocean-950/95 p-4 backdrop-blur";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", "Photo viewer");
  box.innerHTML = `
    <img class="max-h-[78vh] max-w-full rounded-2xl object-contain shadow-2xl" alt="">
    <p class="max-w-2xl text-center text-sm text-white/80" data-caption></p>
    <div class="flex items-center gap-3">
      <button type="button" class="btn btn-light" data-prev>← Prev</button>
      <span class="min-w-14 text-center text-sm text-white/70" data-count></span>
      <button type="button" class="btn btn-light" data-next>Next →</button>
      <button type="button" class="btn btn-coral" data-close>Close</button>
    </div>`;
  document.body.append(box);
  const img = box.querySelector("img");

  const show = (i) => {
    index = (i + items.length) % items.length;
    const item = items[index];
    img.src = item.href;
    img.alt = item.dataset.caption || "";
    box.querySelector("[data-caption]").textContent = item.dataset.caption || "";
    box.querySelector("[data-count]").textContent = `${index + 1} / ${items.length}`;
    gsap.fromTo(img, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.45, ease: "power3.out" });
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

  items.forEach((item, i) =>
    item.addEventListener("click", (event) => {
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
    if (event.key === "Tab") {
      const focusable = [...box.querySelectorAll("button")];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === focusable[0]) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        focusable[0].focus();
      }
    }
  });
}
