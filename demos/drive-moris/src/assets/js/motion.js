import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

import { setOdometer } from "./odometer.js";

gsap.registerPlugin(ScrollTrigger);

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

/** Gentle fade-up for [data-reveal], staggered when siblings reveal together. */
function reveals() {
  ScrollTrigger.batch("[data-reveal]", {
    start: "top 92%",
    once: true,
    onEnter: (batch) =>
      gsap.fromTo(batch, { autoAlpha: 0, y: 28 }, { autoAlpha: 1, y: 0, duration: 0.8, ease: "power3.out", stagger: 0.07 }),
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
  reveals();
  coastRoute();
  window.addEventListener("load", () => ScrollTrigger.refresh());
}
