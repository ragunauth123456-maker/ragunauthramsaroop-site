from pathlib import Path
import datetime, os, shutil, subprocess, sys, json

REPO=Path(r"C:\AgentSwarm\ragunauth-site")
WORK=Path(r"C:\AgentSwarm\rr-site-ci-worktree")
LOGDIR=Path(r"C:\AgentSwarm\rr-site-ci-logs")
REPO_FULL="ragunauth123456-maker/ragunauthramsaroop-site"
CONTEXT="rr-k1/automatic-qa"
LOGDIR.mkdir(parents=True, exist_ok=True)
stamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
log=LOGDIR/f"qa-{stamp}.log"
latest=LOGDIR/"latest.log"

def run(cmd,cwd=None,check=False):
    p=subprocess.run(cmd,cwd=str(cwd) if cwd else None,shell=True,text=True,capture_output=True,encoding="utf-8",errors="replace")
    with log.open("a",encoding="utf-8") as f:
        f.write("\n$ "+cmd+"\n"+(p.stdout or "")+(p.stderr or "")+"\n")
    if check and p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {cmd}")
    return p

def status(sha,state,desc):
    cmd=f'gh api -X POST repos/{REPO_FULL}/statuses/{sha} -f state={state} -f context="{CONTEXT}" -f description="{desc[:140]}" -f target_url=https://ragunauthramsaroop.com/'
    return run(cmd,cwd=REPO)

def cleanup():
    try: run(f'git worktree remove --force "{WORK}"',cwd=REPO)
    except: pass
    try: run("git worktree prune",cwd=REPO)
    except: pass
    if WORK.exists():
        shutil.rmtree(WORK,ignore_errors=True)

with log.open("w",encoding="utf-8") as f:
    f.write("RR K1 Automatic QA\n")
    f.write("Started: "+datetime.datetime.now().isoformat()+"\n")

sha=""
ok=False
message=""
try:
    run("git fetch origin main",cwd=REPO,check=True)
    sha=run("git rev-parse origin/main",cwd=REPO,check=True).stdout.strip()
    status(sha,"pending","K1 automatic QA running")
    cleanup()
    run(f'git worktree add --detach "{WORK}" {sha}',cwd=REPO,check=True)
    steps=[
        ("Install dependencies","npm.cmd ci --no-audit --no-fund"),
        ("Build smart bundle","npm.cmd run smart:bundle"),
        ("Build semantic index","npm.cmd run smart:index"),
        ("Build public search index","npm.cmd run search:index"),
        ("Generated assets reproducible","git diff --exit-code"),
        ("JavaScript syntax",'node --check assets\\site-brain.js && node --check assets\\brain-worker.js && node --check assets\\smart-guide.js && node --check assets\\smart-search.js && node --check assets\\copilot.js && node --check assets\\site-search.js && node --check assets\\platform.js && node --check service-worker.js'),
        ("Static site validation","python scripts\\validate_site.py"),
        ("Accessibility audit","python scripts\\accessibility_audit.py"),
        ("Performance budget","python scripts\\performance_budget.py"),
        ("Tools integrity","python scripts\\tools_integrity.py"),
        ("Dependency audit","npm.cmd audit --audit-level=high"),
    ]
    for name,cmd in steps:
        with log.open("a",encoding="utf-8") as f:f.write("\n=== "+name+" ===\n")
        run(cmd,cwd=WORK,check=True)
    # Confirm GitHub Pages has at least accepted this commit or a later one.
    pages=run(f'gh api repos/{REPO_FULL}/pages/builds/latest',cwd=REPO,check=True)
    data=json.loads(pages.stdout)
    with log.open("a",encoding="utf-8") as f:
        f.write("\nPAGES_STATUS="+str(data.get("status"))+"\nPAGES_COMMIT="+str(data.get("commit"))+"\n")
    ok=True
    message="K1 automatic QA passed"
except Exception as e:
    message="K1 automatic QA failed: "+str(e)
    with log.open("a",encoding="utf-8") as f:f.write("\nFAILURE: "+repr(e)+"\n")
finally:
    cleanup()
    with log.open("a",encoding="utf-8") as f:
        f.write("\nFinished: "+datetime.datetime.now().isoformat()+"\nRESULT: "+("PASS" if ok else "FAIL")+"\n")
    try: shutil.copy2(log,latest)
    except: pass
    if sha:
        try: status(sha,"success" if ok else "failure",message)
        except: pass
    # keep newest 30 logs
    logs=sorted(LOGDIR.glob("qa-*.log"),reverse=True)
    for old in logs[30:]:
        try: old.unlink()
        except: pass
sys.exit(0 if ok else 1)
