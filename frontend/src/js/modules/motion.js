import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger, SplitText);

export const prefersReducedMotion = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export const motionAllowed = () =>
  !prefersReducedMotion() && document.documentElement.classList.contains("motion-ok");

export function initSmoothScroll() {
  if (!motionAllowed()) return null;
  const lenis = new Lenis();
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  return lenis;
}

/**
 * Fade/slide in every [data-reveal] element as it enters the viewport.
 * Optional data-reveal-delay="0.2" (seconds). Runs once per element.
 */
export function initReveals(root = document) {
  window.__motionReady = true;
  if (!motionAllowed()) return;

  const pending = root.querySelectorAll("[data-reveal]:not([data-revealed])");
  pending.forEach((el) => {
    el.dataset.revealed = "";
    gsap.fromTo(
      el,
      { autoAlpha: 0, y: 32 },
      {
        autoAlpha: 1,
        y: 0,
        duration: 0.9,
        ease: "power3.out",
        delay: parseFloat(el.dataset.revealDelay || 0),
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      },
    );
  });
  // New content changes the page height, so recompute trigger positions.
  if (pending.length) ScrollTrigger.refresh();
}

/** Headings marked [data-split] rise in word by word. SplitText keeps them readable to screen readers. */
export function initSplitHeadings(root = document) {
  if (!motionAllowed()) return;

  document.fonts.ready.then(() => {
    root.querySelectorAll("[data-split]:not([data-revealed])").forEach((el) => {
      el.dataset.revealed = "";
      const split = SplitText.create(el, { type: "words", mask: "words", aria: "auto" });
      gsap.set(el, { autoAlpha: 1 });
      gsap.from(split.words, {
        yPercent: 110,
        duration: 0.8,
        ease: "power3.out",
        stagger: 0.05,
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });
  });
}

/**
 * [data-hscroll] sections pin on large screens while their [data-hscroll-track]
 * slides sideways. Smaller screens keep the native swipeable row.
 */
export function initHorizontalScroll() {
  if (!motionAllowed()) return;

  gsap.matchMedia().add("(min-width: 1024px)", () => {
    document.querySelectorAll("[data-hscroll]").forEach((section) => {
      const track = section.querySelector("[data-hscroll-track]");
      if (!track) return;
      track.classList.add("is-pinned");
      const distance = () => Math.max(0, track.scrollWidth - track.clientWidth);
      if (!distance()) return;

      gsap.to(track, {
        x: () => -distance(),
        ease: "none",
        scrollTrigger: {
          trigger: section,
          start: "top top",
          end: () => `+=${distance()}`,
          pin: true,
          scrub: 1,
          invalidateOnRefresh: true,
        },
      });
    });

    // Undo when the screen shrinks below the breakpoint.
    return () => {
      document.querySelectorAll("[data-hscroll-track]").forEach((track) => {
        track.classList.remove("is-pinned");
      });
    };
  });
}

/** Whether this device should get the WebGL hero (otherwise the CSS glow stays). */
export function canRenderHero() {
  if (!motionAllowed() || window.innerWidth < 768) return false;
  if (navigator.connection?.saveData) return false;
  if ((navigator.hardwareConcurrency || 8) < 4 || (navigator.deviceMemory || 8) < 4) return false;
  try {
    return Boolean(document.createElement("canvas").getContext("webgl2"));
  } catch {
    return false;
  }
}

const canHover = () => window.matchMedia("(hover: hover) and (pointer: fine)").matches;

/** [data-magnetic] buttons lean toward the pointer (mouse devices only). */
export function initMagnetic(root = document) {
  if (!motionAllowed() || !canHover()) return;
  root.querySelectorAll("[data-magnetic]:not([data-magnetized])").forEach((el) => {
    el.dataset.magnetized = "";
    const x = gsap.quickTo(el, "x", { duration: 0.4, ease: "power3.out" });
    const y = gsap.quickTo(el, "y", { duration: 0.4, ease: "power3.out" });
    el.addEventListener("pointermove", (event) => {
      const box = el.getBoundingClientRect();
      x((event.clientX - box.left - box.width / 2) * 0.25);
      y((event.clientY - box.top - box.height / 2) * 0.35);
    });
    el.addEventListener("pointerleave", () => {
      x(0);
      y(0);
    });
  });
}

/** Project cards tilt slightly in 3D under the pointer (mouse devices only). */
export function initTilt(root = document) {
  if (!motionAllowed() || !canHover()) return;
  root.querySelectorAll(".project-card:not([data-tilted]), [data-tilt]:not([data-tilted])").forEach((card) => {
    card.dataset.tilted = "";
    gsap.set(card, { transformPerspective: 900 });
    const rotateX = gsap.quickTo(card, "rotationX", { duration: 0.5, ease: "power3.out" });
    const rotateY = gsap.quickTo(card, "rotationY", { duration: 0.5, ease: "power3.out" });
    card.addEventListener("pointermove", (event) => {
      const box = card.getBoundingClientRect();
      rotateY(((event.clientX - box.left) / box.width - 0.5) * 6);
      rotateX(((event.clientY - box.top) / box.height - 0.5) * -6);
    });
    card.addEventListener("pointerleave", () => {
      rotateX(0);
      rotateY(0);
    });
  });
}
