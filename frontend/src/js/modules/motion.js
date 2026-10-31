import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger);

export const prefersReducedMotion = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const motionAllowed = () =>
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
