"""Public career-page research worker. Read-only; does not send messages or submit forms."""
import argparse
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

SENIOR = re.compile(r"\b(?:chief|director|vice[- ]president|\bvp\b|head of|general manager|regional manager|country manager|senior manager)\b", re.I)
DOMAIN = re.compile(r"\b(?:esg|sustainab\w*|government|public affairs|corporate affairs|community|social performance|stakeholder|regulatory|energy|climate|environment\w*|responsib\w*|external affairs|supply chain|sourcing|institutional|strategic partnership\w*)\b", re.I)
WHITESPACE = re.compile(r"\s+")


def safe_public_url(url):
    parsed = urlparse(url)
    return (parsed.scheme == "https" and bool(parsed.hostname) and
            parsed.hostname.lower() not in {"localhost", "127.0.0.1", "::1"} and
            not parsed.username and not parsed.password and parsed.port in (None, 443))


class CareerLinks(HTMLParser):
    """Extract displayed anchor text and URLs; never execute embedded page code."""
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links = []
        self.href = None
        self.words = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_depth += 1
        if tag == "a" and not self.skip_depth:
            self.href = dict(attrs).get("href")
            self.words = []

    def handle_data(self, data):
        if self.href is not None and not self.skip_depth:
            self.words.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            label = WHITESPACE.sub(" ", " ".join(self.words)).strip()
            url = urljoin(self.base_url, self.href)
            if safe_public_url(url) and 8 <= len(label) <= 160:
                self.links.append({"title": label, "url": url})
            self.href = None
            self.words = []
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1


def extract_possible_roles(html, base_url, limit=25):
    parser = CareerLinks(base_url)
    parser.feed(html)
    results, seen = [], set()
    for link in parser.links:
        if SENIOR.search(link["title"]) and DOMAIN.search(link["title"]):
            key = link["url"].lower()
            if key not in seen:
                seen.add(key)
                results.append({**link, "verification": "UNVERIFIED_POSSIBLE_ROLE"})
        if len(results) >= limit:
            break
    return results


def fetch_html(url, timeout=15):
    if not safe_public_url(url):
        raise ValueError("Only public HTTPS company careers URLs are permitted")
    request = Request(url, headers={"User-Agent": "RR-careers-research/1.0 (public read-only)"})
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        if not safe_public_url(final_url):
            raise ValueError("Unsafe redirect from official careers page")
        mime = response.headers.get("Content-Type", "")
        if "html" not in mime.lower():
            raise ValueError("Source did not return HTML")
        raw = response.read(800001)
        if len(raw) > 800000:
            raise ValueError("Public page exceeded research size limit")
        return raw.decode("utf-8", errors="replace"), final_url


def research(sources, fetcher=fetch_html):
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "PUBLIC_CAREERS_RESEARCH_ONLY",
              "outbound_email_sent": 0, "applications_submitted": 0,
              "sources": []}
    for source in sources:
        item = {"company": source["company"], "official_careers_url": source["url"],
                "access": "NOT_VERIFIED", "possible_roles": []}
        try:
            if not safe_public_url(source["url"]):
                raise ValueError("Rejected non-public or non-HTTPS URL")
            html, actual_url = fetcher(source["url"])
            item["access"] = "HTML_RETRIEVED_NOT_JOB_VERIFIED"
            item["final_url"] = actual_url
            item["possible_roles"] = extract_possible_roles(html, actual_url)
            if not item["possible_roles"]:
                item["note"] = "No qualifying public HTML links found; JavaScript or search may be required."
        except Exception as error:
            item["access"] = "FETCH_FAILED"
            item["note"] = str(error)[:180]
        report["sources"].append(item)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path(__file__).with_name("executive_careers_sources.json"))
    parser.add_argument("--output", type=Path, default=Path("executive-careers-artifacts/public_research.json"))
    args = parser.parse_args()
    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    if not isinstance(sources, list) or not all(isinstance(s, dict) and s.get("company") and s.get("url") for s in sources):
        raise SystemExit("Invalid public sources configuration")
    report = research(sources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_count": len(report["sources"]),
                      "accessible_pages": sum(s["access"] == "HTML_RETRIEVED_NOT_JOB_VERIFIED" for s in report["sources"]),
                      "possible_role_links": sum(len(s["possible_roles"]) for s in report["sources"]),
                      "email_sent": 0, "applications_submitted": 0,
                      "artifact": str(args.output)}))


if __name__ == "__main__":
    main()
