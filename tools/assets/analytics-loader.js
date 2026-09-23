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

  function update(value) {
    try { localStorage.setItem(KEY, value); } catch (_) {}
    gtag("consent", "update", {
      analytics_storage: value === "granted" ? "granted" : "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    const el = document.getElementById("rr-analytics-choice");
    if (el) el.remove();
  }

  if (!saved && document.body) {
    const box = document.createElement("aside");
    box.id = "rr-analytics-choice";
    box.setAttribute("aria-label", "Analytics preference");
    box.innerHTML =
      '<div><strong>Privacy-respecting analytics</strong><p>This site uses Google Analytics to understand visits and improve the free tools. Analytics cookies are off unless you allow them.</p></div>' +
      '<div class="rr-analytics-actions"><button type="button" data-choice="denied">No thanks</button><button type="button" class="allow" data-choice="granted">Allow analytics</button><a href="/tools/privacy/">Privacy</a></div>';
    const style = document.createElement("style");
    style.textContent =
      "#rr-analytics-choice{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483600;max-width:860px;margin:auto;background:#071e17;color:#eef6f2;border:1px solid rgba(255,255,255,.2);border-radius:16px;padding:16px 18px;box-shadow:0 16px 50px rgba(0,0,0,.32);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;display:flex;gap:18px;align-items:center;justify-content:space-between}#rr-analytics-choice strong{font-size:15px}#rr-analytics-choice p{margin:4px 0 0;color:#d7e5de}#rr-analytics-choice .rr-analytics-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;flex:0 0 auto}#rr-analytics-choice button,#rr-analytics-choice a{border:1px solid rgba(255,255,255,.3);border-radius:999px;padding:8px 12px;background:transparent;color:#fff;font:700 12px system-ui;cursor:pointer;text-decoration:none}#rr-analytics-choice button.allow{background:#fff;color:#08271d;border-color:#fff}@media(max-width:720px){#rr-analytics-choice{display:block;left:10px;right:10px;max-width:calc(100% - 20px);overflow-wrap:anywhere}#rr-analytics-choice .rr-analytics-actions{margin-top:12px}}@media print{#rr-analytics-choice{display:none!important}}";
    document.head.appendChild(style);
    document.body.appendChild(box);
    box.querySelectorAll("[data-choice]").forEach(btn => btn.addEventListener("click", () => update(btn.dataset.choice)));
  }
})();