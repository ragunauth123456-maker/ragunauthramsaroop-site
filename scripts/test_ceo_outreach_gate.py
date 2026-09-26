import tempfile
import unittest
from pathlib import Path
from unittest import mock
from ceo_outreach_gate import assess

class OutreachGateTests(unittest.TestCase):
    def dossier(self):
        return {
            "company":"ExampleCo", "ceo":"Verified CEO", "fortune_2026_rank":15,
            "ceo_source_url":"https://company.test/leadership",
            "strategy_sources":[{"url":"https://company.test/strategy","published_at":"2026-08-01"}],
            "value_thesis":"Align a stated corporate expansion with accountable country stakeholder commitments and traceable evidence for executive decisions.",
            "supporting_reasons":["Operational milestones depend on tracked institutional commitments.",
                                  "Environmental evidence improves executive cross-functional coordination."],
            "approved_cv_evidence":["Approved executive CV experience"],
            "contact_route":{"address":"office@company.test",
                             "type":"published-corporate-office",
                             "source_url":"https://company.test/contact"},
            "subject":"Company value discussion", "message":"The specific Minto email.",
            "attachments":{"cv_pdf":"cv.pdf","value_brief_pdf":"brief.pdf"},
            "status":"Ready"}
    def test_verified_case_passes_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ("cv.pdf","brief.pdf"):
                (root/name).write_bytes(b"%PDF" + b" " * 4096)
            parser=mock.Mock(open=lambda p: [None] * (2 if "cv" in str(p) else 1))
            with mock.patch.dict("sys.modules",{"fitz":parser}):
                self.assertEqual(assess(self.dossier(),root,set()),[])
    def test_bad_contact_and_duplicate_blocked(self):
        d=self.dossier()
        d["contact_route"]={"address":"private@gmail.com",
                             "type":"verified-professional-ceo",
                             "source_url":"https://example.com","direct_verified":False}
        issues=assess(d,Path("."),{("exampleco","private@gmail.com")})
        self.assertTrue(any("address" in x.lower() for x in issues))
        self.assertTrue(any("duplicate" in x.lower() for x in issues))
        self.assertTrue(any("verification" in x.lower() for x in issues))

if __name__=="__main__":
    unittest.main()
