import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

import { initOdometers, setOdometer } from "./odometer.js";

gsap.registerPlugin(ScrollTrigger, SplitText);

export const motionAllowed = () =>
  document.documentElement.classList.contains("motion-ok") &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export const finePointer = () => window.matchMedia("(hover: hover) and (pointer: fine)").matches;

/** WebGL only where it will run smoothly. */
export function canWebGL() {
  if (window.innerWidth < 1024 || !finePointer() || navigator.connection?.saveData) return false;
  if ((navigator.hardwareConcurrency || 8) < 4) return false;
  try {
    const gl = document.createElement("canvas").getContext("webgl");
    if (!gl) return false;
    // Software renderers (no GPU) would draw the shader on the CPU and make the page sluggish.
    const info = gl.getExtension("WEBGL_debug_renderer_info");
    const renderer = info ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL)) : "";
    return !/swiftshader|llvmpipe|software|basic render/i.test(renderer);
  } catch {
    return false;
  }
}

// "Clutch and brake": gentle start, firm stop, never a bounce.
const DRIVE = "power3.inOut";
const ARRIVE = "expo.out";
const headerBottom = () => document.querySelector("[data-header]")?.getBoundingClientRect().bottom || 0;

function smoothScroll() {
  const lenis = new Lenis({ lerp: 0.09 });
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

/** The dashed lane line down the left edge fills as you scroll: the page's progress bar. */
function laneProgress() {
  const bar = document.querySelector("[data-lane-progress]");
  if (!bar) return;
  gsap.to(bar, { scaleY: 1, ease: "none", scrollTrigger: { start: 0, end: "max", scrub: 0.3 } });
}

/** Everything arrives from the right, like scenery from a car window. */
function reveals() {
  ScrollTrigger.batch("[data-reveal]", {
    start: "top 90%",
    once: true,
    onEnter: (batch) =>
      gsap.fromTo(batch, { autoAlpha: 0, x: 60 }, { autoAlpha: 1, x: 0, duration: 1.1, ease: ARRIVE, stagger: 0.08 }),
  });
}

/** Sign pass: a sign panel wipes in from the right, then its text follows. */
function signs() {
  document.querySelectorAll("[data-sign]").forEach((el) => {
    const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 88%", once: true } });
    tl.fromTo(el, { clipPath: "inset(0 0 0 100%)" }, { clipPath: "inset(0 0 0 0%)", duration: 0.8, ease: DRIVE });
    if (el.children.length) tl.from(el.children, { x: 24, autoAlpha: 0, duration: 0.6, ease: ARRIVE, stagger: 0.05 }, 0.35);
  });
}

/** Headlines: words slide in from the right through a mask. */
function splitHeadings() {
  document.fonts.ready.then(() => {
    document.querySelectorAll("[data-split]").forEach((el) => {
      const split = SplitText.create(el, { type: "words", mask: "words", aria: "auto" });
      gsap.set(el, { autoAlpha: 1 });
      gsap.from(split.words, {
        xPercent: 60,
        yPercent: 100,
        duration: 1.1,
        ease: ARRIVE,
        stagger: 0.06,
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });
  });
}

/** Letterboxed photos open like a film starting: the black bars draw back. */
function letterboxes() {
  document.querySelectorAll("[data-film]").forEach((el) => {
    const img = el.querySelector("img");
    const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 85%", once: true } });
    tl.fromTo(el, { clipPath: "inset(50% 0 50% 0)" }, { clipPath: "inset(0% 0 0% 0)", duration: 1.3, ease: DRIVE });
    if (img) tl.fromTo(img, { scale: 1.2, xPercent: 4 }, { scale: 1, xPercent: 0, duration: 2, ease: ARRIVE }, 0);
  });
}

/** Photos drift sideways against the scroll, like the view from a moving car. */
function drift() {
  document.querySelectorAll("[data-drift]").forEach((el) => {
    const amount = parseFloat(el.dataset.drift) || 6;
    gsap.fromTo(
      el,
      { xPercent: amount },
      { xPercent: -amount, ease: "none", scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true } },
    );
  });
}

/**
 * The coast: the map is pinned while the route draws itself around the island.
 * The odometer counts the kilometres and each stop's sign and photo appear as the line reaches it.
 */
function coastRoute() {
  const section = document.querySelector("[data-coast]");
  if (!section) return;
  gsap.matchMedia().add("(min-width: 768px)", () => {
    section.classList.add("is-pinned");
    const path = section.querySelector("[data-route]");
    const car = section.querySelector("[data-route-car]");
    const odo = section.querySelector("[data-route-km]");
    const stops = [...section.querySelectorAll("[data-stop]")];
    const dots = [...section.querySelectorAll("[data-stop-dot]")];
    const total = Number(section.dataset.km);
    const length = path.getTotalLength();
    gsap.set(path, { strokeDasharray: `${length} ${length}`, strokeDashoffset: length });
    gsap.set(stops, { autoAlpha: 0 });
    gsap.set(stops[0], { autoAlpha: 1 });
    let current = 0;
    const show = (index) => {
      if (index === current) return;
      gsap.to(stops[current], { autoAlpha: 0, x: -60, duration: 0.45, ease: DRIVE, overwrite: true });
      gsap.fromTo(stops[index], { autoAlpha: 0, x: 60 }, { autoAlpha: 1, x: 0, duration: 0.7, ease: ARRIVE, overwrite: true });
      dots.forEach((dot, i) => dot.classList.toggle("is-reached", i <= index));
      current = index;
    };
    dots[0]?.classList.add("is-reached");
    setOdometer(odo, String(0).padStart(3, "0"), { animate: false });
    let lastKm = -1;
    const trigger = ScrollTrigger.create({
      trigger: section,
      start: () => `top ${headerBottom()}px`,
      end: () => `+=${window.innerHeight * 4}`,
      pin: true,
      scrub: 0.6,
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        const progress = self.progress;
        path.style.strokeDashoffset = String(length * (1 - progress));
        const point = path.getPointAtLength(length * progress);
        car.setAttribute("transform", `translate(${point.x} ${point.y})`);
        const km = Math.round(total * progress);
        if (km !== lastKm) {
          setOdometer(odo, String(km).padStart(3, "0"), { duration: 0.3 });
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

/** Buttons lean toward the pointer. */
function magnetic() {
  if (!finePointer()) return;
  document.querySelectorAll("[data-magnetic]").forEach((el) => {
    const x = gsap.quickTo(el, "x", { duration: 0.5, ease: "power3.out" });
    const y = gsap.quickTo(el, "y", { duration: 0.5, ease: "power3.out" });
    el.addEventListener("pointermove", (event) => {
      const box = el.getBoundingClientRect();
      x((event.clientX - box.left - box.width / 2) * 0.3);
      y((event.clientY - box.top - box.height / 2) * 0.4);
    });
    el.addEventListener("pointerleave", () => {
      x(0);
      y(0);
    });
  });
}

/** Closing headline: letters lift in from the right as it scrolls into view. */
function finale() {
  document.querySelectorAll("[data-finale]").forEach((el) => {
    const split = SplitText.create(el, { type: "chars", aria: "auto" });
    gsap.from(split.chars, {
      xPercent: 120,
      opacity: 0,
      stagger: 0.02,
      ease: "none",
      scrollTrigger: { trigger: el, start: "top 95%", end: "top 50%", scrub: true },
    });
  });
}

export function initMotion() {
  if (!motionAllowed()) return;
  smoothScroll();
  laneProgress();
  reveals();
  signs();
  splitHeadings();
  letterboxes();
  drift();
  coastRoute();
  initOdometers(ScrollTrigger);
  magnetic();
  finale();
  window.addEventListener("load", () => ScrollTrigger.refresh());
}
