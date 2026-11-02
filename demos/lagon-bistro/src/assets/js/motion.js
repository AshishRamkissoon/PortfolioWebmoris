import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

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

const headerBottom = () => document.querySelector("[data-header]")?.getBoundingClientRect().bottom || 0;

function smoothScroll() {
  const lenis = new Lenis({ lerp: 0.085 });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  // In-page links glide instead of jumping.
  document.querySelectorAll('a[href^="#"]:not([href="#"]), a[href^="/#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const hash = link.getAttribute("href").replace(/^\//, "");
      if (link.pathname !== location.pathname) return;
      const target = document.querySelector(hash);
      if (!target) return;
      event.preventDefault();
      lenis.scrollTo(target, { offset: -90 });
    });
  });
}

/** Fade-up for [data-reveal], staggered when siblings reveal together. */
function reveals() {
  ScrollTrigger.batch("[data-reveal]", {
    start: "top 90%",
    once: true,
    onEnter: (batch) =>
      gsap.fromTo(batch, { autoAlpha: 0, y: 50 }, { autoAlpha: 1, y: 0, duration: 1.1, ease: "expo.out", stagger: 0.08 }),
  });
}

/** Photos wipe open from the centre while the image settles from a zoom. */
function imageReveals() {
  document.querySelectorAll("[data-reveal-img]").forEach((el) => {
    const img = el.querySelector("img");
    const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 85%", once: true } });
    tl.fromTo(el, { clipPath: "inset(100% 0 0 0)" }, { clipPath: "inset(0% 0 0 0)", duration: 1.4, ease: "expo.inOut" });
    if (img) tl.from(img, { scale: 1.3, duration: 1.8, ease: "expo.out" }, 0.1);
  });
}

/** Headlines: words rise out of a mask; data-split="chars" animates letter by letter. */
function splitHeadings() {
  document.fonts.ready.then(() => {
    document.querySelectorAll("[data-split]").forEach((el) => {
      const chars = el.dataset.split === "chars";
      const split = SplitText.create(el, { type: chars ? "words,chars" : "words", mask: chars ? "chars" : "words", aria: "auto" });
      gsap.set(el, { autoAlpha: 1 });
      gsap.from(chars ? split.chars : split.words, {
        yPercent: 115,
        rotate: chars ? 8 : 0,
        duration: chars ? 0.9 : 1.1,
        ease: "expo.out",
        stagger: chars ? 0.02 : 0.07,
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
      { yPercent: -speed * 50 },
      {
        yPercent: speed * 50,
        ease: "none",
        scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true },
      },
    );
  });
}

/** Marquee rows that speed up, skew and change direction with the scroll. */
function marquee() {
  const rows = [...document.querySelectorAll("[data-marquee]")];
  if (!rows.length) return;
  const tweens = rows.map((row) => {
    const reverse = row.dataset.marquee === "reverse";
    return gsap.fromTo(row, { xPercent: reverse ? -50 : 0 }, { xPercent: reverse ? 0 : -50, duration: 40, ease: "none", repeat: -1 });
  });
  const skew = rows.map((row) => gsap.quickTo(row, "skewX", { duration: 0.6, ease: "power3.out" }));
  let direction = 1;
  ScrollTrigger.create({
    trigger: rows[0].closest("section"),
    start: "top bottom",
    end: "bottom top",
    onUpdate: (self) => {
      const velocity = self.getVelocity();
      direction = self.direction;
      const boost = 1 + Math.min(Math.abs(velocity) / 250, 6);
      tweens.forEach((tween) => {
        tween.timeScale(direction * boost);
        gsap.to(tween, { timeScale: direction, duration: 1.2, ease: "power2.out", overwrite: true });
      });
      skew.forEach((set) => set(gsap.utils.clamp(-12, 12, velocity / -120)));
    },
  });
  ScrollTrigger.addEventListener("scrollEnd", () => skew.forEach((set) => set(0)));
}

/** "Our day": a pinned scene where the sky goes from noon to sunset to night as you scroll. */
function dayToNight() {
  const scene = document.querySelector("[data-day]");
  if (!scene) return;
  scene.classList.add("is-pinned");
  const skies = scene.querySelectorAll("[data-sky]");
  const panels = scene.querySelectorAll("[data-day-panel]");
  const sun = scene.querySelector("[data-sun]");
  const glow = scene.querySelector("[data-sun-glow]");
  const moon = scene.querySelector("[data-moon]");
  const stars = scene.querySelector("[data-stars]");
  const shore = scene.querySelector("[data-shore]");
  const sea = scene.querySelector("[data-sea]");
  const lights = scene.querySelector("[data-lights]");
  const progress = scene.querySelector("[data-day-progress]");
  const ink = scene.querySelectorAll("[data-day-ink]");
  const clock = scene.querySelector("[data-clock]");
  const steps = panels.length - 1;

  gsap.set(panels, { autoAlpha: 0, y: 40 });
  gsap.set(panels[0], { autoAlpha: 1, y: 0 });
  const tl = gsap.timeline({
    defaults: { ease: "none" },
    scrollTrigger: {
      trigger: scene,
      start: () => `top ${headerBottom()}px`,
      end: () => `+=${window.innerHeight * 3}`,
      pin: true,
      scrub: 0.8,
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        // The clock runs from 12:00 to 23:00.
        const minutes = 12 * 60 + Math.round(self.progress * 11 * 60);
        if (clock) clock.textContent = `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
      },
    },
  });

  // Sky layers cross-fade: noon → golden hour → dusk → night.
  skies.forEach((sky, index) => index > 0 && tl.to(sky, { opacity: 1, duration: 1 }, index - 1));
  // The sun sinks along an arc and dives below the horizon; its glow swells at sunset.
  // (High on the right at noon, clear of the text; it sets in the middle.)
  tl.fromTo(sun, { yPercent: -230, xPercent: 170, scale: 0.8 }, { yPercent: 110, xPercent: -50, scale: 1.25, duration: 2.2 }, 0);
  tl.fromTo(glow, { opacity: 0.2, scale: 0.6 }, { opacity: 1, scale: 1.3, duration: 1.4 }, 0.2).to(glow, { opacity: 0, duration: 0.8 }, 1.8);
  // Headline, clock and timeline turn light as the sky darkens.
  tl.fromTo(ink, { color: "#0f141b" }, { color: "#fbf6ec", duration: 0.15 }, 1.45);
  tl.fromTo(sea, { filter: "brightness(1) saturate(1)" }, { filter: "brightness(0.4) saturate(0.8)", duration: 3 }, 0);
  tl.to(shore, { color: "#06080c", duration: 2 }, 0.6);
  tl.fromTo(stars, { opacity: 0 }, { opacity: 1, duration: 1 }, 2);
  tl.fromTo(moon, { yPercent: 120, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 1 }, 2);
  tl.fromTo(lights, { opacity: 0 }, { opacity: 1, duration: 1 }, 1.6);
  if (progress) tl.fromTo(progress, { scaleX: 0 }, { scaleX: 1, duration: 3 }, 0);
  // Text panels change at each step.
  panels.forEach((panel, index) => {
    if (!index) return;
    // Each moment arrives a little before its sky, so the last one is fully readable before the pin ends.
    const at = 0.1 + index * (2.4 / steps);
    tl.to(panels[index - 1], { autoAlpha: 0, y: -40, duration: 0.15 }, at);
    tl.fromTo(panel, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.2 }, at + 0.17);
  });
}

/** Cocktails: a pinned horizontal carousel whose background takes each drink's colour. */
function cocktails() {
  const section = document.querySelector("[data-cocktails]");
  const track = section?.querySelector("[data-cocktail-track]");
  if (!track) return;
  const cards = [...track.querySelectorAll("[data-color]")];
  const tint = section.querySelector("[data-cocktail-tint]");
  let current = -1;
  const setColor = (index) => {
    if (index === current) return;
    current = index;
    gsap.to(tint, { backgroundColor: cards[index].dataset.color, duration: 0.9, ease: "power2.out" });
    cards.forEach((card, i) => card.classList.toggle("is-active", i === index));
  };
  setColor(0);
  gsap.matchMedia().add("(min-width: 1024px)", () => {
    track.style.overflow = "visible";
    const distance = () => Math.max(0, track.scrollWidth - track.clientWidth);
    const tween = gsap.to(track, {
      x: () => -distance(),
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: () => `top ${headerBottom()}px`,
        end: () => `+=${distance()}`,
        pin: true,
        scrub: 1,
        invalidateOnRefresh: true,
        onUpdate: (self) => setColor(Math.min(cards.length - 1, Math.round(self.progress * (cards.length - 1)))),
      },
    });
    // Cards turn slightly as they travel, like a reel.
    cards.forEach((card) =>
      gsap.fromTo(
        card.querySelector("[data-cocktail-photo]"),
        { rotate: 6, y: 30 },
        { rotate: -6, y: -30, ease: "none", scrollTrigger: { trigger: card, containerAnimation: tween, start: "left right", end: "right left", scrub: true } },
      ),
    );
    return () => {
      track.style.overflow = "";
    };
  });
  // Small screens: the colour follows the card nearest the centre of the native scroller.
  gsap.matchMedia().add("(max-width: 1023px)", () => {
    const onScroll = () => {
      const middle = track.scrollLeft + track.clientWidth / 2;
      let best = 0;
      cards.forEach((card, i) => {
        if (Math.abs(card.offsetLeft + card.offsetWidth / 2 - middle) < Math.abs(cards[best].offsetLeft + cards[best].offsetWidth / 2 - middle)) best = i;
      });
      setColor(best);
    };
    track.addEventListener("scroll", onScroll, { passive: true });
    return () => track.removeEventListener("scroll", onScroll);
  });
}

/** Cards tilt in 3D toward the pointer, with a soft light that follows it. */
function tilt() {
  if (!finePointer()) return;
  document.querySelectorAll("[data-tilt]").forEach((card) => {
    const rotateX = gsap.quickTo(card, "rotationX", { duration: 0.6, ease: "power3.out" });
    const rotateY = gsap.quickTo(card, "rotationY", { duration: 0.6, ease: "power3.out" });
    const shine = card.querySelector("[data-shine]");
    gsap.set(card, { transformPerspective: 900 });
    card.addEventListener("pointermove", (event) => {
      const box = card.getBoundingClientRect();
      const x = (event.clientX - box.left) / box.width;
      const y = (event.clientY - box.top) / box.height;
      rotateY((x - 0.5) * 12);
      rotateX((0.5 - y) * 10);
      if (shine) shine.style.background = `radial-gradient(circle at ${x * 100}% ${y * 100}%, rgb(255 198 110 / 0.28), transparent 55%)`;
    });
    card.addEventListener("pointerleave", () => {
      rotateX(0);
      rotateY(0);
      if (shine) shine.style.background = "";
    });
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
      x((event.clientX - box.left - box.width / 2) * 0.35);
      y((event.clientY - box.top - box.height / 2) * 0.45);
    });
    el.addEventListener("pointerleave", () => {
      x(0);
      y(0);
    });
  });
}

/** A ring that trails the pointer, grows over links and shows labels like "View" (desktop). */
function cursor() {
  if (!finePointer()) return;
  const ring = document.createElement("div");
  ring.className = "cursor";
  ring.setAttribute("aria-hidden", "true");
  document.body.append(ring);
  const x = gsap.quickTo(ring, "x", { duration: 0.35, ease: "power3.out" });
  const y = gsap.quickTo(ring, "y", { duration: 0.35, ease: "power3.out" });
  gsap.set(ring, { autoAlpha: 0 });
  window.addEventListener("pointermove", (event) => {
    x(event.clientX);
    y(event.clientY);
    gsap.to(ring, { autoAlpha: 1, duration: 0.3, overwrite: "auto" });
    const target = event.target.closest?.("[data-cursor], a, button");
    const label = target?.dataset.cursor;
    ring.classList.toggle("is-label", Boolean(label));
    ring.classList.toggle("is-link", Boolean(target) && !label);
    ring.textContent = label || "";
  });
  document.documentElement.addEventListener("pointerleave", () => gsap.to(ring, { autoAlpha: 0, duration: 0.3 }));
}

/** Big closing call to action: letters lift one after another while it scrolls into view. */
function wave() {
  document.querySelectorAll("[data-wave]").forEach((el) => {
    const split = SplitText.create(el, { type: "chars", aria: "auto" });
    gsap.from(split.chars, {
      yPercent: 60,
      opacity: 0.2,
      stagger: 0.03,
      ease: "none",
      scrollTrigger: { trigger: el, start: "top 95%", end: "top 45%", scrub: true },
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
  marquee();
  dayToNight();
  cocktails();
  tilt();
  magnetic();
  cursor();
  wave();
  window.addEventListener("load", () => ScrollTrigger.refresh());
}
