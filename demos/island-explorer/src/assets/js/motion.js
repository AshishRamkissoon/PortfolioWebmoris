import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger, SplitText);

export const motionAllowed = () =>
  document.documentElement.classList.contains("motion-ok") &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const finePointer = () => window.matchMedia("(hover: hover) and (pointer: fine)").matches;

/** WebGL ripple only where it will run smoothly. */
export function canRipple() {
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

function smoothScroll() {
  const lenis = new Lenis({ lerp: 0.09 });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  // In-page links (e.g. "How it works") glide instead of jumping.
  document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach((link) => {
    link.addEventListener("click", (event) => {
      const target = document.querySelector(link.getAttribute("href"));
      if (!target) return;
      event.preventDefault();
      lenis.scrollTo(target, { offset: -80 });
    });
  });
}

/** Fade-up for [data-reveal], staggered when siblings reveal together. */
function reveals() {
  ScrollTrigger.batch("[data-reveal]", {
    start: "top 90%",
    once: true,
    onEnter: (batch) =>
      gsap.fromTo(batch, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 1, ease: "expo.out", stagger: 0.09 }),
  });
}

/** Photos wipe in from below while the image inside settles from a slight zoom. */
function imageReveals() {
  document.querySelectorAll("[data-reveal-img]").forEach((el) => {
    const img = el.querySelector("img");
    const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 85%", once: true } });
    tl.to(el, { clipPath: "inset(0% 0 0 0)", duration: 1.3, ease: "expo.inOut" });
    if (img) tl.from(img, { scale: 1.25, duration: 1.6, ease: "expo.out" }, 0);
  });
}

/** Headings rise word by word (screen readers still get the full sentence). */
function splitHeadings() {
  document.fonts.ready.then(() => {
    document.querySelectorAll("[data-split]").forEach((el) => {
      const split = SplitText.create(el, { type: "words", mask: "words", aria: "auto" });
      gsap.set(el, { autoAlpha: 1 });
      gsap.from(split.words, {
        yPercent: 110,
        duration: 1,
        ease: "expo.out",
        stagger: 0.06,
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });
  });
}

/** data-parallax="0.2": moves against the scroll (negative values move with it). */
function parallax() {
  document.querySelectorAll("[data-parallax]").forEach((el) => {
    const speed = parseFloat(el.dataset.parallax) || 0.15;
    gsap.fromTo(
      el,
      { y: -speed * 160 },
      {
        y: speed * 160,
        ease: "none",
        scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true },
      },
    );
  });
}

/** Lines that draw themselves while scrolling (timeline, booking steps). */
function drawLines() {
  document.querySelectorAll("[data-draw-y]").forEach((el) => {
    gsap.fromTo(
      el,
      { scaleY: 0 },
      { scaleY: 1, ease: "none", scrollTrigger: { trigger: el.parentElement, start: "top 70%", end: "bottom 60%", scrub: true } },
    );
  });
  document.querySelectorAll("[data-draw-x]").forEach((el) => {
    gsap.fromTo(
      el,
      { scaleX: 0 },
      { scaleX: 1, duration: 1.6, ease: "expo.inOut", scrollTrigger: { trigger: el.parentElement, start: "top 75%", once: true } },
    );
  });
}

/** Featured tours slide sideways while the section is pinned (large screens only). */
function horizontalScroll() {
  gsap.matchMedia().add("(min-width: 1024px)", () => {
    const section = document.querySelector("[data-hscroll]");
    const track = section?.querySelector("[data-hscroll-track]");
    if (!track) return undefined;
    track.style.overflow = "visible";
    const distance = () => Math.max(0, track.scrollWidth - track.clientWidth);
    // Pin just below the fixed header (and the demo bar), not under it.
    const headerBottom = () => document.querySelector("[data-header]")?.getBoundingClientRect().bottom || 0;
    gsap.to(track, {
      x: () => -distance(),
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: () => `top ${headerBottom()}px`,
        end: () => `+=${distance()}`,
        pin: true,
        scrub: 1,
        invalidateOnRefresh: true,
      },
    });
    return () => {
      track.style.overflow = "";
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

export function initMotion() {
  if (!motionAllowed()) return;
  smoothScroll();
  reveals();
  imageReveals();
  splitHeadings();
  parallax();
  drawLines();
  horizontalScroll();
  magnetic();
  window.addEventListener("load", () => ScrollTrigger.refresh());
}
