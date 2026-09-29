"""Static performance regression guard for the public GitHub Pages export."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.images.append(a)

page = Page()
homepage_text = (ROOT / "index.html").read_text(encoding="utf-8")
page.feed(homepage_text)
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

check(len(page.scripts) <= 2, f"Homepage has {len(page.scripts)} external scripts; budget is 2")
check(not any("/_next/static/" in path for path in page.scripts), "Next.js runtime must not load on the homepage")
check((ROOT / "index.html").stat().st_size <= 25_000, "Homepage HTML exceeded 25 KB budget")
for path in ("/tools/assets/distribution.js", "/tools/assets/report-export.js"):
    check(path not in page.scripts, f"Tool-only script unnecessarily loaded on homepage: {path}")

hero_url = "/assets/preview.png"
check("ragunauth-ramsaroop.floot.app" not in homepage_text, "Homepage must not depend on the legacy Floot image host")
check('http-equiv="Content-Security-Policy"' in homepage_text, "Homepage must enforce a Content Security Policy")
check("'unsafe-inline'" not in homepage_text, "Homepage CSP must not permit unsafe-inline")
check(any(x.get("rel") == "preload" and x.get("as") == "image" and x.get("href") == hero_url
          and x.get("fetchpriority") == "high" for x in page.links), "Missing early high-priority self-hosted hero preload")
check(any(x.get("class") == "portrait" and x.get("fetchpriority") == "high"
          and x.get("width") and x.get("height") for x in page.images),
      "Hero must reserve dimensions and load with high priority")

sw = (ROOT / "service-worker.js").read_text(encoding="utf-8")
match = re.search(r"const CORE=\[([\s\S]*?)\];", sw)
urls = re.findall(r'"(/[^"]+)"', match.group(1)) if match else []
check(bool(match), "Service worker precache not found")
check(len(urls) <= 8, f"Service worker precaches {len(urls)} resources; budget is 8")
check(not any("index.json" in u or u.endswith(".wasm") for u in urls),
      "Large indexes and model assets must be fetched on demand")
check('const V="rr-public-v11"' in sw, "Service worker version must be v11")
check("/assets/home.css" in urls, "Dedicated homepage stylesheet must be available offline")
check("/assets/accessibility.css" in urls, "Accessibility stylesheet must be available offline")
check("/assets/site.css" in urls, "Primary site stylesheet must be available offline")
check("/tools/assets/tools.css" in urls, "Tools stylesheet must be available offline")
check('cache.match("/start/")' not in sw, "Never serve the Start page as a fallback for unrelated URLs")
check('status:503' in sw, "Unknown offline navigation must return an explicit 503")
check('k.startsWith("rr-public-v")' in sw, "Only RR-managed caches should be deleted")
check("validStaticResponse" in sw and 'type.includes("text/css")' in sw, "Cached CSS must be MIME-validated before reuse")

platform = (ROOT / "assets/platform.js").read_text(encoding="utf-8")
platform_compact = "".join(platform.split())
check("afterLoadIdle" in platform
      and 'elseif(location.pathname!=="/")afterLoadIdle(startBrain,4500);' in platform_compact
      and 'elseafterLoadIdle(startBrain,12000);' in platform_compact,
      "Site Brain must defer on secondary pages and the homepage")
accessibility = (ROOT / "assets/accessibility.js").read_text(encoding="utf-8")
check('createElement("style")' not in accessibility, "Accessibility helper must not inject inline style under strict CSP")
analytics = (ROOT / "tools/assets/analytics-loader.js").read_text(encoding="utf-8")
check('if (saved === "granted") loadAnalytics()' in analytics,
      "Third-party analytics must not load before consent")
check('if (value === "granted") loadAnalytics()' in analytics,
      "Analytics must initialize after consent")
check('createElement("style")' not in analytics, "Analytics consent UI must not inject inline style under strict CSP")

home_css = ROOT / "assets/home.css"
check(home_css.exists() and home_css.stat().st_size <= 15_000, "Homepage CSS exceeded 15 KB budget")
css = ROOT / "_next/static/css/5a81eca963785de4.css"
check(css.exists() and css.stat().st_size <= 235_000, "Main CSS exceeded size baseline; review before shipping")
search = ROOT / "assets/search-index.json"
check(search.exists() and search.stat().st_size <= 400_000, "Search index exceeded size baseline")

if errors:
    for error in errors:
        print("FAIL", error)
    raise SystemExit(1)

print(f"PASS: {len(page.scripts)} homepage external scripts, lightweight homepage CSS, {len(urls)} eager cache entries, priority hero, consent-gated analytics")
