/* Optional, free analytics: nothing loads until the site owner supplies an ID. */
(function () {
  "use strict";
  const COUNTER_SITE_ID = "";
  const CLOUDFLARE_BEACON_TOKEN = "";
  const id = COUNTER_SITE_ID.trim();
  if (/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(id)) {
    if (document.querySelector('script[data-id="'+id+'"]')) return;
    const script = document.createElement("script");
    script.src = "https://cdn.counter.dev/script.js";
    script.async = true;
    script.dataset.id = id;
    script.dataset.utcoffset = "-4";
    document.head.appendChild(script);
    return;
  }
  if (CLOUDFLARE_BEACON_TOKEN && /^[a-zA-Z0-9-]{20,100}$/.test(CLOUDFLARE_BEACON_TOKEN)) {
    if (document.querySelector("script[data-cf-beacon]")) return;
    const script = document.createElement("script");
    script.src = "https://static.cloudflareinsights.com/beacon.min.js";
    script.defer = true;
    script.setAttribute("data-cf-beacon", JSON.stringify({token:CLOUDFLARE_BEACON_TOKEN,spa:false}));
    document.head.appendChild(script);
  }
})();
