# GeoLibre GIS workspace integration

Original project: https://github.com/opengeos/GeoLibre
Official browser build: https://web.geolibre.app/
Official embed instructions: https://geolibre.app/user-guide/embedding/
Licence: MIT. Project attribution: Professor Qiusheng Wu and contributors.

RR Free Tools hosts a lightweight integration page at /tools/geolibre/ with an opt-in iframe into the official application using ?layout=compact&welcome=0. No fork, redistribution or proprietary branding of GeoLibre occurs.

Architecture and safety:
- Only the lightweight first-party page, CSS and controller script are loaded initially. The GeoLibre iframe is created after a button click.
- The full application runs at the upstream origin, not on RR's GitHub Pages hosting. Visitors may open the app directly if their browser blocks embedding or a phone viewport is narrow.
- The official hosted viewer reports website visit analytics. The application's client-side workflow does not upload local GIS files to RR servers, but remote datasets, maps and optional online services may issue external network requests.
- No API keys, remote geospatial datasets or authenticated third-party services are bundled with this integration.
- Any later self-hosted fork should preserve MIT attribution, separately account for map-tile/data licences and be isolated from the fast public homepage.

Validation:
- python scripts/test_geolibre_integration.py
- node --check tools/geolibre/geolibre.js
- python scripts/validate_site.py

Changes to the upstream application's availability and optional services are outside the host site's control. The app should remain opt-in to protect Core Web Vitals.
