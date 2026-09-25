"""K1 free executive visibility coordinator. Only authorized first-party publishing."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=Path.home()/'linkedin_profile_update'/'visibility-reports'
def run(args,timeout=80):
    try:
        p=subprocess.run(args,cwd=ROOT,timeout=timeout,text=True,encoding='utf-8',errors='replace',capture_output=True)
        return {'exit':p.returncode,'output':(p.stdout or '')[-1800:],'error':(p.stderr or '')[-500:]}
    except Exception as e:return {'exit':-1,'error':str(e)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--no-fetch',action='store_true',help='Offline QA mode')
    ap.add_argument('--no-indexnow',action='store_true',help='Skip submission during local tests')
    ap.add_argument('--output',type=Path,default=OUT)
    x=ap.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    report={'checked_at':datetime.now(timezone(timedelta(hours=-4))).isoformat(),'runner':'K1 executive visibility','publishing':'LinkedIn native scheduling; no auto-DMs or third-party posting without authorization'}
    before=run(['git','rev-parse','HEAD'])
    report['previous_commit']=before['output'].strip()
    if not x.no_fetch:
        fetch=run(['git','fetch','--depth=50','origin','main'])
        report['git_fetch_exit']=fetch['exit']
        if fetch['exit']==0:
            merge=run(['git','merge','--ff-only','origin/main'])
            report['git_fast_forward_exit']=merge['exit']
            if merge['exit']:report['git_sync_issue']=merge.get('error') or merge.get('output')
        else:report['git_sync_issue']=fetch.get('error')
    after=run(['git','rev-parse','HEAD'])
    report['commit']=after['output'].strip()
    report['source_updated']=report['commit']!=report['previous_commit']
    worker=run([sys.executable,str(ROOT/'scripts'/'linkedin_visibility_worker.py'),'--output',str(x.output)])
    report['visibility_worker_exit']=worker['exit']
    if worker['exit']:report['visibility_worker_issue']=worker.get('error') or worker.get('output')
    page=ROOT/'executive-perspectives'/'index.html'
    report['executive_brief_exists']=page.exists()
    report['draft_queue_exists']=(x.output/'next_linkedin_draft.txt').exists()
    postiz=shutil.which('postiz.cmd') or shutil.which('postiz')
    if postiz:
        auth=run([postiz,'auth:status'],timeout=15)
        auth_text=((auth.get('output') or '')+' '+(auth.get('error') or '')).lower()
        integrations=run([postiz,'integrations:list'],timeout=20)
        response=((integrations.get('output') or '')+' '+(integrations.get('error') or '')).lower()
        if 'no subscription found' in response:
            report['postiz_authentication']='device_authorized'
            report['postiz_publishing']='blocked_hosted_subscription'
        elif integrations['exit']==0 and 'no authentication' not in response and 'error' not in response:
            report['postiz_authentication']='connected'
            report['postiz_publishing']='integration_check_required'
        elif 'not authenticated' in auth_text or 'no authentication' in response or 'invalid' in auth_text:
            report['postiz_authentication']='not_authenticated_or_invalid'
            report['postiz_publishing']='unavailable'
        else:
            report['postiz_authentication']='unverified'
            report['postiz_publishing']='unavailable'
    else:
        report['postiz_authentication']='not_installed'
        report['postiz_publishing']='unavailable'
    report['free_native_linkedin_scheduler']='available_separately'
    if not x.no_indexnow:
        pages=run(['gh','api','repos/ragunauth123456-maker/ragunauthramsaroop-site/pages/builds/latest','--jq','{status,commit}'],timeout=20)
        try:build=json.loads(pages.get('output','')) if pages['exit']==0 else {}
        except ValueError:build={}
        report['github_pages_status']=build.get('status','not_verified')
        if build.get('status')=='built' and build.get('commit')==report['commit']:
            indexed=run([sys.executable,str(ROOT/'scripts'/'indexnow_submit.py'),'--changed-only'],timeout=40)
            report['indexnow_exit']=indexed['exit']
            report['indexnow_response']=indexed.get('output') or indexed.get('error')
        else:report['indexnow_response']='Deferred: current commit is not yet verified deployed by GitHub Pages.'
    (x.output/'daily_runner_status.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if worker['exit']==0 else 1
if __name__=='__main__':raise SystemExit(main())
