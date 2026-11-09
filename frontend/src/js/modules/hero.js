import { motionAllowed } from "./motion.js";

const ROTATE_EVERY = 4500;

/**
 * Home hero picker: tapping a business type shows its typical features and "From" price,
 * points "Start my website" at the brief with that project type, and swaps the demo preview.
 * The chips are plain links (?business=…), so everything also works without JS.
 */
export function initHeroPicker() {
  const hero = document.querySelector("[data-hero]");
  if (!hero?.dataset.heroJson) return;

  const data = JSON.parse(hero.dataset.heroJson);
  const bySlug = Object.fromEntries(data.businesses.map((b) => [b.slug, b]));
  const $ = (selector) => hero.querySelector(selector);
  const chips = hero.querySelectorAll("[data-hero-chip]");
  const result = $("[data-hero-result]");
  const image = $("[data-hero-image]");
  const tags = hero.querySelectorAll("[data-hero-tag]");
  let rotation = null;

  function showPreview(business, features) {
    features.forEach((text, i) => tags[i] && (tags[i].textContent = text));
    if (!image || !business.image || image.getAttribute("src") === business.image) return;
    const swap = () => {
      image.src = business.image;
      image.alt = image.alt.replace(/:.*$/, `: ${business.demo_name}`);
      $("[data-hero-demo-name]").textContent = business.demo_name;
      $("[data-hero-window]").href = business.demo_url;
      $("[data-hero-demo-link]").href = business.demo_url;
      image.classList.remove("is-swapping");
    };
    if (!motionAllowed()) return swap();
    image.classList.add("is-swapping");
    const next = new Image();
    next.src = business.image;
    next.decode().catch(() => {}).finally(() => setTimeout(swap, 200));
  }

  function select(slug) {
    const business = bySlug[slug];
    if (!business) return;
    stopRotation();
    chips.forEach((chip) => {
      if (chip.dataset.heroChip === slug) chip.setAttribute("aria-current", "true");
      else chip.removeAttribute("aria-current");
    });
    $("[data-hero-features]").textContent = business.features.join(" · ");
    const price = $("[data-hero-price]");
    price.hidden = !business.price;
    $("[data-hero-price-value]").textContent = business.price;
    result.hidden = false;
    $("[data-hero-cta]").href = business.quote_url;
    showPreview(business, business.features);
  }

  // With nothing picked, the preview cycles through the demos (never under reduced motion).
  function startRotation() {
    const withDemo = data.businesses.filter((b) => b.image);
    if (!motionAllowed() || withDemo.length < 2 || !image) return;
    let index = 0;
    rotation = setInterval(() => {
      if (document.hidden) return;
      index = (index + 1) % withDemo.length;
      showPreview(withDemo[index], data.defaultFeatures);
    }, ROTATE_EVERY);
  }

  function stopRotation() {
    clearInterval(rotation);
    rotation = null;
  }

  chips.forEach((chip) =>
    chip.addEventListener("click", (event) => {
      event.preventDefault();
      select(chip.dataset.heroChip);
    }),
  );

  if (!hero.querySelector('[data-hero-chip][aria-current="true"]')) startRotation();
}
