/*!
 * Webmoris demo kit — include on every public demo of a ready-made website.
 *
 * Put it as the FIRST element inside <body>, without defer, so the bar is in place
 * before the first paint (no layout shift):
 *
 *   <body>
 *   <script src="/demo-kit.js"
 *           data-template="lagon-bistro"            (slug on webmoris.mu)
 *           data-agency="https://webmoris.mu"
 *           data-lang="en"></script>                 ("en" or "fr")
 *
 * It (1) shows a "Demo website by Webmoris" bar linking to the enquiry form,
 * (2) blocks every form so a demo never collects anyone's details, and
 * (3) adds a robots noindex meta tag (backup for the X-Robots-Tag header).
 * No dependencies; styles are set through the CSSOM, so a strict CSP is fine.
 */
(function () {
  "use strict";

  var script = document.currentScript;
  if (!script) return;
  var config = {
    template: script.dataset.template || "",
    agency: script.dataset.agency || "https://webmoris.mu",
    lang: script.dataset.lang === "fr" ? "fr" : "en",
  };

  var TEXT = {
    en: {
      bar: "Demo website by Webmoris — all businesses and content are fictional.",
      cta: "Get this website",
      formTitle: "This is a demo",
      formBody: "Forms on this demo don't send anything. Want this website for your business?",
      close: "Close",
    },
    fr: {
      bar: "Site de démonstration par Webmoris — entreprises et contenus fictifs.",
      cta: "Obtenir ce site",
      formTitle: "Ceci est une démo",
      formBody: "Les formulaires de cette démo n'envoient rien. Ce site vous intéresse pour votre entreprise ?",
      close: "Fermer",
    },
  }[config.lang];

  // Enquiry page for this template on the agency site (falls back to the contact page).
  var enquiryUrl = new URL(
    config.template
      ? "/" + config.lang + "/contact/ready-made/" + encodeURIComponent(config.template) + "/"
      : "/" + config.lang + "/contact/",
    config.agency,
  ).href;

  function el(tag, styles, text) {
    var node = document.createElement(tag);
    if (styles) Object.assign(node.style, styles);
    if (text) node.textContent = text;
    return node;
  }

  function ctaLink(styles) {
    var link = el("a", styles, TEXT.cta + " →");
    link.href = enquiryUrl;
    link.target = "_blank";
    link.rel = "noopener";
    return link;
  }

  // (3) Keep demos out of search results.
  function addNoindex() {
    if (document.querySelector('meta[name="robots"][data-demo-kit]')) return;
    var meta = document.createElement("meta");
    meta.name = "robots";
    meta.content = "noindex, nofollow";
    meta.dataset.demoKit = "";
    document.head.appendChild(meta);
  }

  // (1) The demo bar, pinned to the top of the page.
  function addBar() {
    var bar = el("div", {
      position: "sticky",
      top: "0",
      zIndex: "2147483000",
      display: "flex",
      flexWrap: "wrap",
      alignItems: "center",
      justifyContent: "center",
      gap: "8px 16px",
      padding: "8px 16px",
      background: "#05060a",
      color: "#eef0f6",
      font: "500 14px/1.4 system-ui, -apple-system, Segoe UI, sans-serif",
      textAlign: "center",
      borderBottom: "1px solid #22e3ff",
    });
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", TEXT.formTitle);
    bar.dataset.demoKit = "bar";
    bar.appendChild(el("span", null, TEXT.bar));
    bar.appendChild(
      ctaLink({
        color: "#05060a",
        background: "#22e3ff",
        padding: "4px 12px",
        borderRadius: "999px",
        fontWeight: "700",
        textDecoration: "none",
        whiteSpace: "nowrap",
      }),
    );
    document.body.insertBefore(bar, document.body.firstChild);

    // Fixed headers on the demo can sit below the bar with: top: var(--demo-bar-h, 0px)
    var root = document.documentElement;
    var publishHeight = function () {
      root.style.setProperty("--demo-bar-h", bar.offsetHeight + "px");
    };
    publishHeight();
    window.addEventListener("resize", publishHeight);
  }

  // (2) Forms never submit; show a friendly explanation instead.
  var dialog;
  function showFormNotice() {
    if (dialog) {
      dialog.style.display = "grid";
      dialog.querySelector("a").focus();
      return;
    }
    dialog = el("div", {
      position: "fixed",
      inset: "0",
      zIndex: "2147483001",
      display: "grid",
      placeItems: "center",
      padding: "16px",
      background: "rgba(5, 6, 10, 0.75)",
    });
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", TEXT.formTitle);
    dialog.dataset.demoKit = "dialog";

    var panel = el("div", {
      maxWidth: "420px",
      padding: "28px",
      borderRadius: "16px",
      background: "#0b0d14",
      color: "#eef0f6",
      border: "1px solid #232838",
      font: "15px/1.6 system-ui, -apple-system, Segoe UI, sans-serif",
      textAlign: "center",
    });
    panel.appendChild(el("h2", { margin: "0 0 8px", fontSize: "22px" }, TEXT.formTitle));
    panel.appendChild(el("p", { margin: "0 0 20px", color: "#c9cfdc" }, TEXT.formBody));
    panel.appendChild(
      ctaLink({
        display: "inline-block",
        color: "#05060a",
        background: "#22e3ff",
        padding: "10px 20px",
        borderRadius: "999px",
        fontWeight: "700",
        textDecoration: "none",
      }),
    );
    var close = el(
      "button",
      { display: "block", margin: "14px auto 0", background: "none", border: "0", color: "#a3abbd", cursor: "pointer", font: "inherit" },
      TEXT.close,
    );
    close.type = "button";
    close.addEventListener("click", hide);
    panel.appendChild(close);
    dialog.appendChild(panel);
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) hide();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") hide();
    });
    document.body.appendChild(dialog);
    panel.querySelector("a").focus();

    function hide() {
      dialog.style.display = "none";
    }
  }

  // Capture phase: runs before any site script, and stops it from submitting too.
  document.addEventListener(
    "submit",
    function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      showFormNotice();
    },
    true,
  );

  function init() {
    addNoindex();
    addBar();
  }
  // At the top of <body> the body already exists: add the bar now, before first paint.
  // (Loaded from <head> or with defer, it falls back to waiting for the DOM.)
  if (document.body) {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
