(() => {
  "use strict";

  // No third-party GIS requests occur until a visitor explicitly starts the embed.
  const APP_URL = "https://web.geolibre.app/?layout=compact&welcome=0";
  const launch = document.getElementById("launch-geolibre");
  const close = document.getElementById("close-geolibre");
  const stage = document.getElementById("gis-stage");
  const status = document.getElementById("gis-status");

  if (!launch || !close || !stage || !status) return;

  launch.addEventListener("click", () => {
    if (stage.querySelector("iframe")) return;

    const iframe = document.createElement("iframe");
    iframe.id = "geolibre-frame";
    iframe.title = "GeoLibre browser-based GIS workspace";
    iframe.setAttribute("allow", "fullscreen; geolocation");
    iframe.setAttribute("loading", "lazy");
    iframe.referrerPolicy = "strict-origin-when-cross-origin";
    iframe.addEventListener("load", () => {
      status.textContent = "GeoLibre window opened. Maps and processing modules may continue loading.";
    }, { once: true });

    // Assign src only after the user has chosen to load third-party content.
    iframe.src = APP_URL;
    stage.replaceChildren(iframe);
    launch.hidden = true;
    launch.setAttribute("aria-expanded", "true");
    close.hidden = false;
    status.textContent = "Loading GeoLibre. If the frame is blocked, use Open full-screen application.";
    stage.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  close.addEventListener("click", () => {
    stage.replaceChildren();
    const placeholder = document.createElement("div");
    placeholder.className = "gis-placeholder";
    const message = document.createElement("p");
    message.textContent = "GeoLibre is closed. Launch the workspace again to reopen it.";
    placeholder.appendChild(message);
    stage.appendChild(placeholder);
    close.hidden = true;
    launch.hidden = false;
    launch.setAttribute("aria-expanded", "false");
    status.textContent = "Embedded GIS session closed.";
    launch.focus();
  });
})();
