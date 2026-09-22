/* Optional privacy-first analytics. Disabled until a Cloudflare Web Analytics beacon token is supplied. */
(function () {
  "use strict";
  const CLOUDFLARE_BEACON_TOKEN = "";
  if (!CLOUDFLARE_BEACON_TOKEN || !/^[a-zA-Z0-9-]{20,100}$/.test(CLOUDFLARE_BEACON_TOKEN)) return;
  if (document.querySelector("script[data-cf-beacon]")) return;
  const beacon = document.createElement("script");
  beacon.type = "module";
  beacon.src = "https://static.cloudflareinsights.com/beacon.min.js";
  beacon.setAttribute("data-cf-beacon", JSON.stringify({ token: CLOUDFLARE_BEACON_TOKEN, spa: false }));
  document.head.appendChild(beacon);
})();
