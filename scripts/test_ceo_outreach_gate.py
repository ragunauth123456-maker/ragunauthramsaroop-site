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
            "to":"office@company.test", "cc":"deputy@company.test",
            "cc_contact":{"full_name":"Deputy Example","current_role":"EVP Corporate Affairs",
                          "address":"deputy@company.test",
                          "professional_email_verified":True,
                          "email_source_url":"https://company.test/contact",
                          "role_source_url":"https://company.test/leadership"},
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

    def test_indirect_route_without_verified_cc_fails(self):
        d=self.dossier()
        d.pop("cc_contact")
        self.assertTrue(any("CC a named" in e for e in assess(d,Path("."),set())))
    def test_opt_out_blocks_even_verified_route(self):
        d=self.dossier()
        d["opted_out"]=True
        self.assertTrue(any("opt-out" in e for e in assess(d,Path("."),set())))
if __name__=="__main__":
    unittest.main()
