/**
 * Project brief: shows one step (fieldset[data-step]) at a time with Back / Next and a
 * progress bar. Without JavaScript every step is visible and it's one ordinary form.
 * Each step's required fields are checked before moving on; after a failed submit
 * (HTMX swaps the form back in) it opens the first step that has an error.
 */
export function initBrief() {
  document.querySelectorAll("form[data-brief]:not([data-brief-ready])").forEach((form) => {
    form.dataset.briefReady = "";
    const steps = [...form.querySelectorAll("[data-step]")];
    if (steps.length < 2) return;
    const prev = form.querySelector("[data-brief-prev]");
    const next = form.querySelector("[data-brief-next]");
    const submit = form.querySelector("[data-brief-submit]");
    const header = form.querySelector("[data-brief-header]");
    const count = form.querySelector("[data-brief-count]");
    const bar = form.querySelector("[data-brief-progress]");
    const stepLabel = form.dataset.stepLabel || "Step {n} of {total}";

    const errorStep = steps.findIndex((step) => step.querySelector(".form-error, [aria-invalid='true']"));
    let index = Math.max(0, errorStep);

    const show = (to, focus) => {
      index = Math.max(0, Math.min(steps.length - 1, to));
      steps.forEach((step, i) => (step.hidden = i !== index));
      prev.hidden = index === 0;
      next.hidden = index === steps.length - 1;
      submit.hidden = index !== steps.length - 1;
      count.textContent = stepLabel.replace("{n}", index + 1).replace("{total}", steps.length);
      bar.style.width = `${((index + 1) / steps.length) * 100}%`;
      if (focus) {
        const legend = steps[index].querySelector("legend");
        legend?.setAttribute("tabindex", "-1");
        legend?.focus({ preventScroll: true });
        form.closest("#quote-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    };

    // Native validation for the current step only (the form itself keeps novalidate,
    // so the server stays the source of truth).
    const stepIsValid = () => {
      const fields = [...steps[index].querySelectorAll("input, select, textarea")].filter(
        (field) => field.willValidate && field.type !== "hidden",
      );
      const radios = steps[index].querySelectorAll("input[type=radio][required]");
      for (const field of fields) {
        if (!field.checkValidity()) {
          field.reportValidity();
          return false;
        }
      }
      if (radios.length && ![...radios].some((radio) => radio.checked)) {
        radios[0].reportValidity();
        return false;
      }
      return true;
    };

    form.classList.add("is-stepped");
    header.hidden = false;
    prev.addEventListener("click", () => show(index - 1, true));
    next.addEventListener("click", () => stepIsValid() && show(index + 1, true));
    // Enter in a text field moves to the next step instead of submitting early.
    form.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.target.tagName === "TEXTAREA" || index === steps.length - 1) return;
      if (event.target.closest("[data-step]")) {
        event.preventDefault();
        if (stepIsValid()) show(index + 1, true);
      }
    });
    show(index, errorStep >= 0);
  });
}
