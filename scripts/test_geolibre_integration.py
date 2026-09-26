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
for sitemap in ("sitemap.xml", "tools/sitemap.xml"):
    root = ET.parse(ROOT / sitemap).getroot()
    locations = [node.text or "" for node in root.iter() if node.tag.endswith("loc")]
    assert URL in locations, "GIS URL missing from " + sitemap

print("PASS GeoLibre: discoverable route, canonical URL, user-triggered iframe and safe fallbacks")
