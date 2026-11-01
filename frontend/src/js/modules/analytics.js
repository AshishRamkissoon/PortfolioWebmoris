/**
 * Privacy-first analytics: Plausible (cookieless) or GA4 after explicit consent.
 * Conversions: [data-track] clicks, [data-track-event] markers rendered by the server
 * (lead sent, purchase), and Calendly bookings.
 */

const CONSENT_KEY = "wm-analytics-consent";

function track(name, props = {}) {
  if (window.plausible) window.plausible(name, { props });
  if (window.gtag) window.gtag("event", name, props);
}

function loadGoogleAnalytics() {
  const id = document.querySelector('meta[name="ga4-id"]')?.content;
  if (!id || window.gtag) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments); // eslint-disable-line prefer-rest-params
  };
  window.gtag("js", new Date());
  window.gtag("config", id, { anonymize_ip: true });
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
  document.head.append(script);
}

function trackRenderedEvents() {
  document.querySelectorAll("[data-track-event]:not([data-tracked])").forEach((el) => {
    el.dataset.tracked = "";
    const { trackEvent, trackValue, trackCurrency } = el.dataset;
    const props = trackValue ? { value: Number(trackValue), currency: trackCurrency } : {};
    track(trackEvent, props);
  });
}

export function registerAnalytics(Alpine) {
  Alpine.data("consent", () => ({
    visible: false,
    init() {
      this.visible = !localStorage.getItem(CONSENT_KEY);
    },
    accept() {
      localStorage.setItem(CONSENT_KEY, "granted");
      this.visible = false;
      loadGoogleAnalytics();
    },
    decline() {
      localStorage.setItem(CONSENT_KEY, "denied");
      this.visible = false;
    },
  }));

  if (localStorage.getItem(CONSENT_KEY) === "granted") loadGoogleAnalytics();

  document.addEventListener("click", (event) => {
    const el = event.target.closest("[data-track]");
    if (el) track(el.dataset.track);
  });
  trackRenderedEvents();
  document.body.addEventListener("htmx:afterSettle", trackRenderedEvents);
  window.addEventListener("message", (event) => {
    if (event.origin === "https://calendly.com" && event.data?.event === "calendly.event_scheduled") {
      track("booking_scheduled");
    }
  });
}
