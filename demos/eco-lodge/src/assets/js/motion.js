import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

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
      el.querySelectorAll(".text-warm, .text-warm-light").forEach((span) => {
        const gradient = span.classList.contains("text-warm") ? "text-warm" : "text-warm-light";
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

/** Map: pins drop onto the island one after another when the map comes into view. */
function mapPins() {
  const pins = document.querySelectorAll("[data-pin]");
  if (!pins.length) return;
  gsap.from(pins, {
    y: -40,
    autoAlpha: 0,
    duration: 0.7,
    ease: "back.out(2)",
    stagger: 0.09,
    scrollTrigger: { trigger: pins[0].closest("[data-map]"), start: "top 75%", once: true },
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
  mapPins();
  window.addEventListener("load", () => ScrollTrigger.refresh());
}
