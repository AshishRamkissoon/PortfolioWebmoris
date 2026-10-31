/** Switch the sticky header to its glass style once the page scrolls. */
export function initHeader() {
  const header = document.querySelector("[data-site-header]");
  if (!header) return;

  const update = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
  update();
  window.addEventListener("scroll", update, { passive: true });
}
