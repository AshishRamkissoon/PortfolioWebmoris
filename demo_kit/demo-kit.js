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
 *
 * Optional (4): if the demo serves /demo-tour.json next to this script, the kit also adds
 * the "Get this website" badge, the "See why it converts" tour, a mobile action bar and a
 * scroll nudge, styled by demo-kit.css (loaded from the same folder). No cookies, no tracking.
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
  // Demos are written in one language, but the kit speaks French to French-speaking browsers.
  if (/^fr\b/i.test((navigator.languages && navigator.languages[0]) || navigator.language || "")) {
    config.lang = "fr";
  }

  var TEXT = {
    en: {
      bar: "Demo website by Webmoris — all businesses and content are fictional.",
      cta: "Get this website",
      formTitle: "This is a demo",
      formBody: "Forms on this demo don't send anything. Want this website for your business?",
      close: "Close",
      contactBody: "On your website, this button calls or messages your business directly. On the demo it goes nowhere.",
      pill: "Like this site? Get it for your business",
      pillShort: "Get this site",
      cardEyebrow: "Ready-made demo by Webmoris",
      cardTitle: "Like this website?",
      pitch: "Get it for your business, with your logo, colours, photos and texts. Online in about 2 weeks.",
      priceFrom: "Ready-made, from",
      priceAsk: "Price on request: ask us, it's quick.",
      checks: ["Fast on mobile data", "Works on every phone", "English & French", "Google-ready (SEO)", "WhatsApp & booking", "Easy to update"],
      toggle: "See why it converts",
      tag: "Why it converts",
      thinking: "The thinking:",
      back: "← Back",
      next: "Next →",
      finish: "Finish",
      of: " of ",
      blueprint: "Page blueprint: why the sections are in this order",
      backToTour: "← Back to the tour",
      endTitle: "Every section has a job",
      endText: "Nothing on this page is there by chance: each part answers a question your customers have, then shows them the next step.",
      call: "Call",
      whatsapp: "WhatsApp",
      closeTour: "Close the tour",
    },
    fr: {
      bar: "Site de démonstration par Webmoris — entreprises et contenus fictifs.",
      cta: "Obtenir ce site",
      formTitle: "Ceci est une démo",
      formBody: "Les formulaires de cette démo n'envoient rien. Ce site vous intéresse pour votre entreprise ?",
      close: "Fermer",
      contactBody: "Sur votre site, ce bouton appelle ou écrit directement à votre entreprise. Sur la démo, il ne mène nulle part.",
      pill: "Ce site vous plaît ? Obtenez-le pour votre entreprise",
      pillShort: "Obtenir ce site",
      cardEyebrow: "Démo clé en main par Webmoris",
      cardTitle: "Ce site vous plaît ?",
      pitch: "Obtenez-le pour votre entreprise, avec votre logo, vos couleurs, vos photos et vos textes. En ligne en 2 semaines environ.",
      priceFrom: "Clé en main, dès",
      priceAsk: "Prix sur demande : demandez-nous, c'est rapide.",
      checks: ["Rapide sur mobile", "Sur tous les téléphones", "Anglais & français", "Prêt pour Google (SEO)", "WhatsApp & réservation", "Facile à modifier"],
      toggle: "Pourquoi ça convertit",
      tag: "Pourquoi ça marche",
      thinking: "L'idée :",
      back: "← Retour",
      next: "Suivant →",
      finish: "Terminer",
      of: " sur ",
      blueprint: "Plan de la page : pourquoi les sections sont dans cet ordre",
      backToTour: "← Retour à la visite",
      endTitle: "Chaque section a un rôle",
      endText: "Rien n'est là par hasard : chaque partie répond à une question de vos clients, puis leur montre l'étape suivante.",
      call: "Appeler",
      whatsapp: "WhatsApp",
      closeTour: "Fermer la visite",
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
  var dialog, dialogText;
  function showFormNotice(message) {
    if (dialog) {
      dialogText.textContent = message || TEXT.formBody;
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
    dialogText = el("p", { margin: "0 0 20px", color: "#c9cfdc" }, message || TEXT.formBody);
    panel.appendChild(dialogText);
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
      // Only exception: a same-site GET form marked as navigation (e.g. a "see prices" search bar).
      // It just opens another page of the demo and sends nothing anywhere.
      var form = event.target;
      if (
        form.hasAttribute("data-demo-navigation") &&
        (form.getAttribute("method") || "get").toLowerCase() === "get" &&
        new URL(form.action, location.href).origin === location.origin
      ) {
        return;
      }
      event.preventDefault();
      event.stopImmediatePropagation();
      showFormNotice(TEXT.formBody);
    },
    true,
  );

  // (4) Optional extras, driven by demo-tour.json: badge, tour, mobile bar, nudge.
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function t(value) {
    if (!value) return "";
    return typeof value === "string" ? value : value[config.lang] || value.en || "";
  }

  function make(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function button(className, text) {
    var node = make("button", className, text);
    node.type = "button";
    return node;
  }

  function loadExtras() {
    if (!window.fetch || !script.src) return;
    fetch(new URL("demo-tour.json", script.src).href, { credentials: "omit" })
      .then(function (response) {
        return response.ok ? response.json() : null;
      })
      .then(function (tour) {
        if (!tour) return;
        var css = document.createElement("link");
        css.rel = "stylesheet";
        css.href = new URL("demo-kit.css", script.src).href;
        css.onload = function () {
          buildExtras(tour, fetchBadgeData());
        };
        document.head.appendChild(css);
      })
      .catch(function (error) {
        if (window.console) console.warn("Webmoris demo kit:", error);
      });
  }

  // Price and WhatsApp link come from the agency site, where they are managed in admin.
  function fetchBadgeData() {
    if (!config.template) return Promise.resolve(null);
    var url = new URL("/api/demo-badge/" + encodeURIComponent(config.template) + "/", config.agency).href;
    return fetch(url, { mode: "cors", credentials: "omit" })
      .then(function (response) {
        return response.ok ? response.json() : null;
      })
      .catch(function () {
        return null;
      });
  }

  function buildExtras(tour, badgeData) {
    var root = make("div", "dk-root");
    root.dataset.demoKit = "extras";
    var theme = tour.theme || {};
    var vars = { accent: "--dk-accent", accentText: "--dk-accent-text", surface: "--dk-surface", surfaceText: "--dk-surface-text", border: "--dk-border" };
    Object.keys(vars).forEach(function (key) {
      if (theme[key]) root.style.setProperty(vars[key], theme[key]);
    });
    document.body.appendChild(root);

    var floats = make("div", "dk-floats");
    root.appendChild(floats);
    var tourApi = buildTour(tour, root, floats);
    buildBadge(tour.badge || {}, badgeData, floats, tourApi);
    if (tour.mobileBar) buildMobileBar(tour.mobileBar, root);
    if (tour.nudge) buildNudge(tour.nudge, root, tourApi);

    // Slide in after a short pause, so the demo makes its first impression alone.
    setTimeout(function () {
      floats.classList.add("dk-in");
    }, reducedMotion ? 0 : 2500);
  }

  // ---- "Get this website" badge ----
  function buildBadge(badge, badgeData, floats, tourApi) {
    var card = make("div", "dk-card");
    card.id = "dk-card";
    card.hidden = true;
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-label", TEXT.cardTitle);

    var close = button("dk-close", "×");
    close.setAttribute("aria-label", TEXT.close);
    card.appendChild(close);
    card.appendChild(make("p", "dk-eyebrow", TEXT.cardEyebrow));
    card.appendChild(make("h2", null, TEXT.cardTitle));
    card.appendChild(make("p", null, t(badge.pitch) || TEXT.pitch));
    var price = make("div", "dk-price");
    function showPrice(value) {
      price.textContent = "";
      if (value) {
        price.appendChild(make("span", null, TEXT.priceFrom));
        price.appendChild(make("strong", null, value));
      } else {
        price.appendChild(make("span", null, TEXT.priceAsk));
      }
    }
    showPrice(t(badge.price));
    card.appendChild(price);
    var checks = make("ul", "dk-checks");
    TEXT.checks.forEach(function (item) {
      checks.appendChild(make("li", null, item));
    });
    card.appendChild(checks);
    var cta = make("a", "dk-cta", TEXT.cta + " →");
    cta.href = enquiryUrl;
    cta.target = "_blank";
    cta.rel = "noopener noreferrer";
    card.appendChild(cta);
    var actions = make("div", "dk-actions");
    card.insertBefore(actions, cta);
    actions.appendChild(cta);
    badgeData.then(function (data) {
      if (!data) return;
      if (data.price) showPrice(t(data.price));
      var link = t(data.whatsapp);
      if (link && /^https:\/\/wa\.me\//.test(link)) {
        var whatsapp = make("a", "dk-whatsapp", TEXT.whatsapp);
        whatsapp.href = link;
        whatsapp.target = "_blank";
        whatsapp.rel = "noopener noreferrer";
        actions.appendChild(whatsapp);
      }
    });
    if (tourApi.available) {
      var why = button("dk-link", TEXT.toggle + " →");
      why.addEventListener("click", function () {
        setOpen(false);
        tourApi.start();
      });
      card.appendChild(why);
    }

    var pill = button("dk-pill");
    pill.setAttribute("aria-expanded", "false");
    pill.setAttribute("aria-controls", "dk-card");
    pill.appendChild(make("span", "dk-w", "W"));
    pill.appendChild(make("span", "dk-long", TEXT.pill));
    pill.appendChild(make("span", "dk-short", TEXT.pillShort));

    function setOpen(open) {
      card.hidden = !open;
      pill.setAttribute("aria-expanded", String(open));
      if (open) {
        tourApi.stop();
        cta.focus();
      }
    }
    pill.addEventListener("click", function () {
      setOpen(card.hidden);
    });
    close.addEventListener("click", function () {
      setOpen(false);
      pill.focus();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !card.hidden) {
        setOpen(false);
        pill.focus();
      }
    });
    floats.insertBefore(card, floats.firstChild);
    floats.appendChild(pill);
    tourApi.onStart(function () {
      setOpen(false);
    });
  }

  // ---- "See why it converts" tour ----
  function visible(node) {
    return node && node.getClientRects().length > 0;
  }

  function buildTour(tour, root, floats) {
    var listeners = [];
    var api = {
      available: false,
      start: function () {},
      stop: function () {},
      onStart: function (fn) {
        listeners.push(fn);
      },
      running: function () {
        return false;
      },
    };
    var stops = (tour.stops || [])
      .map(function (stop) {
        return { data: stop, node: document.querySelector(stop.target) };
      })
      .filter(function (stop) {
        return visible(stop.node);
      });
    var stages = (tour.blueprint || [])
      .map(function (stage) {
        return { data: stage, node: document.querySelector(stage.target) };
      })
      .filter(function (stage) {
        return visible(stage.node);
      });
    if (!stops.length) return api;

    var toggle = button("dk-toggle");
    toggle.setAttribute("aria-pressed", "false");
    toggle.appendChild(make("span", "dk-switch"));
    toggle.appendChild(make("span", null, TEXT.toggle));
    floats.appendChild(toggle);

    var layer, spot, panel, highlights, chips, frame, index = 0, running = false, lastFocus;

    function build() {
      layer = make("div", "dk-layer");
      layer.setAttribute("aria-hidden", "true");
      spot = make("div", "dk-spot");
      layer.appendChild(spot);
      highlights = stops.map(function (stop, i) {
        var box = make("div", "dk-hl");
        var dot = button("dk-dot", String(i + 1));
        dot.tabIndex = -1;
        dot.addEventListener("click", function () {
          go(i);
        });
        box.appendChild(dot);
        layer.appendChild(box);
        return box;
      });
      chips = stages.map(function (stage, i) {
        var chip = make("p", "dk-stage", i + 1 + " · " + t(stage.data.stage));
        layer.appendChild(chip);
        return chip;
      });
      root.appendChild(layer);

      panel = make("div", "dk-panel");
      panel.setAttribute("role", "dialog");
      panel.setAttribute("aria-label", TEXT.toggle);
      panel.tabIndex = -1;
      root.appendChild(panel);
    }

    function place(node, rect, pad) {
      node.style.transform = "translate(" + (rect.left - pad) + "px," + (rect.top - pad) + "px)";
      node.style.width = rect.width + pad * 2 + "px";
      node.style.height = rect.height + pad * 2 + "px";
    }

    // Follow the page while it scrolls (pinned and animated sections move things around).
    function track() {
      stops.forEach(function (stop, i) {
        var rect = stop.node.getBoundingClientRect();
        place(highlights[i], rect, 8);
        if (i === index) place(spot, rect, 10);
      });
      stages.forEach(function (stage, i) {
        var rect = stage.node.getBoundingClientRect();
        chips[i].style.transform = "translate(" + Math.max(rect.left + 16, 16) + "px," + Math.max(rect.top + 16, -60) + "px)";
      });
      frame = requestAnimationFrame(track);
    }

    function scrollTo(node) {
      var rect = node.getBoundingClientRect();
      // On phones the panel is a bottom sheet, so targets go to the top half of the screen.
      var offset = window.innerWidth < 640 ? 150 : Math.max((window.innerHeight - rect.height) / 2, 120);
      var target = window.scrollY + rect.top - offset;
      window.scrollTo({ top: Math.max(target, 0), behavior: reducedMotion ? "auto" : "smooth" });
    }

    function render() {
      var stop = stops[index].data;
      panel.textContent = "";
      var top = make("div", "dk-panel-top");
      top.appendChild(make("span", "dk-eyebrow", TEXT.tag));
      top.appendChild(make("span", null, index + 1 + TEXT.of + stops.length));
      panel.appendChild(top);
      var close = button("dk-close", "×");
      close.setAttribute("aria-label", TEXT.closeTour);
      close.addEventListener("click", stop_);
      panel.appendChild(close);
      panel.appendChild(make("h2", null, t(stop.title)));
      panel.appendChild(make("p", null, t(stop.text)));
      var why = make("p", "dk-why");
      why.appendChild(make("strong", null, TEXT.thinking + " "));
      why.appendChild(document.createTextNode(t(stop.why)));
      panel.appendChild(why);

      var nav = make("div", "dk-nav");
      var back = button("dk-btn", TEXT.back);
      back.disabled = index === 0;
      back.addEventListener("click", function () {
        go(index - 1);
      });
      var steps = make("span", "dk-steps");
      steps.setAttribute("aria-hidden", "true");
      stops.forEach(function (_, i) {
        steps.appendChild(make("i", i <= index ? "dk-on" : ""));
      });
      var last = index === stops.length - 1;
      var next = button("dk-btn dk-btn-primary", last ? TEXT.finish : TEXT.next);
      next.addEventListener("click", function () {
        if (last) showBlueprint(true);
        else go(index + 1);
      });
      nav.appendChild(back);
      nav.appendChild(steps);
      nav.appendChild(next);
      panel.appendChild(nav);
      if (stages.length) {
        var link = button("dk-link", TEXT.blueprint + " →");
        link.addEventListener("click", function () {
          showBlueprint(false);
        });
        panel.appendChild(link);
      }
      highlights.forEach(function (box, i) {
        box.classList.toggle("dk-active", i === index);
      });
      spot.style.display = "";
    }

    function showBlueprint(atEnd) {
      panel.textContent = "";
      var close = button("dk-close", "×");
      close.setAttribute("aria-label", TEXT.closeTour);
      close.addEventListener("click", stop_);
      panel.appendChild(close);
      panel.appendChild(make("p", "dk-eyebrow", TEXT.tag));
      panel.appendChild(make("h2", null, atEnd ? TEXT.endTitle : TEXT.blueprint));
      if (atEnd) panel.appendChild(make("p", null, TEXT.endText));
      var list = make("ol", "dk-blueprint");
      stages.forEach(function (stage, i) {
        var item = make("li");
        var jump = button();
        jump.appendChild(make("em", null, i + 1 + " · " + t(stage.data.stage)));
        jump.appendChild(make("strong", null, t(stage.data.title)));
        jump.appendChild(make("span", null, t(stage.data.text)));
        jump.addEventListener("click", function () {
          scrollTo(stage.node);
        });
        item.appendChild(jump);
        list.appendChild(item);
      });
      panel.appendChild(list);
      var nav = make("div", "dk-nav");
      var back = button("dk-btn", TEXT.backToTour);
      back.addEventListener("click", function () {
        go(atEnd ? 0 : index);
      });
      var get = make("a", "dk-btn dk-btn-primary", TEXT.cta + " →");
      get.href = enquiryUrl;
      get.target = "_blank";
      get.rel = "noopener noreferrer";
      nav.appendChild(back);
      nav.appendChild(get);
      panel.appendChild(nav);
      spot.style.display = "none";
      panel.focus();
    }

    function go(i) {
      index = Math.max(0, Math.min(stops.length - 1, i));
      var rect = stops[index].node.getBoundingClientRect();
      panel.classList.toggle("dk-left", rect.left + rect.width / 2 > window.innerWidth * 0.55);
      render();
      scrollTo(stops[index].node);
      panel.focus();
    }

    function start() {
      if (running) return;
      if (!layer) build();
      listeners.forEach(function (fn) {
        fn();
      });
      running = true;
      lastFocus = document.activeElement;
      document.documentElement.classList.add("dk-xray");
      layer.hidden = false;
      panel.hidden = false;
      toggle.setAttribute("aria-pressed", "true");
      track();
      go(index);
    }

    function stop_() {
      if (!running) return;
      running = false;
      cancelAnimationFrame(frame);
      document.documentElement.classList.remove("dk-xray");
      layer.hidden = true;
      panel.hidden = true;
      toggle.setAttribute("aria-pressed", "false");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    toggle.addEventListener("click", function () {
      if (running) stop_();
      else start();
    });
    document.addEventListener("keydown", function (event) {
      if (!running) return;
      if (event.key === "Escape") stop_();
      else if (event.key === "ArrowRight") go(index + 1);
      else if (event.key === "ArrowLeft") go(index - 1);
    });

    api.available = true;
    api.start = start;
    api.stop = stop_;
    api.running = function () {
      return running;
    };
    return api;
  }

  // ---- Mobile action bar (phones only, via CSS) ----
  function buildMobileBar(bar, root) {
    var nav = make("nav", "dk-mbar");
    nav.setAttribute("aria-label", t(bar.action && bar.action.label) || TEXT.call);
    function demoContact(label, className) {
      var item = button(className, label);
      item.addEventListener("click", function () {
        showFormNotice(TEXT.contactBody);
      });
      nav.appendChild(item);
    }
    if (bar.call) demoContact(TEXT.call, "");
    if (bar.whatsapp) demoContact(TEXT.whatsapp, "dk-wa");
    if (bar.action) {
      var action = make("a", "dk-act", t(bar.action.label));
      action.href = bar.action.href;
      nav.appendChild(action);
    }
    root.appendChild(nav);
    document.documentElement.classList.add("dk-has-mbar");
  }

  // ---- Scroll nudge: once, after the visitor has scrolled past a section ----
  function buildNudge(nudge, root, tourApi) {
    var section = document.querySelector(nudge.after);
    if (!section) return;
    var box = make("div", "dk-nudge");
    box.setAttribute("role", "status");
    box.appendChild(make("span", null, t(nudge.text)));
    var action = make("a", null, t(nudge.action.label));
    action.href = nudge.action.href;
    box.appendChild(action);
    var close = button("dk-close", "×");
    close.setAttribute("aria-label", TEXT.close);
    box.appendChild(close);
    box.hidden = true;
    root.appendChild(box);

    var shown = false;
    function hide() {
      box.classList.remove("dk-in");
      setTimeout(function () {
        box.hidden = true;
      }, 400);
    }
    close.addEventListener("click", hide);
    function check() {
      if (shown || tourApi.running()) return;
      if (section.getBoundingClientRect().bottom < window.innerHeight * 0.5) {
        shown = true;
        window.removeEventListener("scroll", check);
        box.hidden = false;
        requestAnimationFrame(function () {
          box.classList.add("dk-in");
        });
        setTimeout(hide, 12000);
      }
    }
    window.addEventListener("scroll", check, { passive: true });
    tourApi.onStart(hide);
  }


  function init() {
    addNoindex();
    addBar();
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", loadExtras);
    } else {
      loadExtras();
    }
  }
  // At the top of <body> the body already exists: add the bar now, before first paint.
  // (Loaded from <head> or with defer, it falls back to waiting for the DOM.)
  if (document.body) {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
