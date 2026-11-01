/**
 * PayPal Smart Buttons for the order page ([data-paypal]).
 *
 * The browser only asks our server to create/capture: the amount, currency and
 * PayPal order id always come from the server, which also verifies the result.
 */
export function initPayPal() {
  const root = document.querySelector("[data-paypal]");
  if (!root) return;

  const { clientId, currency, mode, planId, reference, createUrl, captureUrl, subscriptionUrl, csrf } =
    root.dataset;
  const buttons = root.querySelector("[data-paypal-buttons]");
  const errorBox = root.querySelector("[data-paypal-error]");

  const showError = (message) => {
    errorBox.textContent = message || "Something went wrong. Please try again.";
    errorBox.classList.remove("hidden");
  };

  const post = async (url, body = {}) => {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify(body),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error);
    return data;
  };

  const finish = (data) => {
    window.location.assign(data.redirect);
  };

  const isSubscription = mode === "subscription";
  const params = new URLSearchParams({ "client-id": clientId, currency, components: "buttons" });
  if (isSubscription) {
    params.set("vault", "true");
    params.set("intent", "subscription");
  } else {
    params.set("intent", "capture");
  }

  const script = document.createElement("script");
  script.src = `https://www.paypal.com/sdk/js?${params}`;
  script.async = true;
  script.onerror = () => showError("PayPal could not be loaded. Please check your connection.");
  script.onload = () => {
    const shared = {
      style: { layout: "vertical", shape: "pill", label: isSubscription ? "subscribe" : "pay" },
      onError: () => showError(),
    };
    const flow = isSubscription
      ? {
          // PayPal ties the subscription to our order through custom_id; the server checks it.
          createSubscription: (data, actions) =>
            actions.subscription.create({ plan_id: planId, custom_id: reference }),
          onApprove: (data) =>
            post(subscriptionUrl, { subscriptionID: data.subscriptionID })
              .then(finish)
              .catch((error) => showError(error.message)),
        }
      : {
          createOrder: () => post(createUrl).then((data) => data.id),
          onApprove: () =>
            post(captureUrl)
              .then(finish)
              .catch((error) => showError(error.message)),
        };
    window.paypal.Buttons({ ...shared, ...flow }).render(buttons);
  };
  document.head.append(script);
}
