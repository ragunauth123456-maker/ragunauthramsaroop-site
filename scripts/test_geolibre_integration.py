"""Verify safe, discoverable GeoLibre integration without contacting a third party."""
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools/geolibre/index.html"
JS = ROOT / "tools/geolibre/geolibre.js"
URL = "https://ragunauthramsaroop.com/tools/geolibre/"


class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


assert PAGE.is_file() and JS.is_file(), "GIS integration files missing"
page = PAGE.read_text(encoding="utf-8")
js = JS.read_text(encoding="utf-8")
html = Audit()
html.feed(page)

assert any(tag == "link" and a.get("rel") == "canonical" and a.get("href") == URL
           for tag, a in html.tags), "Missing canonical URL"
assert any(tag == "button" and a.get("id") == "launch-geolibre" for tag, a in html.tags), "Launch control missing"
assert any(tag == "div" and a.get("id") == "gis-stage" for tag, a in html.tags), "Embed stage missing"
assert not any(tag == "iframe" and a.get("src") for tag, a in html.tags), "No GIS iframe at first paint"
assert any(tag == "script" and a.get("src") == "/tools/geolibre/geolibre.js"
           for tag, a in html.tags), "Missing deferred GIS controller"
assert 'iframe.src = APP_URL' in js and 'launch.addEventListener("click"' in js, "GIS must load only on click"
assert 'iframe.setAttribute("loading", "lazy")' in js, "Missing lazy iframe loading"
assert '"https://web.geolibre.app/?layout=compact&welcome=0"' in js, "Expected official full-app embed"
assert 'stage.replaceChildren()' in js, "Closing the iframe should unload external resources"
assert 'rel="noopener noreferrer"' in page, "External tab links must be safe"

home = (ROOT / "tools/index.html").read_text(encoding="utf-8")
assert '/tools/geolibre/' in home, "GIS link missing from tools directory"
# The link must be a directory card, not merely a featured link outside the searchable grid.
grid = home.split('id="tool-grid">', 1)[1].split("</section>", 1)[0]
listing = Audit()
listing.feed(grid)
geo_cards = [a for tag, a in listing.tags if tag == "a"
             and a.get("data-slug") == "geolibre"
             and a.get("href") == "/tools/geolibre/"
             and a.get("data-group") == "Research & Investment"
             and "card" in a.get("class", "").split()]
assert len(geo_cards) == 1, "Exactly one GeoLibre card must appear in the searchable grid"
assert "GeoLibre GIS Workspace" in grid, "GeoLibre card needs searchable text"
assert 'id="visible-tool-count">27</strong>' in home, "Directory count must include the integration"
assert '1 independent GIS integration' in home, "Do not misrepresent GeoLibre as an RR-developed tool"
assert 'position":27' in home, "Directory structured data must include GeoLibre"
hub = (ROOT / "tools/assets/tools-hub.js").read_text(encoding="utf-8")
assert 'document.querySelectorAll("#tool-grid .card")' in hub
assert 'c.textContent' in hub and 'c.dataset.slug' in hub, "Search must include card names"

category_page = (ROOT / "tools/categories/research-investment/index.html").read_text(encoding="utf-8")
assert 'data-slug="geolibre"' in category_page, "Research category must list GeoLibre"
import json
catalog = json.loads((ROOT / "api/v1/catalog.json").read_text(encoding="utf-8"))
assert len(catalog["tools"]) == 26, "Existing 26 tools must remain unchanged"
integration = [x for x in catalog.get("integrations", []) if x.get("url") == "/tools/geolibre/"]
assert len(integration) == 1 and integration[0].get("type") == "third-party-integration", "Independent GIS attribution missing"
index = json.loads((ROOT / "assets/search-index.json").read_text(encoding="utf-8"))
search_results = [x for x in index.get("documents", []) if x.get("url") == "/tools/geolibre/"]
assert len(search_results) == 1 and search_results[0].get("type") == "Tool", "GeoLibre missing from global search"

for sitemap in ("sitemap.xml", "tools/sitemap.xml"):
    root = ET.parse(ROOT / sitemap).getroot()
    locations = [node.text or "" for node in root.iter() if node.tag.endswith("loc")]
    assert URL in locations, "GIS URL missing from " + sitemap

print("PASS GeoLibre: searchable directory card, 27-resource count, research category, global index, third-party attribution and lazy iframe")
