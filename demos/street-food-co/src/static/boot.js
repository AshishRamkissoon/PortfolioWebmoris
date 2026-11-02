/* Runs before first paint: animations only hide content when motion is allowed,
   and un-hide it again if the main script never loads. */
(function (root) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  root.classList.add("motion-ok");
  setTimeout(function () {
    if (!window.__motionReady) root.classList.remove("motion-ok");
  }, 3000);
})(document.documentElement);
