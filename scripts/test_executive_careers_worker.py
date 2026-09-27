"""Offline tests for the public read-only executive careers research worker."""
import unittest

from executive_careers_worker import extract_possible_roles, research, safe_public_url


class CareersWorkerTests(unittest.TestCase):
    def test_safe_https_only(self):
        self.assertTrue(safe_public_url("https://jobs.cardinalhealth.com/search-jobs"))
        self.assertFalse(safe_public_url("http://jobs.cardinalhealth.com/"))
        self.assertFalse(safe_public_url("https://localhost/jobs"))
        self.assertFalse(safe_public_url("https://example.com:8080/jobs"))
        self.assertFalse(safe_public_url("javascript:alert(1)"))

    def test_extracts_only_relevant_public_roles(self):
        markup = """<a href="/roles/1"><span>Senior Director, Sustainability</span></a>
<a href="/roles/2">Warehouse Associate</a>
<a href="javascript:alert(1)">Director, Government Affairs</a>
<a href="/roles/3">VP Corporate Affairs</a>"""
        actual = extract_possible_roles(markup, "https://jobs.cardinalhealth.com/")
        self.assertEqual([role["title"] for role in actual],
                         ["Senior Director, Sustainability", "VP Corporate Affairs"])
        self.assertTrue(all(r["verification"] == "UNVERIFIED_POSSIBLE_ROLE" for r in actual))

    def test_research_never_sends_and_reports_unavailable(self):
        def fake_fetch(url):
            if "bayer" in url:
                raise RuntimeError("403")
            return '<a href="/job">Director Climate and Sustainability</a>', url
        report = research([
            {"company": "Cardinal Health", "url": "https://jobs.cardinalhealth.com/search-jobs"},
            {"company": "Bayer", "url": "https://jobs.bayer.com/"}
        ], fetcher=fake_fetch)
        self.assertEqual(report["outbound_email_sent"], 0)
        self.assertEqual(report["applications_submitted"], 0)
        self.assertEqual(report["sources"][0]["access"], "HTML_RETRIEVED_NOT_JOB_VERIFIED")
        self.assertEqual(report["sources"][1]["access"], "FETCH_FAILED")
        self.assertEqual(len(report["sources"][0]["possible_roles"]), 1)


if __name__ == "__main__":
    unittest.main()
