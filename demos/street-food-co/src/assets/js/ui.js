import { gsap } from "gsap";

import { setOdometer } from "./odometer.js";

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const mur = (n) => `Rs ${Math.round(n).toLocaleString("en-US")}`;
const KEY = "sfc-basket";

/** The basket lives in localStorage ({ slug: quantity }) so it follows you from the menu to the order page. */
const basket = {
  read() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch {
      return {};
    }
  },
  write(items) {
    try {
      localStorage.setItem(KEY, JSON.stringify(items));
    } catch {
      /* private mode: the basket just won't persist */
    }
    updateCounts();
  },
  add(slug, n = 1) {
    const items = this.read();
    items[slug] = Math.max(0, (items[slug] || 0) + n);
    if (!items[slug]) delete items[slug];
    this.write(items);
  },
  set(slug, n) {
    const items = this.read();
    if (n > 0) items[slug] = n;
    else delete items[slug];
    this.write(items);
  },
  count() {
    return Object.values(this.read()).reduce((sum, n) => sum + n, 0);
  },
};

function updateCounts() {
  const count = basket.count();
  document.querySelectorAll("[data-basket-count]").forEach((el) => {
    el.hidden = count === 0;
    el.textContent = String(count);
  });
}

export function initMobileMenu() {
  const button = document.querySelector("[data-menu-button]");
  const menu = document.getElementById("mobile-menu");
  if (!button || !menu) return;
  const setOpen = (open) => {
    menu.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    if (open && !reducedMotion()) {
      gsap.from(menu.querySelectorAll("[data-menu-link]"), { x: -20, autoAlpha: 0, stagger: 0.05, duration: 0.45, ease: "back.out(2)" });
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

/** A copy of the dish photo flies into the order button, which then bounces. */
function flyToBag(from) {
  const target = [...document.querySelectorAll("[data-basket-count]")].map((el) => el.closest("a")).find((a) => a && a.offsetParent);
  const img = from.closest("[data-dish]")?.querySelector("img");
  if (!target || !img || reducedMotion()) return;
  const a = img.getBoundingClientRect();
  const b = target.getBoundingClientRect();
  const clone = img.cloneNode();
  Object.assign(clone.style, { position: "fixed", left: `${a.left}px`, top: `${a.top}px`, width: `${a.width}px`, height: `${a.height}px`, zIndex: 80, borderRadius: "999px", objectFit: "cover", pointerEvents: "none" });
  clone.removeAttribute("srcset");
  clone.src = img.currentSrc || img.src;
  document.body.append(clone);
  gsap.to(clone, {
    left: b.left + b.width / 2 - 20,
    top: b.top + b.height / 2 - 20,
    width: 40,
    height: 40,
    rotate: 200,
    duration: 0.75,
    ease: "power3.in",
    onComplete: () => {
      clone.remove();
      gsap.fromTo(target, { scale: 1.25 }, { scale: 1, duration: 0.6, ease: "elastic.out(1, 0.4)" });
    },
  });
}

/**
 * Menu / home: "Add" buttons. Without JS they are links to the order form (#dish);
 * with JS they add to the basket, fly into the bag and say "Added".
 */
export function initAddButtons() {
  updateCounts();
  document.querySelectorAll("[data-add]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      basket.add(button.dataset.add);
      flyToBag(button);
      const label = button.querySelector("[data-add-label]");
      if (label) {
        label.textContent = "Added!";
        clearTimeout(button._t);
        button._t = setTimeout(() => {
          label.textContent = "Add";
        }, 1200);
      }
    });
  });
}

/** Menu page: category tabs highlight the section in view; clicking glides to it. */
export function initMenuTabs() {
  const tabs = [...document.querySelectorAll("[data-tab]")];
  if (!tabs.length) return;
  const sections = tabs.map((tab) => document.getElementById(tab.dataset.tab));
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        tabs.forEach((tab) => tab.setAttribute("aria-current", String(tab.dataset.tab === entry.target.id)));
      });
    },
    { rootMargin: "-40% 0px -55% 0px" },
  );
  sections.forEach((section) => section && observer.observe(section));
}

/** "Find the truck": highlight today's stop (on the list and the map). Without JS the whole week shows plainly. */
export function initToday() {
  const today = new Date().getDay();
  document.querySelectorAll("[data-day]").forEach((el) => {
    const isToday = Number(el.dataset.day) === today;
    el.classList.toggle("is-today", isToday);
    el.querySelector("[data-today-badge]")?.toggleAttribute("hidden", !isToday);
  });
  const label = document.querySelector("[data-today-place]");
  const stop = document.querySelector(`[data-day="${today}"][data-place]`);
  if (label && stop) label.textContent = stop.dataset.place;
}

/**
 * Order page: quantity steppers (−/+ around number inputs), prefilled from the basket,
 * and a live summary. The form itself works without JS (the demo kit stops it).
 */
export function initOrder() {
  const form = document.querySelector("[data-order]");
  if (!form) return;
  const inputs = [...form.querySelectorAll("input[data-qty]")];
  const summary = document.querySelector("[data-order-summary]");
  const lines = summary.querySelector("[data-lines]");
  const totalEl = summary.querySelector("[data-total]");
  const empty = summary.querySelector("[data-empty]");
  const saved = basket.read();
  inputs.forEach((input) => {
    if (saved[input.dataset.qty]) input.value = saved[input.dataset.qty];
    const wrap = input.closest(".qty");
    const minus = document.createElement("button");
    const plus = document.createElement("button");
    minus.type = plus.type = "button";
    minus.textContent = "−";
    plus.textContent = "+";
    minus.setAttribute("aria-label", `One less ${input.dataset.name}`);
    plus.setAttribute("aria-label", `One more ${input.dataset.name}`);
    wrap.prepend(minus);
    wrap.append(plus);
    const step = (n) => {
      input.value = String(Math.max(0, Math.min(20, Number(input.value || 0) + n)));
      input.dispatchEvent(new Event("input", { bubbles: true }));
      if (!reducedMotion()) gsap.fromTo(input, { scale: 1.4 }, { scale: 1, duration: 0.4, ease: "back.out(3)" });
    };
    minus.addEventListener("click", () => step(-1));
    plus.addEventListener("click", () => step(1));
  });
  let first = true;
  const update = () => {
    let total = 0;
    lines.innerHTML = "";
    inputs.forEach((input) => {
      const n = Math.max(0, Number(input.value) || 0);
      basket.set(input.dataset.qty, n);
      input.closest("[data-dish]")?.classList.toggle("is-picked", n > 0);
      if (!n) return;
      const line = n * Number(input.dataset.price);
      total += line;
      const li = document.createElement("li");
      li.className = "flex justify-between gap-3";
      li.innerHTML = `<span><strong>${n}×</strong> ${input.dataset.name}</span><span class="font-bold">${mur(line)}</span>`;
      lines.append(li);
    });
    empty.hidden = total > 0;
    setOdometer(totalEl, mur(total), { animate: !first && !reducedMotion(), duration: 0.5 });
    first = false;
  };
  form.addEventListener("input", update);
  summary.hidden = false;
  update();
}
