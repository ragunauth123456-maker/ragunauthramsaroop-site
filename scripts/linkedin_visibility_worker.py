"""Executive visibility audit, editorial staging and measurement. No auto-DMs or platform scraping."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse, csv, json, re, struct
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent.parent
CAMPAIGN=ROOT/'marketing'/'linkedin-visibility'/'campaign.json'
LOCAL_TIMEZONE=timezone(timedelta(hours=-4))
def image_dimensions(path):
    data=path.read_bytes()[:24]
    if data[:8]!=b'\x89PNG\r\n\x1a\n':return None
    return struct.unpack('>II',data[16:24])
def check_site():
    problems=[];checks={}
    page=ROOT/'executive-search'/'index.html'
    html=page.read_text(encoding='utf-8') if page.exists() else ''
    sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
    checks['landing_exists']=bool(html)
    checks['canonical_ok']='<link rel="canonical" href="https://ragunauthramsaroop.com/executive-search/">' in html
    checks['profile_link_ok']='https://www.linkedin.com/in/ragunauth-ramsaroop/' in html
    checks['person_schema_ok']='"@type":"Person"' in html and '"@type":"ProfilePage"' in html
    checks['sitemap_ok']='<loc>https://ragunauthramsaroop.com/executive-search/</loc>' in sitemap
    checks['social_image_ok']=image_dimensions(ROOT/'assets'/'preview.png') in ((1200,628),(1200,630)) if (ROOT/'assets'/'preview.png').exists() else False
    checks['consent_loader_ok']='/tools/assets/analytics-loader.js' in html
    for k,v in checks.items():
        if not v:problems.append(k)
    return checks,problems
def editorial_queue(now):
    conf=json.loads(CAMPAIGN.read_text(encoding='utf-8'))
    pending=[p for p in conf['posts'] if p['status']!='published']
    pending.sort(key=lambda p:p['date'])
    current=next((p for p in pending if p['date']>=now.isoformat()),pending[0] if pending else None)
    return conf,pending,current
def measurable_traffic(csv_path):
    if not csv_path.is_file():return {'state':'not_connected','note':'No actual referral export supplied. Do not infer clicks.'}
    with csv_path.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    relevant=[r for r in rows if 'executive_visibility' in str(r.get('utm_campaign',''))]
    return {'state':'csv_export','rows':len(relevant),'note':'Rows are export records, not verified unique visitors.'}
def outreach_templates(url):
    return {
      'search_partner':f'''Subject: Executive experience | ESG, External Affairs and Government Relations\n\nDear [Recruiter Name],\n\nI would welcome a conversation about director-level and country-facing leadership mandates involving ESG, corporate affairs, government relations, regulatory strategy and responsible resource development. I currently serve as Liaison Director at AGM Inc., with more than 12 years across multinational mining, financial services and commercial operations.\n\nMy professional record: {url}\nLinkedIn: https://www.linkedin.com/in/ragunauth-ramsaroop/\n\nBest regards,\nRagunauth Ramsaroop''',
      'ceo_intro':f'''Subject: Professional introduction | Institutional leadership and responsible growth\n\nDear [CEO Name],\n\nYour organisation's work in [specific verified initiative] prompted me to introduce my background in corporate affairs, government and regulatory engagement, ESG and stakeholder strategy in multinational mining. I publish independent research on governance, energy security and responsible resource development.\n\nExecutive portfolio: {url}\n\nKind regards,\nRagunauth Ramsaroop'''
    }
def run(output_dir):
    output_dir.mkdir(parents=True,exist_ok=True)
    now=datetime.now(LOCAL_TIMEZONE)
    checks,issues=check_site()
    campaign,pending,next_post=editorial_queue(now)
    traffic=measurable_traffic(output_dir/'utm_export.csv')
    report={'generated_at':now.isoformat(),'profile':campaign['profile'],
        'landing_page':campaign['landing_page'],'checks':checks,'issues':issues,
        'drafts_pending':len(pending),'next_post_date':next_post['date'] if next_post else None,
        'next_post_topic':next_post['topic'] if next_post else None,
        'next_post_status':next_post['status'] if next_post else None,
        'measurement':traffic,
        'platform_posting':'manual approval or authorized LinkedIn scheduler only',
        'mass_outreach':False}
    (output_dir/'visibility_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if next_post:
        draft='Audience: '+next_post['audience']+'\nPlanned: '+next_post['date']+'\nStatus: '+next_post['status']+'\n\n'+next_post['text']+'\n'
        (output_dir/'next_linkedin_draft.txt').write_text(draft,encoding='utf-8')
    templates=outreach_templates(campaign['landing_page'])
    (output_dir/'targeted_introduction_templates.txt').write_text('\n\n'.join(templates.values()),encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 1 if issues else 0
if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',type=Path,default=ROOT/'marketing'/'linkedin-visibility'/'local-output')
    args=cli.parse_args()
    raise SystemExit(run(args.output))
