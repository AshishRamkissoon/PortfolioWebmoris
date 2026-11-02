import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

import { setOdometer } from "./odometer.js";

gsap.registerPlugin(ScrollTrigger, SplitText);

const finePointer = () => window.matchMedia("(hover: hover) and (pointer: fine)").matches;

export const motionAllowed = () =>
  document.documentElement.classList.contains("motion-ok") &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const headerBottom = () => document.querySelector("[data-header]")?.getBoundingClientRect().bottom || 0;

function smoothScroll() {
  const lenis = new Lenis({ lerp: 0.1 });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  document.querySelectorAll('a[href^="#"]:not([href="#"]), a[href^="/#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      if (link.pathname !== location.pathname) return;
      const target = document.querySelector(link.hash);
      if (!target) return;
      event.preventDefault();
      lenis.scrollTo(target, { offset: -90 });
    });
  });
}

/** Fade-up with a slight zoom for [data-reveal], staggered when siblings reveal together. */
function reveals() {
  ScrollTrigger.batch("[data-reveal]", {
    start: "top 92%",
    once: true,
    onEnter: (batch) =>
      gsap.fromTo(
        batch,
        { autoAlpha: 0, y: 40, scale: 0.97 },
        { autoAlpha: 1, y: 0, scale: 1, duration: 0.9, ease: "power3.out", stagger: 0.08, clearProps: "transform" },
      ),
  });
}

/**
 * Hero camera move. Dolly in: the photo settles from a close zoom as the page opens.
 * Dolly out: scrolling pushes the camera further in while the text drifts up and fades.
 */
function heroDolly() {
  const hero = document.querySelector("[data-hero]");
  if (!hero) return;
  const media = hero.querySelector("[data-hero-media]");
  const dolly = hero.querySelector("[data-hero-dolly]");
  const content = hero.querySelector("[data-hero-content]");
  gsap.fromTo(dolly, { scale: 1.3 }, { scale: 1.06, duration: 2.6, ease: "expo.out" });
  const scrub = { trigger: hero, start: "top top", end: "bottom top", scrub: true };
  gsap.to(media, { scale: 1.2, yPercent: 10, ease: "none", scrollTrigger: scrub });
  gsap.to(content, { yPercent: -18, autoAlpha: 0.15, ease: "none", scrollTrigger: { ...scrub, end: "bottom 30%" } });
  // A gentle parallax tilt that follows the mouse.
  if (finePointer()) {
    const x = gsap.quickTo(dolly, "xPercent", { duration: 1.2, ease: "power3.out" });
    const y = gsap.quickTo(dolly, "yPercent", { duration: 1.2, ease: "power3.out" });
    hero.addEventListener("pointermove", (event) => {
      x((event.clientX / window.innerWidth - 0.5) * -2.5);
      y((event.clientY / window.innerHeight - 0.5) * -2.5);
    });
  }
}

/**
 * Dolly reveal: a framed photo (rounded, inset) widens to fill the screen while the camera
 * pulls back out of the image, then the headline rises in. Pinned on larger screens.
 */
function dollyReveal() {
  const section = document.querySelector("[data-dolly]");
  if (!section) return;
  const frame = section.querySelector("[data-dolly-frame]");
  const image = section.querySelector("[data-dolly-image]");
  const text = section.querySelector("[data-dolly-text]");
  gsap.matchMedia().add(
    { desktop: "(min-width: 768px)", mobile: "(max-width: 767px)" },
    ({ conditions }) => {
      if (conditions.desktop) section.classList.add("is-pinned");
      const tl = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: conditions.desktop
          ? { trigger: section, start: () => `top ${headerBottom()}px`, end: "+=120%", pin: true, scrub: 0.8, invalidateOnRefresh: true }
          : { trigger: section, start: "top 85%", end: "top 15%", scrub: 0.8 },
      });
      tl.fromTo(frame, { clipPath: "inset(14% 18% 14% 18% round 32px)" }, { clipPath: "inset(0% 0% 0% 0% round 0px)", duration: 1 })
        .fromTo(image, { scale: 1.45 }, { scale: 1, duration: 1.2 }, 0)
        .fromTo(text, { autoAlpha: 0, y: 60 }, { autoAlpha: 1, y: 0, duration: 0.5 }, 0.55);
      return () => section.classList.remove("is-pinned");
    },
  );
}

/** Section headings rise word by word (screen readers still get the whole sentence). */
function splitHeadings() {
  document.fonts.ready.then(() => {
    document.querySelectorAll("[data-split]").forEach((el) => {
      const split = SplitText.create(el, { type: "words", mask: "words", aria: "auto" });
      // Gradient text can't paint through the moving word boxes, so each word gets the gradient itself.
      el.querySelectorAll(".text-gradient, .text-gradient-light").forEach((span) => {
        const gradient = span.classList.contains("text-gradient") ? "text-gradient" : "text-gradient-light";
        span.classList.remove(gradient);
        split.words.filter((word) => span.contains(word)).forEach((word) => word.classList.add(gradient));
      });
      gsap.set(el, { autoAlpha: 1 });
      gsap.from(split.words, {
        yPercent: 110,
        duration: 0.9,
        ease: "expo.out",
        stagger: 0.06,
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });
  });
}

/** Numbers count up from zero when they scroll into view. */
function counters() {
  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = Number(el.textContent);
    if (!target) return;
    const value = { n: 0 };
    el.textContent = "0";
    gsap.to(value, {
      n: target,
      duration: 1.6,
      ease: "power2.out",
      scrollTrigger: { trigger: el, start: "top 90%", once: true },
      onUpdate: () => {
        el.textContent = Math.round(value.n).toLocaleString("en-US");
      },
    });
  });
}

/** Photos slowly zoom out while they cross the screen ([data-zoom]). */
function scrollZoom() {
  document.querySelectorAll("[data-zoom]").forEach((el) => {
    gsap.fromTo(
      el,
      { scale: 1.2 },
      { scale: 1, ease: "none", scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true } },
    );
  });
}

/** Lines that draw themselves when they come into view ([data-draw-x]). */
function drawLines() {
  document.querySelectorAll("[data-draw-x]").forEach((el) => {
    gsap.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: "power3.inOut", scrollTrigger: { trigger: el, start: "top 80%", once: true } });
  });
}

/** Main buttons lean toward the pointer. */
function magnetic() {
  if (!finePointer()) return;
  document.querySelectorAll("[data-magnetic]").forEach((el) => {
    const x = gsap.quickTo(el, "x", { duration: 0.5, ease: "power3.out" });
    const y = gsap.quickTo(el, "y", { duration: 0.5, ease: "power3.out" });
    el.addEventListener("pointermove", (event) => {
      const box = el.getBoundingClientRect();
      x((event.clientX - box.left - box.width / 2) * 0.2);
      y((event.clientY - box.top - box.height / 2) * 0.3);
    });
    el.addEventListener("pointerleave", () => {
      x(0);
      y(0);
    });
  });
}

/**
 * Around the island: the map is pinned while the route draws itself around the coast.
 * A counter shows the kilometres and each stop's card appears as the line reaches it.
 */
function coastRoute() {
  const section = document.querySelector("[data-coast]");
  if (!section) return;
  gsap.matchMedia().add("(min-width: 768px)", () => {
    section.classList.add("is-pinned");
    const path = section.querySelector("[data-route]");
    const car = section.querySelector("[data-route-car]");
    const counter = section.querySelector("[data-route-km]");
    const stops = [...section.querySelectorAll("[data-stop]")];
    const dots = [...section.querySelectorAll("[data-stop-dot]")];
    const total = Number(section.dataset.km);
    const length = path.getTotalLength();
    gsap.set(path, { strokeDasharray: `${length} ${length}`, strokeDashoffset: length });
    gsap.set(stops, { autoAlpha: 0 });
    gsap.set(stops[0], { autoAlpha: 1 });
    dots[0]?.classList.add("is-reached");
    let current = 0;
    const show = (index) => {
      if (index === current) return;
      gsap.to(stops[current], { autoAlpha: 0, y: -20, duration: 0.35, ease: "power2.in", overwrite: true });
      gsap.fromTo(stops[index], { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out", overwrite: true });
      dots.forEach((dot, i) => dot.classList.toggle("is-reached", i <= index));
      current = index;
    };
    setOdometer(counter, "000", { animate: false });
    let lastKm = -1;
    const trigger = ScrollTrigger.create({
      trigger: section,
      start: () => `top ${headerBottom()}px`,
      end: () => `+=${window.innerHeight * 3}`,
      pin: true,
      scrub: 0.6,
      invalidateOnRefresh: true,
      onUpdate: ({ progress }) => {
        path.style.strokeDashoffset = String(length * (1 - progress));
        const point = path.getPointAtLength(length * progress);
        car.setAttribute("transform", `translate(${point.x} ${point.y})`);
        const km = Math.round(total * progress);
        if (km !== lastKm) {
          setOdometer(counter, String(km).padStart(3, "0"), { duration: 0.3 });
          lastKm = km;
        }
        let index = 0;
        stops.forEach((stop, i) => {
          if (progress >= Number(stop.dataset.at) - 0.01) index = i;
        });
        show(index);
      },
    });
    return () => {
      trigger.kill();
      section.classList.remove("is-pinned");
      gsap.set([path, ...stops], { clearProps: "all" });
    };
  });
}

export function initMotion() {
  if (!motionAllowed()) return;
  smoothScroll();
  heroDolly();
  reveals();
  splitHeadings();
  dollyReveal();
  counters();
  scrollZoom();
  drawLines();
  magnetic();
  coastRoute();
  window.addEventListener("load", () => ScrollTrigger.refresh());
}
