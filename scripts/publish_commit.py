"""One-time verified publication release. Stop on any failed quality gate."""
from pathlib import Path
import subprocess, sys, json
repo=Path(__file__).resolve().parents[1]
def cmd(args,timeout=110):
    p=subprocess.run(args,cwd=repo,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
    print("RESULT",args[:3],p.returncode,"STDOUT",(p.stdout or "")[-900:],"STDERR",(p.stderr or "")[-350:],flush=True)
    return p
quality=cmd(["python","scripts/validate_site.py"])
if quality.returncode:sys.exit("Quality checks failed. No push.")
stage=cmd(["git","add","README.md","sitemap.xml","white-papers","research-library","research-papers","scripts/publish_research_archive.py","scripts/publish_commit.py"])
if stage.returncode:sys.exit("Staging failed.")
if cmd(["git","diff","--cached","--check"]).returncode:sys.exit("Diff checks failed.")
cmd(["git","diff","--cached","--stat"])
commit=cmd(["git","-c","user.name=Ragunauth Ramsaroop","-c","user.email=ragunauthramsaroop@icloud.com","commit","-m","Publish verified research PDF library and repository-ready metadata"])
if commit.returncode:sys.exit("Commit failed.")
auth=cmd(["gh","auth","setup-git"],20)
if auth.returncode:sys.exit("GitHub Git authorization failed.")
push=cmd(["git","push","-u","origin","publish/research-archive-2026-09-25"],110)
if push.returncode:sys.exit("Push failed. Local branch and files remain safe.")
pr=cmd(["gh","pr","create","--base","main","--head","publish/research-archive-2026-09-25","--title","Publish verified full-text research archive","--body","Seven independently authored PDFs validated for author attribution and PDF integrity. Adds dedicated landing pages, direct downloads, existing-summary links, citation metadata, RSS feed, sitemap, checksums and Zenodo submission metadata. QA: static site validation passes. External Zenodo and SSRN deposits remain pending account access and rights selection."],75)
if pr.returncode:sys.exit("Branch pushed; PR creation needs attention.")
merge=cmd(["gh","pr","merge","--squash","--delete-branch"],110)
print("RELEASE",json.dumps({"qa_passed":True,"pdfs":7,"branch_pushed":True,"pull_request":pr.stdout.strip(),"merged":merge.returncode==0}),flush=True)
if merge.returncode:sys.exit("Pull request is open but not merged.")
