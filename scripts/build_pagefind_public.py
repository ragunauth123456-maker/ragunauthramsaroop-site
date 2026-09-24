from pathlib import Path
import os, shutil
root=Path(__file__).resolve().parents[1]
dst=root/".pagefind-public"
if dst.exists(): shutil.rmtree(dst)
dst.mkdir(parents=True)
skip={"node_modules","skills","agent","pagefind"}
def keep(name): return name not in skip and (not name.startswith(".") or name==".well-known")
count=0
for base,dirs,files in os.walk(root):
    dirs[:]=[d for d in dirs if keep(d)]
    basep=Path(base)
    for name in files:
        if not name.lower().endswith(".html"): continue
        src=basep/name
        rel=src.relative_to(root)
        out=dst/rel
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,out);count+=1
print("Pagefind staging pages",count)
