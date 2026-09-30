/* RR Free Tools analytics: Google Analytics 4 with Consent Mode.
   Measurement ID is public. Analytics cookies are denied until the visitor opts in.
   Advertising storage/signals remain disabled. */
(function () {
  "use strict";
  const MEASUREMENT_ID = "G-28FHYG7T0G";
  const KEY = "rr_analytics_consent_v1";

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };

  const saved = (() => { try { return localStorage.getItem(KEY); } catch (_) { return null; } })();

  gtag("consent", "default", {
    analytics_storage: saved === "granted" ? "granted" : "denied",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    functionality_storage: "granted",
    security_storage: "granted",
    wait_for_update: 500
  });
  // Initialize third-party analytics only after explicit opt-in.
  let tagStarted = false;
  function loadAnalytics() {
    if (tagStarted) return;
    tagStarted = true;
    gtag("js", new Date());
    gtag("config", MEASUREMENT_ID, {
      send_page_view: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    const tag = document.createElement("script");
    tag.async = true;
    tag.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(MEASUREMENT_ID);
    document.head.appendChild(tag);
  }
  if (saved === "granted") loadAnalytics();

  function update(value) {
    try { localStorage.setItem(KEY, value); } catch (_) {}
    gtag("consent", "update", {
      analytics_storage: value === "granted" ? "granted" : "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    if (value === "granted") loadAnalytics();
    const el = document.getElementById("rr-analytics-choice");
    if (el) el.remove();
  }

  if (!saved && document.body) {
    const box = document.createElement("aside");
    box.id = "rr-analytics-choice";
    box.setAttribute("aria-label", "Analytics preference");
    box.innerHTML =
      '<div><strong>Optional analytics</strong><p>Analytics help improve the site. They remain off unless you choose to allow them.</p></div>' +
      '<div class="rr-analytics-actions"><button type="button" data-choice="denied">Decline</button><button type="button" class="allow" data-choice="granted">Allow</button><a href="/tools/privacy/">Privacy</a></div>';
    if (!document.querySelector('link[href="/tools/assets/analytics-consent.css"]')) {
      const style = document.createElement("link");
      style.rel = "stylesheet";
      style.href = "/tools/assets/analytics-consent.css";
      document.head.appendChild(style);
    }
    document.body.appendChild(box);
    box.querySelectorAll("[data-choice]").forEach(btn => btn.addEventListener("click", () => update(btn.dataset.choice)));
  }
})();