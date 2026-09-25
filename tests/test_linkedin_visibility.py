import json,unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[1]
SPEC=spec_from_file_location('visibility_worker',ROOT/'scripts'/'linkedin_visibility_worker.py')
MOD=module_from_spec(SPEC);SPEC.loader.exec_module(MOD)
class ExecutiveVisibilityTests(unittest.TestCase):
 def test_site_checks(self):
  checks,errors=MOD.check_site()
  self.assertEqual(errors,[],str(checks))
 def test_campaign_has_real_linked_profile(self):
  campaign=json.loads((ROOT/'marketing'/'linkedin-visibility'/'campaign.json').read_text())
  self.assertEqual(campaign['profile'],'https://www.linkedin.com/in/ragunauth-ramsaroop/')
  self.assertGreaterEqual(len(campaign['posts']),4)
  self.assertTrue(all(p['status']!='published' for p in campaign['posts']))
 def test_posting_frequency(self):
  campaign=json.loads((ROOT/'marketing'/'linkedin-visibility'/'campaign.json').read_text())
  self.assertTrue(campaign['publishing_rules']['no_mass_direct_messages'])
  from datetime import datetime
  dates=[datetime.fromisoformat(p['date']) for p in campaign['posts']]
  self.assertEqual(dates,sorted(dates))
  self.assertEqual(len(dates),len(set(dates)))
if __name__=='__main__':unittest.main()
