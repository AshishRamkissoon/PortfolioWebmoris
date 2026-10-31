import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";

gsap.registerPlugin(ScrollTrigger, SplitText);

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

/** Numbers marked [data-count-up="42"] count from 0 when scrolled into view. */
export function initCountUps(root = document) {
  if (!motionAllowed()) return;

  root.querySelectorAll("[data-count-up]:not([data-counted])").forEach((el) => {
    el.dataset.counted = "";
    const end = parseInt(el.dataset.countUp, 10);
    if (!end) return;
    const counter = { value: 0 };
    el.textContent = "0";
    gsap.to(counter, {
      value: end,
      duration: 1.6,
      ease: "power2.out",
      scrollTrigger: { trigger: el, start: "top 90%", once: true },
      onUpdate: () => {
        el.textContent = Math.round(counter.value);
      },
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
