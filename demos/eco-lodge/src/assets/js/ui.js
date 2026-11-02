import { gsap } from "gsap";

import { setOdometer } from "./odometer.js";

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const mur = (n) => `Rs ${Math.round(n).toLocaleString("en-US")}`;
const DAY = 86400000;
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const parse = (s) => {
  const [y, m, d] = (s || "").split("-").map(Number);
  return y ? new Date(y, m - 1, d) : null;
};
const today = () => {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
};

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
 * Demo availability: each room has a seed, and some nights are "booked" in short runs.
 * Deterministic for a given room and date, so the calendar looks the same on every visit.
 */
function isBooked(seed, date) {
  const n = Math.floor(date.getTime() / DAY);
  const block = Math.floor((n + seed * 3) / 3); // nights are booked in runs of about three
  const x = Math.sin(block * 12.9898 + seed * 78.233) * 43758.5453;
  return x - Math.floor(x) < 0.32;
}

/**
 * Availability calendar ([data-calendar]): two months, free and booked nights.
 * Click a free day for check-in, another for check-out (a stay can't cross a booked night).
 * Keeps the form's check-in / check-out inputs in sync, and announces changes through `onChange`.
 */
function calendar(root, { seed, onChange }) {
  const checkin = root.form?.querySelector("[name=checkin]") || document.querySelector("[name=checkin]");
  const checkout = root.form?.querySelector("[name=checkout]") || document.querySelector("[name=checkout]");
  const grid = root.querySelector("[data-cal-grid]");
  const title = root.querySelector("[data-cal-title]");
  const prev = root.querySelector("[data-cal-prev]");
  const next = root.querySelector("[data-cal-next]");
  const months = window.matchMedia("(min-width: 768px)").matches ? 2 : 1;
  let view = new Date(today().getFullYear(), today().getMonth(), 1);
  let start = parse(checkin?.value);
  let end = parse(checkout?.value);

  const free = (d) => d >= today() && !isBooked(seed, d);
  const rangeFree = (a, b) => {
    for (let d = new Date(a); d < b; d = new Date(d.getTime() + DAY)) if (!free(d)) return false;
    return true;
  };
  const emit = () => {
    if (checkin) checkin.value = start ? iso(start) : "";
    if (checkout) checkout.value = end ? iso(end) : "";
    onChange?.(start, end);
  };
  const render = () => {
    grid.innerHTML = "";
    const names = [];
    for (let m = 0; m < months; m++) {
      const first = new Date(view.getFullYear(), view.getMonth() + m, 1);
      names.push(first.toLocaleDateString("en-GB", { month: "long", year: "numeric" }));
      const month = document.createElement("div");
      month.innerHTML = `<p class="mb-3 text-center font-display text-xl">${names[m]}</p>
        <div class="grid grid-cols-7 gap-1 text-center text-[11px] font-bold tracking-wide text-ink-500 uppercase">${["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].map((d) => `<span>${d}</span>`).join("")}</div>`;
      const days = document.createElement("div");
      days.className = "mt-1 grid grid-cols-7 gap-1";
      const offset = (first.getDay() + 6) % 7;
      for (let i = 0; i < offset; i++) days.append(document.createElement("span"));
      const count = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
      for (let day = 1; day <= count; day++) {
        const date = new Date(first.getFullYear(), first.getMonth(), day);
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = String(day);
        const past = date < today();
        const booked = !past && isBooked(seed, date);
        const selected = (start && +date === +start) || (end && +date === +end);
        const inRange = start && end && date > start && date < end;
        button.className = `cal-day ${past ? "is-past" : booked ? "is-booked" : "is-free"}${selected ? " is-selected" : inRange ? " is-range" : ""}`;
        button.disabled = past || booked;
        button.setAttribute("aria-label", `${date.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" })}${booked ? ", booked" : past ? "" : ", available"}`);
        if (selected) button.setAttribute("aria-pressed", "true");
        button.addEventListener("click", () => {
          if (!start || end || date <= start) {
            start = date;
            end = null;
          } else if (rangeFree(start, date)) {
            end = date;
          } else {
            start = date;
            end = null;
          }
          emit();
          render();
        });
        days.append(button);
      }
      month.append(days);
      grid.append(month);
    }
    title.textContent = names.join(" – ");
    prev.disabled = view <= new Date(today().getFullYear(), today().getMonth(), 1);
  };
  prev.addEventListener("click", () => {
    view = new Date(view.getFullYear(), view.getMonth() - 1, 1);
    render();
  });
  next.addEventListener("click", () => {
    view = new Date(view.getFullYear(), view.getMonth() + 1, 1);
    render();
  });
  // Typing dates in the inputs also updates the calendar.
  [checkin, checkout].forEach((input) =>
    input?.addEventListener("change", () => {
      start = parse(checkin.value);
      end = parse(checkout.value);
      if (start) view = new Date(start.getFullYear(), start.getMonth(), 1);
      onChange?.(start, end);
      render();
    }),
  );
  root.hidden = false;
  render();
  return {
    setSeed(newSeed) {
      seed = newSeed;
      if (start && end && !rangeFree(start, end)) {
        start = null;
        end = null;
        emit();
      }
      render();
    },
  };
}

/** Room page: calendar, plus a "book these dates" link that carries the dates to the booking page. */
export function initRoomCalendar() {
  const root = document.querySelector("[data-room-calendar]");
  if (!root) return;
  const link = document.querySelector("[data-book-dates]");
  const note = document.querySelector("[data-dates-note]");
  calendar(root, {
    seed: Number(root.dataset.seed),
    onChange: (start, end) => {
      const params = new URLSearchParams({ room: root.dataset.room });
      if (start) params.set("checkin", iso(start));
      if (end) params.set("checkout", iso(end));
      link.href = `/book/?${params}`;
      const nights = start && end ? Math.round((end - start) / DAY) : 0;
      note.textContent = nights ? `${nights} night${nights > 1 ? "s" : ""}: ${mur(nights * Number(root.dataset.price))} with breakfast` : "Pick your check-in and check-out days.";
    },
  });
}

/**
 * Booking page: room choice, calendar and a live summary that shows the saving against
 * booking sites, breakfast and the free transfer from 3 nights.
 */
export function initBooking() {
  const form = document.querySelector("[data-booking]");
  if (!form) return;
  const summary = document.querySelector("[data-summary]");
  const discount = Number(form.dataset.discount) / 100;
  const query = new URLSearchParams(location.search);
  if (query.get("room")) {
    const radio = form.querySelector(`input[name="room"][value="${CSS.escape(query.get("room"))}"]`);
    if (radio) radio.checked = true;
  }
  for (const name of ["checkin", "checkout"]) if (query.get(name)) form[name].value = query.get(name);
  const room = () => form.querySelector('input[name="room"]:checked');
  const out = (name) => summary.querySelector(`[data-out="${name}"]`);
  summary.hidden = false;
  document.querySelector("[data-summary-fallback]")?.setAttribute("hidden", "");

  let first = true;
  const update = () => {
    const r = room();
    const price = Number(r.dataset.price);
    const start = parse(form.checkin.value);
    const end = parse(form.checkout.value);
    const nights = start && end && end > start ? Math.round((end - start) / DAY) : 0;
    const total = nights * price;
    const ota = Math.round(total / (1 - discount));
    out("room").textContent = r.dataset.name;
    out("dates").textContent = nights ? `${start.toLocaleDateString("en-GB", { day: "numeric", month: "short" })} → ${end.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}` : "Choose your dates";
    out("nights").textContent = String(nights);
    out("rate").textContent = mur(price);
    out("transfer").textContent = nights >= 3 ? "Free" : "From 3 nights";
    out("ota").textContent = nights ? mur(ota) : "—";
    const roll = (name, text) => setOdometer(out(name), text, { animate: !first && !reducedMotion(), duration: 0.6 });
    roll("total", mur(total));
    roll("saving", mur(ota - total));
    first = false;
  };
  const cal = calendar(document.querySelector("[data-booking-calendar]"), { seed: Number(room().dataset.seed), onChange: update });
  form.querySelectorAll('input[name="room"]').forEach((radio) =>
    radio.addEventListener("change", () => {
      cal.setSeed(Number(radio.dataset.seed));
      update();
    }),
  );
  form.addEventListener("input", update);
  update();
}

/** Room page gallery: thumbnails open a full-screen viewer. */
export function initGallery() {
  const gallery = document.querySelector("[data-gallery]");
  if (!gallery) return;
  const links = [...gallery.querySelectorAll("[data-gallery-item]")];
  let index = 0;
  let trigger = null;
  const box = document.createElement("div");
  box.className = "fixed inset-0 z-[60] hidden flex-col items-center justify-center gap-4 bg-forest-950/95 p-4 backdrop-blur";
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
  const close = () => {
    box.classList.replace("flex", "hidden");
    document.documentElement.style.overflow = "";
    trigger?.focus();
  };
  links.forEach((link, i) =>
    link.addEventListener("click", (event) => {
      event.preventDefault();
      trigger = document.activeElement;
      box.classList.replace("hidden", "flex");
      document.documentElement.style.overflow = "hidden";
      show(i);
      box.querySelector("[data-close]").focus();
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
