"""Non-destructive weekly external availability check. Runs on GitHub Actions."""
import urllib.request,sys
BASE="https://ragunauthramsaroop.com"
paths=["/","/start/","/resources/","/methodology/","/evidence/","/guides/","/tools/","/tools/esg-readiness/","/tools/mining-carbon-calculator/","/tools/water-demand-calculator/","/tools/assets/og/rr-free-tools.png"]
bad=[]
for path in paths:
    req=urllib.request.Request(BASE+path,headers={"User-Agent":"RR-free-tools-healthcheck/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=18) as r:
            code=r.status
            typ=r.headers.get("content-type","")
            if code!=200:bad.append((path,str(code)))
            elif path.endswith(".png") and "image/png" not in typ:bad.append((path,"unexpected content type "+typ))
            print("CHECK",path,code,typ)
    except Exception as e:bad.append((path,str(e)));print("FAIL",path,e)
sys.exit(1 if bad else 0)
